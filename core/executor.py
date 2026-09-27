# ============================================
"""
Executor processes planned tasks safely through Tool Registry + Safety Engine.
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.models import TaskPlan, PlanStep, StepStatus
from tools.registry import ToolRegistry, get_tool_registry
from tools.base import ToolResult, RiskLevel
from database.models import ActionLog
from safety.permissions import get_permission_manager
from safety.confirmation import get_confirmation_manager, ConfirmationRequest
from safety.emergency_stop import get_emergency_stop
from app.config import config as app_config
from app.logging_config import logger


class Executor:
    """
    Executes PlanStep list via Tool Registry, handling permissions and confirmations.
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or get_tool_registry()
        self.perm_manager = get_permission_manager()
        self.confirm_manager = get_confirmation_manager()
        self.emergency_stop = get_emergency_stop()

    def execute_plan(self, plan: TaskPlan, on_step_callback=None) -> Dict[str, Any]:
        """
        Executes each step of a TaskPlan safely and sequentially.
        """
        results: List[Dict[str, Any]] = []
        overall_success = True

        for step in plan.steps:
            if self.emergency_stop.is_stopped():
                step.status = StepStatus.CANCELLED
                step.result = "Cancelled by Emergency Stop"
                results.append(step.model_dump())
                break

            if step.status != StepStatus.PENDING:
                continue

            step.status = StepStatus.RUNNING
            if on_step_callback:
                on_step_callback(step)

            try:
                result = self._execute_step(step)
                results.append(result)
                if not result.get("success", False):
                    overall_success = False
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                results.append({
                    "step": step.id,
                    "success": False,
                    "error": str(e),
                })
                overall_success = False

        plan.status = "COMPLETED" if overall_success else "FAILED"
        return {"success": overall_success, "steps": results}

    def _execute_step(self, step: PlanStep) -> Dict[str, Any]:
        tool = self.registry.get(step.tool)
        if not tool:
            step.status = StepStatus.FAILED
            return {"step": step.id, "success": False, "error": f"Tool '{step.tool}' not found"}

        # Risk check + Confirmation for HIGH risk tools
        if tool.risk_level == RiskLevel.HIGH:
            req = ConfirmationRequest(
                tool_name=step.tool,
                arguments=step.arguments,
                risk_level=tool.risk_level,
                description=step.objective,
            )
            approved = self.confirm_manager.request_confirmation(
                tool_name=req.tool_name,
                arguments=req.arguments,
                risk_level=req.risk_level,
                description=req.description,
            )
            if not approved:
                step.status = StepStatus.CANCELLED
                step.result = "Cancelled by user"
                return {"step": step.id, "success": False, "error": "Cancelled by user"}

        # Validate path args if filesystem tool
        validated_args = self._validate_tool_args(tool, step.arguments)

        # Execute
        start_time = time.time()
        result: ToolResult = self.registry.execute_tool(step.tool, validated_args)
        duration_ms = int((time.time() - start_time) * 1000)

        # Verify
        verified = True
        if tool.verify:
            verified = tool.verify(result, **validated_args)

        step.status = StepStatus.COMPLETED if result.success else StepStatus.FAILED
        step.result = result.to_summary()
        step.error = result.error

        # Log action audit
        self._log_audit(tool, validated_args, result, duration_ms)

        return {
            "step": step.id,
            "tool": step.tool,
            "success": result.success,
            "verified": verified,
            "result": result.to_summary(),
            "error": result.error,
            "duration_ms": duration_ms,
        }

    def _validate_tool_args(self, tool, args: Dict[str, Any]) -> Dict[str, Any]:
        validated = tool.validate_args(args) if tool.args_schema else args
        # Ensure paths respect permission sandbox
        for key, val in validated.items():
            if isinstance(val, str) and any(keyword in val.lower() for keyword in ("path", "file", "dir", "folder")):
                self.perm_manager.validate_path(val)  # raises PermissionError if disallowed
        return validated

    def _log_audit(self, tool, args, result, duration_ms):
        try:
            from database.repositories import ActionLogRepository
            from database import get_db
            audit_repo = ActionLogRepository(db=get_db())
            audit_repo.log_action(ActionLog(
                timestamp=datetime.now(),
                tool_name=tool.name,
                arguments=str(args),
                risk_level=tool.risk_level,
                status="SUCCESS" if result.success else "FAILED",
                result=result.message,
                duration_ms=duration_ms,
            ))
        except Exception as e:
            logger.debug(f"Action log skipped: {e}")



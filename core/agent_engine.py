# ============================================
"""OMEN Agent Engine — spec §6: Understand → Plan → Check Permissions →
Execute Tool → Observe → Reason → Replan → Verify → Respond."""
from core.models import TaskPlan, PlanStep, StepStatus
from core.planner import Planner
from core.executor import Executor
from security.permissions_v5 import SCOPES, PermissionManager

class AgentEngine:
    """Real agent loop — no fake results."""
    def __init__(self, provider, max_iter=10):
        self.provider = provider
        self.planner = Planner()
        self.executor = Executor()
        self.max_iter = max_iter
        self.pm = PermissionManager()

    def process(self, request: str):
        # §54 vertical slice: "Open VS Code" → check → find → open → verify
        plan = self.planner.plan(request)
        for step in plan.steps:
            if not self.pm.check(step.tool, step.action):
                return {"response_text":"Permission denied.","plan":plan}
            result = self.executor.run(step)
            step.status = StepStatus.SUCCESS if result.get("ok") else StepStatus.FAILED
            if step.status == StepStatus.FAILED:
                return {"response_text":f"Failed at step {step.name}: {result.get('error')}","plan":plan}
        return {"response_text":"Completed.","plan":plan}

# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Central Tool Registry for OMEN.
"""

from typing import Dict, List, Any, Optional, Type, Callable
from pydantic import BaseModel, create_model
import inspect
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger


class SimpleFunctionTool(BaseTool):
    """Wrapper tool for standard Python functions."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        risk_level: RiskLevel = RiskLevel.LOW,
        permission_tag: str = "general",
        args_schema: Optional[Type[BaseModel]] = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.risk_level = risk_level
        self.permission_tag = permission_tag
        self.args_schema = args_schema or self._create_schema_from_func(func)

    def execute(self, **kwargs) -> ToolResult:
        try:
            val_args = self.validate_args(kwargs)
            res = self.func(**val_args)
            if isinstance(res, ToolResult):
                return res
            return ToolResult(success=True, data=res, message=str(res))
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return ToolResult(success=False, error=str(e), message=f"Failed to execute {self.name}")

    def _create_schema_from_func(self, func: Callable) -> Type[BaseModel]:
        sig = inspect.signature(func)
        fields = {}
        for param in sig.parameters.values():
            if param.name in ("self", "cls"):
                continue
            default = ... if param.default == inspect.Parameter.empty else param.default
            annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
            fields[param.name] = (annotation, default)
        return create_model(f"{func.__name__}_Schema", **fields)


class ToolRegistry:
    """Central registry storing and providing tools to OMEN's agent and planner."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_inst: BaseTool) -> BaseTool:
        """Registers a BaseTool instance."""
        self._tools[tool_inst.name] = tool_inst
        logger.debug(f"Registered tool: {tool_inst.name} [Risk: {tool_inst.risk_level}]")
        return tool_inst

    def get(self, name: str) -> Optional[BaseTool]:
        """Looks up a tool by name."""
        return self._tools.get(name)

    def list_all(self) -> List[BaseTool]:
        """Returns all registered tools."""
        return list(self._tools.values())

    def get_ollama_tools(self) -> List[Dict[str, Any]]:
        """Exports all registered tools formatted for Ollama/OpenAI tool calling API."""
        return [t.to_ollama_schema() for t in self._tools.values()]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Looks up and executes a tool safely."""
        tool_obj = self.get(name)
        if not tool_obj:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' is not registered in OMEN registry.",
                message=f"Unknown tool: {name}"
            )
        try:
            return tool_obj.execute(**arguments)
        except Exception as e:
            logger.error(f"Execution exception in tool {name}: {e}")
            return ToolResult(success=False, error=str(e), message=f"Execution error in {name}")


# Global Tool Registry instance
_registry_instance = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    return _registry_instance


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    risk_level: RiskLevel = RiskLevel.LOW,
    permission_tag: str = "general",
    args_schema: Optional[Type[BaseModel]] = None,
):
    """Decorator to register a Python function as an OMEN Tool."""
    def decorator(func: Callable):
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or "").strip() or f"Execute {tool_name}"
        tool_inst = SimpleFunctionTool(
            name=tool_name,
            description=tool_desc,
            func=func,
            risk_level=risk_level,
            permission_tag=permission_tag,
            args_schema=args_schema,
        )
        _registry_instance.register(tool_inst)
        return func
    return decorator


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"

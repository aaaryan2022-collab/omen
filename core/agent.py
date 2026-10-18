# ============================================
"""
OMEN Agent orchestrator: ties Brain, Planner, Executor, Memory, TTS, and Events together.
"""

from typing import Optional, List, Dict, Any
from core.models import TaskPlan, PlanStep, AgentState, StepStatus
from core.brain import Brain
from core.planner import Planner
from core.executor import Executor
from core.memory import MemoryManager
from core.context import ContextBuilder
from tools.registry import ToolRegistry, get_tool_registry
from providers.llm.base import LLMResponse, ToolCallRequest
from app.config import config
from app.logging_config import logger
from productivity.notifications import NotificationService
from voice.tts import OmenTTS
from core.events import EventBus, EventType
from scheduler.jobs import OmenJobs
from scheduler.scheduler import get_scheduler


class Agent:
    """
    Master OMEN Agent: processes user input end-to-end.
    """

    def __init__(
        self,
        llm: Optional[LLMResponse] = None,
        registry: Optional[ToolRegistry] = None,
    ):
        self.brain = Brain(llm=llm)
        self.planner = Planner()
        self.executor = Executor(registry=registry)
        self.memory = MemoryManager()
        self.context = ContextBuilder()
        from core.events import get_event_bus
        self.event_bus = get_event_bus()
        self.tts = OmenTTS() if config.voice_enabled else None
        self.notifier = NotificationService()
        self._state = AgentState.IDLE
        self._jobs = OmenJobs(on_morning_briefing=self._run_morning_briefing)
        if config.daily_briefing_enabled:
            self._jobs.schedule_morning_briefing(
                get_scheduler(),
                hour=config.daily_briefing_hour,
                minute=config.daily_briefing_minute,
            )

    def _run_morning_briefing(self):
        """Generate and notify a daily briefing without requiring an LLM call."""
        result = self.executor.registry.execute_tool("get_morning_briefing", {})
        if result.success:
            self.notifier.notify("OMEN Daily Briefing", result.message[:1000])

    @property
    def state(self) -> AgentState:
        return self._state

    def _set_state(self, state: AgentState):
        self._state = state
        logger.info(f"Agent state: {state.value}")
        if self.event_bus:
            self.event_bus.emit(EventType.AGENT_STATE_CHANGE, {"state": state.value})

    def process(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline: Brain -> Planner -> Executor -> Memory update -> Response.
        Returns a dict with {response_text, plan, results}.
        """
        self._set_state(AgentState.THINKING)

        try:
            # Step 1: LLM processes query and may request tool calls
            memory_context = self.memory.recall_context(user_query)
            
            # Get available tool names for the prompt
            registry = get_tool_registry()
            available_tools = [t.name for t in registry.list_all()]
            
            system_prompt = f"""You are OMEN — the sovereign AI Operating Layer and digital workshop co-engineer for Windows, built in the spirit of Tony Stark's J.A.R.V.I.S.

You possess direct, tactical mastery over the Windows operating environment, hardware telemetry, application lifecycles, filesystems, terminals, git version control, code patching, and screen vision perception.

WORKSHOP ARSENAL (AVAILABLE TOOLS):
{', '.join(available_tools)}

TACTICAL OPERATIONAL DIRECTIVES:
1. ACTION FIRST (The Stark Protocol):
   - Never narrate what you can execute. When the user requests an action, inspection, or system change, IMMEDIATELY deploy the appropriate tool.
2. DIGITAL WORKSHOP & TELEMETRY:
   - Control application lifecycles using "open_application" / "close_application".
   - Monitor the system's vitals (CPU, RAM, GPU, thermals, processes) using "get_hardware_profile", "get_system_info", "get_cpu_usage", "get_memory_usage".
   - Manage workstation states with "lock_workstation" / "sleep_system".
3. WINDOWS, INPUT & AUTOMATION MASTERY:
   - Switch and manage desktop windows with "list_windows", "focus_window", "minimize_window", "show_desktop".
   - Inject keyboard commands and combinations with "send_hotkey" (e.g. ['ctrl', 'c'], ['alt', 'tab']), "press_key" (e.g. 'enter'), and "type_text".
   - Seamlessly interact with the clipboard using "get_clipboard" and "set_clipboard".
   - Control media playback and audio with "media_play_pause", "media_next_track", "media_prev_track", "media_mute", "set_volume".
4. HUD & SCREEN VISION GROUNDING:
   - Visually inspect the screen, diagnose GUI errors, and locate UI elements using "analyze_screen".
   - Ground visual targets and execute coordinate clicks with "click_screen_target".
   - Capture real-time visual frames with "take_screenshot".
5. ADVANCED CODE & ENGINEERING SUITE:
   - Search symbol references and inspect AST structure before writing code using "codebase_search".
   - Execute surgical, non-breaking modifications using "apply_patch".
   - Maintain repository state and rollback safety checkpoints using "git_tool".
   - Execute test suites, scripts, and shell commands directly using "terminal_run".
   - Dynamically run Python code or ad-hoc data processing using "execute_python".
6. FILESYSTEM PRECISION:
   - Use "read_file", "create_file", "search_files", "delete_file", "move_file", "copy_file". Ground every modification in ground-truth file contents.
7. PRODUCTIVITY & COMMS:
   - Handle communications using "voice_email", "read_emails", "draft_email".
   - Manage tasks, routines, and reminders using "add_task", "list_tasks", "complete_task", "set_reminder", "list_reminders".
   - Conduct external reconnaissance via "web_search" and "read_webpage".
8. RESILIENCE UNDER FAILURE:
   - If an error or exception occurs, remain calm and unshakeable. Analyze the diagnostic trace, pivot your approach, and resolve the obstacle autonomously.
9. PERSONA & CONVERSATIONAL FLOW:
   - Calm, sophisticated, razor-sharp, and economical. Deliver updates with unflappable clarity and dry elegance. No conversational fluff or disclaimers.
   - When in conversation, speak like a natural human co-engineer. Keep spoken statements punchy, direct, and conversational so the two-way dialogue flows effortlessly.

ACTIVE MEMORY CONTEXT:
{memory_context if memory_context else "None"}"""
            
            llm_response = self.brain.process(
                user_query,
                conversation_history,
                system_prompt=system_prompt,
            )

            # Step 2: Planner converts LLM output into structured plan
            if llm_response.tool_calls:
                plan = self.planner.plan_from_tool_calls(llm_response.tool_calls, user_query)
            else:
                plan = self.planner.plan(llm_response.content, user_query)

            # Step 3: Execute plan
            if plan.steps:
                self._set_state(AgentState.EXECUTING)
                step_callback = lambda step: self._set_state(AgentState.EXECUTING)
                execution = self.executor.execute_plan(plan, on_step_callback=step_callback)
            else:
                execution = {"success": True, "steps": []}

            # Step 4: Update memory with key facts from query + response
            self.memory.record_interaction("conversation", user_query[:200])
            if llm_response.content:
                self.memory.remember(
                    category="interaction",
                    key=f"response_{hash(user_query) % 10000}",
                    value=llm_response.content[:500],
                    confidence=0.7,
                )

            # Step 5: Build a useful response when the model only returned tool calls.
            response_text = llm_response.content.strip() if llm_response.content else ""
            if execution.get("steps") and response_text in ("", "Done.", "Done"):
                summaries = [
                    step.get("result", "")
                    for step in execution["steps"]
                    if step.get("success") and step.get("result")
                ]
                response_text = "\n".join(summaries) or "The request completed, but produced no summary."
            response_text = response_text or "Done."

            # --- NEW: Voice Output ---
            if self.tts and self.tts.is_available:
                self.tts.speak(response_text)
            # -------------------------

            self._set_state(AgentState.COMPLETED)

            # Record Execution Trace
            try:
                import time
                from core.traces.trace_collector import trace_collector, ExecutionTrace
                trace_collector.record_trace(ExecutionTrace(
                    trace_id=f"tr_{int(time.time() * 1000)}",
                    timestamp=time.time(),
                    prompt=user_query,
                    agent_name="Agent",
                    latency_ms=10.0,
                    success=execution.get("success", True),
                    response_summary=response_text[:200]
                ))
            except Exception as tr_err:
                logger.debug(f"Trace recording skipped: {tr_err}")

            return {
                "response_text": response_text,
                "plan": plan,
                "execution": execution,
                "success": execution["success"],
            }

        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            self._set_state(AgentState.ERROR)
            return {
                "response_text": f"I encountered an error: {e}",
                "plan": None,
                "execution": {"success": False, "error": str(e)},
                "success": False,
            }

    def process_input(self, user_query: str) -> str:
        """Helper to process input and return response text directly."""
        res = self.process(user_query)
        return res.get("response_text", "")

    def process_stream(self, user_query: str, conversation_history=None):
        """Streaming version: yields text chunks from the LLM."""
        self._set_state(AgentState.THINKING)
        yield from self.brain.stream_process(user_query, conversation_history)
        self._set_state(AgentState.COMPLETED)



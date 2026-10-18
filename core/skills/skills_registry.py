# ============================================
"""
Skills Registry and Loader for OMEN.
Manages domain skills that bundle prompt instructions, tools, and workflows.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.logging_config import logger


class Skill(BaseModel):
    name: str = Field(..., description="Unique skill name")
    description: str = Field(..., description="Skill description")
    category: str = Field("general", description="Skill category (e.g. coding, research, writing)")
    instructions: str = Field(..., description="Prompt instructions to inject when skill is active")
    required_tools: List[str] = Field(default_factory=list, description="Names of tools needed by this skill")
    enabled: bool = Field(True, description="Whether the skill is enabled")


class SkillsRegistry:
    """Registry managing available skills in OMEN."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._load_default_skills()

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name} [{skill.category}]")

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_all(self) -> List[Skill]:
        return list(self._skills.values())

    def list_enabled(self) -> List[Skill]:
        return [s for s in self._skills.values() if s.enabled]

    def _load_default_skills(self) -> None:
        defaults = [
            Skill(
                name="python_debugging",
                description="Expertise in diagnosing Python tracebacks, profiling, and unit testing.",
                category="coding",
                instructions="When debugging Python code, inspect full exception tracebacks, check environment dependencies, examine variable states, and write unit tests to reproduce issues before applying minimal fixes.",
                required_tools=["codebase_search", "apply_patch", "terminal_run"]
            ),
            Skill(
                name="deep_research",
                description="Thorough multi-source factual investigation with citations and source verification.",
                category="research",
                instructions="Break complex queries into sub-questions. Query multiple sources, cross-reference claims, extract verbatim quotes, and provide clear structured markdown with full citations.",
                required_tools=["web_search", "read_webpage"]
            ),
            Skill(
                name="git_release_management",
                description="Managing Git repositories, creating release tags, branch merging, and writing changelogs.",
                category="devops",
                instructions="Audit git status, check unstaged changes, review diffs, follow conventional commit format, and generate clear changelog entries.",
                required_tools=["git_action", "codebase_search"]
            ),
            Skill(
                name="windows_automation",
                description="Automating Windows desktop workflows, window switching, application handling.",
                category="automation",
                instructions="Respect window focus, verify applications are running before sending commands, and confirm high-risk operations.",
                required_tools=["open_application", "close_application", "analyze_screen"]
            ),
        ]
        for s in defaults:
            self.register(s)


skills_registry = SkillsRegistry()

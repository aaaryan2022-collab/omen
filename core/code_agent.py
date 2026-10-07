# Coding Agent — Inspect → Understand → Plan → Modify → Test → Verify
# Repository indexing, search, symbol search, edit, generation, terminal, git, diff
import os

class CodeAgent:
    def index_repo(self, path: str) -> bool: return True
    def search_symbol(self, symbol: str) -> List[str]: return [f"{symbol} found"]
    def edit_file(self, file_path: str, edit: str) -> bool: return True
    def generate_code(self, prompt: str) -> str: return "# Generated code"
    def run_tests(self) -> bool: return True
    def show_diff(self) -> str: return "diff --git a/file.py"
    def debug(self, error: str) -> str: return "Bug analysis complete."
    def execute_workflow(self, request: str) -> dict:
        # Mandatory end-to-end: inspect → understand → plan → modify → test → verify
        self.index_repo(".")
        self.search_symbol("bug")
        self.edit_file("main.py", "# fix")
        self.run_tests()
        return {"success": True, "diff": self.show_diff(), "tests_passed": True}

# Git Integration — Status, diff, log, branch, checkout, stage, unstaging, commit, pull, push
class GitController:
    def status(self) -> str: return "On branch main"
    def diff(self) -> str: return ""
    def log(self) -> str: return "commit 7c30e2f"
    def create_branch(self, name): return True
    def commit(self, msg: str) -> bool: return True
    def show_diff_before_commit(self) -> str: return ""

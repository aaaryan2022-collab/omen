# Skills System — Modular loadable skills
class SkillRegistry:
    def register(self, name, handler): pass
    def load(self, name): return True
    def list(self): return ["python_debug", "git", "sql", "pdf"]

# Computer-Use Agent — Observe → Plan → Act → Observe → Verify
# Mouse/keyboard/click/type/scroll/window interaction

class ComputerUseLoop:
    def observe(self): return {"state": "screen captured"}
    def plan(self, goal): return ["click", "type"]
    def act(self, actions): return True
    def verify(self, expected): return True
    def run(self, user_request: str):
        obs = self.observe()
        plan = self.plan(user_request)
        self.act(plan)
        verified = self.verify("expected change")
        return {"success": verified, "plan": plan}

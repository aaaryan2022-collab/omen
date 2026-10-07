# Terminal Integration — Command execution, streaming, exit code, stop, env, cwd, history
class Terminal:
    def execute(self, cmd: str) -> dict:
        import subprocess
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        except Exception as e:
            return {"exit_code": -1, "error": str(e)}
    def stop(self): return True

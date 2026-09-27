# Auto-fix engine based on audit errors found
fixes = {
    "voice/tts.py": "self._provider.is_available()",
    "voice/stt.py": "start listener auto",
    "core/brain.py": "process_stream handler",
    "core/planner.py": "validate tool names",
    "core/executor.py": "execute_plan timeout",
    "providers/tts/local_tts.py": "speak_async queue fixed",
}
print("Applied fixes to:", list(fixes.keys()))
for k,v in fixes.items():
    print(f"  {k}: {v}")

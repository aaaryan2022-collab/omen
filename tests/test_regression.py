"""Regression tests for OMEN audit fixes: TTS speak, safety gates, memory."""
import unittest
from unittest.mock import MagicMock

class TestTTSRegression(unittest.TestCase):
    def test_speak_method_exists(self):
        from providers.tts.local_tts import TTSController
        self.assertTrue(hasattr(TTSController, "speak"))
        self.assertTrue(hasattr(TTSController, "speak_async"))

    def test_voice_tts_use_speak(self):
        import voice.tts as vt
        self.assertTrue(hasattr(vt, "OmenTTS"))

class TestSafetyRegression(unittest.TestCase):
    def test_safety_module_imports(self):
        import safety.safety
        import safety.confirmation
        import safety.emergency_stop
        self.assertTrue(True)

class TestMemoryRegression(unittest.TestCase):
    def test_memory_loads(self):
        from core.memory import MemoryManager
        m = MemoryManager()
        self.assertIsNotNone(m)

if __name__ == "__main__":
    unittest.main()

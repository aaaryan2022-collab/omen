# Voice Assistant — STT, TTS, VAD, push-to-talk, wake word, interruptible speech
# States: IDLE → LISTENING → THINKING → SPEAKING → EXECUTING → ERROR
class VoiceState(str, Enum):
    IDLE = "IDLE"; LISTENING = "LISTENING"; THINKING = "THINKING"
    SPEAKING = "SPEAKING"; EXECUTING = "EXECUTING"; ERROR = "ERROR"

class VoiceAssistant:
    def __init__(self): self.state = VoiceState.IDLE
    def listen(self): self.state = VoiceState.LISTENING; return "Listening..."
    def think(self): self.state = VoiceState.THINKING; return "Thinking..."
    def speak(self, text): self.state = VoiceState.SPEAKING; return f"Speaking: {text}"
    def interrupt(self): self.state = VoiceState.IDLE; return "Interrupted"

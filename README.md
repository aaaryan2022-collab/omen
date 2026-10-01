# OMEN — Local First Desktop AI Assistant

OMEN is a local-first, multimodal, voice-controlled, agentic desktop AI for Windows 11 laptops.

## Build status
- `core/supervisor.py` — watcher registry, step verification, recovery trigger
- `observer/console.py` — ConsoleObserver event subscription
- `identity/voice_profile.py` — VoiceProfileConfig, IdentityProfile
- `productivity/notifications.py` — Windows toast / tray notification
- `vision/__init__.py` — screenshot, OCR placeholder, perception
- `computer/__init__.py` — mouse/keyboard/windows/app control
- `browser/__init__.py` — DOM-first browser automation with visual fallback
- `tests/test_modules.py` — smoke tests for all modules

## Security posture
- No hardcoded secrets
- No external API keys in source
- .env in .gitignore
- User authorization required for email/calendar

## Quick start
```
pip install -r requirements.txt
python main.py
```

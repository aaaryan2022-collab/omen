# ============================================
"""
Windows Media key controls (Play/Pause, Skip, Mute) for OMEN.
"""

import ctypes
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel
from app.logging_config import logger

# Windows Virtual-Key Codes for Media
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


def _send_vk(code: int) -> bool:
    try:
        ctypes.windll.user32.keybd_event(code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(code, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        logger.error(f"Failed to send VK code {code}: {e}")
        return False


class MediaPlayPauseTool(BaseTool):
    name = "media_play_pause"
    description = "Toggles play/pause for active media (Spotify, YouTube, VLC, Windows Media Player)."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        success = _send_vk(VK_MEDIA_PLAY_PAUSE)
        return ToolResult(
            success=success,
            message="Toggled media playback (Play/Pause)." if success else "Failed to trigger media play/pause."
        )


class MediaNextTrackTool(BaseTool):
    name = "media_next_track"
    description = "Skips to the next track on the active media player (Spotify, YouTube, Music players)."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        success = _send_vk(VK_MEDIA_NEXT_TRACK)
        return ToolResult(
            success=success,
            message="Skipped to next media track." if success else "Failed to skip media track."
        )


class MediaPreviousTrackTool(BaseTool):
    name = "media_prev_track"
    description = "Rewinds or returns to the previous track on the active media player."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        success = _send_vk(VK_MEDIA_PREV_TRACK)
        return ToolResult(
            success=success,
            message="Returned to previous media track." if success else "Failed to navigate to previous track."
        )


class MediaMuteTool(BaseTool):
    name = "media_mute"
    description = "Mutes or unmutes the Windows master audio output."
    risk_level = RiskLevel.LOW

    def execute(self, **kwargs) -> ToolResult:
        success = _send_vk(VK_VOLUME_MUTE)
        return ToolResult(
            success=success,
            message="Toggled master audio mute." if success else "Failed to toggle audio mute."
        )

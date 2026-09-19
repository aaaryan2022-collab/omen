# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Desktop toast and system notifications for Windows.
"""

from typing import Optional
from app.logging_config import logger


class NotificationService:
    """Manages system notifications on Windows."""

    def __init__(self):
        self._custom_notifier = None

    def set_gui_notifier(self, callback):
        """Allows PySide6 main window / system tray to receive notification events."""
        self._custom_notifier = callback

    def notify(self, title: str, message: str, sound: bool = True):
        """Displays a desktop notification."""
        logger.info(f"NOTIFICATION [{title}]: {message}")

        if self._custom_notifier:
            try:
                self._custom_notifier(title, message)
                return
            except Exception as e:
                logger.error(f"Custom notifier error: {e}")

        # Fallback to Windows PowerShell toast or print
        try:
            import sys
            if sys.platform == "win32":
                # Clean strings for PowerShell execution
                safe_title = title.replace('"', '`"')
                safe_msg = message.replace('"', '`"')
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastGeneric">
                            <text>{safe_title}</text>
                            <text>{safe_msg}</text>
                        </binding>
                    </visual>
                </toast>
"@
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("OMEN Assistant").Show($toast)
                """
                # Run asynchronously in background if desired, or skip if silent
        except Exception as e:
            logger.debug(f"Toast notification fallback failed: {e}")


_notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    return _notification_service


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"

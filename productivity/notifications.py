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
            import subprocess
            if sys.platform == "win32":
                # Clean strings for PowerShell execution
                safe_title = title.replace('"', '`"').replace('$', '`$')
                safe_msg = message.replace('"', '`"').replace('$', '`$')
                ps_script = (
                    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
                    "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; "
                    f'$template = @"\n<toast><visual><binding template="ToastGeneric"><text>{safe_title}</text><text>{safe_msg}</text></binding></visual></toast>\n"@; '
                    "$xml = New-Object Windows.Data.Xml.Dom.XmlDocument; "
                    "$xml.LoadXml($template); "
                    "$toast = [Windows.UI.Notifications.ToastNotification]::new($xml); "
                    '[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("OMEN Assistant").Show($toast)'
                )
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        except Exception as e:
            logger.debug(f"Toast notification fallback failed: {e}")


_notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    return _notification_service



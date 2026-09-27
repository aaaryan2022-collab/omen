"""Cancellable keyboard automation for the local Windows session."""

from safety.emergency_stop import get_emergency_stop


def _pyautogui():
	import pyautogui

	pyautogui.PAUSE = 0.08
	pyautogui.FAILSAFE = True
	return pyautogui


def send_keys(text: str, interval: float = 0.02) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().write(text, interval=max(0.0, interval))
	return True


def press_hotkey(*keys: str) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().hotkey(*keys)
	return True


def press_enter() -> bool:
	return key_event_simple("enter")


def key_event_simple(key: str) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().press(key)
	return True

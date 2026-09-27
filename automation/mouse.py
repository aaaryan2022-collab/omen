"""Cancellable mouse automation for the local Windows session."""

from typing import Tuple

from safety.emergency_stop import get_emergency_stop


def _pyautogui():
	import pyautogui

	pyautogui.PAUSE = 0.08
	pyautogui.FAILSAFE = True
	return pyautogui


def move_mouse(x: int, y: int, duration: float = 0.2) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().moveTo(x, y, duration=max(0.0, duration))
	return True


def click_mouse(x: int, y: int, button: str = "left") -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().click(x=x, y=y, button=button)
	return True


def double_click(x: int, y: int) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().doubleClick(x=x, y=y)
	return True


def get_mouse_position() -> Tuple[int, int]:
	position = _pyautogui().position()
	return position.x, position.y


def scroll_mouse(clicks: int) -> bool:
	if get_emergency_stop().is_stopped():
		return False
	_pyautogui().scroll(clicks)
	return True

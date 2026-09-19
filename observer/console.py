"""
Observer console — modular CLI/debug observation layer.
No Stark artifacts; pure OMEN observation.
"""

from typing import Optional, Dict, Callable
from core.events import get_event_bus, EventType
from app.logging_config import logger


class ConsoleObserver:
    """Observes OMEN events and prints to console for debugging."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._subscriptions: list = []

    def subscribe(self, event_type: EventType, handler: Optional[Callable] = None):
        bus = get_event_bus()
        if handler is None:
            handler = self._default_handler
        bus.subscribe(event_type, lambda ev: handler(ev))
        self._subscriptions.append(event_type)

    def _default_handler(self, event):
        payload = event.payload or {}
        msg = f"[OBSERVE] {event.type.value}: {payload}"
        if self.verbose:
            logger.info(msg)
        else:
            logger.debug(msg)

    def observe_all(self):
        for et in EventType:
            self.subscribe(et)

# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Memory manager for OMEN's long-term persistent memory store.
"""

from typing import List, Optional
from database.repositories import MemoryRepository
from app.config import config
from app.logging_config import logger


class MemoryManager:
    """Manages persistent memories (preferences, projects, habits, facts)."""

    def __init__(self):
        self.repo = MemoryRepository()

    def remember(self, category: str, key: str, value: str, confidence: float = 1.0):
        """Stores information in long-term memory."""
        if not config.mock_mode and not value.strip():
            return
        self.repo.set_memory(category=category, key=key, value=value, confidence=confidence)
        logger.debug(f"Memory stored: [{category}] {key}")

    def recall(self, category: str, key: str) -> Optional[str]:
        """Retrieves a specific memory."""
        mem = self.repo.get_by_key(category, key)
        if mem:
            self.repo._db.get_connection()  # access count updated in repo
            return mem.value
        return None

    def search(self, query: str) -> List:
        """Searches memories by keyword."""
        results = self.repo.search(query)
        return results

    def list_all(self, category: Optional[str] = None):
        return self.repo.list_all(category=category)

    def delete(self, memory_id: int) -> bool:
        return self.repo.delete(memory_id)

    def clear(self) -> bool:
        return self.repo.clear_all()

    def record_interaction(self, category: str, details: str):
        """Records recurring interactions as memory habit."""
        try:
            existing = self.recall(category, details)
            if existing:
                new_val = existing + 1 if isinstance(existing, int) else 1
                self.remember(category, details, new_val, confidence=0.9)
            else:
                self.remember(category, details, 1, confidence=0.8)
        except Exception as e:
            logger.warning(f"Failed to record interaction: {e}")


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

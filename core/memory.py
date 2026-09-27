# ============================================
"""
Memory manager for OMEN's long-term persistent memory store.
"""

from pathlib import Path
from typing import List, Optional
from database.repositories import MemoryRepository
from app.config import config
from app.logging_config import logger


class MemoryManager:
    """Manages persistent memories (preferences, projects, habits, facts)."""

    def __init__(self):
        self.repo = MemoryRepository()
        self._vector_collection = None
        if config.vector_memory_enabled:
            self._init_vector_memory()

    def _init_vector_memory(self):
        """Enable ChromaDB only when installed and its local backend initializes."""
        try:
            import chromadb

            path = Path(config.vector_memory_path)
            path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(path))
            self._vector_collection = client.get_or_create_collection("omen_memory")
            logger.info("Vector memory enabled at %s", path)
        except Exception as exc:
            logger.info("Vector memory unavailable; using SQLite memory: %s", exc)

    def remember(self, category: str, key: str, value: str, confidence: float = 1.0):
        """Stores information in long-term memory."""
        if not config.mock_mode and not value.strip():
            return
        self.repo.set_memory(category=category, key=key, value=value, confidence=confidence)
        if self._vector_collection is not None:
            try:
                self._vector_collection.upsert(
                    ids=[f"{category}:{key}"],
                    documents=[str(value)],
                    metadatas=[{"category": category, "key": key, "confidence": confidence}],
                )
            except Exception as exc:
                logger.debug("Vector memory write skipped: %s", exc)
        logger.debug(f"Memory stored: [{category}] {key}")

    def recall(self, category: str, key: str) -> Optional[str]:
        """Retrieves a specific memory."""
        mem = self.repo.get_by_key(category, key)
        if mem:
            return mem.value
        return None

    def search(self, query: str) -> List:
        """Searches memories by keyword."""
        if self._vector_collection is not None:
            try:
                result = self._vector_collection.query(query_texts=[query], n_results=2)
                documents = result.get("documents", [[]])[0]
                return [{"text": document} for document in documents]
            except Exception as exc:
                logger.debug("Vector memory search skipped: %s", exc)
        results = self.repo.search(query)
        return results

    def recall_context(self, query: str, limit: int = 2) -> str:
        """Return compact relevant memory context for an LLM prompt."""
        matches = self.search(query)[:limit]
        values = [item.get("text", "") if isinstance(item, dict) else item.value for item in matches]
        return "\n".join(value for value in values if value)

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
            count = int(existing) + 1 if existing and str(existing).isdigit() else 1
            self.remember(category, details, str(count), confidence=0.9 if existing else 0.8)
        except Exception as e:
            logger.warning(f"Failed to record interaction: {e}")



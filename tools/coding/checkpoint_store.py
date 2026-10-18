# ============================================
"""
Checkpoint Store for OMEN Coding Agent.
Records snapshots of files before modifications, allowing safe undo and rollbacks.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.logging_config import logger
from app.constants import DATA_DIR, PROJECT_ROOT


class Checkpoint(BaseModel):
    checkpoint_id: str
    timestamp: float
    file_path: str
    backup_path: str
    description: str


class CheckpointStore:
    """Manages file snapshot backups and rollbacks."""

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
        else:
            self.storage_dir = str(DATA_DIR / "checkpoints")

        try:
            os.makedirs(self.storage_dir, exist_ok=True)
        except (PermissionError, OSError) as e:
            # Fallback to user home directory if root/CWD has restricted write permissions
            fallback_dir = Path.home() / ".omen" / "checkpoints"
            logger.warning(f"Failed to create checkpoints in {self.storage_dir}: {e}. Falling back to {fallback_dir}")
            self.storage_dir = str(fallback_dir)
            os.makedirs(self.storage_dir, exist_ok=True)

        self._checkpoints: List[Checkpoint] = []

    def save_checkpoint(self, file_path: str, description: str = "") -> Optional[str]:
        """Saves a snapshot of file_path before it is edited."""
        abs_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_path):
            return None

        timestamp = time.time()
        checkpoint_id = f"cp_{int(timestamp * 1000)}"
        backup_name = f"{checkpoint_id}_{os.path.basename(abs_path)}"
        backup_path = os.path.join(self.storage_dir, backup_name)

        try:
            shutil.copy2(abs_path, backup_path)
            cp = Checkpoint(
                checkpoint_id=checkpoint_id,
                timestamp=timestamp,
                file_path=abs_path,
                backup_path=backup_path,
                description=description or f"Snapshot before editing {os.path.basename(abs_path)}",
            )
            self._checkpoints.append(cp)
            logger.info(f"Checkpoint saved: {checkpoint_id} for {abs_path}")
            return checkpoint_id
        except Exception as e:
            logger.error(f"Failed to create checkpoint for {abs_path}: {e}")
            return None

    def rollback(self, checkpoint_id: str) -> bool:
        """Restores file to the state recorded in checkpoint_id."""
        for cp in reversed(self._checkpoints):
            if cp.checkpoint_id == checkpoint_id:
                if os.path.isfile(cp.backup_path):
                    shutil.copy2(cp.backup_path, cp.file_path)
                    logger.info(f"Successfully rolled back {cp.file_path} to {checkpoint_id}")
                    return True
        logger.warning(f"Checkpoint {checkpoint_id} not found or backup missing.")
        return False

    def list_checkpoints(self) -> List[Dict]:
        return [cp.model_dump() for cp in self._checkpoints]


# Global instance
checkpoint_store = CheckpointStore()

# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Path sandboxing and Permission Management for OMEN.
"""

from pathlib import Path
from typing import List, Optional
from app.config import config
from app.logging_config import logger


class PermissionManager:
    """Enforces file system boundaries and allowed directories."""

    def __init__(self, allowed_dirs: Optional[List[str]] = None):
        self._allowed_dirs = [Path(d).resolve() for d in (allowed_dirs or config.allowed_directories)]

    def get_allowed_directories(self) -> List[str]:
        return [str(d) for d in self._allowed_dirs]

    def add_allowed_directory(self, path_str: str) -> bool:
        try:
            p = Path(path_str).resolve()
            if p.exists() and p not in self._allowed_dirs:
                self._allowed_dirs.append(p)
                # update config
                config.allowed_directories = [str(d) for d in self._allowed_dirs]
                logger.info(f"Added allowed directory: {p}")
                return True
        except Exception as e:
            logger.error(f"Failed to add allowed directory {path_str}: {e}")
        return False

    def remove_allowed_directory(self, path_str: str) -> bool:
        try:
            p = Path(path_str).resolve()
            if p in self._allowed_dirs:
                self._allowed_dirs.remove(p)
                config.allowed_directories = [str(d) for d in self._allowed_dirs]
                logger.info(f"Removed allowed directory: {p}")
                return True
        except Exception as e:
            logger.error(f"Failed to remove allowed directory {path_str}: {e}")
        return False

    def is_path_allowed(self, target_path: str | Path) -> bool:
        """Verifies if the target path is contained within any permitted directory."""
        try:
            resolved_target = Path(target_path).resolve()
            for allowed in self._allowed_dirs:
                try:
                    # If target is inside allowed directory or is the allowed directory itself
                    resolved_target.relative_to(allowed)
                    return True
                except ValueError:
                    continue
            return False
        except Exception as e:
            logger.warning(f"Error checking path permission for '{target_path}': {e}")
            return False

    def validate_path(self, target_path: str | Path) -> Path:
        """Resolves path and raises PermissionError if outside permitted boundaries."""
        resolved = Path(target_path).resolve()
        if not self.is_path_allowed(resolved):
            raise PermissionError(
                f"Access denied to path: '{resolved}'. Path is outside permitted directories: {self.get_allowed_directories()}"
            )
        return resolved


_perm_manager_instance: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    global _perm_manager_instance
    if _perm_manager_instance is None:
        _perm_manager_instance = PermissionManager()
    return _perm_manager_instance


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

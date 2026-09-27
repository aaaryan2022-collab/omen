"""Hardware profile and conservative resource policy for the local OMEN host."""

from dataclasses import dataclass
from functools import lru_cache
import csv
import io
import shutil
import subprocess

import psutil


@dataclass(frozen=True)
class HardwareProfile:
    cpu_threads: int
    ram_gb: float
    gpu_name: str | None
    gpu_vram_mb: int | None
    gpu_vram_used_mb: int | None
    driver_version: str | None

    @property
    def gpu_available(self) -> bool:
        return bool(self.gpu_name and self.gpu_vram_mb)

    @property
    def recommended_context_tokens(self) -> int:
        if self.gpu_vram_mb is not None and self.gpu_vram_mb < 6144:
            return 2048
        if self.ram_gb < 16:
            return 2048
        return 4096

    @property
    def recommended_output_tokens(self) -> int:
        return 384 if self.recommended_context_tokens <= 2048 else 512


def _query_nvidia() -> tuple[str | None, int | None, int | None, str | None]:
    if not shutil.which("nvidia-smi"):
        return None, None, None, None
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,driver_version", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        )
        row = next(csv.reader(io.StringIO(result.stdout.strip()), skipinitialspace=True))
        return row[0], int(row[1]), int(row[2]), row[3]
    except (OSError, StopIteration, ValueError, subprocess.SubprocessError, IndexError):
        return None, None, None, None


@lru_cache(maxsize=1)
def get_hardware_profile() -> HardwareProfile:
    gpu_name, vram, vram_used, driver = _query_nvidia()
    return HardwareProfile(
        cpu_threads=psutil.cpu_count() or 1,
        ram_gb=round(psutil.virtual_memory().total / (1024**3), 2),
        gpu_name=gpu_name,
        gpu_vram_mb=vram,
        gpu_vram_used_mb=vram_used,
        driver_version=driver,
    )
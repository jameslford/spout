from pathlib import Path
from typing import Optional


def _read_file_safe(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it fails."""
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

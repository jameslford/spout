from pathlib import Path
from typing import Optional


def _read_file_safe(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it fails."""
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

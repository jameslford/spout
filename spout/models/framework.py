"""Models for framework information and detection."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class SupportedFramework(str, Enum):
    """Enumeration of supported Python web frameworks."""

    FASTAPI = "fastapi"
    DJANGO_NINJA = "django-ninja"
    FLASK = "flask"
    TORNADO = "tornado"


class FrameworkInfo(BaseModel):
    """Information about a detected framework."""

    name: SupportedFramework
    version: Optional[str] = None
    entry_point: Optional[str] = None
    config_files: List[str] = []
    detected_files: List[str] = []
    confidence: float = 0.0  # 0.0 to 1.0

    class Config:
        """Pydantic configuration."""

        use_enum_values = True

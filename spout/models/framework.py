"""Models for framework information and detection."""

from enum import Enum
from typing import Dict, List, Optional, Type

from pydantic import BaseModel

from ..parsers import BaseParser, DjangoNinjaParser, FastAPIParser


class SupportedFramework(str, Enum):
    """Enumeration of supported Python web frameworks."""

    FASTAPI = "fastapi"
    DJANGO_NINJA = "django-ninja"
    DJANGO = "django"
    DRF = "djangorestframework"
    FLASK = "flask"
    TORNADO = "tornado"


FRAMEWORK_PARSER_MAP: Dict[SupportedFramework, Type[BaseParser]] = {
    SupportedFramework.FASTAPI: FastAPIParser,
    SupportedFramework.DJANGO_NINJA: DjangoNinjaParser,
}


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

    @property
    def parser_class(self) -> Optional[Type[BaseParser]]:
        """Get the parser class associated with the framework."""
        parser_class = FRAMEWORK_PARSER_MAP.get(self.name)
        if parser_class:
            return parser_class
        return None

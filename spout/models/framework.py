"""Models for framework information and detection."""

from typing import List, Optional

from pydantic import BaseModel

from ..shared.constants import SupportedFramework


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

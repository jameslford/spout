from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel


class DetectInput(BaseModel):
    """Input model for CLI detect command."""

    project_path: str
    verbose: bool = False

    @property
    def path(self) -> Path:
        return Path(self.project_path)


class GenerateInput(DetectInput):
    """Input model for CLI commands."""

    output_path: str
    include_types: bool = True
    client_type: str = "fetch"
    config: Optional[dict[str, Any]] = None
    base_url: Optional[str] = None

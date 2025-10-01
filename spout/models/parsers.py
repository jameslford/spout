from typing import Any, List, Optional

from pydantic import BaseModel


class ParserInput(BaseModel):
    """Input model for parsers."""

    file_path: str
    config: Optional[dict[str, Any]] = None

    @property
    def path(self) -> str:
        return self.file_path

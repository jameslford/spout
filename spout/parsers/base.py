from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from shared.utils import _read_file_safe

from ..models.endpoint import Endpoint


class BaseParser(ABC):
    """Base class for all parsers."""

    def __init__(self, project_path: Path, detected_files: List[str]):
        self.project_path = project_path
        self.detected_files = detected_files

    @abstractmethod
    def parse(self, file_path: Path) -> List[Endpoint]:
        """Parse the given file and return a list of endpoints."""
        pass

    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        return _read_file_safe(file_path)

"""Base framework detector interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ..models import FrameworkInfo, Endpoint
from ..shared.utils import _read_file_safe


class BaseFrameworkDetector(ABC):
    """Abstract base class for framework detectors."""

    def __init__(self, project_path: Path, framework_info: FrameworkInfo):
        self.project_path = project_path
        self.framework_info = framework_info
        self.detected_files = framework_info.detected_files

    @classmethod
    @abstractmethod
    def detect(cls, project_path: Path) -> Optional[FrameworkInfo]:
        """
        Detect if the framework is present in the given project.

        Args:
            project_path: Path to the project directory

        Returns:
            FrameworkInfo if detected, None otherwise
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> List[Endpoint]:
        """Parse the given file and return a list of endpoints."""
        pass

    @classmethod
    def _find_python_files(cls, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        return list(project_path.rglob("*.py"))

    @classmethod
    def _read_file_safe(cls, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        return _read_file_safe(file_path)

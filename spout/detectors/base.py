"""Base framework detector interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ..models.framework import FrameworkInfo
from ..shared.utils import _read_file_safe


class BaseFrameworkDetector(ABC):
    """Abstract base class for framework detectors."""

    @abstractmethod
    def detect(self, project_path: Path) -> Optional[FrameworkInfo]:
        """
        Detect if the framework is present in the given project.

        Args:
            project_path: Path to the project directory

        Returns:
            FrameworkInfo if detected, None otherwise
        """
        pass

    def _find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        return list(project_path.rglob("*.py"))

    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        return _read_file_safe(file_path)

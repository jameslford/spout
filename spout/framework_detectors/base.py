"""Base framework detector interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ..models.framework import FrameworkInfo
from ..models.endpoint import Endpoint


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

    @abstractmethod
    def parse_endpoints(
        self, project_path: Path, framework_info: FrameworkInfo
    ) -> List[Endpoint]:
        """
        Parse endpoints from the detected framework.

        Args:
            project_path: Path to the project directory
            framework_info: Information about the detected framework

        Returns:
            List of detected endpoints
        """
        pass

    def _find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        return list(project_path.rglob("*.py"))

    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

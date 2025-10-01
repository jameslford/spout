"""Django Ninja framework detector and parser."""

import re
from pathlib import Path
from typing import Optional

from ..models.framework import FrameworkInfo, SupportedFramework
from .base import BaseFrameworkDetector


class DjangoNinjaDetector(BaseFrameworkDetector):
    """Detector for Django Ninja framework."""

    def detect(self, project_path: Path) -> Optional[FrameworkInfo]:
        """Detect Django Ninja framework in the project."""
        confidence = 0.0
        detected_files = []

        # Check for django-ninja in requirements files
        req_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
        for req_file in req_files:
            req_path = project_path / req_file
            if req_path.exists():
                content = self._read_file_safe(req_path)
                if content and ("django-ninja" in content.lower()):
                    confidence += 0.4
                    detected_files.append(str(req_path))

        # Check for Django settings
        settings_files = list(project_path.rglob("settings.py"))
        if settings_files:
            confidence += 0.2
            detected_files.extend([str(f) for f in settings_files])

        # Check for Django Ninja imports in Python files
        python_files = self._find_python_files(project_path)
        ninja_files = []

        for py_file in python_files:
            content = self._read_file_safe(py_file)
            if content:
                # Look for Ninja imports
                if re.search(r"from\s+ninja\s+import|import\s+ninja", content):
                    confidence += 0.3
                    ninja_files.append(str(py_file))

                # Look for NinjaAPI instantiation
                if re.search(r"NinjaAPI\s*\(|api\s*=\s*NinjaAPI", content):
                    confidence += 0.3
                    if str(py_file) not in ninja_files:
                        ninja_files.append(str(py_file))

        detected_files.extend(ninja_files)

        if confidence >= 0.4:  # Minimum confidence threshold
            return FrameworkInfo(
                name=SupportedFramework.DJANGO_NINJA,
                detected_files=detected_files,
                confidence=min(confidence, 1.0),
            )

        return None

"""
Django Ninja framework detector and parser.
"""

import re
from pathlib import Path
from typing import Optional

from ..models import (
    FrameworkInfo,
    SupportedFramework,
)
from .django_base_detector import DjangoBaseDetector


class DjangoNinjaDetector(DjangoBaseDetector):
    """Detector for Django Ninja framework."""

    SPECIAL_FUNCTION_PARAMETERS = ["request"]

    @classmethod
    def detect(cls, project_path: Path) -> Optional[FrameworkInfo]:
        """Detect Django Ninja framework in the project."""
        confidence = 0.0
        detected_files = []

        # Check for django-ninja in requirements files
        req_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
        for req_file in req_files:
            req_path = project_path / req_file
            if req_path.exists():
                content = cls._read_file_safe(req_path)
                if content and ("django-ninja" in content.lower()):
                    confidence += 0.4
                    detected_files.append(str(req_path))

        # Check for Django settings

        # Check for Django Ninja imports in Python files
        python_files = cls._find_python_files(project_path)
        django_settings = cls._find_django_settings(python_files)
        if not django_settings:
            return None
        confidence += 0.3
        ninja_files = []

        for py_file in python_files:
            content = cls._read_file_safe(py_file)
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
                settings_file=django_settings,
            )

        return None

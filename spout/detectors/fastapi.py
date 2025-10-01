"""FastAPI framework detector and parser."""

import ast
import re
from pathlib import Path
from typing import List, Optional

from ..models.endpoint import Endpoint, EndpointMethod, EndpointParameter, ParameterType
from ..models.framework import FrameworkInfo, SupportedFramework
from .base import BaseFrameworkDetector


class FastAPIDetector(BaseFrameworkDetector):
    """Detector for FastAPI framework."""

    def detect(self, project_path: Path) -> Optional[FrameworkInfo]:
        """Detect FastAPI framework in the project."""
        confidence = 0.0
        detected_files = []

        # Check for FastAPI in requirements files
        req_files = ["requirements.txt", "pyproject.toml", "Pipfile"]
        for req_file in req_files:
            req_path = project_path / req_file
            if req_path.exists():
                content = self._read_file_safe(req_path)
                if content and ("fastapi" in content.lower()):
                    confidence += 0.3
                    detected_files.append(str(req_path))

        # Check for FastAPI imports in Python files
        python_files = self._find_python_files(project_path)
        fastapi_files = []

        for py_file in python_files:
            content = self._read_file_safe(py_file)
            if content:
                # Look for FastAPI imports
                if re.search(r"from\s+fastapi\s+import|import\s+fastapi", content):
                    confidence += 0.2
                    fastapi_files.append(str(py_file))

                # Look for FastAPI app instantiation
                if re.search(r"FastAPI\s*\(|app\s*=\s*FastAPI", content):
                    confidence += 0.3
                    if str(py_file) not in fastapi_files:
                        fastapi_files.append(str(py_file))

        detected_files.extend(fastapi_files)

        if confidence >= 0.3:  # Minimum confidence threshold
            return FrameworkInfo(
                name=SupportedFramework.FASTAPI,
                detected_files=detected_files,
                confidence=min(confidence, 1.0),
            )

        return None

from pathlib import Path
from typing import Optional

from ..models.framework import FrameworkInfo
from .django_ninja import DjangoNinjaDetector
from .fastapi import FastAPIDetector


def detect_framework(project_path: Path) -> Optional[FrameworkInfo]:
    """
    Detect the web framework used in the given project.

    Args:
        project_path: Path to the Python project

    Returns:
        FrameworkInfo if a supported framework is detected, None otherwise
    """
    best_match = None
    best_confidence = 0.0

    for detector in [FastAPIDetector(), DjangoNinjaDetector()]:
        framework_info = detector.detect(project_path)
        if framework_info and framework_info.confidence > best_confidence:
            best_match = framework_info
            best_confidence = framework_info.confidence

    return best_match

from pathlib import Path
from typing import Optional, Type

from .base import BaseFrameworkDetector
from .django_ninja import DjangoNinjaDetector
from .fastapi import FastAPIDetector

DETECTORS = [FastAPIDetector, DjangoNinjaDetector]


def detect_framework(project_path: Path) -> Optional[BaseFrameworkDetector]:
    """
    Detect the web framework used in the given project.

    Args:
        project_path: Path to the Python project

    Returns:
        FrameworkInfo if a supported framework is detected, None otherwise
    """
    best_match = None
    best_confidence = 0.0
    best_detector: Optional[Type[BaseFrameworkDetector]] = None

    for detector in DETECTORS:
        framework_info = detector.detect(project_path)
        if framework_info and framework_info.confidence > best_confidence:
            best_match = framework_info
            best_confidence = framework_info.confidence
            best_detector = detector
    if best_detector and best_match:
        return best_detector(project_path, best_match)
    return None

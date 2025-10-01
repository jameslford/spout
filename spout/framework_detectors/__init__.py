"""Framework detectors package."""

from .base import BaseFrameworkDetector
from .fastapi import FastAPIDetector
from .django_ninja import DjangoNinjaDetector

# Registry of all available detectors
DETECTORS = [
    FastAPIDetector(),
    DjangoNinjaDetector(),
]

__all__ = [
    "BaseFrameworkDetector",
    "FastAPIDetector",
    "DjangoNinjaDetector",
    "DETECTORS",
]

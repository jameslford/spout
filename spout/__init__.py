"""
Spout - Generate TypeScript clients from Python web frameworks.

A tool for automatically detecting Python web frameworks with typed responses
and generating corresponding TypeScript clients.
"""

__version__ = "0.1.0"
__author__ = "James Ford"
__email__ = "jameslford@example.com"

from .core import SpoutGenerator
from .models.endpoint import Endpoint, EndpointMethod, EndpointParameter
from .models.framework import FrameworkInfo, SupportedFramework

__all__ = [
    "SpoutGenerator",
    "Endpoint",
    "EndpointMethod",
    "EndpointParameter",
    "FrameworkInfo",
    "SupportedFramework",
]

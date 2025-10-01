"""Core Spout functionality."""

from pathlib import Path
from typing import List, Optional

from .framework_detectors import DETECTORS
from .generators import GENERATORS
from .models.framework import FrameworkInfo
from .models.endpoint import Endpoint


class SpoutGenerator:
    """Main class for generating TypeScript clients from Python frameworks."""

    def __init__(self):
        """Initialize the generator."""
        self.detectors = DETECTORS

    def detect_framework(self, project_path: Path) -> Optional[FrameworkInfo]:
        """
        Detect the web framework used in the given project.

        Args:
            project_path: Path to the Python project

        Returns:
            FrameworkInfo if a supported framework is detected, None otherwise
        """
        best_match = None
        best_confidence = 0.0

        for detector in self.detectors:
            framework_info = detector.detect(project_path)
            if framework_info and framework_info.confidence > best_confidence:
                best_match = framework_info
                best_confidence = framework_info.confidence

        return best_match

    def parse_endpoints(
        self, project_path: Path, framework_info: FrameworkInfo
    ) -> List[Endpoint]:
        """
        Parse endpoints from the detected framework.

        Args:
            project_path: Path to the Python project
            framework_info: Information about the detected framework

        Returns:
            List of parsed endpoints
        """
        # Find the appropriate detector for the framework
        for detector in self.detectors:
            # Check if this detector handles the framework
            test_info = detector.detect(project_path)
            if test_info and test_info.name == framework_info.name:
                return detector.parse_endpoints(project_path, framework_info)

        return []

    def generate_client(
        self,
        endpoints: List[Endpoint],
        client_type: str = "fetch",
        base_url: str = "",
        include_types: bool = True,
    ) -> str:
        """
        Generate TypeScript client code from endpoints.

        Args:
            endpoints: List of API endpoints
            client_type: Type of client to generate (fetch, axios, etc.)
            base_url: Base URL for API calls
            include_types: Whether to include TypeScript type definitions

        Returns:
            Generated TypeScript code

        Raises:
            ValueError: If client_type is not supported
        """
        if client_type not in GENERATORS:
            available = ", ".join(GENERATORS.keys())
            raise ValueError(
                f"Unsupported client type: {client_type}. Available: {available}"
            )

        generator_class = GENERATORS[client_type]
        generator = generator_class(base_url=base_url, include_types=include_types)

        return generator.generate(endpoints)

    def generate_from_project(
        self,
        project_path: Path,
        client_type: str = "fetch",
        base_url: str = "",
        include_types: bool = True,
    ) -> Optional[str]:
        """
        Generate TypeScript client from a Python project.

        Args:
            project_path: Path to the Python project
            client_type: Type of client to generate
            base_url: Base URL for API calls
            include_types: Whether to include TypeScript type definitions

        Returns:
            Generated TypeScript code if successful, None if no framework detected
        """
        # Detect framework
        framework_info = self.detect_framework(project_path)
        if not framework_info:
            return None

        # Parse endpoints
        endpoints = self.parse_endpoints(project_path, framework_info)
        if not endpoints:
            return None

        # Generate client
        return self.generate_client(
            endpoints=endpoints,
            client_type=client_type,
            base_url=base_url,
            include_types=include_types,
        )

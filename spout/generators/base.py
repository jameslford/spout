"""Base TypeScript client generator."""

from abc import ABC, abstractmethod
from typing import List

from ..models.endpoint import Endpoint


class BaseClientGenerator(ABC):
    """Abstract base class for TypeScript client generators."""

    def __init__(self, base_url: str = "", include_types: bool = True):
        """
        Initialize the generator.

        Args:
            base_url: Base URL for API calls
            include_types: Whether to include TypeScript type definitions
        """
        self.base_url = base_url
        self.include_types = include_types

    @abstractmethod
    def generate(self, endpoints: List[Endpoint]) -> str:
        """
        Generate TypeScript client code from endpoints.

        Args:
            endpoints: List of API endpoints to generate client for

        Returns:
            Generated TypeScript code as string
        """
        pass

    def _generate_types(self, endpoints: List[Endpoint]) -> str:
        """Generate TypeScript type definitions from endpoints."""
        if not self.include_types:
            return ""

        types = set()

        for endpoint in endpoints:
            # Generate parameter types
            for param in endpoint.parameters:
                if param.type not in ["string", "number", "boolean", "any", "object"]:
                    types.add(param.type)

            # Generate response types
            for response in endpoint.responses:
                if response.type not in [
                    "string",
                    "number",
                    "boolean",
                    "any",
                    "object",
                ]:
                    types.add(response.type)

        if not types:
            return ""

        type_definitions = ["// Type definitions"]
        for type_name in sorted(types):
            # This is a simplified type definition - in practice, you'd want
            # more sophisticated type extraction from Python models
            type_definitions.append(f"export interface {type_name} {{")
            type_definitions.append("  // TODO: Extract actual type definition")
            type_definitions.append("}")
            type_definitions.append("")

        return "\n".join(type_definitions)

    def _sanitize_method_name(self, name: str) -> str:
        """Sanitize method name for TypeScript."""
        # Remove invalid characters and ensure it starts with a letter
        import re

        name = re.sub(r"[^a-zA-Z0-9_]", "", name)
        if name and name[0].isdigit():
            name = f"method{name}"
        return name or "unknownMethod"

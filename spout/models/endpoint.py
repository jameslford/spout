"""Models for API endpoint definitions."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EndpointMethod(str, Enum):
    """HTTP methods for API endpoints."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ParameterType(str, Enum):
    """Types of endpoint parameters."""

    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"
    FORM = "form"


class EndpointParameter(BaseModel):
    """Represents a parameter for an API endpoint."""

    name: str
    type: str  # TypeScript type string
    python_type: str  # Original Python type
    parameter_type: ParameterType
    required: bool = True
    default: Optional[Any] = None
    description: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class EndpointResponse(BaseModel):
    """Represents a response schema for an API endpoint."""

    status_code: int
    type: str  # TypeScript type string
    python_type: str  # Original Python type
    description: Optional[str] = None


class Endpoint(BaseModel):
    """Represents an API endpoint with all its metadata."""

    path: str
    method: EndpointMethod
    function_name: str
    parameters: List[EndpointParameter] = []
    responses: List[EndpointResponse] = []
    description: Optional[str] = None
    tags: List[str] = []
    deprecated: bool = False

    # Framework-specific metadata
    framework_data: Dict[str, Any] = {}

    class Config:
        """Pydantic configuration."""

        use_enum_values = True

    @property
    def typescript_method_name(self) -> str:
        """Generate a TypeScript-friendly method name."""
        # Convert path parameters and method to camelCase
        method_prefix = self.method.lower()

        generic_parts = ["api", "v1", "v2", "v3", "v4", "v5"]

        def exclude_part(part: str) -> bool:
            fast_style = part.startswith("{") and part.endswith("}")
            django_style = part.startswith("<") and part.endswith(">")
            generic_style = part.lower() in generic_parts
            return fast_style or django_style or generic_style

        path_parts = [
            part for part in self.path.split("/") if part and not exclude_part(part)
        ]

        if not path_parts:
            return method_prefix
        print("path_parts before:", path_parts)

        # Convert kebab-case to camelCase
        camel_parts = []
        print("path_parts:", path_parts)
        for part in path_parts:
            words = part.replace("-", "_").split("_")
            camel_parts.extend([words[0].lower()] + [w.capitalize() for w in words[1:]])
        if camel_parts and len(camel_parts) > 1:
            first = camel_parts[0]
            if first.endswith("s"):
                # Plural to singular (basic heuristic)
                first = first[:-1]
                camel_parts[0] = first
        return method_prefix + "".join(word.capitalize() for word in camel_parts)

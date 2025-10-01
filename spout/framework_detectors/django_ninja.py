"""Django Ninja framework detector and parser."""

import re
from pathlib import Path
from typing import Optional
import ast
from pathlib import Path
from typing import List, Optional

from ..models import (
    Endpoint,
    EndpointMethod,
    EndpointParameter,
    ParameterType,
    FrameworkInfo,
    SupportedFramework,
)
from .base import BaseFrameworkDetector


class DjangoNinjaDetector(BaseFrameworkDetector):
    """Detector for Django Ninja framework."""

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
        settings_files = list(project_path.rglob("settings.py"))
        if settings_files:
            confidence += 0.2
            detected_files.extend([str(f) for f in settings_files])

        # Check for Django Ninja imports in Python files
        python_files = cls._find_python_files(project_path)
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
            )

        return None

    def parse(self) -> List[Endpoint]:
        """Parse Django Ninja endpoints from the project."""
        endpoints = []

        for file_path_str in self.detected_files:
            if not file_path_str.endswith(".py"):
                continue

            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            content = self._read_file_safe(file_path)
            if not content:
                continue

            try:
                tree = ast.parse(content)
                endpoints.extend(self._parse_ast_for_endpoints(tree, file_path))
            except SyntaxError:
                # Skip files with syntax errors
                continue

        return endpoints

    def _parse_ast_for_endpoints(
        self, tree: ast.AST, file_path: Path
    ) -> List[Endpoint]:
        """Parse AST tree for Django Ninja endpoints."""
        endpoints = []

        for node in ast.walk(tree):
            # Look for decorator calls like @api.get("/path")
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    endpoint = self._parse_decorator_endpoint(
                        decorator, node, file_path
                    )
                    if endpoint:
                        endpoints.append(endpoint)

        return endpoints

    def _parse_decorator_endpoint(
        self, decorator: ast.AST, func_node: ast.FunctionDef, file_path: Path
    ) -> Optional[Endpoint]:
        """Parse a Django Ninja decorator to extract endpoint information."""
        # Handle @api.get(), @router.post(), etc.
        if not isinstance(decorator, ast.Call):
            return None

        if not isinstance(decorator.func, ast.Attribute):
            return None

        method_name = decorator.func.attr.upper()
        if method_name not in [m.value for m in EndpointMethod]:
            return None

        # Extract path from the first argument
        if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
            return None

        path = decorator.args[0].value
        if not isinstance(path, str):
            return None

        # Parse function parameters
        parameters = self._parse_function_parameters(func_node)

        return Endpoint(
            path=path,
            method=EndpointMethod(method_name),
            function_name=func_node.name,
            parameters=parameters,
            description=ast.get_docstring(func_node),
            framework_data={
                "file_path": str(file_path),
                "line_number": func_node.lineno,
            },
        )

    def _parse_function_parameters(
        self, func_node: ast.FunctionDef
    ) -> List[EndpointParameter]:
        """Parse function parameters to extract endpoint parameters."""
        parameters = []

        for arg in func_node.args.args:
            if arg.arg in ["self", "cls", "request"]:  # Skip Django-specific parameters
                continue

            param_type = "any"  # Default type
            if arg.annotation:
                param_type = self._ast_to_type_string(arg.annotation)

            # Determine parameter type based on name patterns
            if "path" in arg.arg.lower() or "id" in arg.arg.lower():
                parameter_type = ParameterType.PATH
            elif "body" in arg.arg.lower() or "data" in arg.arg.lower():
                parameter_type = ParameterType.BODY
            else:
                parameter_type = ParameterType.QUERY

            parameters.append(
                EndpointParameter(
                    name=arg.arg,
                    type=param_type,
                    python_type=param_type,
                    parameter_type=parameter_type,
                    required=True,  # TODO: Detect optional parameters
                )
            )

        return parameters

    def _ast_to_type_string(self, annotation: ast.AST) -> str:
        """Convert AST type annotation to TypeScript type string."""
        if isinstance(annotation, ast.Name):
            type_mapping = {
                "str": "string",
                "int": "number",
                "float": "number",
                "bool": "boolean",
                "dict": "object",
                "list": "any[]",
                "List": "any[]",
                "Dict": "object",
            }
            return type_mapping.get(annotation.id, annotation.id)
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return "any"  # Fallback for complex types

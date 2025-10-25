"""Base framework detector interface."""

import ast
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from shared.utils import classproperty

from ..models import FrameworkInfo, Endpoint
from ..models.endpoint import (
    EndpointMethod,
    EndpointParameter,
    ParameterType,
    TypeScriptInterface,
)


class BaseFrameworkDetector(ABC):
    """Abstract base class for framework detectors."""

    GENERIC_FUNCTION_PARAMETERS = ["self", "cls"]
    SPECIAL_FUNCTION_PARAMETERS = []

    @classproperty
    def function_parameters(cls):
        return cls.GENERIC_FUNCTION_PARAMETERS + cls.SPECIAL_FUNCTION_PARAMETERS

    def __init__(self, project_path: Path, framework_info: FrameworkInfo):
        self.project_path = project_path
        self.framework_info = framework_info
        self.detected_files: List[Path] = framework_info.detected_files

    @classmethod
    @abstractmethod
    def detect(cls, project_path: Path) -> Optional[FrameworkInfo]:
        """
        Detect if the framework is present in the given project.

        Args:
            project_path: Path to the project directory

        Returns:
            FrameworkInfo if detected, None otherwise
        """
        pass

    @classmethod
    def _find_python_files(cls, project_path: Path) -> List[Path]:
        """Find all Python files in the project, excluding virtual environments and other non-project directories."""
        # Directories to exclude from scanning
        exclude_patterns = {
            # Virtual environments
            "venv",
            "env",
            ".venv",
            ".env",
            # Python cache and build directories
            "__pycache__",
            ".pytest_cache",
            "build",
            "dist",
            ".tox",
            # Version control
            ".git",
            ".hg",
            ".svn",
            # IDE and editor directories
            ".vscode",
            ".idea",
            ".vs",
            # Node.js (for mixed projects)
            "node_modules",
            # Other common patterns
            ".mypy_cache",
            ".coverage",
            "htmlcov",
            # Site-packages (system Python installations)
            "site-packages",
        }

        python_files = []

        for py_file in project_path.rglob("*.py"):
            # Check if any part of the path matches exclude patterns
            should_exclude = False

            for part in py_file.parts:
                # Exclude directories that start with . (except current directory)
                if part.startswith(".") and len(part) > 1:
                    should_exclude = True
                    break

                # Exclude specific directory patterns
                if part.lower() in exclude_patterns:
                    should_exclude = True
                    break

                # Exclude directories that end with common virtual env suffixes
                if part.endswith(("venv", "-venv", "_venv", ".venv")):
                    should_exclude = True
                    break

            # Additional check for test files
            if not should_exclude:
                # Check if this is a test file in a test directory
                if py_file.name.startswith("test_"):
                    # Check if any parent directory is named "test" or "tests"
                    for parent in py_file.parents:
                        if parent.name.lower() in ("test", "tests"):
                            should_exclude = True
                            break

            if not should_exclude:
                python_files.append(py_file)

        return python_files

    @classmethod
    def _read_file_safe(cls, file_path: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    def parse(self) -> List[Endpoint]:
        """Parse FastAPI endpoints from the project."""
        endpoints = []

        for file_path in self.detected_files:
            if not str(file_path).endswith(".py"):
                continue

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
        """Parse AST tree for FastAPI endpoints."""
        endpoints = []

        for node in ast.walk(tree):
            # Look for decorator calls like @app.get("/path")
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
        """Parse a FastAPI decorator to extract endpoint information."""
        # Handle @app.get(), @router.post(), etc.
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

        # Parse return type annotation
        return_type = None
        python_return_type = None
        return_interface = None

        if func_node.returns:
            python_return_type = self._ast_to_python_type_string(func_node.returns)
            return_type = self._ast_to_typescript_type_string(func_node.returns)

            # Check if the return type is a Pydantic model (on-demand parsing)
            model_name = None
            if isinstance(func_node.returns, ast.Name):
                model_name = func_node.returns.id
            elif isinstance(func_node.returns, ast.Subscript):
                # Handle List[Model], Optional[Model], etc.
                model_name = self._extract_inner_type_name(func_node.returns)

            # Only parse the model if we found a potential model name
            if model_name:
                return_interface = self._parse_pydantic_model_by_name(model_name)

        return Endpoint(
            path=path,
            method=EndpointMethod(method_name),
            function_name=func_node.name,
            parameters=parameters,
            description=ast.get_docstring(func_node),
            return_type=return_type,
            python_return_type=python_return_type,
            return_interface=return_interface,
            framework_data={
                "file_path": str(file_path),
                "line_number": func_node.lineno,
            },
        )

    def _parse_function_parameters(
        self, func_node: ast.FunctionDef
    ) -> List[EndpointParameter]:
        """
        Parse function parameters to extract endpoint parameters.
        """
        parameters = []

        for arg in func_node.args.args:
            if arg.arg in self.function_parameters:  # Skip Django-specific parameters
                continue

            param_type = "any"  # Default type
            if arg.annotation:
                param_type = self._ast_to_typescript_type_string(arg.annotation)

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
                    required=True,
                )
            )

        return parameters

    def _parse_pydantic_model_by_name(
        self, model_name: str
    ) -> Optional[TypeScriptInterface]:
        """
        Find and parse a Pydantic model by name from the project files.
        Only searches when we actually need a specific model, not upfront.
        """
        # Search all Python files in the project for the model

        for py_file in self.framework_info.detected_files:
            content = self._read_file_safe(py_file)
            if not content:
                continue

            # Quick check if the model name appears in the file
            if model_name not in content:
                continue

            try:
                tree = ast.parse(content)
                interface = self._find_pydantic_model_in_ast(tree, model_name)
                if interface:
                    return interface
            except SyntaxError:
                continue

        return None

    def _find_pydantic_model_in_ast(
        self, tree: ast.AST, target_model_name: str
    ) -> Optional[TypeScriptInterface]:
        """Find a specific Pydantic model by name in an AST tree."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == target_model_name:
                # Check if this class inherits from BaseModel
                is_pydantic_model = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseModel":
                        is_pydantic_model = True
                        break
                    elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                        is_pydantic_model = True
                        break

                if is_pydantic_model:
                    return self._parse_pydantic_model_fields(node)

        return None

    def _parse_pydantic_model_fields(
        self, class_node: ast.ClassDef
    ) -> Optional[TypeScriptInterface]:
        """Parse fields from a Pydantic model class definition."""
        fields = {}
        optional_fields = []

        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                # This is a field with type annotation
                field_name = node.target.id

                # Skip private fields and class config
                if field_name.startswith("_") or field_name in [
                    "Config",
                    "model_config",
                ]:
                    continue

                # Parse the type annotation
                field_type = self._ast_to_typescript_type_string(node.annotation)

                # Check if field is optional (has default value or is Optional)
                is_optional = False
                if node.value is not None:  # Has default value
                    is_optional = True
                elif self._is_optional_type(node.annotation):
                    is_optional = True

                fields[field_name] = field_type
                if is_optional:
                    optional_fields.append(field_name)

        if not fields:
            return None

        return TypeScriptInterface(
            name=class_node.name,
            fields=fields,
            optional_fields=optional_fields,
            description=ast.get_docstring(class_node),
            source_model=class_node.name,
        )

    def _is_optional_type(self, annotation: ast.AST) -> bool:
        """Check if a type annotation represents an Optional type."""
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id in ["Optional", "Union"]
        return False

    def _extract_inner_type_name(self, annotation: ast.AST) -> Optional[str]:
        """Extract the inner type name from generic types like List[Model], Optional[Model]."""
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.slice, ast.Name):
                return annotation.slice.id
            elif isinstance(annotation.slice, ast.Tuple) and annotation.slice.elts:
                # Handle Union types - take the first non-None type
                for elt in annotation.slice.elts:
                    if isinstance(elt, ast.Name) and elt.id != "None":
                        return elt.id
        return None

    def _ast_to_typescript_type_string(self, annotation: ast.AST) -> str:
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
                "None": "null",
                "Optional": "any | null",
            }
            return type_mapping.get(annotation.id, annotation.id)
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like List[str], Dict[str, int], Optional[User]
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if base_type == "List":
                    inner_type = self._ast_to_typescript_type_string(annotation.slice)
                    return f"{inner_type}[]"
                elif base_type == "Dict":
                    if (
                        isinstance(annotation.slice, ast.Tuple)
                        and len(annotation.slice.elts) == 2
                    ):
                        key_type = self._ast_to_typescript_type_string(
                            annotation.slice.elts[0]
                        )
                        value_type = self._ast_to_typescript_type_string(
                            annotation.slice.elts[1]
                        )
                        return f"Record<{key_type}, {value_type}>"
                    return "object"
                elif base_type == "Optional":
                    inner_type = self._ast_to_typescript_type_string(annotation.slice)
                    return f"{inner_type} | null"
                elif base_type == "Union":
                    if isinstance(annotation.slice, ast.Tuple):
                        union_types = [
                            self._ast_to_typescript_type_string(t)
                            for t in annotation.slice.elts
                        ]
                        return " | ".join(union_types)
            return "any"
        else:
            return "any"  # Fallback for complex types

    def _ast_to_python_type_string(self, annotation: ast.AST) -> str:
        """Convert AST type annotation to Python type string for reference."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    return f"{base_type}[{annotation.slice.id}]"
                elif isinstance(annotation.slice, ast.Tuple):
                    slice_types = [
                        self._ast_to_python_type_string(t)
                        for t in annotation.slice.elts
                    ]
                    return f"{base_type}[{', '.join(slice_types)}]"
                elif hasattr(annotation.slice, "value"):  # Handle single slice
                    return f"{base_type}[{self._ast_to_python_type_string(annotation.slice)}]"
            return "Any"
        else:
            return "Any"

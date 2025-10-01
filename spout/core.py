"""Core Spout functionality."""

from typing import TYPE_CHECKING, Dict, List, Type

from .detectors import detect_framework
from .generators import GENERATORS, BaseClientGenerator
from .models.cli_input import DetectInput, GenerateInput
from .models.endpoint import Endpoint
from .models.framework import FrameworkInfo
from .parsers import DjangoNinjaParser, FastAPIParser
from .shared.constants import SupportedFramework

if TYPE_CHECKING:
    from .parsers.base import BaseParser


class SpoutDetector:
    """Class for detecting the web framework used in a Python project."""

    def __init__(self, input_data: DetectInput):
        """Initialize the detector."""
        self.input_data = input_data
        self._framework_info = None

    @property
    def framework_info(self) -> FrameworkInfo:
        if self._framework_info is None:
            framework = detect_framework(self.input_data.path)
            if not framework:
                raise ValueError(
                    f"No supported framework detected in {self.input_data.path}"
                )
            self._framework_info = framework
        return self._framework_info


class SpoutParser(SpoutDetector):
    """Class for parsing endpoints from the detected framework."""

    FRAMEWORK_PARSER_MAP: Dict[SupportedFramework, Type[BaseParser]] = {
        SupportedFramework.FASTAPI: FastAPIParser,
        SupportedFramework.DJANGO_NINJA: DjangoNinjaParser,
    }

    def __init__(self, input_data: DetectInput):
        """Initialize the parser."""
        self.input_data = input_data
        self._framework_info = None
        self._parser = None
        self._endpoints = None

    @property
    def parser(self) -> "BaseParser":
        if self._parser is None:
            parser_class = self.FRAMEWORK_PARSER_MAP.get(self.framework_info.name)
            if not parser_class:
                raise ValueError(
                    f"No parser available for framework: {self.framework_info.name}"
                )
            self._parser = parser_class(
                self.input_data.path, self.framework_info.detected_files
            )
        return self._parser

    @property
    def endpoints(self) -> List[Endpoint]:
        if self._endpoints is None:
            self._endpoints = self.parser.parse(self.input_data.path)
        return self._endpoints


class SpoutGenerator(SpoutParser):
    """Main class for generating TypeScript clients from Python frameworks."""

    def __init__(self, input_data: GenerateInput):
        """Initialize the generator."""
        self.input_data = input_data
        self._framework_info = None
        self._parser = None
        self._generator = None

    @property
    def generator(self) -> "BaseClientGenerator":
        if self._generator is None:
            if self.input_data.client_type not in GENERATORS:
                raise ValueError(
                    f"Unsupported client type: {self.input_data.client_type}. Available: {list(GENERATORS.keys())}"
                )
            self._generator = GENERATORS[self.input_data.client_type](
                base_url=self.input_data.base_url,
                include_types=self.input_data.include_types,
            )
        return self._generator

    def generate_client(self) -> str:
        """
        Generate TypeScript client code from endpoints.

        Returns:
            Generated TypeScript code

        Raises:
            ValueError: If client_type is not supported
        """
        if self.input_data.client_type not in GENERATORS:
            available = ", ".join(GENERATORS.keys())
            raise ValueError(
                f"Unsupported client type: {self.input_data.client_type}. Available: {available}"
            )

        generator_class = GENERATORS[self.input_data.client_type]
        generator = generator_class(
            base_url=self.input_data.base_url,
            include_types=self.input_data.include_types,
        )
        return generator.generate(self.endpoints)

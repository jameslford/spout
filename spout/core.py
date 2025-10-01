"""Core Spout functionality."""

from typing import List, Optional

from .framework_detectors import detect_framework, BaseFrameworkDetector
from .generators import GENERATORS, BaseClientGenerator
from .models import DetectInput, GenerateInput, Endpoint, FrameworkInfo


class SpoutDetector:
    """Class for detecting the web framework used in a Python project."""

    def __init__(self, input_data: DetectInput | GenerateInput):
        """Initialize the detector."""
        self.input_data: DetectInput | GenerateInput = input_data
        self._detector: Optional[BaseFrameworkDetector] = None
        self._framework_info = None
        self._endpoints: Optional[List[Endpoint]] = None

    @property
    def detector(self) -> BaseFrameworkDetector:
        if self._detector is None:
            print("project path is:", self.input_data.path)
            detector = detect_framework(self.input_data.path)
            if not detector:
                raise ValueError(
                    f"No supported framework detected in {self.input_data.path}"
                )
            self._detector = detector
        return self._detector

    @property
    def framework_info(self) -> FrameworkInfo:
        if self._framework_info is None:
            self._framework_info = self.detector.framework_info
        return self._framework_info

    @property
    def endpoints(self) -> List[Endpoint]:
        if self._endpoints is None:
            self._endpoints = self.detector.parse(self.input_data.path)
        return self._endpoints


class SpoutGenerator(SpoutDetector):
    """Main class for generating TypeScript clients from Python frameworks."""

    def __init__(self, input_data: GenerateInput):
        """Initialize the generator."""
        super().__init__(input_data)
        self.input_data: GenerateInput = input_data
        self._generator: BaseClientGenerator | None = None

    @property
    def generator(self) -> "BaseClientGenerator":
        if self._generator is None:
            if self.input_data.client_type not in GENERATORS:
                raise ValueError(
                    f"Unsupported client type: {self.input_data.client_type}. Available: {list(GENERATORS.keys())}"
                )
            generator = GENERATORS[self.input_data.client_type](
                base_url=self.input_data.base_url,
                include_types=self.input_data.include_types,
            )
            self._generator = generator
        return self._generator  # type: ignore

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

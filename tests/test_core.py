"""Basic tests for Spout functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from spout.core import SpoutGenerator
from spout.models.endpoint import Endpoint, EndpointMethod
from spout.models.framework import FrameworkInfo, SupportedFramework
from spout.models.cli_input import GenerateInput


@pytest.fixture
def generator():
    """Create a SpoutGenerator instance for testing."""
    input_data = GenerateInput(project_path=".", output_path="./output.tsx")
    return SpoutGenerator(input_data)


@pytest.fixture
def sample_endpoints():
    """Create sample endpoints for testing."""
    return [
        Endpoint(
            path="/users",
            method=EndpointMethod.GET,
            function_name="get_users",
            description="Get list of users",
        ),
        Endpoint(
            path="/users/{user_id}",
            method=EndpointMethod.GET,
            function_name="get_user",
            description="Get user by ID",
        ),
        Endpoint(
            path="/users",
            method=EndpointMethod.POST,
            function_name="create_user",
            description="Create a new user",
        ),
    ]


class TestSpoutGenerator:
    """Test cases for SpoutGenerator."""

    def test_generate_client_fetch(self, sample_endpoints):
        """Test generating fetch client."""
        input_data = GenerateInput(project_path=".", output_path="./output.tsx")
        generator = SpoutGenerator(input_data)
        generator._endpoints = sample_endpoints  # Directly set endpoints for testing
        client_code = generator.generate_client()

        assert "fetch" in client_code
        assert "ApiClient" in client_code
        assert "getUsers" in client_code
        assert "getUser" in client_code
        assert "postUsers" in client_code

    def test_generate_client_axios(self, sample_endpoints):
        """Test generating axios client."""
        input_data = GenerateInput(
            project_path=".", output_path="./output.tsx", client_type="axios"
        )
        generator = SpoutGenerator(input_data)
        generator._endpoints = sample_endpoints  # Directly set endpoints for testing
        client_code = generator.generate_client()

        assert "axios" in client_code
        assert "ApiClient" in client_code
        assert "getUsers" in client_code
        assert "getUser" in client_code
        assert "postUsers" in client_code

    def test_generate_client_invalid_type(self, sample_endpoints):
        """Test generating client with invalid type."""
        with pytest.raises(ValueError):
            input_data = GenerateInput(
                project_path=".", output_path="./output.tsx", client_type="invalid"
            )
            generator = SpoutGenerator(input_data)
            generator._endpoints = (
                sample_endpoints  # Directly set endpoints for testing
            )
            generator.generate_client()

    @patch("detectors.detect_service.detect_framework")
    @patch("parsers.fastapi.FastAPIParser.parse_endpoints")
    def test_generate_from_project(self, mock_parse, mock_detect, sample_endpoints):
        """Test generating client from project."""
        # Mock framework detection
        mock_detect.return_value = FrameworkInfo(
            name=SupportedFramework.FASTAPI, confidence=0.9
        )

        # Mock endpoint parsing
        mock_parse.return_value = sample_endpoints

        # Generate client
        generator = SpoutGenerator(
            GenerateInput(
                project_path="/fake/path",
                output_path="./output.tsx",
                client_type="fetch",
            )
        )
        result = generator.generate_client()

        assert result is not None
        assert "ApiClient" in result
        mock_detect.assert_called_once()
        mock_parse.assert_called_once()


class TestEndpointModels:
    """Test cases for endpoint models."""

    def test_endpoint_typescript_method_name(self):
        """Test TypeScript method name generation."""
        endpoint = Endpoint(
            path="/users/{user_id}/posts",
            method=EndpointMethod.GET,
            function_name="get_user_posts",
        )

        assert endpoint.typescript_method_name == "getUserPosts"

    def test_endpoint_with_hyphens(self):
        """Test TypeScript method name with hyphens."""
        endpoint = Endpoint(
            path="/api/user-profiles",
            method=EndpointMethod.POST,
            function_name="create_user_profile",
        )

        assert endpoint.typescript_method_name == "postApiUserProfiles"


if __name__ == "__main__":
    pytest.main([__file__])

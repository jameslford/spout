"""Basic tests for Spout functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from spout.core import SpoutGenerator
from spout.models.framework import FrameworkInfo, SupportedFramework
from spout.models.endpoint import Endpoint, EndpointMethod


@pytest.fixture
def generator():
    """Create a SpoutGenerator instance for testing."""
    return SpoutGenerator()


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

    def test_init(self, generator):
        """Test generator initialization."""
        assert generator.detectors is not None
        assert len(generator.detectors) > 0

    def test_generate_client_fetch(self, generator, sample_endpoints):
        """Test generating fetch client."""
        client_code = generator.generate_client(
            endpoints=sample_endpoints,
            client_type="fetch",
            base_url="https://api.example.com",
        )

        assert "fetch" in client_code
        assert "ApiClient" in client_code
        assert "getUsers" in client_code
        assert "getUser" in client_code
        assert "postUsers" in client_code

    def test_generate_client_axios(self, generator, sample_endpoints):
        """Test generating axios client."""
        client_code = generator.generate_client(
            endpoints=sample_endpoints,
            client_type="axios",
            base_url="https://api.example.com",
        )

        assert "axios" in client_code
        assert "ApiClient" in client_code
        assert "getUsers" in client_code
        assert "getUser" in client_code
        assert "postUsers" in client_code

    def test_generate_client_invalid_type(self, generator, sample_endpoints):
        """Test generating client with invalid type."""
        with pytest.raises(ValueError):
            generator.generate_client(
                endpoints=sample_endpoints, client_type="invalid_type"
            )

    @patch("spout.core.SpoutGenerator.detect_framework")
    @patch("spout.core.SpoutGenerator.parse_endpoints")
    def test_generate_from_project(
        self, mock_parse, mock_detect, generator, sample_endpoints
    ):
        """Test generating client from project."""
        # Mock framework detection
        mock_detect.return_value = FrameworkInfo(
            name=SupportedFramework.FASTAPI, confidence=0.9
        )

        # Mock endpoint parsing
        mock_parse.return_value = sample_endpoints

        # Generate client
        result = generator.generate_from_project(
            project_path=Path("/fake/path"), client_type="fetch"
        )

        assert result is not None
        assert "ApiClient" in result
        mock_detect.assert_called_once()
        mock_parse.assert_called_once()

    @patch("spout.core.SpoutGenerator.detect_framework")
    def test_generate_from_project_no_framework(self, mock_detect, generator):
        """Test generating client when no framework is detected."""
        mock_detect.return_value = None

        result = generator.generate_from_project(
            project_path=Path("/fake/path"), client_type="fetch"
        )

        assert result is None


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

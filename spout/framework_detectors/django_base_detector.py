from pathlib import Path
import re
from typing import List, Optional
from spout.models.framework import FrameworkInfo
from .base import BaseFrameworkDetector


class DjangoBaseDetector(BaseFrameworkDetector):
    """Base detector for Django-based frameworks."""

    def __init__(self, project_path: Path, framework_info: FrameworkInfo):
        if not framework_info.settings_file:
            raise ValueError("Django framework detection requires a settings file.")
        super().__init__(project_path, framework_info)

    @classmethod
    def _find_django_settings(cls, python_files: List[Path]) -> Optional[str]:
        """
        Find THE main Django settings file by scoring candidates on multiple indicators.

        Returns exactly one file path - the most likely main settings file.
        Uses confidence scoring based on:
        - INSTALLED_APPS (required)
        - ROOT_URLCONF (high confidence)
        - WSGI_APPLICATION/ASGI_APPLICATION (high confidence)

        Files with all 3 indicators are nearly certain to be the main settings file.
        """
        # Find all Python files that contain INSTALLED_APPS constant

        candidates = []

        for py_file in python_files:
            content = cls._read_file_safe(py_file)
            if not content or not cls._contains_installed_apps(content):
                continue

            # Score this candidate based on Django settings indicators
            score = 1  # Base score for having INSTALLED_APPS

            if cls._contains_url_conf(content):
                score += 2  # ROOT_URLCONF is a strong indicator

            if cls._contains_wsgi_or_asgi(content):
                score += 2  # WSGI/ASGI is a strong indicator

            # Bonus points for being named settings.py or being in settings directory
            if py_file.name == "settings.py":
                score += 1
            elif py_file.parent.name == "settings":
                score += 0.5

            # Penalty for being in test directories (to avoid test settings)
            if "test" in str(py_file).lower():
                score -= 1

            candidates.append((py_file, score))

        if not candidates:
            return None

        # Sort by score (highest first) and return the best candidate
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_candidate = candidates[0][0]

        return str(best_candidate)

    @classmethod
    def _contains_installed_apps(cls, content: str) -> bool:
        """
        Check if the file content contains INSTALLED_APPS constant definition.

        Looks for patterns like:
        - INSTALLED_APPS = [
        - INSTALLED_APPS = (
        - INSTALLED_APPS=[
        - INSTALLED_APPS+=[  (for extending)
        """
        # Look for INSTALLED_APPS assignment patterns
        patterns = [
            r"INSTALLED_APPS\s*=\s*\[",  # INSTALLED_APPS = [
            r"INSTALLED_APPS\s*=\s*\(",  # INSTALLED_APPS = (
            r"INSTALLED_APPS\s*\+=\s*\[",  # INSTALLED_APPS += [
            r"INSTALLED_APPS\s*\+=\s*\(",  # INSTALLED_APPS += (
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                return True

        return False

    @classmethod
    def _contains_url_conf(cls, content: str) -> bool:
        """
        search for the `ROOT_URLCONF` setting in the content, which should be a string assignment like:
        ROOT_URLCONF = 'myproject.urls'
        """
        pattern = r"ROOT_URLCONF\s*=\s*['\"]"  # ROOT_URLCONF = '
        return bool(re.search(pattern, content))

    @classmethod
    def _contains_wsgi_or_asgi(cls, content: str) -> bool:
        """
        Check if the file content contains WSGI or ASGI application definition.

        Looks for patterns like:
        - WSGI_APPLICATION = 'myproject.wsgi.application'
        - ASGI_APPLICATION = 'myproject.asgi.application'
        """
        patterns = [
            r"WSGI_APPLICATION\s*=\s*['\"]",  # WSGI_APPLICATION = '
            r"ASGI_APPLICATION\s*=\s*['\"]",  # ASGI_APPLICATION = '
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                return True

        return False

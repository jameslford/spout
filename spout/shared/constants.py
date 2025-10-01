from enum import Enum


class SupportedFramework(str, Enum):
    """Enumeration of supported Python web frameworks."""

    FASTAPI = "fastapi"
    DJANGO_NINJA = "django-ninja"
    DJANGO = "django"
    DRF = "djangorestframework"
    FLASK = "flask"
    TORNADO = "tornado"

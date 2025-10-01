"""TypeScript client generators package."""

from .axios import AxiosClientGenerator
from .base import BaseClientGenerator
from .fetch import FetchClientGenerator

# Registry of available generators
GENERATORS = {
    "fetch": FetchClientGenerator,
    "axios": AxiosClientGenerator,
}

__all__ = [
    "BaseClientGenerator",
    "FetchClientGenerator",
    "AxiosClientGenerator",
    "GENERATORS",
]

"""TypeScript client generators package."""

from .base import BaseClientGenerator
from .fetch import FetchClientGenerator
from .axios import AxiosClientGenerator

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

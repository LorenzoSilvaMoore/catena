from importlib.metadata import version, PackageNotFoundError

try:
    __version__: str | None = version("catena-scf")
except PackageNotFoundError:
    __version__ = None  # package not installed (e.g. running from source)

from . import mathlib
from . import strings
from . import cache
from . import numbers

from .catena import (
    SimpleContinuedFraction,
    FiniteSimpleContinuedFraction,
    PeriodicSimpleContinuedFraction,
)

from .generators import (
    Generator,
    CachedGenerator,
    FiniteGenerator,
    PeriodicGenerator,
)

__all__ = [
    "SimpleContinuedFraction",
    "FiniteSimpleContinuedFraction",
    "PeriodicSimpleContinuedFraction",
    "Generator",
    "CachedGenerator",
    "FiniteGenerator",
    "PeriodicGenerator",
]
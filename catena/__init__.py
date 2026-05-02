# from .catena import (
#     Method,
#     StringMethod,
#     Convert,
#     FinateSimpleContinuedFraction,
# )

# __all__ = [
#     "Method",
#     "StringMethod",
#     "Convert",
#     "FinateSimpleContinuedFraction",
# ]

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("catena-scf")
except PackageNotFoundError:
    __version__ = None  # package not installed (e.g. running from source)

from . import mathlib

from .catena import (
    SimpleContinuedFraction,
    FiniteSimpleContinuedFraction,
    PeriodicSimpleContinuedFraction,
)

from .generators import (
    Generator,
    CachedGenerator,
    FiniteGenerator,
)

__all__ = [
    "SimpleContinuedFraction",
    "FiniteSimpleContinuedFraction",
    "PeriodicSimpleContinuedFraction",
    "Generator",
    "CachedGenerator",
    "FiniteGenerator",
]
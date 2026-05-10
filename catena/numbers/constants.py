from ..catena import (
    SimpleContinuedFraction, 
    FiniteSimpleContinuedFraction, 
    PeriodicSimpleContinuedFraction
)


# e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, ...]
# Pattern: a(3k+1)=1, a(3k+2)=1, a(3k)=2k  (0-indexed body)
def _e_generator(n: int) -> int:
    """Returns the generator for the simple continued fraction expansion of e."""
    k, r = divmod(n+1, 3)
    return 2 * (k+1) if r == 2 else 1

e = SimpleContinuedFraction(
    generator=_e_generator,
    integer_part=2,
)

phi = PeriodicSimpleContinuedFraction(
    period=[1],
    pre_period=[],
    integer_part=1
)

sqrt2 = PeriodicSimpleContinuedFraction(
    period=[2],
    pre_period=[],
    integer_part=1
)

sqrt3 = PeriodicSimpleContinuedFraction(
    period=[1, 2],
    pre_period=[],
    integer_part=1
)

sqrt5 = PeriodicSimpleContinuedFraction(
    period=[4],
    pre_period=[],
    integer_part=2
)

def metallic_mean(n: int) -> SimpleContinuedFraction:
    """Returns the n-th metallic mean as a simple continued fraction."""
    return PeriodicSimpleContinuedFraction(
        period=[n],
        pre_period=[],
        integer_part=n
    )

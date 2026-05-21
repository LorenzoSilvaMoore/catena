from math import gcd, lcm

from typing import Optional, Tuple
from decimal import Decimal

from .core import get_sign

def _square_part_sqrt(D: int) -> int:
    """Returns the largest integer s such that s² divides D."""
    s, n, p = 1, D, 2
    while p * p <= n:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        s *= p ** (count // 2)
        p += 1
    return s


def simplify_quadratic_surd(P: int, Q: int, D: int) -> Tuple[int, int, int]:
    """
    Simplifies the quadratic surd ``(P + √D) / Q`` by dividing the parameters
    by their GCD ``g`` such that ``g | P, Q`` and ``g² | D``. Preseves signs.

    Args:
        P (int): Coefficient of the surd.
        Q (int): Denominator.
        D (int): Radicand.

    Returns:
        tuple[int, int, int]: ``(P', Q', D')`` such that ``(P' + √D') / Q'``
        is the simplified form of the original surd.
    """
    g = gcd(P, Q)
    g = gcd(g, _square_part_sqrt(D))
    return P // g, Q // g, D // (g * g)


def normalize_quadratic_surd(P: int, Q: int, D: int) -> tuple[int, int, int]:
    """
    Normalizes the quadratic surd ``(P + √D) / Q`` by multiplying the parameters
    by a common factor ``k`` such that the resulting denominator is positive and
    the radicand is non-negative. Preseves signs.

    Args:
        P (int): Coefficient of the surd.
        Q (int): Denominator.
        D (int): Radicand.

    Returns:
        tuple[int, int, int]: ``(P', Q', D')`` such that ``(P' + √D') / Q'`` is 
        the normalized form of the original surd.

    Note:
        No typechecking is performed on the input.  The function assumes that
        ``Q`` is non-zero and ``D`` is non-negative.
    """
    t = abs(D - P**2) # We most preserve the sign of the input.
    l = lcm(Q, t)
    k = l // t
    return P * k, Q * k, D * k**2


def quadratic_roots_from_coefficients(A: int, B: int, C: int) -> Optional[Tuple[Decimal, Decimal]]:
    """
    Returns the two real roots of the quadratic equation ``A·x² + B·x + C = 0``
    as :class:`~decimal.Decimal` values, or ``None`` if the discriminant is
    negative. x₀ is the larger root and x₁ is the smaller root, so that x₀ ≥ x₁.

    Args:
        A (int): Leading coefficient.
        B (int): Linear coefficient.
        C (int): Constant term.

    Returns:
        tuple[Decimal, Decimal] | None: ``(x₀, x₁)`` where ``x₀ ≥ x₁``,
        or ``None`` if ``B² - 4AC < 0``.
    """
    sign = get_sign(A)
    Av, Bv = Decimal(A * sign), Decimal(B * sign)
    discriminant = B**2 - 4 * A * C
    if discriminant < 0:
        return None  # No real roots
    sqrt_disc = Decimal(discriminant).sqrt()
    x0 = (-Bv + sqrt_disc) / (2 * Av)
    x1 = (-Bv - sqrt_disc) / (2 * Av)
    return x0, x1


def quadratic_surd_from_coefficients(A: int, B: int, C: int) -> Optional[Tuple[int, int, int]]:
    """
    Converts the quadratic equation ``A·x² + B·x + C = 0`` into the canonical
    surd form ``(P + √D) / Q`` by reducing coefficients by their GCD and
    normalising the sign so that ``Q > 0``.

    Args:
        A (int): Leading coefficient.
        B (int): Linear coefficient.
        C (int): Constant term.

    Returns:
        tuple[int, int, int] | None: ``(P, Q, D)`` such that the larger root
        equals ``(P + √D) / Q``, or ``None`` if ``B² - 4AC < 0``.
    """
    g = gcd(A, B, C)
    A //= g
    B //= g
    C //= g
    discriminant = B**2 - 4 * A * C

    sign = get_sign(A)

    P = -B * sign
    Q = 2 * A * sign
    D = discriminant
    if D < 0:
        return None  # No real roots

    return simplify_quadratic_surd(P, Q, D)



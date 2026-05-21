#     @staticmethod
#     def from_rational_to_scf(p: int, q: int) -> tuple[int, list[int]]:
#         scf = []
#         while abs(p) > 0 and q != 0:
#             # head, p, q = Method.breakdown(p, q)
#             (head, q), p = Method.euclid_breakdown(p, q)
#             scf.append(head)
#         return scf[0], scf[1:]

#     @staticmethod
#     def from_float_to_rational(r: Decimal) -> IntPair:
#         frac = Fraction(r)
#         return frac.numerator, frac.denominator

#     @staticmethod
#     def from_float_to_scf(r: Decimal) -> tuple[int, list[int]]:
#         return Convert.from_rational_to_scf(*Convert.from_float_to_rational(r))

#     @staticmethod
#     def from_float_to_digits(r: Decimal, num_digits: int = 50) -> tuple[int, list[int]]:
#         d = int(r * 10**num_digits)
#         digits = []
#         zero_flag = True
#         for _ in range(num_digits):
#             if zero_flag:
#                 if c:=d%10:
#                     zero_flag = False
#                     digits.append(c)
#             else:
#                 digits.append(d%10)
#             d //= 10
#         digits.append(d)
#         return digits[-1], digits[-2::-1]
    
#     @staticmethod
#     def from_float_to_armonic(r: Decimal) -> list[int]:
#         return Method.greedy_algorithm(*Convert.from_float_to_rational(r))
    
#     @staticmethod
#     def from_str_to_rational(s: FloatAsStr) -> IntPair:
#         return Method.simplify(int(s.replace(".", "")), 10**len(s.split(".")[1]))
    
#     @staticmethod
#     def from_str_to_scf(s: FloatAsStr) -> tuple[int, list[int]]:
#         return Convert.from_rational_to_scf(*Convert.from_str_to_rational(s))
    
#     @staticmethod
#     def from_str_to_digits(s: FloatAsStr) -> tuple[int, list[int]]:
#         h, b = s.split(".")
#         return int(h), list(map(int, b))
    
#     @staticmethod
#     def from_str_to_armonic(s: FloatAsStr) -> tuple[int, list[int]]:
#         print(Convert.from_str_to_rational(s))
#         return Method.greedy_algorithm(*Convert.from_str_to_rational(s))

from fractions import Fraction
from decimal import Decimal, InvalidOperation
from math import isqrt
from typing import Optional

from .core import euclidean_step, simplify
from .quadratic import normalize_quadratic_surd

type Rational = Fraction | tuple[int, int] | int

def _is_finite_decimal(s: str) -> bool:
    """
    Checks whether a string represents a finite decimal number.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is a valid finite decimal, False otherwise.
    """
    try:
        d = Decimal(s)
        return d.is_finite()
    except InvalidOperation:
        return False

def from_rational_to_scf(r: Rational) -> tuple[int, list[int]]:
    """
    Converts a rational number to its simple continued fraction (SCF) representation.

    Uses the Euclidean algorithm to compute the sequence of partial quotients.

    Args:
        r (Rational): The rational number to convert. Accepted types:
            - ``Fraction``: a ``fractions.Fraction`` instance.
            - ``tuple[int, int]``: a ``(numerator, denominator)`` pair.
            - ``int``: treated as the fraction ``r/1``.

    Returns:
        tuple[int, list[int]]: A pair ``(a0, [a1, a2, ...])`` where ``a0`` is
        the integer part and the list contains the remaining partial quotients.

    Raises:
        ValueError: If ``r`` is not one of the accepted types.
    """
    if isinstance(r, Fraction):
        p, q = r.numerator, r.denominator
    elif isinstance(r, tuple) and len(r) == 2:
        p, q = r
    elif isinstance(r, int):
        p, q = r, 1
    else:
        raise ValueError(f"Invalid input type: {type(r)}. Expected Fraction, tuple[int, int], or int.")
    
    if p == 0:
        return 0, []
    
    if q == 0:
        raise ValueError("Denominator cannot be zero.")

    scf = []
    while abs(p) > 0 and q != 0:
        h, q, p = euclidean_step(p, q)
        scf.append(h)
    
    return scf[0], scf[1:]


def from_float_to_rational(f: float, limit_denominator: Optional[int] = None) -> Rational:
    """
    Converts a floating-point number to a rational approximation.

    Args:
        f (float): The float to convert.
        limit_denominator (int, optional): If provided, the denominator of the
            resulting fraction is bounded by this value. Defaults to None
            (exact conversion via ``fractions.Fraction``).

    Returns:
        Rational: A ``(numerator, denominator)`` tuple representing the fraction.
    """
    if limit_denominator is None:
        r = Fraction(f)
    else:
        r = Fraction(f).limit_denominator(limit_denominator)
    return r.numerator, r.denominator

def from_float_to_scf(f: float, limit_denominator: Optional[int] = None) -> tuple[int, list[int]]:
    """
    Converts a floating-point number to its simple continued fraction (SCF) representation.

    Delegates to :func:`from_float_to_rational` followed by :func:`from_rational_to_scf`.

    Args:
        f (float): The float to convert.
        limit_denominator (int, optional): If provided, the rational approximation
            uses a denominator bounded by this value. Defaults to None.

    Returns:
        tuple[int, list[int]]: A pair ``(a0, [a1, a2, ...])`` representing the SCF.
    """
    return from_rational_to_scf(from_float_to_rational(f, limit_denominator))

def from_decimal_to_rational(d: str) -> Rational:
    """
    Converts a decimal string to an exact rational number in lowest terms.

    The string must represent a finite decimal (e.g. ``"3.14"`` or ``"42"``).  
    The resulting fraction is simplified via :func:`~catena.mathlib.core.simplify`.

    Args:
        d (str): A finite decimal string to convert.

    Returns:
        Rational: A ``(numerator, denominator)`` tuple in lowest terms.

    Raises:
        ValueError: If ``d`` is not a string or does not represent a finite decimal.
    """
    if not isinstance(d, str):
        raise ValueError(f"Input must be a string, got {type(d)}")

    if not _is_finite_decimal(d):
        raise ValueError(f"Input must be a finite decimal string, got '{d}'")

    if '.' in d:
        integer_part, fractional_part = d.split('.')
        numerator = int(integer_part + fractional_part)
        denominator = 10 ** len(fractional_part)
        numerator, denominator = simplify(numerator, denominator)

    else:
        numerator = int(d)
        denominator = 1
    return numerator, denominator


def from_quadratic_surd_to_scf(P: int, Q: int, D: int):
    if Q == 0:
        raise ValueError("Q cannot be zero")
    if D < 0:
        raise ValueError("D must be non-negative")
    
    P, Q, D = normalize_quadratic_surd(P, Q, D)

    if (s:=isqrt(D))**2 == D:
        raise ValueError("D must not be a perfect square")

    m, d = P, Q
    a = (m + s) // d
    if d < 0 and (a * d - m) <= s:# This is a logic step to avoid the 
        a -= 1                    # need to use floating point approximation for s.
    
    visited = dict()
    scf: list[int] = []
    while (m, d) not in visited:
        visited[(m, d)] = len(scf)
        scf.append(a)

        m = a * d - m
        d = (D - m * m) // d
        a = (m + s) // d
        if d < 0 and (a * d - m) <= s:
            a -= 1

    return scf[0], tuple(scf[1:visited[(m, d)]]), tuple(scf[visited[(m, d)]:])


def from_quadratic_surd_to_conjugate_scf(P: int, Q: int, D: int):
    return from_quadratic_surd_to_scf(-P, -Q, D)

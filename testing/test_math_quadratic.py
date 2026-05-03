"""Tests for catena.mathlib.quadratic and the quadratic-surd conversion helpers
in catena.mathlib.convert.

Sections
--------
  1. _square_part_sqrt        — largest s with s² | D
  2. simplify_quadratic_surd  — (P + √D)/Q → reduce by common factor
  3. normalize_quadratic_surd — scale so that Q | (D − P²)
  4. quadratic_roots_from_coefficients  — (A,B,C) → Decimal pair or None
  5. quadratic_surd_from_coefficients   — (A,B,C) → (P,Q,D) canonical form
  6. from_quadratic_surd_to_scf         — (P,Q,D) → (int_part, pre_period, period)
  7. from_quadratic_surd_to_conjugate_scf

Reference surds used throughout
---------------------------------
  √2  : (P=0, Q=1, D=2)   →  x²-2=0         →  A=1,B=0,C=-2
  φ   : (P=1, Q=2, D=5)   →  x²-x-1=0       →  A=1,B=-1,C=-1
  √3  : (P=0, Q=1, D=3)   →  x²-3=0         →  A=1,B=0,C=-3
  √5  : (P=0, Q=1, D=5)   →  x²-5=0         →  A=1,B=0,C=-5
  1/√2: (P=0, Q=2, D=2)   →  2x²-1=0        →  A=2,B=0,C=-1
"""

import pytest
from math import gcd, sqrt, isclose, isqrt
from decimal import Decimal

import catena.mathlib.quadratic as quadratic
import catena.mathlib.convert as convert
from catena.catena import PeriodicSimpleContinuedFraction


# ===========================================================================
# 1.  _square_part_sqrt
# ===========================================================================

def test_square_part_sqrt_of_1():
    assert quadratic._square_part_sqrt(1) == 1


def test_square_part_sqrt_perfect_square_4():
    assert quadratic._square_part_sqrt(4) == 2


def test_square_part_sqrt_perfect_square_9():
    assert quadratic._square_part_sqrt(9) == 3


def test_square_part_sqrt_perfect_square_36():
    # 36 = 4 · 9  →  s = 2 · 3 = 6
    assert quadratic._square_part_sqrt(36) == 6


def test_square_part_sqrt_4_times_non_square():
    # 8 = 4 · 2  →  s = 2
    assert quadratic._square_part_sqrt(8) == 2


def test_square_part_sqrt_mixed():
    # 12 = 4 · 3  →  s = 2
    assert quadratic._square_part_sqrt(12) == 2


def test_square_part_sqrt_prime_is_one():
    # 5 is prime: only odd exponents
    assert quadratic._square_part_sqrt(5) == 1


def test_square_part_sqrt_20():
    # 20 = 4 · 5  →  s = 2
    assert quadratic._square_part_sqrt(20) == 2


def test_square_part_sqrt_100():
    # 100 = 4 · 25  →  s = 2 · 5 = 10
    assert quadratic._square_part_sqrt(100) == 10


def test_square_part_sqrt_45():
    # 45 = 9 · 5  →  s = 3
    assert quadratic._square_part_sqrt(45) == 3


# ===========================================================================
# 2.  simplify_quadratic_surd
# ===========================================================================

def test_simplify_already_reduced():
    # (1 + √2) / 1  — nothing to factor out
    assert quadratic.simplify_quadratic_surd(1, 1, 2) == (1, 1, 2)


def test_simplify_common_factor_in_P_Q():
    # (0 + √8) / 2  =  √2  →  (0, 1, 2)
    # sq(8)=2, gcd(0,2)=2, g=gcd(2,2)=2
    assert quadratic.simplify_quadratic_surd(0, 2, 8) == (0, 1, 2)


def test_simplify_common_factor_all():
    # (4 + √12) / 6  =  (2 + √3) / 3
    # sq(12)=2, gcd(4,6)=2, g=gcd(2,2)=2
    assert quadratic.simplify_quadratic_surd(4, 6, 12) == (2, 3, 3)


def test_simplify_common_factor_P_Q_and_sqrt():
    # (6 + √12) / 4  =  (3 + √3) / 2
    # sq(12)=2, gcd(6,4)=2, g=gcd(2,2)=2
    assert quadratic.simplify_quadratic_surd(6, 4, 12) == (3, 2, 3)


def test_simplify_no_square_factor_in_D():
    # D=3 is square-free: sq(3)=1. gcd(8,10)=2, gcd(2,1)=1 → no reduction
    assert quadratic.simplify_quadratic_surd(8, 10, 3) == (8, 10, 3)


def test_simplify_preserves_negative_signs():
    # (-4 + √12) / -6  →  (-2 + √3) / -3
    P, Q, D = quadratic.simplify_quadratic_surd(-4, -6, 12)
    assert (P, Q, D) == (-2, -3, 3)


def test_simplify_zero_P():
    # (0 + √20) / 4  =  √5 / 2  =  (0 + √5) / 2
    # sq(20)=2, gcd(0,4)=4, g=gcd(4,2)=2  →  (0, 2, 5)
    assert quadratic.simplify_quadratic_surd(0, 4, 20) == (0, 2, 5)


def test_simplify_value_preserved():
    """Value (P + √D)/Q is unchanged after simplification."""
    P, Q, D = 4, 6, 12
    P2, Q2, D2 = quadratic.simplify_quadratic_surd(P, Q, D)
    original = (P + sqrt(D)) / Q
    simplified = (P2 + sqrt(D2)) / Q2
    assert isclose(original, simplified, rel_tol=1e-12)


# ===========================================================================
# 3.  normalize_quadratic_surd
# ===========================================================================

def test_normalize_already_normalized():
    # (D - P²) / Q must be an integer after normalization.
    # (1 + √3) / 2 : t=|3-1|=2, lcm(2,2)=2, k=1 → no change
    assert quadratic.normalize_quadratic_surd(1, 2, 3) == (1, 2, 3)


def test_normalize_requires_scaling():
    # (1 + √3) / 3 : t=2, lcm(3,2)=6, k=3 → (3, 9, 27)
    P, Q, D = quadratic.normalize_quadratic_surd(1, 3, 3)
    assert (P, Q, D) == (3, 9, 27)


def test_normalize_sqrt5_half():
    # (0 + √5) / 2 : t=5, lcm(2,5)=10, k=2 → (0, 4, 20)
    assert quadratic.normalize_quadratic_surd(0, 2, 5) == (0, 4, 20)


def test_normalize_value_preserved():
    """Value (P + √D)/Q equals (P' + √D')/Q' after normalization."""
    cases = [(1, 3, 3), (0, 2, 5), (2, 3, 7), (1, 4, 5)]
    for P, Q, D in cases:
        P2, Q2, D2 = quadratic.normalize_quadratic_surd(P, Q, D)
        assert isclose((P + sqrt(D)) / Q, (P2 + sqrt(D2)) / Q2, rel_tol=1e-12)


def test_normalize_divisibility_condition():
    """After normalization, (D' - P'²) is divisible by Q'."""
    cases = [(1, 3, 3), (0, 2, 5), (2, 5, 11), (3, 7, 13)]
    for P, Q, D in cases:
        P2, Q2, D2 = quadratic.normalize_quadratic_surd(P, Q, D)
        assert (D2 - P2 * P2) % Q2 == 0, f"Divisibility failed for ({P},{Q},{D})"


def test_normalize_integer_start_unchanged():
    # (2 + √5) / 1 : t=|5-4|=1, lcm(1,1)=1, k=1 → (2, 1, 5)
    assert quadratic.normalize_quadratic_surd(2, 1, 5) == (2, 1, 5)


# ===========================================================================
# 4.  quadratic_roots_from_coefficients
# ===========================================================================

def test_roots_sqrt2():
    # x² - 2 = 0  →  ±√2
    x0, x1 = quadratic.quadratic_roots_from_coefficients(1, 0, -2)
    assert isclose(float(x0), sqrt(2), rel_tol=1e-12)
    assert isclose(float(x1), -sqrt(2), rel_tol=1e-12)


def test_roots_phi():
    # x² - x - 1 = 0  →  (1±√5)/2
    x0, x1 = quadratic.quadratic_roots_from_coefficients(1, -1, -1)
    assert isclose(float(x0), (1 + sqrt(5)) / 2, rel_tol=1e-12)
    assert isclose(float(x1), (1 - sqrt(5)) / 2, rel_tol=1e-12)


def test_roots_larger_is_first():
    """x0 >= x1 always."""
    cases = [(1, 0, -2), (1, -1, -1), (2, 0, -1), (1, 6, 8)]
    for A, B, C in cases:
        pair = quadratic.quadratic_roots_from_coefficients(A, B, C)
        if pair is not None:
            x0, x1 = pair
            assert x0 >= x1


def test_roots_negative_discriminant_returns_none():
    # x² + 1 = 0  →  no real roots
    assert quadratic.quadratic_roots_from_coefficients(1, 0, 1) is None


def test_roots_zero_discriminant():
    # x² + 6x + 9 = 0  →  x = -3 (double root)
    x0, x1 = quadratic.quadratic_roots_from_coefficients(1, 6, 9)
    assert isclose(float(x0), -3.0, rel_tol=1e-12)
    assert isclose(float(x1), -3.0, rel_tol=1e-12)


def test_roots_negative_leading_coeff():
    # -x² + 2 = 0  is the same equation as x² - 2 = 0
    x0, x1 = quadratic.quadratic_roots_from_coefficients(-1, 0, 2)
    assert isclose(float(x0), sqrt(2), rel_tol=1e-12)
    assert isclose(float(x1), -sqrt(2), rel_tol=1e-12)


def test_roots_vieta_sum():
    """Sum of roots = -B/A (Vieta's formula)."""
    cases = [(1, -1, -1), (2, -4, 1), (3, 6, 2)]
    for A, B, C in cases:
        x0, x1 = quadratic.quadratic_roots_from_coefficients(A, B, C)
        assert isclose(float(x0 + x1), -B / A, rel_tol=1e-10)


def test_roots_vieta_product():
    """Product of roots = C/A (Vieta's formula)."""
    cases = [(1, -1, -1), (2, -4, 1), (3, 6, 2)]
    for A, B, C in cases:
        x0, x1 = quadratic.quadratic_roots_from_coefficients(A, B, C)
        assert isclose(float(x0 * x1), C / A, rel_tol=1e-10)


# ===========================================================================
# 5.  quadratic_surd_from_coefficients
# ===========================================================================

def test_surd_from_coefficients_sqrt2():
    # x² - 2 = 0  →  (0 + √2) / 1
    assert quadratic.quadratic_surd_from_coefficients(1, 0, -2) == (0, 1, 2)


def test_surd_from_coefficients_phi():
    # x² - x - 1 = 0  →  (1 + √5) / 2
    assert quadratic.quadratic_surd_from_coefficients(1, -1, -1) == (1, 2, 5)


def test_surd_from_coefficients_sqrt3():
    # x² - 3 = 0  →  (0 + √3) / 1
    assert quadratic.quadratic_surd_from_coefficients(1, 0, -3) == (0, 1, 3)


def test_surd_from_coefficients_sqrt5():
    # x² - 5 = 0  →  (0 + √5) / 1
    assert quadratic.quadratic_surd_from_coefficients(1, 0, -5) == (0, 1, 5)


def test_surd_from_coefficients_inv_sqrt2():
    # 2x² - 1 = 0  →  (0 + √2) / 2
    assert quadratic.quadratic_surd_from_coefficients(2, 0, -1) == (0, 2, 2)


def test_surd_from_coefficients_no_real_roots():
    # x² + 1 = 0  →  None
    assert quadratic.quadratic_surd_from_coefficients(1, 0, 1) is None


def test_surd_from_coefficients_Q_positive():
    """Returned Q is always positive."""
    cases = [(1, 0, -2), (1, -1, -1), (2, 0, -1), (-1, 0, 2)]
    for A, B, C in cases:
        result = quadratic.quadratic_surd_from_coefficients(A, B, C)
        if result is not None:
            _, Q, _ = result
            assert Q > 0


def test_surd_from_coefficients_value_is_larger_root():
    """(P + √D)/Q equals the larger root of Ax²+Bx+C=0."""
    cases = [(1, 0, -2), (1, -1, -1), (2, 0, -1), (1, 6, 8)]
    for A, B, C in cases:
        result = quadratic.quadratic_surd_from_coefficients(A, B, C)
        if result is None:
            continue
        P, Q, D = result
        surd_value = (P + sqrt(D)) / Q
        roots = quadratic.quadratic_roots_from_coefficients(A, B, C)
        assert isclose(surd_value, float(roots[0]), rel_tol=1e-10)


def test_surd_from_coefficients_gcd_reduction():
    # 2x² - 4 = 0  is equivalent to x² - 2 = 0  →  same surd (0, 1, 2)
    assert quadratic.quadratic_surd_from_coefficients(2, 0, -4) == (0, 1, 2)


# ===========================================================================
# 6.  from_quadratic_surd_to_scf
# ===========================================================================

def test_from_surd_to_scf_sqrt2():
    # (0 + √2)/1 = √2 = [1; (2)]
    int_part, pre, per = convert.from_quadratic_surd_to_scf(0, 1, 2)
    assert int_part == 1
    assert pre == ()
    assert per == (2,)


def test_from_surd_to_scf_phi():
    # (1 + √5)/2 = φ = [1; (1)]
    int_part, pre, per = convert.from_quadratic_surd_to_scf(1, 2, 5)
    assert int_part == 1
    assert pre == ()
    assert per == (1,)


def test_from_surd_to_scf_sqrt3():
    # (0 + √3)/1 = √3 = [1; (1, 2)]
    int_part, pre, per = convert.from_quadratic_surd_to_scf(0, 1, 3)
    assert int_part == 1
    assert pre == ()
    assert per == (1, 2)


def test_from_surd_to_scf_sqrt5():
    # (0 + √5)/1 = √5 = [2; (4)]
    int_part, pre, per = convert.from_quadratic_surd_to_scf(0, 1, 5)
    assert int_part == 2
    assert pre == ()
    assert per == (4,)


def test_from_surd_to_scf_inv_sqrt2():
    # (0 + √2)/2 = 1/√2 = [0; 1, (2)]
    int_part, pre, per = convert.from_quadratic_surd_to_scf(0, 2, 2)
    assert int_part == 0
    assert pre == (1,)
    assert per == (2,)


def test_from_surd_to_scf_roundtrip_via_pscf():
    """SCF constructed from surd converges to the expected value."""
    cases = [
        ((0, 1, 2), sqrt(2)),
        ((1, 2, 5), (1 + sqrt(5)) / 2),
        ((0, 1, 3), sqrt(3)),
        ((0, 1, 5), sqrt(5)),
        ((0, 2, 2), 1 / sqrt(2)),
    ]
    for (P, Q, D), expected in cases:
        int_part, pre, per = convert.from_quadratic_surd_to_scf(P, Q, D)
        pscf = PeriodicSimpleContinuedFraction(
            period=list(per), pre_period=list(pre), integer_part=int_part
        )
        p, q = pscf.convergent(30)
        assert isclose(p / q, expected, rel_tol=1e-9), \
            f"Failed for ({P},{Q},{D}): got {p/q}, expected {expected}"


def test_from_surd_to_scf_zero_Q_raises():
    with pytest.raises(ValueError):
        convert.from_quadratic_surd_to_scf(1, 0, 2)


def test_from_surd_to_scf_negative_D_raises():
    with pytest.raises(ValueError):
        convert.from_quadratic_surd_to_scf(0, 1, -1)


def test_from_surd_to_scf_perfect_square_D_raises():
    with pytest.raises(ValueError):
        convert.from_quadratic_surd_to_scf(0, 1, 4)


# ===========================================================================
# 7.  from_quadratic_surd_to_conjugate_scf
# ===========================================================================

def test_conjugate_scf_sqrt2_converges_to_negative_sqrt2():
    int_part, pre, per = convert.from_quadratic_surd_to_conjugate_scf(0, 1, 2)
    pscf = PeriodicSimpleContinuedFraction(
        period=list(per), pre_period=list(pre), integer_part=int_part
    )
    p, q = pscf.convergent(30)
    assert isclose(p / q, -sqrt(2), rel_tol=1e-9)


def test_conjugate_scf_phi_converges_to_negative_reciprocal():
    # Conjugate of φ is (1-√5)/2 ≈ -0.618
    int_part, pre, per = convert.from_quadratic_surd_to_conjugate_scf(1, 2, 5)
    pscf = PeriodicSimpleContinuedFraction(
        period=list(per), pre_period=list(pre), integer_part=int_part
    )
    p, q = pscf.convergent(30)
    assert isclose(p / q, (1 - sqrt(5)) / 2, rel_tol=1e-9)


def test_conjugate_scf_different_from_principal():
    """Principal and conjugate SCFs represent different values."""
    P, Q, D = 0, 1, 2
    int1, pre1, per1 = convert.from_quadratic_surd_to_scf(P, Q, D)
    int2, pre2, per2 = convert.from_quadratic_surd_to_conjugate_scf(P, Q, D)
    # At least one attribute must differ
    assert (int1, pre1, per1) != (int2, pre2, per2)


def test_conjugate_scf_same_quadratic_coefficients():
    """Both SCFs are roots of the same quadratic."""
    P, Q, D = 0, 1, 2
    int1, pre1, per1 = convert.from_quadratic_surd_to_scf(P, Q, D)
    int2, pre2, per2 = convert.from_quadratic_surd_to_conjugate_scf(P, Q, D)
    pscf1 = PeriodicSimpleContinuedFraction(
        period=list(per1), pre_period=list(pre1), integer_part=int1
    )
    pscf2 = PeriodicSimpleContinuedFraction(
        period=list(per2), pre_period=list(pre2), integer_part=int2
    )
    assert pscf1.quadratic_coefficients() == pscf2.quadratic_coefficients()

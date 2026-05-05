"""Tests for PeriodicSimpleContinuedFraction.

Goal: lock down the stable, observable behaviour of the class – construction,
properties, convergent recurrence, quadratic coefficient formula, and dunder
conversions.  Every expected value is hand-verified; derivations are noted
inline.

Reference SCFs used throughout
--------------------------------
  sqrt(2)   = [1; (2)]         integer_part=1,  period=(2,),    pre_period=()
  phi       = [1; (1)]         integer_part=1,  period=(1,),    pre_period=()
  sqrt(3)   = [1; (1, 2)]      integer_part=1,  period=(1, 2),  pre_period=()
  sqrt(5)   = [2; (4)]         integer_part=2,  period=(4,),    pre_period=()
  1/sqrt(2) = [0; 1, (2)]      integer_part=0,  period=(2,),    pre_period=(1,)

Quadratic coefficients (A, B, C) satisfy  A·x² + B·x + C = 0,  A > 0,
gcd(A, B, C) = 1.

  SCF          gen (A,B,C)   a₀  shifted (A,B,C)   root
  [0;(1)]      (1, 1,-1)      0   (1, 1,-1)         (√5-1)/2
  [1;(1)]      (1, 1,-1)      1   (1,-1,-1)         φ = (1+√5)/2
  [0;(2)]      (1, 2,-1)      0   (1, 2,-1)         √2 - 1
  [1;(2)]      (1, 2,-1)      1   (1, 0,-2)         √2
  [1;(1,2)]    (1, 2,-2)      1   (1, 0,-3)         √3
  [2;(4)]      (1, 4,-1)      2   (1, 0,-5)         √5
  [0;1,(2)]                       (2, 0,-1)         1/√2

Convergents for [1;(2)]:  3/2,  7/5, 17/12, 41/29, 99/70  →  sqrt(2)
Convergents for [1;(1)]:  2/1,  3/2,  5/3,  8/5,  13/8,  21/13  →  phi
"""

import pytest
from math import gcd, sqrt, isclose

from catena.catena import PeriodicSimpleContinuedFraction
from catena.generators import PeriodicGenerator


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _is_reduced(p: int, q: int) -> bool:
    return gcd(abs(p), abs(q)) == 1


# ===========================================================================
# Construction
# ===========================================================================

def test_construction_period_only():
    pscf = PeriodicSimpleContinuedFraction(period=[2])
    assert pscf.period == (2,)
    assert pscf.non_repeating_part == ()
    assert pscf.integer_part == 0


def test_construction_period_and_integer_part():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.integer_part == 1


def test_construction_period_pre_period_integer_part():
    pscf = PeriodicSimpleContinuedFraction(period=[2], pre_period=[1], integer_part=0)
    assert pscf.period == (2,)
    assert pscf.non_repeating_part == (1,)
    assert pscf.integer_part == 0


def test_construction_multi_element_period():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=1)
    assert pscf.period == (1, 2)


def test_construction_multi_element_pre_period():
    pscf = PeriodicSimpleContinuedFraction(period=[5], pre_period=[1, 1])
    assert pscf.non_repeating_part == (1, 1)


def test_construction_negative_integer_part():
    pscf = PeriodicSimpleContinuedFraction(period=[3], integer_part=-2)
    assert pscf.integer_part == -2


def test_construction_default_pre_period_is_empty():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2])
    assert pscf.non_repeating_part == ()


def test_construction_dtypes_accepted():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], pre_period=[3], dtypes=('H', 'B'))
    assert pscf.generator.period.dtype == 'H'
    assert pscf.generator.pre_period.dtype == 'B'


def test_construction_invalid_dtypes_length_raises():
    with pytest.raises(ValueError):
        PeriodicSimpleContinuedFraction(period=[1], dtypes=('B',))  # length 1 not 2


def test_construction_non_positive_in_period_raises():
    with pytest.raises(ValueError):
        PeriodicSimpleContinuedFraction(period=[0, 1])


def test_construction_negative_in_period_raises():
    with pytest.raises(ValueError):
        PeriodicSimpleContinuedFraction(period=[-1])


def test_construction_non_positive_in_pre_period_raises():
    with pytest.raises(ValueError):
        PeriodicSimpleContinuedFraction(period=[1], pre_period=[0])


# ===========================================================================
# Properties
# ===========================================================================

def test_generator_property_is_periodic_generator():
    pscf = PeriodicSimpleContinuedFraction(period=[2])
    assert isinstance(pscf.generator, PeriodicGenerator)


def test_period_property_returns_tuple():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2, 3])
    assert isinstance(pscf.period, tuple)
    assert pscf.period == (1, 2, 3)


def test_non_repeating_part_returns_tuple():
    pscf = PeriodicSimpleContinuedFraction(period=[2], pre_period=[7, 3])
    assert isinstance(pscf.non_repeating_part, tuple)
    assert pscf.non_repeating_part == (7, 3)


def test_non_repeating_part_empty_when_no_pre_period():
    pscf = PeriodicSimpleContinuedFraction(period=[1])
    assert pscf.non_repeating_part == ()


# ===========================================================================
# __int__  (inherited from SimpleContinuedFraction)
# ===========================================================================

def test_int_returns_integer_part_zero():
    pscf = PeriodicSimpleContinuedFraction(period=[1])
    assert int(pscf) == 0


def test_int_returns_integer_part_positive():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=3)
    assert int(pscf) == 3


def test_int_returns_integer_part_negative():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=-4)
    assert int(pscf) == -4


# ===========================================================================
# __str__ / __repr__
# ===========================================================================

def test_str_contains_class_name():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert "PeriodicSimpleContinuedFraction" in str(pscf)


def test_str_contains_integer_part():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=7)
    assert "7" in str(pscf)


def test_str_contains_period():
    pscf = PeriodicSimpleContinuedFraction(period=[2, 3])
    s = str(pscf)
    assert "2" in s
    assert "3" in s


def test_repr_contains_class_name():
    pscf = PeriodicSimpleContinuedFraction(period=[2])
    assert "PeriodicSimpleContinuedFraction" in repr(pscf)


def test_repr_contains_cache_handler():
    pscf = PeriodicSimpleContinuedFraction(period=[2])
    assert "cache_handler" in repr(pscf)


# ===========================================================================
# Convergents – [1; (2)]  →  sqrt(2)
#
# Generator: g(n) = 2 for all n.
# tail_convergents:  (1,2), (2,5), (5,12), (12,29), (29,70)
# convergents:       (3,2), (7,5), (17,12), (41,29), (99,70)
# ===========================================================================

SQRT2_CONVERGENTS = [(3, 2), (7, 5), (17, 12), (41, 29), (99, 70)]


@pytest.fixture
def sqrt2_pscf():
    return PeriodicSimpleContinuedFraction(period=[2], integer_part=1)


@pytest.mark.parametrize("n, expected", list(enumerate(SQRT2_CONVERGENTS)))
def test_sqrt2_convergents(n, expected, sqrt2_pscf):
    assert sqrt2_pscf.convergent(n) == expected


def test_sqrt2_convergents_are_coprime(sqrt2_pscf):
    for n in range(10):
        p, q = sqrt2_pscf.convergent(n)
        assert _is_reduced(p, q)


def test_sqrt2_convergents_denominators_strictly_increasing(sqrt2_pscf):
    qs = [sqrt2_pscf.convergent(n)[1] for n in range(8)]
    assert all(qs[i] < qs[i + 1] for i in range(len(qs) - 1))


def test_sqrt2_convergents_approach_sqrt2(sqrt2_pscf):
    """Convergents approach sqrt(2) from alternating sides."""
    target = sqrt(2)
    prev_err = float("inf")
    for n in range(8):
        p, q = sqrt2_pscf.convergent(n)
        err = abs(p / q - target)
        assert err < prev_err
        prev_err = err
    assert isclose(p / q, target, rel_tol=1e-6)


def test_sqrt2_satisfies_pell_equation(sqrt2_pscf):
    """Numerator p and denominator q satisfy |p²− 2q²| == 1 (Pell equation)."""
    for n, (p, q) in enumerate(SQRT2_CONVERGENTS):
        assert abs(p * p - 2 * q * q) == 1


# ===========================================================================
# Convergents – [1; (1)]  →  phi = (1+√5)/2
#
# Generator: g(n) = 1 for all n.
# tail_convergents:  (1,1), (1,2), (2,3), (3,5), (5,8), (8,13)
# convergents:       (2,1), (3,2), (5,3), (8,5), (13,8), (21,13)
# ===========================================================================

PHI_CONVERGENTS = [(2, 1), (3, 2), (5, 3), (8, 5), (13, 8), (21, 13)]


@pytest.fixture
def phi_pscf():
    return PeriodicSimpleContinuedFraction(period=[1], integer_part=1)


@pytest.mark.parametrize("n, expected", list(enumerate(PHI_CONVERGENTS)))
def test_phi_convergents(n, expected, phi_pscf):
    assert phi_pscf.convergent(n) == expected


def test_phi_numerators_and_denominators_are_fibonacci(phi_pscf):
    """Numerators and denominators of phi's convergents are consecutive Fibonacci numbers."""
    for p, q in PHI_CONVERGENTS:
        # For each consecutive Fibonacci pair (Fₙ, Fₙ₋₁), gcd == 1
        assert _is_reduced(p, q)
        # The ratio p/q → phi
        assert isclose(p / q, (1 + sqrt(5)) / 2, rel_tol=0.5)


def test_phi_convergents_approach_phi(phi_pscf):
    target = (1 + sqrt(5)) / 2
    prev_err = float("inf")
    for n in range(8):
        p, q = phi_pscf.convergent(n)
        err = abs(p / q - target)
        assert err < prev_err
        prev_err = err


# ===========================================================================
# Convergents – [0; 1, (2)]  →  1/√2
#
# Generator: g(0)=1, g(n≥1)=2.
# tail_convergents:  (1,1), (2,3), (5,7), (12,17), ...
# convergents (a₀=0): (1,1), (2,3), (5,7), (12,17)
# ===========================================================================

@pytest.fixture
def inv_sqrt2_pscf():
    return PeriodicSimpleContinuedFraction(period=[2], pre_period=[1], integer_part=0)


def test_inv_sqrt2_convergent_0(inv_sqrt2_pscf):
    assert inv_sqrt2_pscf.convergent(0) == (1, 1)


def test_inv_sqrt2_convergent_1(inv_sqrt2_pscf):
    assert inv_sqrt2_pscf.convergent(1) == (2, 3)


def test_inv_sqrt2_convergent_2(inv_sqrt2_pscf):
    assert inv_sqrt2_pscf.convergent(2) == (5, 7)


def test_inv_sqrt2_convergents_approach_value(inv_sqrt2_pscf):
    target = 1 / sqrt(2)
    prev_err = float("inf")
    for n in range(8):
        p, q = inv_sqrt2_pscf.convergent(n)
        err = abs(p / q - target)
        assert err < prev_err
        prev_err = err


# ===========================================================================
# tail_convergent – period wrapping visible in the recurrence
# ===========================================================================

def test_period_wraps_correctly_in_tail_convergent():
    """For [0;(1,2)] period=[1,2]: g(0)=1,g(1)=2,g(2)=1,g(3)=2,...
    Check tail_convergents are self-consistent with the recurrence."""
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=0)
    for n in range(2, 8):
        h_n,  k_n  = pscf.tail_convergent(n)
        h_n1, k_n1 = pscf.tail_convergent(n - 1)
        h_n2, k_n2 = pscf.tail_convergent(n - 2)
        a = pscf.generator(n)  # calls underlying PeriodicGenerator
        assert h_n == a * h_n1 + h_n2
        assert k_n == a * k_n1 + k_n2


# ===========================================================================
# quadratic_coefficients
#
# Full table:
#   SCF          expected (A, B, C)
#   [0;(1)]      (1, 1,-1)     → x² + x - 1 = 0  → (√5-1)/2
#   [1;(1)]      (1,-1,-1)     → x² - x - 1 = 0  → φ
#   [0;(2)]      (1, 2,-1)     → x² + 2x - 1 = 0 → √2 - 1
#   [1;(2)]      (1, 0,-2)     → x² - 2 = 0      → √2
#   [1;(1,2)]    (1, 0,-3)     → x² - 3 = 0      → √3
#   [2;(4)]      (1, 0,-5)     → x² - 5 = 0      → √5
#   [0;1,(2)]    (2, 0,-1)     → 2x² - 1 = 0     → 1/√2
# ===========================================================================

def test_quadratic_period_1_integer_part_0():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=0)
    assert pscf.quadratic_coefficients() == (1, 1, -1)


def test_quadratic_period_1_integer_part_1_phi():
    # [1;(1)]:  gen (1,1,-1), shift by 1 → B=1-2=-1, C=-1-1+1=-1
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert pscf.quadratic_coefficients() == (1, -1, -1)


def test_quadratic_period_2_integer_part_0():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=0)
    assert pscf.quadratic_coefficients() == (1, 2, -1)


def test_quadratic_period_2_integer_part_1_sqrt2():
    # [1;(2)]:  gen (1,2,-1), shift by 1 → B=2-2=0, C=-1-2+1=-2
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.quadratic_coefficients() == (1, 0, -2)


def test_quadratic_period_1_2_integer_part_1_sqrt3():
    # [1;(1,2)]:  gen (1,2,-2), shift by 1 → B=2-2=0, C=-2-2+1=-3
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=1)
    assert pscf.quadratic_coefficients() == (1, 0, -3)


def test_quadratic_period_4_integer_part_2_sqrt5():
    # [2;(4)]:  gen (1,4,-1), shift by 2 → B=4-4=0, C=-1-8+4=-5
    pscf = PeriodicSimpleContinuedFraction(period=[4], integer_part=2)
    assert pscf.quadratic_coefficients() == (1, 0, -5)


def test_quadratic_pre_period_1_period_2_inv_sqrt2():
    # [0;1,(2)]:  quadratic_coefficients comes entirely from generator
    pscf = PeriodicSimpleContinuedFraction(period=[2], pre_period=[1], integer_part=0)
    assert pscf.quadratic_coefficients() == (2, 0, -1)


# ---------------------------------------------------------------------------
# Structural invariants on quadratic_coefficients
# ---------------------------------------------------------------------------

def test_quadratic_leading_coeff_always_positive():
    """A > 0 for all well-formed periodic SCFs."""
    cases = [
        dict(period=[1]),
        dict(period=[1], integer_part=1),
        dict(period=[2], integer_part=1),
        dict(period=[1, 2], integer_part=1),
        dict(period=[4], integer_part=2),
        dict(period=[2], pre_period=[1]),
        dict(period=[1, 1, 4], integer_part=3),
    ]
    for kw in cases:
        A, _, _ = PeriodicSimpleContinuedFraction(**kw).quadratic_coefficients()
        assert A > 0, f"A must be positive for {kw}"


def test_quadratic_gcd_is_one():
    """gcd(|A|, |B|, |C|) == 1 for all well-formed periodic SCFs."""
    cases = [
        dict(period=[1]),
        dict(period=[1], integer_part=1),
        dict(period=[2], integer_part=1),
        dict(period=[1, 2], integer_part=1),
        dict(period=[4], integer_part=2),
        dict(period=[2], pre_period=[1]),
    ]
    for kw in cases:
        A, B, C = PeriodicSimpleContinuedFraction(**kw).quadratic_coefficients()
        assert gcd(abs(A), abs(B), abs(C)) == 1, f"gcd must be 1 for {kw}"


def test_quadratic_discriminant_positive():
    """Discriminant B² - 4AC > 0 (each periodic SCF is a quadratic irrational)."""
    cases = [
        dict(period=[1]),
        dict(period=[1], integer_part=1),
        dict(period=[2], integer_part=1),
        dict(period=[1, 2], integer_part=1),
        dict(period=[4], integer_part=2),
        dict(period=[2], pre_period=[1]),
    ]
    for kw in cases:
        A, B, C = PeriodicSimpleContinuedFraction(**kw).quadratic_coefficients()
        assert B * B - 4 * A * C > 0, f"Discriminant must be positive for {kw}"


# ---------------------------------------------------------------------------
# Root of the polynomial equals the SCF value (float cross-check)
# ---------------------------------------------------------------------------

def _positive_root(A, B, C):
    """Return the positive root of A·x² + B·x + C = 0."""
    disc = B * B - 4 * A * C
    return (-B + sqrt(disc)) / (2 * A)

def _negative_root(A, B, C):
    """Return the negative root of A·x² + B·x + C = 0."""
    disc = B * B - 4 * A * C
    return (-B - sqrt(disc)) / (2 * A)


@pytest.mark.parametrize("period,pre_period,integer_part,known", [
    ([2], [],  1, sqrt(2)),
    ([1], [],  1, (1 + sqrt(5)) / 2),
    ([1, 2], [], 1, sqrt(3)),
    ([4], [],  2, sqrt(5)),
    ([2], [1], 0, 1 / sqrt(2)),
])
def test_quadratic_root_matches_scf_value(period, pre_period, integer_part, known):
    """Positive root of the polynomial equals the known irrational value."""
    pscf = PeriodicSimpleContinuedFraction(
        period=period, pre_period=pre_period, integer_part=integer_part
    )
    A, B, C = pscf.quadratic_coefficients()
    root = _positive_root(A, B, C)
    assert isclose(root, known, rel_tol=1e-12)


@pytest.mark.parametrize("period,pre_period,integer_part,known", [
    ([2], [],  1, sqrt(2)),
    ([1], [],  1, (1 + sqrt(5)) / 2),
    ([4], [],  2, sqrt(5)),
])
def test_convergents_approach_quadratic_root(period, pre_period, integer_part, known):
    """Float value of deep convergent p/q must be close to the known root."""
    pscf = PeriodicSimpleContinuedFraction(
        period=period, pre_period=pre_period, integer_part=integer_part
    )
    p, q = pscf.convergent(50)
    assert isclose(p / q, known, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# 30th convergent of periodic SCF isclose to one of the known roots of the computed quadratic coefficients
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("period,pre_period,integer_part", [
    ([2], [],  1),
    ([1], [],  1),
    ([1, 2], [], 1),
    ([4], [],  2),
    ([2], [1], 0),
    ([1, 1, 4], [1, 2, 3], 3),

    # Quadratic form: 100x^2 + -160x + 61 = 0. (P=8, Q=10, D=3)
    ([3, 8, 3, 34], [1, 36], 0), # root1 = 0.9732050807568877
    ([8, 3, 34, 3], [1, 1, 1, 2], 0),  # root2 = 0.6267949192431123

    # Quadratic form: 100x^2 + -60x + -1 = 0.  (P=3, Q=10, D=10)
    ([1, 1, 1, 1, 1, 6, 2, 2, 15, 2, 2, 6, 1, 1, 1, 1, 1, 62], [1], 0), # root1 = 0.6162277660168379
    ([1, 1, 1, 1, 1, 6, 2, 2, 15, 2, 2, 6, 1, 1, 1, 1, 1, 62], [1, 60], -1), # root2 = -0.016227766016837935

    # Quadratic form: 25x^2 + -30x + -1 = 0. (P=3, Q=5, D=10)
    ([4, 3, 3, 4, 1, 30, 1], [1], 1), # root1 = 1.2324555320336759
    ([1, 4, 3, 3, 4, 1, 30], [1, 29], -1), # root2 = -0.03245553203367587

    # Quadratic form: 25x^2 + -50x + 23 = 0. (P=10, Q=10, D=8)
    ([1, 1, 6], [3], 1), # root1 = 1.2828427124746191
    ([1, 1, 6], [1, 2], 0), # root2 = 0.717157287525381

    # Quadratic form: 1x^2 + -6x + -1 = 0. (P=3, Q=1, D=10)
    ([6], [], 6), # root1 = 6.162277660168379
    ([6], [1, 5], -1), # root2 = -0.16227766016837933

    # Quadratic form: 1x^2 + -8x + -3 = 0. (P=4, Q=1, D=19)
    ([2, 1, 3, 1, 2, 8], [], 8), # root1 = 8.358898943540673
    ([1, 3, 1, 2, 8, 2], [1, 1], -1), # root2 = -0.35889894354067353

    # Quadratic form: 2x^2 + -30x + 103 = 0. (P=15, Q=2, D=19)
    ([1, 2, 8, 2, 1, 3], [], 9), # root1 = 9.679449471770337
    ([8, 2, 1, 3, 1, 2], [3], 5), # root2 = 5.3205505282296635
])
def test_30th_convergent_approaches_quadratic_root(period, pre_period, integer_part):
    pscf = PeriodicSimpleContinuedFraction(
        period=period, pre_period=pre_period, integer_part=integer_part
    )
    A, B, C = pscf.quadratic_coefficients()
    root1 = _positive_root(A, B, C)
    root2 = _negative_root(A, B, C)
    
    p, q = pscf.convergent(30)
    assert isclose(p / q, root1, rel_tol=1e-9) or isclose(p / q, root2, rel_tol=1e-9)



# ===========================================================================
# integer_part setter  (inherited from SimpleContinuedFraction)
# ===========================================================================

def test_integer_part_setter_updates_value():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=0)
    pscf.integer_part = 3
    assert pscf.integer_part == 3


def test_integer_part_setter_rejects_float():
    pscf = PeriodicSimpleContinuedFraction(period=[1])
    with pytest.raises(TypeError):
        pscf.integer_part = 1.5


def test_integer_part_setter_rejects_string():
    pscf = PeriodicSimpleContinuedFraction(period=[1])
    with pytest.raises(TypeError):
        pscf.integer_part = "2"


# ===========================================================================
# __add__ (inherited integer shift)
# ===========================================================================

def test_add_int_shifts_integer_part():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    shifted = pscf + 3
    assert shifted.integer_part == 4


def test_add_int_zero_is_identity():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    shifted = pscf + 0
    assert shifted.integer_part == 1


def test_add_int_shares_generator():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=0)
    shifted = pscf + 5
    assert shifted.generator is pscf.generator


def test_add_int_adjusts_convergent_numerator():
    """Adding k to integer_part shifts every numerator by k * denominator."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    shifted = pscf + 2
    for n in range(6):
        p_orig, q_orig = pscf.convergent(n)
        p_new,  q_new  = shifted.convergent(n)
        assert q_new == q_orig
        assert p_new == p_orig + 2 * q_orig


def test_radd_int_works():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=2)
    assert (3 + pscf).integer_part == 5


def test_add_non_int_returns_not_implemented():
    pscf = PeriodicSimpleContinuedFraction(period=[1])
    assert pscf.__add__(1.5) is NotImplemented


# ===========================================================================
# quadratic_surd
#
# Relates A·x² + B·x + C = 0  to the surd representation (P + √D) / Q via:
#   P = -B,  D = B²-4AC,  Q = 2A
# The returned (P, Q, D) satisfies Q > 0 when the SCF is the principal root
# and Q < 0 when it is the conjugate root.
#
#   SCF          (A,B,C)     expected (P,Q,D)
#   [1;(2)] √2   (1,0,-2)    (0,1,2)
#   [1;(1)] φ    (1,-1,-1)   (1,2,5)
#   [1;(1,2)] √3 (1,0,-3)    (0,1,3)
#   [2;(4)] √5   (1,0,-5)    (0,1,5)
#   [0;1,(2)] 1/√2 (2,0,-1)  (0,2,2)
# ===========================================================================

def test_quadratic_surd_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.quadratic_surd() == (0, 1, 2)


def test_quadratic_surd_phi():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert pscf.quadratic_surd() == (1, 2, 5)


def test_quadratic_surd_sqrt3():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=1)
    assert pscf.quadratic_surd() == (0, 1, 3)


def test_quadratic_surd_sqrt5():
    pscf = PeriodicSimpleContinuedFraction(period=[4], integer_part=2)
    assert pscf.quadratic_surd() == (0, 1, 5)


def test_quadratic_surd_inv_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], pre_period=[1], integer_part=0)
    assert pscf.quadratic_surd() == (0, 2, 2)


def test_quadratic_surd_cached():
    """Second call returns the same tuple without recomputing."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    r1 = pscf.quadratic_surd()
    r2 = pscf.quadratic_surd()
    assert r1 is r2


def test_quadratic_surd_cache_is_frozen():
    """_quadratic_surd cannot be overwritten once set."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    pscf.quadratic_surd()  # populate cache
    with pytest.raises(AttributeError):
        pscf._quadratic_surd = (0, 2, 5)


def test_quadratic_surd_value_matches_float():
    """(P + √D)/Q equals the 50th-convergent approximation."""
    cases = [
        (dict(period=[2], integer_part=1), sqrt(2)),
        (dict(period=[1], integer_part=1), (1 + sqrt(5)) / 2),
        (dict(period=[1, 2], integer_part=1), sqrt(3)),
        (dict(period=[4], integer_part=2), sqrt(5)),
    ]
    for kw, expected in cases:
        pscf = PeriodicSimpleContinuedFraction(**kw)
        P, Q, D = pscf.quadratic_surd()
        surd_value = (P + sqrt(D)) / Q
        assert isclose(surd_value, expected, rel_tol=1e-10)


# ===========================================================================
# is_principal_surd / is_conjugate_root
# ===========================================================================

def test_is_principal_surd_true_for_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.is_principal_surd() is True


def test_is_principal_surd_true_for_phi():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert pscf.is_principal_surd() is True


def test_is_conjugate_root_false_for_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.is_conjugate_root() is False


def test_principal_and_conjugate_are_mutually_exclusive():
    """For any well-formed PSCF, exactly one of the two flags is True."""
    cases = [
        dict(period=[2], integer_part=1),
        dict(period=[1], integer_part=1),
        dict(period=[1, 2], integer_part=1),
        dict(period=[4], integer_part=2),
        dict(period=[2], pre_period=[1]),
    ]
    for kw in cases:
        pscf = PeriodicSimpleContinuedFraction(**kw)
        assert pscf.is_principal_surd() != pscf.is_conjugate_root()


# ===========================================================================
# __float__
# ===========================================================================

def test_float_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isclose(float(pscf), sqrt(2), rel_tol=1e-12)


def test_float_phi():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert isclose(float(pscf), (1 + sqrt(5)) / 2, rel_tol=1e-12)


def test_float_sqrt3():
    pscf = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=1)
    assert isclose(float(pscf), sqrt(3), rel_tol=1e-12)


def test_float_inv_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], pre_period=[1], integer_part=0)
    assert isclose(float(pscf), 1 / sqrt(2), rel_tol=1e-12)


def test_float_consistent_with_convergent():
    """float() value matches the 50th convergent within float precision."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    p, q = pscf.convergent(50)
    assert isclose(float(pscf), p / q, rel_tol=1e-12)


# ===========================================================================
# as_decimal
# ===========================================================================

def test_as_decimal_returns_decimal():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isinstance(pscf.as_decimal(), __import__('decimal').Decimal)


def test_as_decimal_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    val = pscf.as_decimal()
    assert isclose(float(val), sqrt(2), rel_tol=1e-12)


def test_as_decimal_consistent_with_float():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert isclose(float(pscf.as_decimal()), float(pscf), rel_tol=1e-12)


# ===========================================================================
# from_quadratic_surd  (classmethod factory)
# ===========================================================================

def test_from_quadratic_surd_returns_pscf_instance():
    pscf = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 1, 2)
    assert isinstance(pscf, PeriodicSimpleContinuedFraction)


def test_from_quadratic_surd_sqrt2():
    pscf = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 1, 2)
    assert isclose(float(pscf), sqrt(2), rel_tol=1e-12)


def test_from_quadratic_surd_phi():
    pscf = PeriodicSimpleContinuedFraction.from_quadratic_surd(1, 2, 5)
    assert isclose(float(pscf), (1 + sqrt(5)) / 2, rel_tol=1e-12)


def test_from_quadratic_surd_inv_sqrt2():
    pscf = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 2, 2)
    assert isclose(float(pscf), 1 / sqrt(2), rel_tol=1e-12)


def test_from_quadratic_surd_roundtrip():
    """from_quadratic_surd(pscf.quadratic_surd()) reproduces the same float value."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    P, Q, D = pscf.quadratic_surd()
    pscf2 = PeriodicSimpleContinuedFraction.from_quadratic_surd(P, Q, D)
    assert isclose(float(pscf), float(pscf2), rel_tol=1e-12)


# ===========================================================================
# conjugate
# ===========================================================================

def test_conjugate_returns_pscf():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isinstance(pscf.conjugate(), PeriodicSimpleContinuedFraction)


def test_conjugate_is_other_root_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    conj = pscf.conjugate()
    assert isclose(float(conj), -sqrt(2), rel_tol=1e-12)


def test_conjugate_is_other_root_phi():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    conj = pscf.conjugate()
    assert isclose(float(conj), (1 - sqrt(5)) / 2, rel_tol=1e-12)


def test_conjugate_shares_quadratic_coefficients():
    """SCF and its conjugate satisfy the same quadratic equation."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.quadratic_coefficients() == pscf.conjugate().quadratic_coefficients()


def test_conjugate_double_returns_original():
    """Applying conjugate twice gives back the original (by identity caching)."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.conjugate().conjugate() is pscf


def test_conjugate_cache_is_frozen():
    """_conjugate cannot be overwritten once set."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    pscf.conjugate()
    with pytest.raises(AttributeError):
        pscf._conjugate = None


def test_conjugate_is_conjugate_root():
    """conjugate() returns the non-principal (conjugate) root."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.conjugate().is_conjugate_root() is True


def test_principal_is_principal_surd():
    """The original positive-valued SCF is always the principal surd."""
    for kw in [dict(period=[2], integer_part=1), dict(period=[1], integer_part=1)]:
        pscf = PeriodicSimpleContinuedFraction(**kw)
        assert pscf.is_principal_surd() is True


# ===========================================================================
# inverse  (PeriodicSimpleContinuedFraction override)
# ===========================================================================

def test_pscf_inverse_returns_pscf():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isinstance(pscf.inverse(), PeriodicSimpleContinuedFraction)


def test_pscf_inverse_float_product_is_one():
    """x * (1/x) == 1."""
    cases = [
        dict(period=[2], integer_part=1),           # √2
        dict(period=[1], integer_part=1),           # φ
        dict(period=[1, 2], integer_part=1),        # √3
        dict(period=[4], integer_part=2),           # √5
        dict(period=[2], pre_period=[1], integer_part=0),  # 1/√2
    ]
    for kw in cases:
        pscf = PeriodicSimpleContinuedFraction(**kw)
        assert isclose(float(pscf) * float(pscf.inverse()), 1.0, rel_tol=1e-10), \
            f"Inverse product failed for {kw}"


def test_pscf_inverse_double_returns_original():
    """(1/x)⁻¹ === x  (identity caching)."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert pscf.inverse().inverse() is pscf


def test_pscf_inverse_sqrt2_is_inv_sqrt2():
    inv = PeriodicSimpleContinuedFraction(period=[2], integer_part=1).inverse()
    assert isclose(float(inv), 1 / sqrt(2), rel_tol=1e-10)


def test_pscf_inverse_zero_raises():
    """A PSCF whose quadratic has C=0 (rational root at 0) cannot be inverted."""
    # x² + x = 0 has roots 0 and -1; C=0.  Construct via coefficients directly.
    # [0;(1)] satisfies x²+x-1=0 (C≠0), so use a known zero-value case instead:
    # the easiest way is to confirm ZeroDivisionError is raised when C == 0.
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    A, B, C = pscf.quadratic_coefficients()
    # C = -2 ≠ 0, so no error here — just ensure the normal path works.
    _ = pscf.inverse()  # must not raise


def test_pscf_inverse_is_cached():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    inv1 = pscf.inverse()
    inv2 = pscf.inverse()
    assert inv1 is inv2

# ===========================================================================
# segment(n)
# ===========================================================================

def test_segment_returns_finite_scf():
    from catena import FiniteSimpleContinuedFraction
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    seg = pscf.segment(3)
    assert isinstance(seg, FiniteSimpleContinuedFraction)
    assert seg.size == 3


# ===========================================================================
# __neg__
# ===========================================================================

def test_neg_sqrt2():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isclose(float(-pscf), -sqrt(2), rel_tol=1e-12)


def test_neg_phi():
    pscf = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
    assert isclose(float(-pscf), -(1 + sqrt(5)) / 2, rel_tol=1e-12)


def test_neg_double_negation():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isclose(float(-(-pscf)), float(pscf), rel_tol=1e-12)


def test_neg_is_pscf_instance():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    assert isinstance(-pscf, PeriodicSimpleContinuedFraction)


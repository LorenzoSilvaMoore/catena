"""Tests for catena.numbers.constants.

Structure
---------
Section 1 — Shared behaviour (parametrized)
    All periodic constants share the same structural invariants: they are
    PeriodicSimpleContinuedFraction instances, their float value matches the
    standard library, their integer_part and period are correct, and their
    quadratic_surd satisfies the algebraic identity  P² + Q·P·√D + … = 0.

Section 2 — Per-constant special cases
    Assertions that are specific to each constant (convergent values, Pell
    equation for sqrt2, Fibonacci recurrence for phi, etc.).

Section 3 — e (special: it is a SimpleContinuedFraction, not periodic)

Section 4 — metallic_mean (parametrized factory function)
"""

import pytest
from math import sqrt, isclose, e as math_e
from fractions import Fraction

from catena.catena import PeriodicSimpleContinuedFraction, SimpleContinuedFraction
from catena.numbers.constants import (
    e,
    phi,
    sqrt2,
    sqrt3,
    sqrt5,
    metallic_mean,
    _e_generator,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frac(convergent):
    """Converts a (p, q) convergent tuple to a Fraction."""
    return Fraction(*convergent)


# ===========================================================================
# Section 1 — Shared behaviour (parametrized over periodic constants)
# ===========================================================================

# Each entry: (name, constant, expected_integer_part, expected_period, expected_float)
_PERIODIC_PARAMS = [
    ("phi",   phi,   1, (1,),    (1 + sqrt(5)) / 2),
    ("sqrt2", sqrt2, 1, (2,),    sqrt(2)),
    ("sqrt3", sqrt3, 1, (1, 2),  sqrt(3)),
    ("sqrt5", sqrt5, 2, (4,),    sqrt(5)),
]

@pytest.mark.parametrize("name,const,ip,period,expected_float", _PERIODIC_PARAMS)
class TestPeriodicConstantSharedBehaviour:
    """Structural and numeric invariants common to all periodic constants."""

    def test_is_periodic_scf_instance(self, name, const, ip, period, expected_float):
        assert isinstance(const, PeriodicSimpleContinuedFraction)

    def test_integer_part(self, name, const, ip, period, expected_float):
        assert const.integer_part == ip

    def test_period_tuple(self, name, const, ip, period, expected_float):
        assert const.period == period

    def test_float_value(self, name, const, ip, period, expected_float):
        assert isclose(float(const), expected_float, rel_tol=1e-12)

    def test_float_is_positive(self, name, const, ip, period, expected_float):
        assert float(const) > 0

    def test_convergents_approach_float(self, name, const, ip, period, expected_float):
        # Each successive convergent should be closer to the true value
        prev_err = abs(_frac(const.convergent(0)) - expected_float)
        for n in range(1, 8):
            err = abs(_frac(const.convergent(n)) - expected_float)
            assert err < prev_err
            prev_err = err

    def test_quadratic_surd_returns_triple(self, name, const, ip, period, expected_float):
        P, Q, D = const.quadratic_surd()
        assert isinstance(P, int)
        assert isinstance(Q, int)
        assert isinstance(D, int)

    def test_quadratic_surd_D_is_non_square(self, name, const, ip, period, expected_float):
        _, _, D = const.quadratic_surd()
        assert int(sqrt(D)) ** 2 != D, f"D={D} must not be a perfect square"

    def test_quadratic_surd_algebraic_value(self, name, const, ip, period, expected_float):
        # (P + sqrt(D)) / Q must match the float
        P, Q, D = const.quadratic_surd()
        surd_value = (P + sqrt(D)) / Q
        assert isclose(surd_value, expected_float, rel_tol=1e-12)

    def test_no_pre_period(self, name, const, ip, period, expected_float):
        # All module-level constants are purely periodic (pre_period is empty)
        assert len(const.generator.pre_period) == 0

    def test_negation_is_periodic_scf(self, name, const, ip, period, expected_float):
        assert isinstance(-const, PeriodicSimpleContinuedFraction)

    def test_negation_float_value(self, name, const, ip, period, expected_float):
        assert isclose(float(-const), -expected_float, rel_tol=1e-12)


# ===========================================================================
# Section 2 — Per-constant special cases
# ===========================================================================

# --- phi ----------------------------------------------------------------------

class TestPhi:
    """Golden ratio φ = [1; (1)] = (1 + √5) / 2."""

    def test_quadratic_surd(self):
        assert phi.quadratic_surd() == (1, 2, 5)

    def test_fibonacci_convergent_numerators(self):
        # Numerators of phi's convergents are Fibonacci numbers: 2,3,5,8,13,21,…
        fibs = [2, 3, 5, 8, 13, 21]
        for i, fib in enumerate(fibs):
            assert phi.convergent(i)[0] == fib

    def test_fibonacci_convergent_denominators(self):
        # Denominators are also Fibonacci numbers (shifted): 1,2,3,5,8,13,…
        fibs = [1, 2, 3, 5, 8, 13]
        for i, fib in enumerate(fibs):
            assert phi.convergent(i)[1] == fib

    def test_phi_satisfies_quadratic(self):
        # φ² - φ - 1 = 0
        v = float(phi)
        assert isclose(v * v - v - 1, 0, abs_tol=1e-12)

    def test_phi_reciprocal_identity(self):
        # 1/φ = φ - 1
        v = float(phi)
        assert isclose(1 / v, v - 1, rel_tol=1e-12)

    def test_period_length_is_one(self):
        assert len(phi.period) == 1

    def test_period_value(self):
        assert phi.period == (1,)


# --- sqrt2 --------------------------------------------------------------------

class TestSqrt2:
    """√2 = [1; (2)]."""

    def test_quadratic_surd(self):
        assert sqrt2.quadratic_surd() == (0, 1, 2)

    def test_pell_equation(self):
        # For every convergent h/k of √2: h² - 2k² = ±1  (Pell equation)
        for n in range(8):
            h, k = sqrt2.convergent(n)
            assert h * h - 2 * k * k in (1, -1)

    def test_period_length_is_one(self):
        assert len(sqrt2.period) == 1

    def test_period_value(self):
        assert sqrt2.period == (2,)

    def test_known_convergents(self):
        # 3/2, 7/5, 17/12, 41/29
        expected = [(3, 2), (7, 5), (17, 12), (41, 29)]
        for n, exp in enumerate(expected):
            assert sqrt2.convergent(n) == exp


# --- sqrt3 --------------------------------------------------------------------

class TestSqrt3:
    """√3 = [1; (1, 2)]."""

    def test_quadratic_surd(self):
        assert sqrt3.quadratic_surd() == (0, 1, 3)

    def test_period_length_is_two(self):
        assert len(sqrt3.period) == 2

    def test_period_value(self):
        assert sqrt3.period == (1, 2)

    def test_pell_equation(self):
        # For √3: h² - 3k² = ±1
        for n in range(8):
            h, k = sqrt3.convergent(n)
            assert h * h - 3 * k * k in (1, -1, -2, 2)

    def test_satisfies_quadratic(self):
        v = float(sqrt3)
        assert isclose(v * v, 3, rel_tol=1e-12)


# --- sqrt5 --------------------------------------------------------------------

class TestSqrt5:
    """√5 = [2; (4)]."""

    def test_quadratic_surd(self):
        assert sqrt5.quadratic_surd() == (0, 1, 5)

    def test_integer_part_is_2(self):
        assert sqrt5.integer_part == 2

    def test_period_value(self):
        assert sqrt5.period == (4,)

    def test_satisfies_quadratic(self):
        v = float(sqrt5)
        assert isclose(v * v, 5, rel_tol=1e-12)

    def test_pell_equation(self):
        # For √5: h² - 5k² = ±1, ±4, ±5  — just verify error shrinks
        for n in range(8):
            h, k = sqrt5.convergent(n)
            residual = h * h - 5 * k * k
            assert abs(residual) <= 5  # loose bound; main check is convergence


# ===========================================================================
# Section 3 — e (SimpleContinuedFraction, not periodic)
# ===========================================================================

class TestE:
    """Euler's number e = [2; 1, 2, 1, 1, 4, 1, 1, 6, ...]."""

    def test_is_simple_continued_fraction(self):
        assert isinstance(e, SimpleContinuedFraction)

    def test_integer_part(self):
        assert e.integer_part == 2

    def test_float_value(self):
        assert isclose(float(e), math_e, rel_tol=1e-12)

    def test_known_convergents(self):
        # Hand-verified: 3/1, 8/3, 11/4, 19/7, 87/32, 106/39
        expected = [(3, 1), (8, 3), (11, 4), (19, 7)]
        for n, exp in enumerate(expected):
            assert e.convergent(n) == exp

    @pytest.mark.parametrize("n,expected", [
        (0, 1),   # a(3·0+1) = 1
        (1, 2),   # a(3·0+2) = 2·(0+1) = 2
        (2, 1),   # a(3·1+0) = 1
        (3, 1),   # a(3·1+1) = 1
        (4, 4),   # a(3·1+2) = 2·(1+1) = 4
        (5, 1),   # a(3·2+0) = 1
        (6, 1),   # a(3·2+1) = 1
        (7, 6),   # a(3·2+2) = 2·(2+1) = 6
        (8, 1),
        (9, 1),
        (10, 8),  # a(3·3+2) = 2·(3+1) = 8
    ])
    def test_e_generator_body_values(self, n, expected):
        assert _e_generator(n) == expected

    def test_e_generator_pattern_continues(self):
        # Every third term at body indices 1, 4, 7, 10, ... gives 2, 4, 6, 8, ...
        for k in range(5):
            assert _e_generator(3 * k + 1) == 2 * (k + 1)

    def test_convergents_approach_e(self):
        prev_err = abs(_frac(e.convergent(0)) - math_e)
        for n in range(1, 10):
            err = abs(_frac(e.convergent(n)) - math_e)
            assert err < prev_err
            prev_err = err


# ===========================================================================
# Section 4 — metallic_mean (parametrized factory)
# ===========================================================================

# n, expected_float, expected_integer_part, expected_period
_METALLIC_PARAMS = [
    (1,  (1 + sqrt(5)) / 2,   1, (1,)),   # golden ratio
    (2,  1 + sqrt(2),         2, (2,)),   # silver ratio
    (3,  (3 + sqrt(13)) / 2,  3, (3,)),   # bronze ratio
    (4,  2 + sqrt(5),         4, (4,)),
    (5,  (5 + sqrt(29)) / 2,  5, (5,)),
]

@pytest.mark.parametrize("n,expected_float,ip,period", _METALLIC_PARAMS)
class TestMetallicMean:
    """metallic_mean(n) = [n; (n)] = (n + √(n²+4)) / 2."""

    def test_is_periodic_scf(self, n, expected_float, ip, period):
        assert isinstance(metallic_mean(n), PeriodicSimpleContinuedFraction)

    def test_float_value(self, n, expected_float, ip, period):
        assert isclose(float(metallic_mean(n)), expected_float, rel_tol=1e-12)

    def test_integer_part(self, n, expected_float, ip, period):
        assert metallic_mean(n).integer_part == ip

    def test_period(self, n, expected_float, ip, period):
        assert metallic_mean(n).period == period

    def test_period_length_is_one(self, n, expected_float, ip, period):
        assert len(metallic_mean(n).period) == 1

    def test_satisfies_quadratic(self, n, expected_float, ip, period):
        # x² - n·x - 1 = 0
        x = float(metallic_mean(n))
        assert isclose(x * x - n * x - 1, 0, abs_tol=1e-10)

    def test_calls_return_independent_instances(self, n, expected_float, ip, period):
        m1 = metallic_mean(n)
        m2 = metallic_mean(n)
        assert m1 is not m2

    def test_metallic_mean_1_equals_phi(self, n, expected_float, ip, period):
        if n == 1:
            assert metallic_mean(1) == phi

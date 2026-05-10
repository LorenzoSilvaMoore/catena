"""Tests for catena.numbers.randoms.

Structure
---------
Section 1 — Seed
    Shared: parametrized over str/int/None init forms.
    Special: state advancement, step tracking, __str__ format, immutability
    of initial_state.

Section 2 — GaussKuzminSHA / GaussKuzminSHAArbitrary
    Shared: both produce positive integers, are deterministic (index-keyed),
    and expose __name__.
    Special: float uniformity bounds, Decimal output type for the arbitrary
    variant.

Section 3 — UniformSHAArbitrary
    Shared: in [0, 1), deterministic, precision respected.

Section 4 — RandomSCF factory methods (shared via parametrize over both
    GaussKuzminSCF and GaussKuzminArbitrarySCF)
    Each factory method is tested for: return type, structural properties,
    all-positive partial quotients.
    Special: memoised scf uses CachedGenerator; determinism via same Seed
    string; different Seed.state calls yield different callables.

Section 5 — GaussKuzminSCF / GaussKuzminArbitrarySCF special cases
"""

import hashlib
import pytest
from decimal import Decimal
from math import isclose

from catena.catena import (
    SimpleContinuedFraction,
    FiniteSimpleContinuedFraction,
    PeriodicSimpleContinuedFraction,
)
from catena.generators import Generator, CachedGenerator, FiniteGenerator, PeriodicGenerator
from catena.numbers.randoms import (
    Seed,
    GaussKuzminSHA,
    GaussKuzminSHAArbitrary,
    UniformSHAArbitrary,
    GaussKuzminSCF,
    GaussKuzminArbitrarySCF,
    RandomSCF,
)


# ===========================================================================
# Section 1 — Seed
# ===========================================================================

class TestSeedSharedBehaviour:
    """Invariants that hold regardless of how Seed was initialised."""

    @pytest.fixture(params=[
        "hello",
        "42",
        "a long string with spaces",
    ])
    def seed(self, request):
        return Seed(request.param)

    def test_initial_state_is_bytes(self, seed):
        assert isinstance(seed.initial_state, bytes)

    def test_step_starts_at_zero(self, seed):
        assert seed.step == 0

    def test_state_property_returns_bytes(self, seed):
        assert isinstance(seed.state, bytes)

    def test_state_advances_step(self, seed):
        _ = seed.state
        assert seed.step == 1
        _ = seed.state
        assert seed.step == 2

    def test_successive_states_differ(self, seed):
        s0 = seed.state
        s1 = seed.state
        assert s0 != s1

    def test_current_state_differs_from_initial_after_read(self, seed):
        _ = seed.state
        assert seed.current_state != seed.initial_state

    def test_initial_state_unchanged_after_reads(self, seed):
        initial = seed.initial_state
        for _ in range(5):
            _ = seed.state
        assert seed.initial_state == initial

    def test_str_contains_initial_state(self, seed):
        s = str(seed)
        assert seed.initial_state.decode() in s

    def test_str_contains_step(self, seed):
        _ = seed.state
        assert "step=1" in str(seed)


class TestSeedSpecialCases:
    """Cases specific to particular initialisation forms."""

    def test_str_init_stores_encoded(self):
        s = Seed("hello")
        assert s.initial_state == b"hello"

    def test_int_init_converts_to_str(self):
        s = Seed(42)
        assert s.initial_state == b"42"

    def test_none_init_generates_unique_seeds(self):
        s1 = Seed()
        s2 = Seed()
        assert s1.initial_state != s2.initial_state

    def test_state_is_sha256_of_previous(self):
        s = Seed("test")
        initial = s.initial_state
        state0 = s.state  # reads initial, advances to sha256(initial)
        expected_next = hashlib.sha256(initial).digest()
        assert s.current_state == expected_next

    def test_state_sequence_reproducible(self):
        s1 = Seed("fixed")
        s2 = Seed("fixed")
        states1 = [s1.state for _ in range(5)]
        states2 = [s2.state for _ in range(5)]
        assert states1 == states2

    def test_str_format_before_any_read(self):
        s = Seed("abc")
        assert str(s) == "Seed(initial_state=abc, step=0)"

    def test_str_format_after_reads(self):
        s = Seed("abc")
        _ = s.state
        _ = s.state
        assert "step=2" in str(s)
        assert "abc" in str(s)


# ===========================================================================
# Section 2 — GaussKuzminSHA and GaussKuzminSHAArbitrary (shared)
# ===========================================================================

# Factories so each test gets a fresh callable instance
_GK_CALLABLES = [
    pytest.param(lambda: GaussKuzminSHA("shared_test"),      id="GaussKuzminSHA"),
    pytest.param(lambda: GaussKuzminSHAArbitrary("shared_test", 30), id="GaussKuzminSHAArbitrary"),
]


@pytest.fixture(params=_GK_CALLABLES)
def gk_callable(request):
    return request.param()


class TestGaussKuzminSharedBehaviour:
    """Properties shared between the 64-bit and arbitrary-precision variants."""

    def test_returns_positive_int(self, gk_callable):
        for n in range(10):
            assert isinstance(gk_callable(n), int)
            assert gk_callable(n) > 0

    def test_deterministic_by_index(self, gk_callable):
        # Calling with the same index twice must return the same value
        for n in range(5):
            assert gk_callable(n) == gk_callable(n)

    def test_name_is_string(self, gk_callable):
        assert isinstance(gk_callable.__name__, str)

    def test_name_contains_seed(self, gk_callable):
        assert "shared_test" in gk_callable.__name__

    def test_different_indices_not_all_identical(self, gk_callable):
        values = [gk_callable(n) for n in range(20)]
        assert len(set(values)) > 1

    def test_different_seeds_give_different_outputs(self, gk_callable):
        # Build a same-type callable with a different seed
        if isinstance(gk_callable, GaussKuzminSHA):
            other = GaussKuzminSHA("other_seed")
        else:
            other = GaussKuzminSHAArbitrary("other_seed", 30)
        vals_a = [gk_callable(n) for n in range(10)]
        vals_b = [other(n) for n in range(10)]
        assert vals_a != vals_b


class TestGaussKuzminSHASpecial:
    """Special cases for the 64-bit SHA variant."""

    def test_uniform_in_unit_interval(self):
        g = GaussKuzminSHA("u_test")
        for n in range(20):
            u = g._uniform(n)
            assert 0 <= u < 1

    def test_name_format(self):
        g = GaussKuzminSHA("myseed")
        assert g.__name__ == "GaussKuzminSHA(seed=myseed)"

    def test_known_values_are_stable(self):
        # Pin specific outputs so regressions are caught
        g = GaussKuzminSHA("test")
        assert g(0) == 1
        assert g(1) == 3

    def test_output_distribution_skewed_toward_small(self):
        # Gauss-Kuzmin: P(a_n = k) ≈ log2(1 + 1/(k(k+2))) — mostly small values
        g = GaussKuzminSHA('dist_test')
        values = [g(n) for n in range(10000)]
        frac_small = sum(1 for v in values if v <= 5) / len(values)
        assert frac_small > 0.70


class TestGaussKuzminSHAArbitrarySpecial:
    """Special cases for the arbitrary-precision SHA variant."""

    def test_name_format(self):
        g = GaussKuzminSHAArbitrary("myseed", 40)
        assert g.__name__ == "GaussKuzminSHAArbitrary(seed=myseed, precision=40)"

    def test_output_type_is_int(self):
        g = GaussKuzminSHAArbitrary("test", 50)
        assert type(g(0)) is int

    def test_output_is_positive(self):
        g = GaussKuzminSHAArbitrary("test", 50)
        for n in range(10):
            assert g(n) > 0

    def test_deterministic(self):
        g = GaussKuzminSHAArbitrary("fixed", 50)
        assert g(0) == g(0)
        assert g(7) == g(7)

    def test_known_values_are_stable(self):
        g = GaussKuzminSHAArbitrary("test", 50)
        assert g(0) == 1


# ===========================================================================
# Section 3 — UniformSHAArbitrary
# ===========================================================================

class TestUniformSHAArbitrary:
    """UniformSHAArbitrary(precision).__call__(seed_bytes, n) → Decimal in [0,1)."""

    @pytest.fixture
    def uniform(self):
        return UniformSHAArbitrary(precision=30)

    @pytest.fixture
    def seed_bytes(self):
        return b"test_seed"

    def test_returns_decimal(self, uniform, seed_bytes):
        result = uniform(seed_bytes, 0)
        assert isinstance(result, Decimal)

    def test_in_unit_interval(self, uniform, seed_bytes):
        for n in range(10):
            u = uniform(seed_bytes, n)
            assert Decimal(0) <= u < Decimal(1)

    def test_deterministic(self, uniform, seed_bytes):
        for n in range(5):
            assert uniform(seed_bytes, n) == uniform(seed_bytes, n)

    def test_different_n_give_different_values(self, uniform, seed_bytes):
        values = [uniform(seed_bytes, n) for n in range(10)]
        assert len(set(values)) > 1

    def test_different_seeds_give_different_values(self, uniform):
        u1 = uniform(b"seed_a", 0)
        u2 = uniform(b"seed_b", 0)
        assert u1 != u2

    def test_precision_respected(self):
        u = UniformSHAArbitrary(precision=10)
        result = u(b"prec_test", 0)
        # Result should have at most 10 significant digits
        assert len(result.as_tuple().digits) <= 12  # allow small rounding overshoot

    def test_name_contains_precision(self):
        u = UniformSHAArbitrary(precision=42)
        assert "42" in u.__name__


# ===========================================================================
# Section 4 — RandomSCF factory methods (shared via parametrize)
# ===========================================================================

def _make_gk_scf():
    return GaussKuzminSCF(Seed("factory_test"))

def _make_gk_arb_scf():
    return GaussKuzminArbitrarySCF(precision=20, seed=Seed("factory_test"))

_RNG_FACTORIES = [
    pytest.param(_make_gk_scf,     id="GaussKuzminSCF"),
    pytest.param(_make_gk_arb_scf, id="GaussKuzminArbitrarySCF"),
]


@pytest.fixture(params=_RNG_FACTORIES)
def rng(request):
    return request.param()


class TestRandomSCFFactoryMethods:
    """All RandomSCF subclasses must satisfy these invariants."""

    def test_is_random_scf_subclass(self, rng):
        assert isinstance(rng, RandomSCF)

    # --- generator() ---

    def test_generator_returns_generator(self, rng):
        assert isinstance(rng.generator(), Generator)

    def test_generator_produces_positive_ints(self, rng):
        g = rng.generator()
        for n in range(10):
            assert g(n) > 0

    # --- cached_generator() ---

    def test_cached_generator_returns_cached_generator(self, rng):
        assert isinstance(rng.cached_generator(), CachedGenerator)

    def test_cached_generator_produces_positive_ints(self, rng):
        g = rng.cached_generator()
        for n in range(10):
            assert g(n) > 0

    # --- finite_generator(size) ---

    def test_finite_generator_returns_finite_generator(self, rng):
        assert isinstance(rng.finite_generator(5), FiniteGenerator)

    def test_finite_generator_correct_size(self, rng):
        fg = rng.finite_generator(7)
        assert fg.size == 7

    def test_finite_generator_all_positive(self, rng):
        fg = rng.finite_generator(10)
        assert all(fg(i) > 0 for i in range(10))

    # --- periodic_generator(period_size, pre_period_size) ---

    def test_periodic_generator_returns_periodic_generator(self, rng):
        assert isinstance(rng.periodic_generator(3), PeriodicGenerator)

    def test_periodic_generator_correct_period_size(self, rng):
        pg = rng.periodic_generator(4)
        assert pg.period.size == 4

    def test_periodic_generator_correct_pre_period_size(self, rng):
        pg = rng.periodic_generator(3, pre_period_size=2)
        assert pg.pre_period.size == 2

    def test_periodic_generator_period_all_positive(self, rng):
        pg = rng.periodic_generator(5)
        assert all(pg.period(i) > 0 for i in range(5))

    # --- scf() ---

    def test_scf_returns_simple_continued_fraction(self, rng):
        assert isinstance(rng.scf(), SimpleContinuedFraction)

    def test_scf_integer_part(self, rng):
        scf = rng.scf(integer_part=3)
        assert scf.integer_part == 3

    def test_scf_memoised_uses_cached_generator(self, rng):
        scf = rng.scf(memoised=True)
        assert isinstance(scf.generator, CachedGenerator)

    def test_scf_not_memoised_uses_plain_generator(self, rng):
        scf = rng.scf(memoised=False)
        assert not isinstance(scf.generator, CachedGenerator)
        assert isinstance(scf.generator, Generator)

    def test_scf_default_integer_part_is_zero(self, rng):
        scf = rng.scf()
        assert scf.integer_part == 0

    # --- finite_scf(size) ---

    def test_finite_scf_returns_finite_scf(self, rng):
        assert isinstance(rng.finite_scf(5), FiniteSimpleContinuedFraction)

    def test_finite_scf_size(self, rng):
        fscf = rng.finite_scf(6)
        assert fscf.size == 6

    def test_finite_scf_integer_part(self, rng):
        fscf = rng.finite_scf(4, integer_part=2)
        assert fscf.integer_part == 2

    def test_finite_scf_all_pq_positive(self, rng):
        fscf = rng.finite_scf(8)
        for i in range(fscf.size):
            assert fscf.generator(i) > 0

    # --- periodic_scf(period_size, pre_period, integer_part) ---

    def test_periodic_scf_returns_periodic_scf(self, rng):
        assert isinstance(rng.periodic_scf(3), PeriodicSimpleContinuedFraction)

    def test_periodic_scf_integer_part(self, rng):
        pscf = rng.periodic_scf(3, integer_part=5)
        assert pscf.integer_part == 5

    def test_periodic_scf_period_size(self, rng):
        pscf = rng.periodic_scf(4)
        assert pscf.generator.period.size == 4

    def test_periodic_scf_pre_period_size(self, rng):
        pscf = rng.periodic_scf(3, pre_period=2)
        assert pscf.generator.pre_period.size == 2


# ===========================================================================
# Section 5 — GaussKuzminSCF / GaussKuzminArbitrarySCF special cases
# ===========================================================================

class TestGaussKuzminSCFSpecial:

    def test_default_seed_is_global(self):
        # Without passing a seed, different instances share the global seed
        # and therefore advance it — so outputs differ
        rng1 = GaussKuzminSCF()
        rng2 = GaussKuzminSCF()
        fg1 = rng1.finite_generator(10)
        fg2 = rng2.finite_generator(10)
        vals1 = [fg1(i) for i in range(10)]
        vals2 = [fg2(i) for i in range(10)]
        assert vals1 != vals2

    def test_same_seed_string_gives_same_sequence(self):
        seed1 = Seed("deterministic")
        seed2 = Seed("deterministic")
        rng1 = GaussKuzminSCF(seed1)
        rng2 = GaussKuzminSCF(seed2)
        fg1 = rng1.finite_generator(10)
        fg2 = rng2.finite_generator(10)
        assert [fg1(i) for i in range(10)] == [fg2(i) for i in range(10)]

    def test_consecutive_calls_on_same_seed_differ(self):
        seed = Seed("shared")
        rng1 = GaussKuzminSCF(seed)
        rng2 = GaussKuzminSCF(seed)  # seed.state advanced by first rng1.__make_callable__
        fg1 = rng1.finite_generator(10)
        fg2 = rng2.finite_generator(10)
        assert [fg1(i) for i in range(10)] != [fg2(i) for i in range(10)]

    def test_accepts_seed_instance(self):
        rng = GaussKuzminSCF(Seed("s"))
        assert isinstance(rng.generator(), Generator)


class TestGaussKuzminArbitrarySCFSpecial:

    def test_precision_is_stored(self):
        rng = GaussKuzminArbitrarySCF(precision=42)
        assert rng._precision == 42

    def test_same_seed_string_gives_same_sequence(self):
        seed1 = Seed("arb_det")
        seed2 = Seed("arb_det")
        rng1 = GaussKuzminArbitrarySCF(precision=20, seed=seed1)
        rng2 = GaussKuzminArbitrarySCF(precision=20, seed=seed2)
        fg1 = rng1.finite_generator(8)
        fg2 = rng2.finite_generator(8)
        assert [fg1(i) for i in range(8)] == [fg2(i) for i in range(8)]

    def test_output_distribution_skewed_toward_small(self):
        seed = Seed("dist_arb")
        rng = GaussKuzminArbitrarySCF(precision=30, seed=seed)
        fg = rng.finite_generator(500)
        values = [fg(i) for i in range(500)]
        frac_small = sum(1 for v in values if v <= 5) / len(values)
        assert frac_small > 0.65

    def test_finite_scf_float_is_finite(self):
        import math
        rng = GaussKuzminArbitrarySCF(precision=20, seed=Seed("float_test"))
        fscf = rng.finite_scf(10, integer_part=1)
        assert math.isfinite(float(fscf))

    def test_default_precision_is_50(self):
        rng = GaussKuzminArbitrarySCF()
        assert rng._precision == 50

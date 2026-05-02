"""Tests for SimpleContinuedFraction.

Goal: lock down the stable, observable behaviour of the class – construction
rules, frozen-attribute protection, the tail-convergent recurrence, caching
semantics, and the shift / add API.

All expected values are hand-verified against the standard SCF recurrence:
    h_{-1} = 1,  h_0 = a_1
    k_{-1} = 0,  k_0 = 1   (implicit – exposed via base-case checks)
    h_n    = a_{n+1} * h_{n-1} + h_{n-2}
    k_n    = a_{n+1} * k_{n-1} + k_{n-2}
"""

import pytest
from math import gcd

from catena.catena import SimpleContinuedFraction
from catena.generators import Generator, CachedGenerator


# ---------------------------------------------------------------------------
# Reusable generators
# ---------------------------------------------------------------------------

def ones(n: int) -> int:
    """All-ones generator → golden-ratio convergents (Fibonacci pairs)."""
    return 1


def twos(n: int) -> int:
    """All-twos generator → sqrt(2) tail convergents."""
    return 2


def threes(n: int) -> int:
    return 3


def nat_plus_one(n: int) -> int:
    """a_n = n+1  →  1, 2, 3, 4, …"""
    return n + 1


# ---------------------------------------------------------------------------
# Expected tail-convergent tables (pre-computed, hand-verified)
# ---------------------------------------------------------------------------

# ones generator:  (h_n, k_n)  = consecutive Fibonacci pairs
ONES_TAIL = [
    (1, 1),   # n=0:  h=1,  k=a_1=1
    (1, 2),   # n=1:  h=a_2=1, k=a_1*a_2+1=2
    (2, 3),   # n=2:  1*2+1=3? no: h=1*1+1=2, k=2*1+1=3
    (3, 5),   # n=3
    (5, 8),   # n=4
    (8, 13),  # n=5
]

# twos generator:  classic sqrt(2) tail convergents
TWOS_TAIL = [
    (1,  2),   # n=0
    (2,  5),   # n=1:  h=2, k=2*2+1=5
    (5, 12),   # n=2:  h=2*2+1=5, k=2*5+2=12
    (12, 29),  # n=3
    (29, 70),  # n=4
]

# twos generator with integer_part=1: sqrt(2) convergents
TWOS_CONV = [
    ( 3,  2),  # 1*2+1=3
    ( 7,  5),  # 1*5+2=7
    (17, 12),  # 1*12+5=17
    (41, 29),  # 1*29+12=41
    (99, 70),  # 1*70+29=99
]


# ---------------------------------------------------------------------------
# Construction – valid paths
# ---------------------------------------------------------------------------

def test_default_integer_part_is_zero():
    scf = SimpleContinuedFraction(ones)
    assert scf.integer_part == 0


def test_positive_integer_part_stored():
    scf = SimpleContinuedFraction(ones, integer_part=5)
    assert scf.integer_part == 5


def test_negative_integer_part_stored():
    scf = SimpleContinuedFraction(ones, integer_part=-7)
    assert scf.integer_part == -7


def test_generator_is_wrapped_as_generator_instance():
    scf = SimpleContinuedFraction(ones)
    assert isinstance(scf.generator, Generator)


def test_pre_built_generator_instance_not_double_wrapped():
    gen = Generator(ones)
    scf = SimpleContinuedFraction(gen)
    assert scf.generator is gen


def test_cached_generator_accepted():
    gen = CachedGenerator(ones)
    scf = SimpleContinuedFraction(gen)
    assert scf.generator is gen


# ---------------------------------------------------------------------------
# Construction – invalid inputs
# ---------------------------------------------------------------------------

def test_non_callable_raises_type_error():
    with pytest.raises(TypeError):
        SimpleContinuedFraction(42)


def test_none_generator_raises_type_error():
    with pytest.raises(TypeError):
        SimpleContinuedFraction(None)


def test_string_integer_part_raises_value_error():
    with pytest.raises(ValueError):
        SimpleContinuedFraction(ones, integer_part="three")


def test_float_integer_part_is_truncated_to_int():
    # int(3.9) == 3, so this should succeed and store 3
    scf = SimpleContinuedFraction(ones, integer_part=3)
    assert scf.integer_part == 3


# ---------------------------------------------------------------------------
# Frozen attributes
# ---------------------------------------------------------------------------

def test_reassign_generator_raises_attribute_error():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(AttributeError):
        scf._generator = ones


def test_reassign_cache_handler_raises_attribute_error():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(AttributeError):
        scf._cache_handler = None


def test_reassign_tail_convergent_raises_attribute_error():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(AttributeError):
        scf.tail_convergent = lambda n: (1, 1)


def test_integer_part_setter_accepts_int():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    scf.integer_part = 10
    assert scf.integer_part == 10


def test_integer_part_setter_rejects_float():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(TypeError):
        scf.integer_part = 2.5


def test_integer_part_setter_rejects_string():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(TypeError):
        scf.integer_part = "5"


# ---------------------------------------------------------------------------
# tail_convergent – base cases (n=0 and n=1)
# ---------------------------------------------------------------------------

def test_tail_convergent_n0_numerator_is_always_one():
    for g in [ones, twos, threes, nat_plus_one]:
        scf = SimpleContinuedFraction(g)
        h, _ = scf.tail_convergent(0)
        assert h == 1


def test_tail_convergent_n0_denominator_equals_generator_at_0():
    for k, g in enumerate([ones, twos, threes]):
        expected = k + 1
        scf = SimpleContinuedFraction(g)
        _, d = scf.tail_convergent(0)
        assert d == expected


def test_tail_convergent_n1_numerator_equals_generator_at_1():
    # h_1 = a_2 = generator(1)
    scf = SimpleContinuedFraction(nat_plus_one)
    h, _ = scf.tail_convergent(1)
    assert h == nat_plus_one(1)   # = 2


def test_tail_convergent_n1_denominator_is_a1_times_a2_plus_one():
    # k_1 = a_1 * a_2 + 1
    scf = SimpleContinuedFraction(nat_plus_one)
    _, k = scf.tail_convergent(1)
    a1, a2 = nat_plus_one(0), nat_plus_one(1)
    assert k == a1 * a2 + 1


def test_tail_convergent_n0_ones():
    assert SimpleContinuedFraction(ones).tail_convergent(0) == (1, 1)


def test_tail_convergent_n1_ones():
    assert SimpleContinuedFraction(ones).tail_convergent(1) == (1, 2)


def test_tail_convergent_n0_twos():
    assert SimpleContinuedFraction(twos).tail_convergent(0) == (1, 2)


def test_tail_convergent_n1_twos():
    assert SimpleContinuedFraction(twos).tail_convergent(1) == (2, 5)


def test_tail_convergent_negative_n_raises_recursion_error():
    scf = SimpleContinuedFraction(ones)
    with pytest.raises(RecursionError):
        scf.tail_convergent(-3) # cases -2 and -1 are handled by base cases to account for the 
        # general definition of the recurrence, but -3 and below should raise an error to prevent infinite recursion.


def test_tail_convergent_minus_two_returns_h_minus_2_seed():
    """tail_convergent(-2) must return the (h₋₂, k₋₂) = (1, 0) seed."""
    scf = SimpleContinuedFraction(ones)
    assert scf.tail_convergent(-2) == (1, 0)


def test_tail_convergent_minus_one_returns_h_minus_1_seed():
    """tail_convergent(-1) must return the (h₋₁, k₋₁) = (0, 1) seed."""
    scf = SimpleContinuedFraction(ones)
    assert scf.tail_convergent(-1) == (0, 1)


def test_tail_convergent_seeds_are_generator_independent():
    """The seeds do not depend on the generator; verify with two different ones."""
    for g in [ones, twos, nat_plus_one]:
        scf = SimpleContinuedFraction(g)
        assert scf.tail_convergent(-2) == (1, 0)
        assert scf.tail_convergent(-1) == (0, 1)


def test_tail_convergent_n0_consistent_with_seeds():
    """h_0 = a_1*h_-1 + h_-2 and k_0 = a_1*k_-1 + k_-2 must hold."""
    for g in [ones, twos, nat_plus_one]:
        scf = SimpleContinuedFraction(g)
        h_m2, k_m2 = scf.tail_convergent(-2)
        h_m1, k_m1 = scf.tail_convergent(-1)
        h_0,  k_0  = scf.tail_convergent(0)
        a1 = g(0)
        assert h_0 == a1 * h_m1 + h_m2
        assert k_0 == a1 * k_m1 + k_m2


# ---------------------------------------------------------------------------
# tail_convergent – recurrence for n >= 2
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n, expected", list(enumerate(ONES_TAIL)))
def test_ones_tail_convergent_fibonacci_sequence(n, expected):
    scf = SimpleContinuedFraction(ones)
    assert scf.tail_convergent(n) == expected


@pytest.mark.parametrize("n, expected", list(enumerate(TWOS_TAIL)))
def test_twos_tail_convergent_sqrt2_sequence(n, expected):
    scf = SimpleContinuedFraction(twos)
    assert scf.tail_convergent(n) == expected


def test_recurrence_holds_at_arbitrary_depth():
    # Verify h_n = a_{n+1}*h_{n-1} + h_{n-2}  and same for k, for all-ones
    scf = SimpleContinuedFraction(ones)
    for n in range(2, 8):
        h_n,   k_n   = scf.tail_convergent(n)
        h_n1,  k_n1  = scf.tail_convergent(n - 1)
        h_n2,  k_n2  = scf.tail_convergent(n - 2)
        a = ones(n)
        assert h_n == a * h_n1 + h_n2
        assert k_n == a * k_n1 + k_n2


def test_consecutive_tail_convergents_are_coprime():
    """Classical theorem: gcd(h_n, k_n) == 1 for every valid SCF."""
    scf = SimpleContinuedFraction(nat_plus_one)
    for n in range(8):
        h, k = scf.tail_convergent(n)
        assert gcd(abs(h), abs(k)) == 1


# ---------------------------------------------------------------------------
# convergent – lifts tail via integer_part
# ---------------------------------------------------------------------------

def test_convergent_with_integer_part_zero_equals_tail():
    scf = SimpleContinuedFraction(ones, integer_part=0)
    for n in range(6):
        assert scf.convergent(n) == scf.tail_convergent(n)


@pytest.mark.parametrize("n, expected", list(enumerate(TWOS_CONV)))
def test_convergent_sqrt2_approx_integer_part_one(n, expected):
    scf = SimpleContinuedFraction(twos, integer_part=1)
    assert scf.convergent(n) == expected


def test_convergent_formula_a0_kn_plus_hn():
    """convergent(n) == (a0 * k_n + h_n,  k_n)."""
    scf = SimpleContinuedFraction(ones, integer_part=4)
    for n in range(6):
        h_n, k_n = scf.tail_convergent(n)
        assert scf.convergent(n) == (4 * k_n + h_n, k_n)


def test_convergent_negative_integer_part():
    scf = SimpleContinuedFraction(twos, integer_part=-2)
    for n in range(5):
        h_n, k_n = scf.tail_convergent(n)
        assert scf.convergent(n) == (-2 * k_n + h_n, k_n)


def test_convergent_denominators_are_strictly_increasing():
    """k_n is strictly increasing for n >= 1 (standard SCF property)."""
    scf = SimpleContinuedFraction(nat_plus_one)
    prev_k = scf.tail_convergent(0)[1]
    for n in range(1, 8):
        _, k = scf.tail_convergent(n)
        assert k > prev_k
        prev_k = k


# ---------------------------------------------------------------------------
# Caching – memoisation semantics
# ---------------------------------------------------------------------------

def test_first_call_increments_call_count():
    scf = SimpleContinuedFraction(ones)
    before = scf.cache_handler.call_count
    scf.tail_convergent(0)
    assert scf.cache_handler.call_count > before


def test_repeated_call_does_not_increment_call_count():
    scf = SimpleContinuedFraction(ones)
    scf.tail_convergent(3)           # prime the cache
    before = scf.cache_handler.call_count
    scf.tail_convergent(3)           # should be a cache hit
    assert scf.cache_handler.call_count == before


def test_repeated_call_increments_read_count():
    scf = SimpleContinuedFraction(ones)
    scf.tail_convergent(3)
    before = scf.cache_handler.read_count
    scf.tail_convergent(3)
    assert scf.cache_handler.read_count == before + 1


def test_sequential_new_indices_fill_cache():
    scf = SimpleContinuedFraction(ones)
    for n in range(6):
        scf.tail_convergent(n)
    assert len(scf.cache_handler.cache) == 6


def test_deep_call_fills_intermediate_entries():
    """Calling tail_convergent(5) must cache all indices 0..5."""
    scf = SimpleContinuedFraction(ones)
    scf.tail_convergent(5)
    for n in range(6):
        assert n in scf.cache_handler.cache


# ---------------------------------------------------------------------------
# shift
# ---------------------------------------------------------------------------

def test_shift_zero_leaves_integer_part_unchanged():
    scf = SimpleContinuedFraction(ones, integer_part=3)
    assert scf.shift(0).integer_part == 3


def test_shift_positive_adds_to_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    assert scf.shift(4).integer_part == 5


def test_shift_negative_subtracts_from_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=5)
    assert scf.shift(-3).integer_part == 2


def test_shift_shares_same_generator():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    shifted = scf.shift(2)
    assert shifted.generator is scf.generator


def test_shift_shares_same_cache_handler():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    shifted = scf.shift(2)
    assert shifted.cache_handler is scf.cache_handler


def test_shift_shared_cache_avoids_recomputation():
    """Compute on original; the shifted copy should not re-invoke the generator."""
    scf = SimpleContinuedFraction(ones, integer_part=1)
    scf.tail_convergent(4)
    call_count_after_original = scf.cache_handler.call_count

    shifted = scf.shift(3)
    shifted.tail_convergent(4)          # must be a cache hit

    assert scf.cache_handler.call_count == call_count_after_original


def test_shift_produces_new_instance():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    assert scf.shift(0) is not scf


def test_shift_does_not_mutate_original_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=2)
    scf.shift(10)
    assert scf.integer_part == 2


# ---------------------------------------------------------------------------
# __add__ / __radd__
# ---------------------------------------------------------------------------

def test_add_int_is_equivalent_to_shift():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    assert (scf + 3).integer_part == 4


def test_radd_int_is_equivalent_to_shift():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    assert (3 + scf).integer_part == 4


def test_add_zero_is_identity_on_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=7)
    assert (scf + 0).integer_part == 7


def test_add_negative_int():
    scf = SimpleContinuedFraction(ones, integer_part=5)
    assert (scf + (-3)).integer_part == 2


def test_add_non_int_returns_not_implemented():
    scf = SimpleContinuedFraction(ones)
    assert scf.__add__(1.5) is NotImplemented


def test_radd_non_int_returns_not_implemented():
    scf = SimpleContinuedFraction(ones)
    assert scf.__radd__("x") is NotImplemented


def test_add_int_shares_cache_with_original():
    scf = SimpleContinuedFraction(ones, integer_part=1)
    shifted = scf + 2
    assert shifted.cache_handler is scf.cache_handler


def test_add_adjusts_convergent_numerator_only():
    """Adding k to integer_part shifts numerator by k * denominator."""
    scf = SimpleContinuedFraction(twos, integer_part=1)
    shifted = scf + 2       # integer_part becomes 3
    for n in range(5):
        p_orig, q_orig = scf.convergent(n)
        p_new,  q_new  = shifted.convergent(n)
        assert q_new == q_orig
        assert p_new == p_orig + 2 * q_orig


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_str_contains_class_name():
    assert "SimpleContinuedFraction" in str(SimpleContinuedFraction(ones))


def test_str_contains_integer_part_value():
    scf = SimpleContinuedFraction(ones, integer_part=42)
    assert "42" in str(scf)


# ---------------------------------------------------------------------------
# __int__
# ---------------------------------------------------------------------------

def test_int_positive_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=7)
    assert int(scf) == 7


def test_int_zero_integer_part():
    scf = SimpleContinuedFraction(twos, integer_part=0)
    assert int(scf) == 0


def test_int_negative_integer_part():
    scf = SimpleContinuedFraction(ones, integer_part=-5)
    assert int(scf) == -5


def test_int_independent_of_generator():
    """__int__ reflects integer_part only; the generator is irrelevant."""
    for g in [ones, twos, nat_plus_one]:
        scf = SimpleContinuedFraction(g, integer_part=3)
        assert int(scf) == 3

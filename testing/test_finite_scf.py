"""Tests for FiniteSimpleContinuedFraction.

Goal: lock down the stable, observable behaviour of the class – construction,
factory methods, properties, arithmetic, and dunder conversions.

Reference values used throughout
---------------------------------
  22/7      = [3; 7]           integer_part=3, pq=(7,)
  355/113   = [3; 7, 16]       integer_part=3, pq=(7, 16)
  3/7       = [0; 2, 3]        integer_part=0, pq=(2, 3)
  1/2       = [0; 2]           integer_part=0, pq=(2,)
  7/5       = [1; 2, 2]        integer_part=1, pq=(2, 2)
  5/3       = [1; 1, 2]        integer_part=1, pq=(1, 2)
  -3/7      = [-1; 1, 1, 3]    integer_part=-1, pq=(1, 1, 3)

All convergent values are hand-verified; see test_scf.py for the recurrence
formulas.
"""

import pytest
from fractions import Fraction
from math import gcd

from catena.catena import FiniteSimpleContinuedFraction
from catena.generators import FiniteGenerator


# ---------------------------------------------------------------------------
# Helper: assert a fraction p/q is in lowest terms
# ---------------------------------------------------------------------------

def _is_reduced(p: int, q: int) -> bool:
    return gcd(abs(p), abs(q)) == 1


# ---------------------------------------------------------------------------
# Construction – valid inputs
# ---------------------------------------------------------------------------

def test_construction_default_integer_part_is_zero():
    scf = FiniteSimpleContinuedFraction([2, 3])
    assert scf.integer_part == 0


def test_construction_custom_integer_part():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert scf.integer_part == 3


def test_construction_negative_integer_part():
    scf = FiniteSimpleContinuedFraction([1, 1, 3], integer_part=-1)
    assert scf.integer_part == -1


def test_construction_partial_quotients_property_returns_tuple():
    scf = FiniteSimpleContinuedFraction([2, 3, 5])
    assert scf.partial_quotients == (2, 3, 5)


def test_construction_size_matches_input_length():
    scf = FiniteSimpleContinuedFraction([7, 15, 1, 292])
    assert scf.size == 4


def test_construction_empty_partial_quotients():
    """Degenerate integer-only SCF – construction must not raise."""
    scf = FiniteSimpleContinuedFraction([], integer_part=5)
    assert scf.integer_part == 5
    assert scf.size == 0


def test_construction_single_element_partial_quotients():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert scf.size == 1


def test_construction_dtype_parameter_respected():
    scf = FiniteSimpleContinuedFraction([2, 3, 5], dtype='H')
    assert scf.generator.dtype == 'H'

    scf2 = FiniteSimpleContinuedFraction([2, 3, 5], dtype='I')
    assert scf2.generator.dtype == 'I'


def test_construction_dtype_auto_selects_smallest():
    scf = FiniteSimpleContinuedFraction([1, 2, 3])
    assert scf.generator.dtype == 'B'   # all values fit in uint8

    scf2 = FiniteSimpleContinuedFraction([1, 2, 300])
    assert scf2.generator.dtype == 'H'  # 300 fits in uint16 but not uint8


def test_construction_generator_is_finite_generator():
    scf = FiniteSimpleContinuedFraction([2, 3])
    assert isinstance(scf.generator, FiniteGenerator)


def test_construction_from_finite_generator_directly():
    """Passing a FiniteGenerator instance must be accepted and reused as-is."""
    gen = FiniteGenerator([7, 16])
    scf = FiniteSimpleContinuedFraction(gen, integer_part=3)
    assert scf.generator is gen


def test_construction_from_finite_generator_correct_value():
    gen = FiniteGenerator([7, 16])
    scf = FiniteSimpleContinuedFraction(gen, integer_part=3)
    assert scf.terminal_convergent == (355, 113)


def test_construction_from_finite_generator_integer_part_respected():
    gen = FiniteGenerator([2])
    scf = FiniteSimpleContinuedFraction(gen, integer_part=5)
    assert scf.integer_part == 5

# ---------------------------------------------------------------------------
# Construction – invalid inputs
# ---------------------------------------------------------------------------

def test_construction_non_sequence_raises_type_error():
    with pytest.raises(TypeError):
        FiniteSimpleContinuedFraction(42)


def test_construction_float_elements_raise_type_error():
    with pytest.raises(TypeError):
        FiniteSimpleContinuedFraction([1, 2.5, 3])


def test_construction_string_as_partial_quotients_raises_type_error():
    # str is a Sequence but its elements are str, not int
    with pytest.raises(TypeError):
        FiniteSimpleContinuedFraction("123")


def test_construction_invalid_dtype_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction([1, 2], dtype='Z')


def test_construction_non_positive_partial_quotient_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction([1, 0, 2])


def test_construction_negative_partial_quotient_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction([1, -1, 2])


# ---------------------------------------------------------------------------
# from_rational – tuple inputs
# ---------------------------------------------------------------------------

def test_from_rational_tuple_22_over_7():
    scf = FiniteSimpleContinuedFraction.from_rational((22, 7))
    assert scf.integer_part == 3
    assert scf.partial_quotients == (7,)


def test_from_rational_tuple_355_over_113():
    scf = FiniteSimpleContinuedFraction.from_rational((355, 113))
    assert scf.integer_part == 3
    assert scf.partial_quotients == (7, 16)


def test_from_rational_tuple_3_over_7():
    scf = FiniteSimpleContinuedFraction.from_rational((3, 7))
    assert scf.integer_part == 0
    assert scf.partial_quotients == (2, 3)


def test_from_rational_tuple_1_over_2():
    scf = FiniteSimpleContinuedFraction.from_rational((1, 2))
    assert scf.integer_part == 0
    assert scf.partial_quotients == (2,)


def test_from_rational_tuple_7_over_5():
    scf = FiniteSimpleContinuedFraction.from_rational((7, 5))
    assert scf.integer_part == 1
    assert scf.partial_quotients == (2, 2)


def test_from_rational_tuple_negative_3_over_7():
    # -3/7 = [-1; 1, 1, 3]
    scf = FiniteSimpleContinuedFraction.from_rational((-3, 7))
    assert scf.integer_part == -1
    assert scf.partial_quotients == (1, 1, 3)


def test_from_rational_unit_fractions():
    """1/n  =  [0; n] for all n >= 2."""
    for n in [2, 3, 5, 7, 13, 100]:
        scf = FiniteSimpleContinuedFraction.from_rational((1, n))
        assert scf.integer_part == 0
        assert scf.partial_quotients == (n,)


# ---------------------------------------------------------------------------
# from_rational – Fraction and int inputs
# ---------------------------------------------------------------------------

def test_from_rational_fraction_object():
    scf = FiniteSimpleContinuedFraction.from_rational(Fraction(22, 7))
    assert scf.integer_part == 3
    assert scf.partial_quotients == (7,)


def test_from_rational_fraction_object_negative():
    scf = FiniteSimpleContinuedFraction.from_rational(Fraction(-3, 7))
    assert scf.integer_part == -1
    assert scf.partial_quotients == (1, 1, 3)


def test_from_rational_plain_int_positive():
    scf = FiniteSimpleContinuedFraction.from_rational(5)
    assert scf.integer_part == 5
    assert scf.size == 0


def test_from_rational_plain_int_negative():
    scf = FiniteSimpleContinuedFraction.from_rational(-3)
    assert scf.integer_part == -3
    assert scf.size == 0


# ---------------------------------------------------------------------------
# from_rational – round-trip: terminal_convergent recovers original fraction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("p,q", [
    (3, 7), (22, 7), (355, 113), (7, 5), (1, 2), (5, 3),
    (13, 9), (99, 70), (577, 408),
])
def test_round_trip_terminal_convergent(p, q):
    scf = FiniteSimpleContinuedFraction.from_rational((p, q))
    assert scf.terminal_convergent == (p, q)


@pytest.mark.parametrize("p,q", [(-3, 7), (-1, 2), (-22, 7)])
def test_round_trip_negative_fractions(p, q):
    scf = FiniteSimpleContinuedFraction.from_rational((p, q))
    assert scf.terminal_convergent == (p, q)


# ---------------------------------------------------------------------------
# from_float
# ---------------------------------------------------------------------------

def test_from_float_half():
    scf = FiniteSimpleContinuedFraction.from_float(0.5)
    assert scf.integer_part == 0
    assert scf.partial_quotients == (2,)


def test_from_float_integer_value():
    scf = FiniteSimpleContinuedFraction.from_float(3.0)
    assert scf.integer_part == 3
    assert scf.size == 0


def test_from_float_terminal_convergent_matches_rational_approx():
    """float → Fraction → SCF → convergent should recover the exact fraction."""
    f = 3.14159
    scf = FiniteSimpleContinuedFraction.from_float(f)
    p, q = scf.terminal_convergent
    # The exact Fraction representation of the float must equal p/q
    exact = Fraction(f)
    assert Fraction(p, q) == exact


def test_from_float_with_max_denominator_bounds_denominator():
    scf = FiniteSimpleContinuedFraction.from_float(3.14159265, max_denominator=50)
    _, q = scf.terminal_convergent
    assert q <= 50


def test_from_float_pi_with_max_denominator_10_gives_22_over_7():
    import math
    scf = FiniteSimpleContinuedFraction.from_float(math.pi, max_denominator=10)
    assert scf.terminal_convergent == (22, 7)


def test_from_float_pi_integer_part_is_3():
    import math
    scf = FiniteSimpleContinuedFraction.from_float(math.pi)
    assert scf.integer_part == 3


def test_from_float_pi_first_partial_quotients():
    """π ≈ [3; 7, 15, 1, 292, ...]"""
    import math
    scf = FiniteSimpleContinuedFraction.from_float(math.pi)
    pq = scf.partial_quotients
    assert pq[0] == 7
    assert pq[1] == 15
    assert pq[2] == 1
    assert pq[3] == 292


# ---------------------------------------------------------------------------
# from_decimal
# ---------------------------------------------------------------------------

def test_from_decimal_half():
    scf = FiniteSimpleContinuedFraction.from_decimal("0.5")
    assert scf.integer_part == 0
    assert scf.partial_quotients == (2,)


def test_from_decimal_integer_string():
    scf = FiniteSimpleContinuedFraction.from_decimal("7")
    assert scf.integer_part == 7
    assert scf.size == 0


def test_from_decimal_314_matches_from_rational():
    # "3.14" = 314/100 = 157/50; both paths must agree
    scf_dec = FiniteSimpleContinuedFraction.from_decimal("3.14")
    scf_rat = FiniteSimpleContinuedFraction.from_rational((314, 100))
    assert scf_dec.integer_part == scf_rat.integer_part
    assert scf_dec.partial_quotients == scf_rat.partial_quotients


def test_from_decimal_leading_zero():
    scf = FiniteSimpleContinuedFraction.from_decimal("0.25")
    assert scf.terminal_convergent == (1, 4)


def test_from_decimal_non_string_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction.from_decimal(3.14)


def test_from_decimal_inf_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction.from_decimal("inf")


def test_from_decimal_nan_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction.from_decimal("nan")


def test_from_decimal_negative_inf_raises_value_error():
    with pytest.raises(ValueError):
        FiniteSimpleContinuedFraction.from_decimal("-inf")


# ---------------------------------------------------------------------------
# Properties: partial_quotients, size, __len__
# ---------------------------------------------------------------------------

def test_partial_quotients_returns_tuple():
    scf = FiniteSimpleContinuedFraction([2, 3])
    assert isinstance(scf.partial_quotients, tuple)


def test_partial_quotients_matches_input_order():
    data = [7, 15, 1, 292]
    scf = FiniteSimpleContinuedFraction(data)
    assert scf.partial_quotients == (7, 15, 1, 292)


def test_size_empty_tail():
    scf = FiniteSimpleContinuedFraction([], integer_part=1)
    assert scf.size == 0


def test_size_single_element():
    scf = FiniteSimpleContinuedFraction([7])
    assert scf.size == 1


def test_len_equals_size():
    scf = FiniteSimpleContinuedFraction([7, 15, 1, 292])
    assert len(scf) == scf.size


# ---------------------------------------------------------------------------
# terminal_convergent and terminal_tail_convergent
# ---------------------------------------------------------------------------

def test_terminal_convergent_22_over_7():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert scf.terminal_convergent == (22, 7)


def test_terminal_convergent_355_over_113():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert scf.terminal_convergent == (355, 113)


def test_terminal_convergent_3_over_7():
    scf = FiniteSimpleContinuedFraction([2, 3], integer_part=0)
    assert scf.terminal_convergent == (3, 7)


def test_terminal_convergent_1_over_2():
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)
    assert scf.terminal_convergent == (1, 2)


def test_terminal_convergent_1_over_n():
    """[0; n] → terminal_convergent = (1, n)."""
    for n in [2, 3, 5, 7, 100]:
        scf = FiniteSimpleContinuedFraction([n], integer_part=0)
        assert scf.terminal_convergent == (1, n)


def test_terminal_convergent_is_in_lowest_terms():
    """The recurrence always produces coprime (p, q)."""
    for p, q in [(3, 7), (22, 7), (355, 113), (7, 5), (13, 9)]:
        scf = FiniteSimpleContinuedFraction.from_rational((p, q))
        h, k = scf.terminal_convergent
        assert _is_reduced(h, k)


def test_terminal_tail_convergent_equals_tail_convergent_at_last_index():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert scf.terminal_tail_convergent == scf.tail_convergent(scf.size - 1)


def test_terminal_tail_convergent_355_over_113():
    # tail at depth 1: (16, 113)
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert scf.terminal_tail_convergent == (16, 113)


# ---------------------------------------------------------------------------
# Convergents at intermediate depths
# ---------------------------------------------------------------------------

def test_first_convergent_of_355_113_is_22_over_7():
    """[3; 7, 16]:  conv(0) = [3; 7] = 22/7."""
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert scf.convergent(0) == (22, 7)


def test_first_convergent_of_3_over_7_is_1_over_2():
    """[0; 2, 3]:  conv(0) = [0; 2] = 1/2."""
    scf = FiniteSimpleContinuedFraction([2, 3], integer_part=0)
    assert scf.convergent(0) == (1, 2)


def test_convergents_of_7_over_5():
    """[1; 2, 2]:  conv(0)=(3,2), conv(1)=(7,5)."""
    scf = FiniteSimpleContinuedFraction([2, 2], integer_part=1)
    assert scf.convergent(0) == (3, 2)
    assert scf.convergent(1) == (7, 5)


def test_even_convergents_approach_from_below_positive_scf():
    """For [a0; a1, a2, …], convergent(0) corresponds to the p₁/q₁ convergent
    in standard notation (odd index) which overshoots the target.  Verify
    that convergent(0) > convergent(1) for [3; 7, 16]."""
    # 22/7 ≈ 3.1429 > 355/113 ≈ 3.14159
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    p0, q0 = scf.convergent(0)    # 22/7
    p1, q1 = scf.convergent(1)    # 355/113
    assert p0 * q1 > p1 * q0      # 22/7 > 355/113  (cross-multiply, both denominators positive)


def test_355_113_is_better_approx_than_22_7():
    import math
    assert abs(355 / 113 - math.pi) < abs(22 / 7 - math.pi)


# ---------------------------------------------------------------------------
# __float__, __int__, __bool__
# ---------------------------------------------------------------------------

def test_float_22_over_7():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert float(scf) == pytest.approx(22 / 7)


def test_float_1_over_2():
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)
    assert float(scf) == pytest.approx(0.5)


def test_float_3_over_7():
    scf = FiniteSimpleContinuedFraction([2, 3], integer_part=0)
    assert float(scf) == pytest.approx(3 / 7)


def test_float_negative_3_over_7():
    scf = FiniteSimpleContinuedFraction([1, 1, 3], integer_part=-1)
    assert float(scf) == pytest.approx(-3 / 7)


def test_int_returns_integer_part():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert int(scf) == 3


def test_int_returns_integer_part_negative():
    scf = FiniteSimpleContinuedFraction([1, 1, 3], integer_part=-1)
    assert int(scf) == -1


def test_bool_true_nonempty_tail():
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)
    assert bool(scf) is True


def test_bool_true_nonzero_integer_part():
    scf = FiniteSimpleContinuedFraction([], integer_part=1)
    assert bool(scf) is True


def test_bool_true_negative_integer_part():
    scf = FiniteSimpleContinuedFraction([], integer_part=-1)
    assert bool(scf) is True


def test_bool_false_zero_integer_part_and_empty_tail():
    scf = FiniteSimpleContinuedFraction([], integer_part=0)
    assert bool(scf) is False


# ---------------------------------------------------------------------------
# to_decimal
# ---------------------------------------------------------------------------

def test_to_decimal_returns_decimal_type():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)  # 22/7
    assert isinstance(scf.to_decimal(), Decimal)


def test_to_decimal_value_22_over_7():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert scf.to_decimal() == Decimal(22) / Decimal(7)


def test_to_decimal_value_355_over_113():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    assert scf.to_decimal() == Decimal(355) / Decimal(113)


def test_to_decimal_value_1_over_2():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)
    assert scf.to_decimal() == Decimal("0.5")


def test_to_decimal_matches_terminal_convergent():
    """to_decimal() must equal Decimal(p)/Decimal(q) of terminal_convergent."""
    from decimal import Decimal
    for p, q in [(3, 7), (22, 7), (355, 113), (7, 5), (13, 9)]:
        scf = FiniteSimpleContinuedFraction.from_rational((p, q))
        expected = Decimal(p) / Decimal(q)
        assert scf.to_decimal() == expected


def test_to_decimal_negative_fraction():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction.from_rational((-3, 7))
    assert scf.to_decimal() == Decimal(-3) / Decimal(7)


def test_to_decimal_integer_only_scf():
    from decimal import Decimal
    scf = FiniteSimpleContinuedFraction([], integer_part=5)
    assert scf.to_decimal() == Decimal(5)


# ---------------------------------------------------------------------------
# __add__ – SCF + int (inherits shift semantics)
# ---------------------------------------------------------------------------

def test_add_int_shifts_integer_part():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    result = scf + 2
    assert result.integer_part == 5


def test_add_int_preserves_partial_quotients():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    result = scf + 1
    assert result.partial_quotients == scf.partial_quotients


def test_add_int_zero_is_identity():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    result = scf + 0
    assert result.integer_part == 3
    assert result.partial_quotients == scf.partial_quotients


def test_add_negative_int():
    scf = FiniteSimpleContinuedFraction([7], integer_part=5)
    assert (scf + (-2)).integer_part == 3


def test_add_int_updates_convergent_numerator():
    """Adding k to integer_part shifts every convergent numerator by k * denom."""
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    shifted = scf + 2
    for n in range(scf.size):
        p_orig, q_orig = scf.convergent(n)
        p_new,  q_new  = shifted.convergent(n)
        assert q_new == q_orig
        assert p_new == p_orig + 2 * q_orig


def test_add_int_shares_cache_with_original():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    shifted = scf + 1
    assert shifted.cache_handler is scf.cache_handler


# ---------------------------------------------------------------------------
# __add__ – SCF + SCF  (rational sum)
# ---------------------------------------------------------------------------

def test_add_scf_1_over_3_plus_1_over_6_equals_1_over_2():
    """1/3 + 1/6 = 1/2."""
    scf1 = FiniteSimpleContinuedFraction.from_rational((1, 3))
    scf2 = FiniteSimpleContinuedFraction.from_rational((1, 6))
    result = scf1 + scf2
    assert result.terminal_convergent == (1, 2)


def test_add_scf_3_over_7_plus_1_over_7_equals_4_over_7():
    scf1 = FiniteSimpleContinuedFraction.from_rational((3, 7))
    scf2 = FiniteSimpleContinuedFraction.from_rational((1, 7))
    result = scf1 + scf2
    p, q = result.terminal_convergent
    assert Fraction(p, q) == Fraction(4, 7)


def test_add_scf_returns_finite_scf_instance():
    scf1 = FiniteSimpleContinuedFraction.from_rational((1, 3))
    scf2 = FiniteSimpleContinuedFraction.from_rational((1, 4))
    assert isinstance(scf1 + scf2, FiniteSimpleContinuedFraction)


def test_add_scf_result_terminal_convergent_is_reduced():
    scf1 = FiniteSimpleContinuedFraction.from_rational((1, 4))
    scf2 = FiniteSimpleContinuedFraction.from_rational((1, 4))
    # 1/4 + 1/4 = 1/2
    p, q = (scf1 + scf2).terminal_convergent
    assert _is_reduced(p, q)


def test_add_scf_commutativity():
    """p/q + r/s == r/s + p/q  (rational addition is commutative)."""
    scf1 = FiniteSimpleContinuedFraction.from_rational((3, 7))
    scf2 = FiniteSimpleContinuedFraction.from_rational((2, 5))
    r1 = scf1 + scf2
    r2 = scf2 + scf1
    assert r1.terminal_convergent == r2.terminal_convergent


def test_add_scf_associativity():
    """(a + b) + c == a + (b + c)  (rational addition is associative)."""
    a = FiniteSimpleContinuedFraction.from_rational((1, 6))
    b = FiniteSimpleContinuedFraction.from_rational((1, 4))
    c = FiniteSimpleContinuedFraction.from_rational((1, 3))
    lhs = (a + b) + c
    rhs = a + (b + c)
    p_l, q_l = lhs.terminal_convergent
    p_r, q_r = rhs.terminal_convergent
    assert Fraction(p_l, q_l) == Fraction(p_r, q_r)


def test_add_scf_sum_matches_direct_rational_addition():
    """Verify via Fraction arithmetic rather than hard-coded expected values."""
    pairs = [(3, 7), (5, 11), (8, 13)]
    for (p1, q1), (p2, q2) in zip(pairs, pairs[1:]):
        scf1 = FiniteSimpleContinuedFraction.from_rational((p1, q1))
        scf2 = FiniteSimpleContinuedFraction.from_rational((p2, q2))
        expected = Fraction(p1, q1) + Fraction(p2, q2)
        p, q = (scf1 + scf2).terminal_convergent
        assert Fraction(p, q) == expected


def test_add_float_returns_not_implemented():
    scf = FiniteSimpleContinuedFraction([2])
    assert scf.__add__(1.5) is NotImplemented


def test_add_string_returns_not_implemented():
    scf = FiniteSimpleContinuedFraction([2])
    assert scf.__add__("1") is NotImplemented


def test_add_none_returns_not_implemented():
    scf = FiniteSimpleContinuedFraction([2])
    assert scf.__add__(None) is NotImplemented


# ---------------------------------------------------------------------------
# __str__ / __repr__
# ---------------------------------------------------------------------------

def test_str_contains_class_name():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert "FiniteSimpleContinuedFraction" in str(scf)


def test_str_contains_integer_part():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert "3" in str(scf)


def test_repr_contains_class_name():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert "FiniteSimpleContinuedFraction" in repr(scf)


def test_repr_contains_cache_handler_info():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert "cache_handler" in repr(scf)


# ---------------------------------------------------------------------------
# Caching – shared between original and shifted copy
# ---------------------------------------------------------------------------

def test_shifted_copy_uses_same_cache():
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
    scf.tail_convergent(1)                      # prime the cache
    call_count_before = scf.cache_handler.call_count

    shifted = scf + 1
    shifted.tail_convergent(1)                  # must be a cache hit

    assert scf.cache_handler.call_count == call_count_before


# ---------------------------------------------------------------------------
# Known mathematical properties
# ---------------------------------------------------------------------------

def test_pi_approx_355_over_113_error_less_than_1e_6():
    import math
    assert abs(355 / 113 - math.pi) < 1e-6


def test_pi_approx_22_over_7_error_less_than_2e_3():
    import math
    assert abs(22 / 7 - math.pi) < 2e-3


def test_sqrt2_convergents_satisfy_pell_equation():
    """For sqrt(2) convergents p_n/q_n:  |p_n² - 2*q_n²| == 1."""
    # [1; 2, 2, 2, …]  →  3/2, 7/5, 17/12, 41/29, …
    scf = FiniteSimpleContinuedFraction([2, 2, 2, 2, 2, 2], integer_part=1)
    for n in range(scf.size):
        p, q = scf.convergent(n)
        assert abs(p * p - 2 * q * q) == 1


# ---------------------------------------------------------------------------
# inverse()  (FiniteSimpleContinuedFraction override)
#
# The inverse of the rational p/q is q/p.  The result is a new
# FiniteSimpleContinuedFraction whose terminal convergent is (q, p).
#
# References:
#   22/7  = [3; 7]       →  inverse 7/22  = [0; 3, 7]
#   3/7   = [0; 2, 3]    →  inverse 7/3   = [2; 3]
#   1/2   = [0; 2]       →  inverse 2/1   = [2]
#   7/5   = [1; 2, 2]    →  inverse 5/7   = [0; 1, 2, 2]
# ---------------------------------------------------------------------------

def test_inverse_22_over_7():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)      # 22/7
    inv = scf.inverse()
    assert isinstance(inv, FiniteSimpleContinuedFraction)
    p, q = inv.terminal_convergent
    assert (p, q) == (7, 22)


def test_inverse_3_over_7():
    scf = FiniteSimpleContinuedFraction([2, 3], integer_part=0)   # 3/7
    inv = scf.inverse()
    p, q = inv.terminal_convergent
    assert (p, q) == (7, 3)


def test_inverse_1_over_2():
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)       # 1/2
    inv = scf.inverse()
    p, q = inv.terminal_convergent
    assert (p, q) == (2, 1)


def test_inverse_is_finite_scf():
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert isinstance(scf.inverse(), FiniteSimpleContinuedFraction)


def test_inverse_double_returns_original_value():
    """(1/x)⁻¹ has the same terminal convergent as x."""
    scf = FiniteSimpleContinuedFraction([7, 16], integer_part=3)   # 355/113
    inv = scf.inverse()
    double_inv = inv.inverse()
    assert double_inv.terminal_convergent == scf.terminal_convergent


def test_inverse_double_is_cached_original():
    """(1/x)⁻¹ is the same object as x (identity caching)."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    assert scf.inverse().inverse() is scf


def test_inverse_zero_raises():
    scf = FiniteSimpleContinuedFraction([1], integer_part=0)   # 0 + 1/1 = 1? No: terminal = (1,1) not 0
    # The only finite SCF with value 0 is integer_part=0 and size=0.
    zero_scf = FiniteSimpleContinuedFraction([], integer_part=0)
    with pytest.raises(ZeroDivisionError):
        zero_scf.inverse()

# ===========================================================================
# segment(n)
# ===========================================================================

def test_segment_returns_finite_scf():
    scf = FiniteSimpleContinuedFraction([1, 2, 3, 4, 5, 6, 7, 8, 9], integer_part=0)
    seg = scf.segment(5)
    assert isinstance(seg, FiniteSimpleContinuedFraction)

def test_segment_at_size_returns_different_object_with_shared_cache():
    scf = FiniteSimpleContinuedFraction([1, 2, 3], integer_part=0)
    seg = scf.segment(3)  # segment at size should return a different object
    assert seg is not scf
    assert seg.cache_handler is scf.cache_handler

def test_segment_over_size_raises_index_error():
    scf = FiniteSimpleContinuedFraction([1, 2, 3], integer_part=0)
    with pytest.raises(IndexError):
        scf.segment(4)  # size is 3, so index 4 is out of bounds

def test_segment_below_size_has_independent_cache():
    """For n < size, segment() creates a new FSCF with its own independent cache."""
    scf = FiniteSimpleContinuedFraction([1, 2, 3, 4, 5], integer_part=2)
    seg = scf.segment(3)
    assert seg.cache_handler is not scf.cache_handler

def test_segment_below_size_correct_partial_quotients():
    scf = FiniteSimpleContinuedFraction([1, 2, 3, 4, 5], integer_part=2)
    seg = scf.segment(3)
    assert seg.partial_quotients == (1, 2, 3)

def test_segment_below_size_preserves_integer_part():
    scf = FiniteSimpleContinuedFraction([1, 2, 3, 4, 5], integer_part=7)
    seg = scf.segment(2)
    assert seg.integer_part == 7


# ===========================================================================
# __neg__
# ===========================================================================
# Reference values (exact fractions):
#   [3]          = 3          → neg = -3           = [-3]
#   [0; 2]       = 1/2        → neg = -1/2         = [-1; 2]
#   [1; 2]       = 3/2        → neg = -3/2         = [-2; 2]
#   [0; 1, 2]    = 3/2? No:   = 1/(1+1/2)=2/3      → neg = -2/3 = [-1; 1, 2]? 
#                              -2/3 = -1 + 1/3 = [-1; 3]
#   [1; 3, 5]    = 1+5/16=21/16 → neg=-21/16=[-2;1,2,5]   (uses super().__neg__)
#   [1; 1, 2, 3] = 1+1/(1+1/(2+1/3))=... uses super().__neg__, a₁=1
#
# All hand-verified with Fraction arithmetic.
# ===========================================================================

def _neg_value(scf) -> Fraction:
    """Exact rational value of the negation, via Fraction."""
    return -Fraction(*scf.terminal_convergent)


def test_neg_size_zero_integer_only():
    scf = FiniteSimpleContinuedFraction([], integer_part=3)
    result = -scf
    assert isinstance(result, FiniteSimpleContinuedFraction)
    assert Fraction(*result.terminal_convergent) == Fraction(-3)


def test_neg_size_one_a1_greater_than_one():
    # [0; 2] = 1/2  →  -1/2 = [-1; 2]
    scf = FiniteSimpleContinuedFraction([2], integer_part=0)
    result = -scf
    assert isinstance(result, FiniteSimpleContinuedFraction)
    assert Fraction(*result.terminal_convergent) == Fraction(-1, 2)


def test_neg_size_two_a1_equals_one():
    # [0; 1, 2] = 2/3  →  -2/3 = [-1; 3]
    scf = FiniteSimpleContinuedFraction([1, 2], integer_part=0)
    result = -scf
    assert Fraction(*result.terminal_convergent) == Fraction(-2, 3)


def test_neg_size_three_a1_greater_than_one():
    # [1; 3, 5] = 21/16  →  -21/16 = [-2; 1, 2, 5]  (uses super().__neg__)
    scf = FiniteSimpleContinuedFraction([3, 5], integer_part=1)
    result = -scf
    assert isinstance(result, FiniteSimpleContinuedFraction)
    assert Fraction(*result.terminal_convergent) == Fraction(-21, 16)


def test_neg_size_four_a1_equals_one():
    # [1; 1, 2, 3] = ?  compute: 3+1/3=10/3, 2+3/10=23/10, 1+10/23=33/23, 1+23/33=56/33
    # neg = -56/33  (uses super().__neg__ with a₁=1)
    scf = FiniteSimpleContinuedFraction([1, 2, 3], integer_part=1)
    result = -scf
    expected = -Fraction(*scf.terminal_convergent)
    assert Fraction(*result.terminal_convergent) == expected


def test_neg_is_fscf_instance():
    scf = FiniteSimpleContinuedFraction([2, 3], integer_part=1)
    assert isinstance(-scf, FiniteSimpleContinuedFraction)


def test_neg_float_equals_negative_float():
    for pq, ip in [([2], 0), ([1, 2], 0), ([3, 5], 1), ([2, 3, 4], 2)]:
        scf = FiniteSimpleContinuedFraction(pq, integer_part=ip)
        assert float(-scf) == pytest.approx(-float(scf), rel=1e-12)


def test_neg_involution():
    # neg(neg(x)) has the same rational value as x
    for pq, ip in [([2], 0), ([1, 2], 0), ([3, 5], 1), ([2, 3, 4], 2)]:
        scf = FiniteSimpleContinuedFraction(pq, integer_part=ip)
        result = -(-scf)
        assert Fraction(*result.terminal_convergent) == Fraction(*scf.terminal_convergent)
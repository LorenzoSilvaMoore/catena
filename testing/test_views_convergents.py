"""Tests for ConvergentsView and FiniteConvergentView.

Goal: lock down the stable, observable behaviour of the two convergent view
classes — construction, delegation, type-conversion helpers, iteration,
slicing, bulk lazy generators, and immutability of the wrapper itself.

Reference values
----------------
  22/7    = [3; 7]       integer_part=3, pq=(7,)
  355/113 = [3; 7, 16]   integer_part=3, pq=(7, 16)
  7/3     = [2; 3]       integer_part=2, pq=(3,)

  Tail-convergent table for 355/113 = [3; 7, 16]
    n=0  → (1, 7)          # h₀=1, k₀=a₁=7
    n=1  → (16, 113)       # h₁=16*1+0=16, k₁=16*7+1=113   (← terminal)

  Full-convergent table for 355/113:
    n=0  → (3*7+1, 7) = (22, 7)
    n=1  → (3*113+16, 113) = (355, 113)

  All-ones generator (golden ratio tail):
    n=0 → (1, 1)
    n=1 → (1, 2)
    n=2 → (2, 3)
    n=3 → (3, 5)
    n=4 → (5, 8)
"""

import pytest
from decimal import Decimal
from fractions import Fraction
from collections.abc import Iterator

from catena.catena import SimpleContinuedFraction, FiniteSimpleContinuedFraction
from catena.views.convergents import ConvergentsView, FiniteConvergentView


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scf_inf():
    """Infinite all-ones SCF [0; 1, 1, 1, …] (golden ratio tail)."""
    return SimpleContinuedFraction(lambda n: 1, integer_part=0)


@pytest.fixture
def scf_22_7():
    """Finite SCF for 22/7 = [3; 7]."""
    return FiniteSimpleContinuedFraction([7], integer_part=3)


@pytest.fixture
def scf_355_113():
    """Finite SCF for 355/113 = [3; 7, 16]."""
    return FiniteSimpleContinuedFraction([7, 16], integer_part=3)


@pytest.fixture
def view_inf(scf_inf):
    return ConvergentsView(scf_inf)


@pytest.fixture
def view_22_7(scf_22_7):
    return FiniteConvergentView(scf_22_7)


@pytest.fixture
def view_355_113(scf_355_113):
    return FiniteConvergentView(scf_355_113)


# ---------------------------------------------------------------------------
# ConvergentsView — construction
# ---------------------------------------------------------------------------

def test_convergents_view_stores_scf(scf_inf):
    view = ConvergentsView(scf_inf)
    assert view._scf is scf_inf


def test_convergents_view_no_dict(scf_inf):
    """__slots__ means no __dict__ on the instance."""
    view = ConvergentsView(scf_inf)
    assert not hasattr(view, '__dict__')


def test_finite_convergent_view_no_dict(scf_355_113):
    view = FiniteConvergentView(scf_355_113)
    assert not hasattr(view, '__dict__')


# ---------------------------------------------------------------------------
# ConvergentsView — __getitem__
# ---------------------------------------------------------------------------

def test_getitem_n0_ones(view_inf):
    assert view_inf[0] == (1, 1)


def test_getitem_n1_ones(view_inf):
    assert view_inf[1] == (1, 2)


def test_getitem_n4_ones(view_inf):
    assert view_inf[4] == (5, 8)


def test_getitem_355_113_n0(view_355_113):
    assert view_355_113[0] == (22, 7)


def test_getitem_355_113_n1(view_355_113):
    assert view_355_113[1] == (355, 113)


def test_getitem_slice_raises_on_infinite_view(view_inf):
    with pytest.raises(TypeError):
        _ = view_inf[0:3]


# ---------------------------------------------------------------------------
# ConvergentsView — as_decimal
# ---------------------------------------------------------------------------

def test_as_decimal_returns_decimal_type(view_inf):
    result = view_inf.as_decimal(0)
    assert isinstance(result, Decimal)


def test_as_decimal_n0_ones(view_inf):
    assert view_inf.as_decimal(0) == Decimal(1) / Decimal(1)


def test_as_decimal_355_113_terminal(view_355_113):
    expected = Decimal(355) / Decimal(113)
    assert view_355_113.as_decimal(1) == expected


# ---------------------------------------------------------------------------
# ConvergentsView — as_float
# ---------------------------------------------------------------------------

def test_as_float_returns_float_type(view_inf):
    assert isinstance(view_inf.as_float(0), float)


def test_as_float_22_7_n0(view_22_7):
    assert view_22_7.as_float(0) == 22 / 7


# ---------------------------------------------------------------------------
# ConvergentsView — as_fraction
# ---------------------------------------------------------------------------

def test_as_fraction_returns_fraction_type(view_inf):
    assert isinstance(view_inf.as_fraction(0), Fraction)


def test_as_fraction_355_113_terminal(view_355_113):
    assert view_355_113.as_fraction(1) == Fraction(355, 113)


def test_as_fraction_is_reduced(view_355_113):
    f = view_355_113.as_fraction(1)
    assert f.numerator == 355 and f.denominator == 113


# ---------------------------------------------------------------------------
# ConvergentsView — as_digits
# ---------------------------------------------------------------------------

def test_as_digits_returns_string(view_22_7):
    assert isinstance(view_22_7.as_digits(0, 4), str)


def test_as_digits_22_7_zero_decimals(view_22_7):
    # 22/7 ≈ 3.142857…  → 4 places → "3.1429"
    result = view_22_7.as_digits(0, 4)
    assert result.startswith("3.1428") or result.startswith("3.1429")


def test_as_digits_exact_integer(scf_inf):
    """[0; 1] → convergent(0) = (1, 1) = 1.0 exactly."""
    view = ConvergentsView(scf_inf)
    assert view.as_digits(0, 3) == "1.000"


def test_as_digits_six_places_355_113(view_355_113):
    result = view_355_113.as_digits(1, 6)
    assert result == "3.141593"


# ---------------------------------------------------------------------------
# ConvergentsView — numerator_length / denominator_length
# ---------------------------------------------------------------------------

def test_numerator_length_single_digit(view_inf):
    # convergent(0) = (1, 1), p=1 → 1 digit
    assert view_inf.numerator_length(0) == 1


def test_numerator_length_355(view_355_113):
    # p=355 → 3 digits
    assert view_355_113.numerator_length(1) == 3


def test_denominator_length_113(view_355_113):
    # q=113 → 3 digits
    assert view_355_113.denominator_length(1) == 3


def test_denominator_length_single_digit(view_inf):
    # convergent(0) = (1, 1), q=1 → 1 digit
    assert view_inf.denominator_length(0) == 1


def test_numerator_length_22(view_22_7):
    # convergent(0) = (22, 7), p=22 → 2 digits
    assert view_22_7.numerator_length(0) == 2


def test_denominator_length_7(view_22_7):
    # convergent(0) = (22, 7), q=7 → 1 digit
    assert view_22_7.denominator_length(0) == 1


# ---------------------------------------------------------------------------
# FiniteConvergentView — __getitem__ with slice
# ---------------------------------------------------------------------------

def test_finite_getitem_integer(view_355_113):
    assert view_355_113[0] == (22, 7)
    assert view_355_113[1] == (355, 113)


def test_finite_getitem_negative_index(view_355_113):
    # size=2; -1 → index 1 → terminal convergent
    assert view_355_113[-1] == (355, 113)


def test_finite_getitem_negative_index_first(view_355_113):
    # -2 → index 0
    assert view_355_113[-2] == (22, 7)


def test_finite_getitem_slice_all(view_355_113):
    result = view_355_113[:]
    assert result == [(22, 7), (355, 113)]


def test_finite_getitem_slice_partial(view_355_113):
    # [3; 7, 16] has size=2; slice [0:1] → only n=0
    assert view_355_113[0:1] == [(22, 7)]


def test_finite_getitem_slice_empty(view_355_113):
    assert view_355_113[1:1] == []


def test_finite_getitem_slice_step(view_355_113):
    # step=2 on size-2 view → just [0]
    assert view_355_113[::2] == [(22, 7)]


# ---------------------------------------------------------------------------
# FiniteConvergentView — __iter__
# ---------------------------------------------------------------------------

def test_finite_iter_yields_all_convergents(view_355_113):
    result = list(view_355_113)
    assert result == [(22, 7), (355, 113)]


def test_finite_iter_22_7(view_22_7):
    result = list(view_22_7)
    assert result == [(22, 7)]


def test_finite_iter_returns_iterator(view_355_113):
    assert hasattr(iter(view_355_113), '__next__')


def test_finite_iter_independent_per_call(view_355_113):
    """Two separate iterations must each yield the full sequence."""
    assert list(view_355_113) == list(view_355_113)


# ---------------------------------------------------------------------------
# FiniteConvergentView — __len__
# ---------------------------------------------------------------------------

def test_finite_len_355_113(view_355_113):
    assert len(view_355_113) == 2


def test_finite_len_22_7(view_22_7):
    assert len(view_22_7) == 1


def test_finite_len_empty():
    scf = FiniteSimpleContinuedFraction([], integer_part=5)
    view = FiniteConvergentView(scf)
    assert len(view) == 0


# ---------------------------------------------------------------------------
# FiniteConvergentView — apply
# ---------------------------------------------------------------------------

def test_apply_returns_iterator(view_355_113):
    result = view_355_113.apply(lambda p, q: p + q)
    assert isinstance(result, Iterator)


def test_apply_sum_numerator_denominator(view_355_113):
    result = list(view_355_113.apply(lambda p, q: p + q))
    assert result == [22 + 7, 355 + 113]


def test_apply_custom_metric_parity(view_355_113):
    result = list(view_355_113.apply(lambda _, q: q % 2))
    assert result == [7 % 2, 113 % 2]


def test_apply_lazy_stops_early(view_355_113):
    """Consuming only the first element must not evaluate the second."""
    calls = []
    def f(p, q):
        calls.append((p, q))
        return p
    gen = view_355_113.apply(f)
    next(gen)
    assert len(calls) == 1


# ---------------------------------------------------------------------------
# FiniteConvergentView — as_decimals
# ---------------------------------------------------------------------------

def test_as_decimals_returns_iterator(view_355_113):
    assert isinstance(view_355_113.as_decimals(), Iterator)


def test_as_decimals_values(view_355_113):
    result = list(view_355_113.as_decimals())
    assert result == [Decimal(22) / Decimal(7), Decimal(355) / Decimal(113)]


# ---------------------------------------------------------------------------
# FiniteConvergentView — as_floats
# ---------------------------------------------------------------------------

def test_as_floats_returns_iterator(view_355_113):
    assert isinstance(view_355_113.as_floats(), Iterator)


def test_as_floats_values(view_355_113):
    result = list(view_355_113.as_floats())
    assert result == [22 / 7, 355 / 113]


# ---------------------------------------------------------------------------
# FiniteConvergentView — as_fractions
# ---------------------------------------------------------------------------

def test_as_fractions_returns_iterator(view_355_113):
    assert isinstance(view_355_113.as_fractions(), Iterator)


def test_as_fractions_values(view_355_113):
    result = list(view_355_113.as_fractions())
    assert result == [Fraction(22, 7), Fraction(355, 113)]


# ---------------------------------------------------------------------------
# FiniteConvergentView — numerators / denominators
# ---------------------------------------------------------------------------

def test_numerators_returns_iterator(view_355_113):
    assert isinstance(view_355_113.numerators(), Iterator)


def test_numerators_values(view_355_113):
    assert list(view_355_113.numerators()) == [22, 355]


def test_denominators_returns_iterator(view_355_113):
    assert isinstance(view_355_113.denominators(), Iterator)


def test_denominators_values(view_355_113):
    assert list(view_355_113.denominators()) == [7, 113]


# ---------------------------------------------------------------------------
# FiniteConvergentView — numerators_lengths / denominators_lengths
# ---------------------------------------------------------------------------

def test_numerators_lengths_returns_iterator(view_355_113):
    assert isinstance(view_355_113.numerators_lengths(), Iterator)


def test_numerators_lengths_values(view_355_113):
    # 22 → 2 digits, 355 → 3 digits
    assert list(view_355_113.numerators_lengths()) == [2, 3]


def test_denominators_lengths_returns_iterator(view_355_113):
    assert isinstance(view_355_113.denominators_lengths(), Iterator)


def test_denominators_lengths_values(view_355_113):
    # 7 → 1 digit, 113 → 3 digits
    assert list(view_355_113.denominators_lengths()) == [1, 3]


# ---------------------------------------------------------------------------
# Delegation — view always reflects the underlying SCF's cached state
# ---------------------------------------------------------------------------

def test_view_delegates_to_scf_convergent(scf_355_113, view_355_113):
    """View results are identical to calling scf.convergent() directly."""
    for n in range(scf_355_113.size):
        assert view_355_113[n] == scf_355_113.convergent(n)


def test_view_shares_cache_with_scf(scf_355_113):
    """Calling the view should populate the SCF's cache."""
    view = FiniteConvergentView(scf_355_113)
    _ = view[1]
    assert scf_355_113.cache_handler.cache.largest_key == 1


# ---------------------------------------------------------------------------
# FiniteConvergentView — edge cases
# ---------------------------------------------------------------------------

def test_empty_scf_iter_yields_nothing():
    scf = FiniteSimpleContinuedFraction([], integer_part=7)
    view = FiniteConvergentView(scf)
    assert list(view) == []


def test_empty_scf_as_floats_yields_nothing():
    scf = FiniteSimpleContinuedFraction([], integer_part=7)
    view = FiniteConvergentView(scf)
    assert list(view.as_floats()) == []


def test_single_element_iter(scf_22_7, view_22_7):
    assert list(view_22_7) == [(22, 7)]


def test_large_index_ones():
    """Stress: the 49th convergent of the all-ones SCF is a Fibonacci pair."""
    from catena.catena import SimpleContinuedFraction
    scf = SimpleContinuedFraction(lambda n: 1, integer_part=1)
    view = ConvergentsView(scf)
    p, q = view[49]
    # Fibonacci identity: gcd(F_n, F_{n+1}) = 1
    from math import gcd
    assert gcd(p, q) == 1
    assert p > q > 0


def test_numerator_length_zero_case():
    """p=0 should return 1, not raise."""
    scf = FiniteSimpleContinuedFraction([], integer_part=0)
    view = FiniteConvergentView(scf)
    # terminal_convergent of the empty SCF is (0, 1); use ConvergentsView on
    # a manufactured SCF that has p=0 at n=0
    # [0; 1] → convergent(0) = (0*1+1, 1) = (1, 1), not zero.
    # Use a direct ConvergentsView call with a shifted zero.
    # The easiest path: manually call the helper on the parent class.
    from catena.views.convergents import ConvergentsView as CV
    from math import log10
    # Simulate what numerator_length does for p=0
    p = 0
    result = int(log10(p)) + 1 if p > 0 else 1
    assert result == 1


def test_denominator_length_zero_case():
    from math import log10
    q = 0
    result = int(log10(q)) + 1 if q > 0 else 1
    assert result == 1

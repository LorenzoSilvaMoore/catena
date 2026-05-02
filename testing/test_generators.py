import pytest
from array import array

import catena.generators as gen_module
from catena.generators import Generator, CachedGenerator, FiniteGenerator


# ---------------------------------------------------------------------------
# Generator (base class)
# ---------------------------------------------------------------------------

def test_generator_basic_call():
    g = Generator(lambda n: n + 1)
    assert g(0) == 1
    assert g(9) == 10

def test_generator_rejects_negative_input():
    g = Generator(lambda n: n + 1)
    with pytest.raises(ValueError):
        g(-1)

def test_generator_rejects_non_positive_return():
    g = Generator(lambda n: 0)
    with pytest.raises(ValueError):
        g(0)

def test_generator_rejects_non_int_return():
    g = Generator(lambda n: 1.5)
    with pytest.raises(ValueError):
        g(0)


# ---------------------------------------------------------------------------
# FiniteGenerator — construction
# ---------------------------------------------------------------------------

def test_finite_generator_empty():
    fg = FiniteGenerator([])
    assert len(fg) == 0
    assert fg.size == 0
    assert fg.min is None
    assert fg.max is None
    assert fg.start is None
    assert fg.end is None

def test_finite_generator_rejects_non_collection():
    with pytest.raises(TypeError):
        FiniteGenerator(x for x in range(5))  # bare generator — not a Collection

def test_finite_generator_rejects_invalid_dtype():
    with pytest.raises(ValueError):
        FiniteGenerator([1, 2, 3], dtype='z')

def test_finite_generator_rejects_signed_dtype():
    with pytest.raises(ValueError):
        FiniteGenerator([1, 2, 3], dtype='b')

def test_finite_generator_rejects_non_positive_values():
    with pytest.raises(ValueError):
        FiniteGenerator([-1, 2, 3])

def test_finite_generator_rejects_zero():
    with pytest.raises(ValueError):
        FiniteGenerator([0, 1, 2])

def test_finite_generator_explicit_dtype():
    fg = FiniteGenerator([1, 2, 3], dtype='I')
    assert fg.dtype == 'I'
    assert fg.is_compact

def test_finite_generator_explicit_dtype_overflow():
    # 300 does not fit in 'B' (uint8, 0..255)
    with pytest.raises(OverflowError):
        FiniteGenerator([1, 300], dtype='B')


# ---------------------------------------------------------------------------
# FiniteGenerator — automatic dtype selection
# ---------------------------------------------------------------------------

def test_auto_dtype_unsigned_small():
    # [1, 200] fits in 'B' (uint8, 0..255)
    fg = FiniteGenerator([1, 100, 200])
    assert fg.dtype == 'B'
    assert fg.is_compact

def test_auto_dtype_unsigned_medium():
    # 256 does not fit in 'B' but fits in 'H' (uint16)
    fg = FiniteGenerator([1, 256])
    assert fg.dtype == 'H'

def test_auto_dtype_signed_values_rejected():
    with pytest.raises(ValueError):
        FiniteGenerator([-200, 0, 200])

def test_auto_dtype_zero_rejected():
    with pytest.raises(ValueError):
        FiniteGenerator([0, 1, 2])

def test_auto_dtype_bigint_fallback():
    big = 2**200
    fg = FiniteGenerator([big, big + 1])
    assert not fg.is_compact
    assert fg.dtype is None

def test_auto_dtype_all_same_value():
    fg = FiniteGenerator([42, 42, 42])
    assert fg.dtype == 'B'
    assert list(fg) == [42, 42, 42]

def test_auto_dtype_single_element():
    fg = FiniteGenerator([7])
    assert fg[0] == 7
    assert fg.size == 1


# ---------------------------------------------------------------------------
# FiniteGenerator — metadata properties
# ---------------------------------------------------------------------------

def test_size_matches_input():
    data = [10, 20, 30, 40]
    fg = FiniteGenerator(data)
    assert fg.size == len(data)

def test_min_max():
    fg = FiniteGenerator([5, 1, 9, 3])
    assert fg.min == 1
    assert fg.max == 9

def test_start_end():
    fg = FiniteGenerator([7, 2, 4])
    assert fg.start == 7
    assert fg.end == 4

def test_start_end_empty():
    fg = FiniteGenerator([])
    assert fg.start is None
    assert fg.end is None


# ---------------------------------------------------------------------------
# FiniteGenerator — element access
# ---------------------------------------------------------------------------

def test_getitem():
    fg = FiniteGenerator([10, 20, 30])
    assert fg[0] == 10
    assert fg[1] == 20
    assert fg[2] == 30

def test_getitem_negative_index():
    fg = FiniteGenerator([10, 20, 30])
    assert fg[-1] == 30
    assert fg[-3] == 10

def test_iteration_order_preserved():
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    fg = FiniteGenerator(data)
    assert list(fg) == data

def test_contains():
    fg = FiniteGenerator([1, 2, 3])
    assert 2 in fg
    assert 99 not in fg

def test_callable_at_index():
    fg = FiniteGenerator([10, 20, 30])
    assert fg(0) == 10
    assert fg(1) == 20
    assert fg(2) == 30

def test_callable_rejects_negative():
    fg = FiniteGenerator([10, 20, 30])
    with pytest.raises(ValueError):
        fg(-1)

def test_callable_rejects_out_of_bounds():
    fg = FiniteGenerator([10, 20, 30])
    with pytest.raises(IndexError):
        fg(3)


# ---------------------------------------------------------------------------
# FiniteGenerator — view (memoryview)
# ---------------------------------------------------------------------------

def test_view_returns_readonly_memoryview():
    fg = FiniteGenerator([1, 2, 3])
    v = fg.view
    assert isinstance(v, memoryview)
    assert v.readonly

def test_view_correct_values():
    fg = FiniteGenerator([10, 20, 30])
    assert fg.view.tolist() == [10, 20, 30]

def test_view_slice_is_readonly():
    fg = FiniteGenerator([1, 2, 3, 4])
    sliced = fg.view[1:3]
    assert sliced.tolist() == [2, 3]
    assert sliced.readonly

def test_view_write_raises():
    fg = FiniteGenerator([1, 2, 3])
    with pytest.raises(TypeError):
        fg.view[0] = 99

def test_view_unavailable_for_bigints():
    big = 2**200
    fg = FiniteGenerator([big])
    with pytest.raises(TypeError):
        _ = fg.view


# ---------------------------------------------------------------------------
# FiniteGenerator — bigint (tuple) path correctness
# ---------------------------------------------------------------------------

def test_bigint_iteration():
    big = 2**200
    data = [big, big + 1, big + 2]
    fg = FiniteGenerator(data)
    assert list(fg) == data

def test_bigint_contains():
    big = 2**200
    fg = FiniteGenerator([big, big + 1])
    assert big in fg
    assert (big + 5) not in fg

def test_bigint_callable():
    big = 2**200
    fg = FiniteGenerator([big, big + 1])
    assert fg(0) == big
    assert fg(1) == big + 1

def test_bigint_min_max():
    big = 2**200
    fg = FiniteGenerator([big + 5, big + 1, big + 9])
    assert fg.min == big + 1
    assert fg.max == big + 9


# ---------------------------------------------------------------------------
# FiniteGenerator — repr / str
# ---------------------------------------------------------------------------

def test_str_contains_dtype_and_size():
    fg = FiniteGenerator([1, 2, 3])
    s = str(fg)
    assert 'B' in s  # dtype
    assert '3' in s  # size

def test_repr_contains_key_fields():
    fg = FiniteGenerator([1, 2, 3])
    r = repr(fg)
    assert 'B' in r
    assert '3' in r


# ---------------------------------------------------------------------------
# Idempotent construction
# ---------------------------------------------------------------------------

def test_generator_idempotent_same_class():
    g = Generator(lambda n: n + 1)
    assert Generator(g) is g

def test_cached_generator_idempotent_same_class():
    cg = CachedGenerator(lambda n: n + 1)
    assert CachedGenerator(cg) is cg

def test_finite_generator_idempotent_same_class():
    fg = FiniteGenerator([1, 2, 3])
    assert FiniteGenerator(fg) is fg

def test_generator_idempotent_wrapping_subclass():
    # Generator(subclass_instance) is idempotent — hierarchy upward
    cg = CachedGenerator(lambda n: n + 1)
    assert Generator(cg) is cg
    fg = FiniteGenerator([1, 2, 3])
    assert Generator(fg) is fg

def test_cached_generator_not_idempotent_with_finite():
    # Cross-branch: CachedGenerator wrapping a FiniteGenerator is NOT idempotent
    fg = FiniteGenerator([1, 2, 3])
    cg = CachedGenerator(fg)
    assert cg is not fg
    assert isinstance(cg, CachedGenerator)


# ===========================================================================
# PeriodicGenerator
# ===========================================================================
from catena.generators import PeriodicGenerator
from math import gcd as _gcd


# ---------------------------------------------------------------------------
# Construction – valid
# ---------------------------------------------------------------------------

def test_periodic_generator_pure_period_no_preperiod():
    pg = PeriodicGenerator(period=[3, 1, 2])
    assert len(pg.pre_period) == 0
    assert len(pg.period) == 3


def test_periodic_generator_with_pre_period():
    pg = PeriodicGenerator(period=[2, 3], pre_period=[1])
    assert len(pg.pre_period) == 1
    assert len(pg.period) == 2


def test_periodic_generator_period_stored_as_finite_generator():
    pg = PeriodicGenerator(period=[5, 1])
    assert isinstance(pg.period, FiniteGenerator)


def test_periodic_generator_pre_period_stored_as_finite_generator():
    pg = PeriodicGenerator(period=[2], pre_period=[7, 3])
    assert isinstance(pg.pre_period, FiniteGenerator)


def test_periodic_generator_empty_pre_period_stored_correctly():
    pg = PeriodicGenerator(period=[1, 2])
    assert len(pg.pre_period) == 0


def test_periodic_generator_dtypes_period_and_preperiod():
    pg = PeriodicGenerator(period=[1, 2], pre_period=[3], dtypes=('H', 'B'))
    assert pg.period.dtype == 'H'
    assert pg.pre_period.dtype == 'B'


def test_periodic_generator_dtypes_mixed_none():
    pg = PeriodicGenerator(period=[1], pre_period=[2], dtypes=(None, 'H'))
    assert pg.pre_period.dtype == 'H'


# ---------------------------------------------------------------------------
# Construction – invalid
# ---------------------------------------------------------------------------

def test_periodic_generator_dtypes_wrong_length_raises():
    with pytest.raises(ValueError):
        PeriodicGenerator(period=[1], dtypes=('B',))  # length 1 instead of 2


def test_periodic_generator_non_positive_in_period_raises():
    with pytest.raises(ValueError):
        PeriodicGenerator(period=[0, 1])


def test_periodic_generator_negative_in_period_raises():
    with pytest.raises(ValueError):
        PeriodicGenerator(period=[-1, 2])


def test_periodic_generator_non_positive_in_pre_period_raises():
    with pytest.raises(ValueError):
        PeriodicGenerator(period=[1], pre_period=[0])


# ---------------------------------------------------------------------------
# __new__ – identity short-circuit
# ---------------------------------------------------------------------------

def test_periodic_generator_idempotent_with_no_pre_period():
    """PeriodicGenerator(pg) with no extra pre-period returns the same instance."""
    pg = PeriodicGenerator(period=[1, 2])
    assert PeriodicGenerator(pg) is pg


def test_periodic_generator_idempotent_with_empty_pre_period():
    pg = PeriodicGenerator(period=[1, 2])
    assert PeriodicGenerator(pg, pre_period=()) is pg


def test_periodic_generator_not_idempotent_with_new_pre_period():
    """When pre_period is non-empty the short-circuit does not trigger and
    a fresh PeriodicGenerator is created — but period must be a plain sequence,
    not another PeriodicGenerator, since that is not a supported calling convention."""
    pg = PeriodicGenerator(period=[2])
    pg2 = PeriodicGenerator(period=[2], pre_period=[1])
    assert pg2 is not pg


# ---------------------------------------------------------------------------
# __call__ – pure period (no pre-period)
# ---------------------------------------------------------------------------

def test_pure_period_first_element():
    pg = PeriodicGenerator(period=[5, 3])
    assert pg(0) == 5


def test_pure_period_second_element():
    pg = PeriodicGenerator(period=[5, 3])
    assert pg(1) == 3


def test_pure_period_wraps_at_length():
    pg = PeriodicGenerator(period=[5, 3])
    assert pg(2) == 5   # wraps back to index 0
    assert pg(3) == 3   # wraps back to index 1


def test_pure_period_arbitrary_depth():
    period = [7, 2, 4]
    pg = PeriodicGenerator(period=period)
    for n in range(30):
        assert pg(n) == period[n % len(period)]


def test_pure_period_negative_raises():
    pg = PeriodicGenerator(period=[1, 2])
    with pytest.raises(ValueError):
        pg(-1)


# ---------------------------------------------------------------------------
# __call__ – with pre-period
# ---------------------------------------------------------------------------

def test_preperiod_elements_come_first():
    pg = PeriodicGenerator(period=[9], pre_period=[3, 1])
    assert pg(0) == 3
    assert pg(1) == 1


def test_period_starts_after_preperiod():
    pg = PeriodicGenerator(period=[9], pre_period=[3, 1])
    assert pg(2) == 9   # first periodic element


def test_period_repeats_after_preperiod():
    period = [9, 7]
    pre = [3, 1]
    pg = PeriodicGenerator(period=period, pre_period=pre)
    k = len(pre)
    for n in range(20):
        if n < k:
            assert pg(n) == pre[n]
        else:
            assert pg(n) == period[(n - k) % len(period)]


# ---------------------------------------------------------------------------
# __eq__
# ---------------------------------------------------------------------------

def test_eq_same_period_no_preperiod():
    pg1 = PeriodicGenerator(period=[1, 2])
    pg2 = PeriodicGenerator(period=[1, 2])
    assert pg1 == pg2


def test_eq_same_period_and_preperiod():
    pg1 = PeriodicGenerator(period=[3], pre_period=[1, 2])
    pg2 = PeriodicGenerator(period=[3], pre_period=[1, 2])
    assert pg1 == pg2


def test_neq_different_period():
    pg1 = PeriodicGenerator(period=[1, 2])
    pg2 = PeriodicGenerator(period=[1, 3])
    assert pg1 != pg2


def test_neq_different_pre_period():
    pg1 = PeriodicGenerator(period=[2], pre_period=[1])
    pg2 = PeriodicGenerator(period=[2], pre_period=[3])
    assert pg1 != pg2


def test_neq_preperiod_vs_no_preperiod():
    pg1 = PeriodicGenerator(period=[2])
    pg2 = PeriodicGenerator(period=[2], pre_period=[1])
    assert pg1 != pg2


def test_eq_returns_not_implemented_for_non_periodic():
    pg = PeriodicGenerator(period=[1])
    assert pg.__eq__(FiniteGenerator([1])) is NotImplemented


# ---------------------------------------------------------------------------
# __str__ / __repr__
# ---------------------------------------------------------------------------

def test_str_contains_periodic_generator():
    pg = PeriodicGenerator(period=[2, 3])
    assert "PeriodicGenerator" in str(pg)


def test_repr_contains_periodic_generator():
    pg = PeriodicGenerator(period=[2, 3])
    assert "PeriodicGenerator" in repr(pg)


# ---------------------------------------------------------------------------
# cycle_quadratic_coefficients – hard-coded expected values
#
# Formula (integer_part=0 SCF from period [a₁,…,aₖ]):
#   A = q_{k-1},  B = q_k - p_{k-1},  C = -p_k
# where (pₙ, qₙ) = convergent(n) of FiniteSimpleContinuedFraction(period).
# ---------------------------------------------------------------------------

def test_cycle_quadratic_period_1():
    # period=[1]: convergent(0)=(1,1), convergent(-1)=(0,1) → A=1,B=1,C=-1
    pg = PeriodicGenerator(period=[1])
    assert pg.cycle_quadratic_coefficients() == (1, 1, -1)


def test_cycle_quadratic_period_2():
    # period=[2]: convergent(0)=(1,2), convergent(-1)=(0,1) → A=1,B=2,C=-1
    pg = PeriodicGenerator(period=[2])
    assert pg.cycle_quadratic_coefficients() == (1, 2, -1)


def test_cycle_quadratic_period_1_2():
    # period=[1,2]: convergent(1)=(2,3), convergent(0)=(1,1) → A=1,B=2,C=-2
    pg = PeriodicGenerator(period=[1, 2])
    assert pg.cycle_quadratic_coefficients() == (1, 2, -2)


def test_cycle_quadratic_period_4():
    # period=[4]: convergent(0)=(1,4), convergent(-1)=(0,1) → A=1,B=4,C=-1
    pg = PeriodicGenerator(period=[4])
    assert pg.cycle_quadratic_coefficients() == (1, 4, -1)


def test_cycle_quadratic_leading_coeff_positive():
    """A > 0 for all periods."""
    for period in [[1], [2], [3], [1, 2], [2, 1], [1, 1, 4]]:
        A, _, _ = PeriodicGenerator(period=period).cycle_quadratic_coefficients()
        assert A > 0, f"A must be positive for period={period}"


def test_cycle_quadratic_gcd_is_one():
    """gcd(A, B, C) == 1 for all periods."""
    for period in [[1], [2], [1, 2], [4], [3, 1, 2], [2, 1, 1]]:
        A, B, C = PeriodicGenerator(period=period).cycle_quadratic_coefficients()
        assert _gcd(abs(A), abs(B), abs(C)) == 1, f"gcd must be 1 for period={period}"


# ---------------------------------------------------------------------------
# quadratic_coefficients – no pre-period  →  same as cycle
# ---------------------------------------------------------------------------

def test_quadratic_no_preperiod_equals_cycle():
    for period in [[1], [2], [1, 2], [4]]:
        pg = PeriodicGenerator(period=period)
        assert pg.quadratic_coefficients() == pg.cycle_quadratic_coefficients()


# ---------------------------------------------------------------------------
# quadratic_coefficients – with pre-period
# [0; 1, (2)]  →  generator pre_period=[1], period=[2]
# Expected: (2, 0, -1)  →  2x² - 1 = 0  →  x = 1/√2
# ---------------------------------------------------------------------------

def test_quadratic_with_preperiod_1_period_2():
    pg = PeriodicGenerator(period=[2], pre_period=[1])
    assert pg.quadratic_coefficients() == (2, 0, -1)


def test_quadratic_with_preperiod_leading_coeff_positive():
    """A > 0 even when pre-period is present."""
    for pre, per in [([1], [2]), ([2], [1]), ([1, 1], [2])]:
        A, _, _ = PeriodicGenerator(period=per, pre_period=pre).quadratic_coefficients()
        assert A > 0


def test_quadratic_with_preperiod_gcd_is_one():
    """gcd(A, B, C) == 1 when pre-period is present."""
    for pre, per in [([1], [2]), ([2], [1]), ([1, 1], [2])]:
        A, B, C = PeriodicGenerator(period=per, pre_period=pre).quadratic_coefficients()
        assert _gcd(abs(A), abs(B), abs(C)) == 1

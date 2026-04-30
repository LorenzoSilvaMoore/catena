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

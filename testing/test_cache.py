"""Tests for BaseCache.

Goal: lock down the stable, observable behaviour of BaseCache — construction,
auto-computation on miss, immutability invariants, key-range tracking,
statistics, pruning, seeding, reset, copy, and the blocked UserDict methods.

Reference function
------------------
  squares(n) = n * n    →  simple, pure, side-effect-free

  Triangular number: tri(n) = n*(n+1)//2
"""

import pytest

from catena.cache import BaseCache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def squares(n: int) -> int:
    return n * n


def tri(n: int) -> int:
    return n * (n + 1) // 2


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_construction_stores_func():
    c = BaseCache(func=squares)
    assert c.func is squares


def test_construction_func_name_from_named_function():
    c = BaseCache(func=squares)
    assert c.func_name == "squares"


def test_construction_func_name_from_lambda():
    f = lambda n: n
    c = BaseCache(func=f)
    assert isinstance(c.func_name, str) and len(c.func_name) > 0


def test_construction_empty_cache():
    c = BaseCache(func=squares)
    assert len(c) == 0


def test_construction_counters_start_at_zero():
    c = BaseCache(func=squares)
    assert c.call_count == 0
    assert c.read_count == 0


def test_construction_key_range_empty():
    c = BaseCache(func=squares)
    assert c.smallest_key is None
    assert c.largest_key is None


def test_construction_maxsize_none_by_default():
    c = BaseCache(func=squares)
    assert c.maxsize is None


def test_construction_invalid_maxsize_raises():
    with pytest.raises(ValueError):
        BaseCache(func=squares, maxsize=0)
    with pytest.raises(ValueError):
        BaseCache(func=squares, maxsize=-3)
    with pytest.raises(ValueError):
        BaseCache(func=squares, maxsize=1.5)


def test_construction_valid_maxsize_accepted():
    c = BaseCache(func=squares, maxsize=5)
    assert c.maxsize == 5


# ---------------------------------------------------------------------------
# __getitem__ — miss path (auto-compute)
# ---------------------------------------------------------------------------

def test_miss_computes_and_stores():
    c = BaseCache(func=squares)
    result = c[4]
    assert result == 16


def test_miss_increments_call_count():
    c = BaseCache(func=squares)
    c[3]
    assert c.call_count == 1


def test_miss_does_not_increment_read_count():
    c = BaseCache(func=squares)
    c[3]
    assert c.read_count == 0


def test_miss_stores_result_in_cache():
    c = BaseCache(func=squares)
    c[7]
    assert 7 in c


def test_multiple_misses_accumulate_call_count():
    c = BaseCache(func=squares)
    for n in range(5):
        c[n]
    assert c.call_count == 5


# ---------------------------------------------------------------------------
# __getitem__ — hit path
# ---------------------------------------------------------------------------

def test_hit_returns_correct_value():
    c = BaseCache(func=squares)
    c[5]          # miss — stores 25
    result = c[5]  # hit
    assert result == 25


def test_hit_increments_read_count():
    c = BaseCache(func=squares)
    c[5]
    c[5]
    assert c.read_count == 1


def test_hit_does_not_increment_call_count():
    c = BaseCache(func=squares)
    c[5]
    c[5]
    assert c.call_count == 1


def test_multiple_hits_accumulate_read_count():
    c = BaseCache(func=squares)
    c[2]
    for _ in range(4):
        c[2]
    assert c.read_count == 4
    assert c.call_count == 1


# ---------------------------------------------------------------------------
# __setitem__ — immutability
# ---------------------------------------------------------------------------

def test_manual_write_stores_value():
    c = BaseCache(func=squares)
    c[10] = 999
    assert c[10] == 999
    assert c.read_count == 1   # hit on c[10]


def test_overwrite_raises_key_error():
    c = BaseCache(func=squares)
    c[10] = 100
    with pytest.raises(KeyError):
        c[10] = 200


def test_auto_computed_key_cannot_be_overwritten():
    c = BaseCache(func=squares)
    c[3]           # auto-computes 9
    with pytest.raises(KeyError):
        c[3] = 999


# ---------------------------------------------------------------------------
# Key-range tracking
# ---------------------------------------------------------------------------

def test_smallest_key_after_single_insert():
    c = BaseCache(func=squares)
    c[5]
    assert c.smallest_key == 5


def test_largest_key_after_single_insert():
    c = BaseCache(func=squares)
    c[5]
    assert c.largest_key == 5


def test_smallest_key_updates_on_lower_insert():
    c = BaseCache(func=squares)
    c[7]
    c[2]
    assert c.smallest_key == 2


def test_largest_key_updates_on_higher_insert():
    c = BaseCache(func=squares)
    c[2]
    c[9]
    assert c.largest_key == 9


def test_key_range_with_multiple_inserts():
    c = BaseCache(func=squares)
    for n in [3, 1, 7, 5, 2]:
        c[n]
    assert c.smallest_key == 1
    assert c.largest_key == 7


def test_key_range_none_when_empty():
    c = BaseCache(func=squares)
    assert c.smallest_key is None
    assert c.largest_key is None


def test_non_integer_key_does_not_affect_range():
    c = BaseCache(func=lambda k: k)
    c["hello"] = "world"
    assert c.smallest_key is None
    assert c.largest_key is None


# ---------------------------------------------------------------------------
# get() — no side effects
# ---------------------------------------------------------------------------

def test_get_returns_value_on_hit():
    c = BaseCache(func=squares)
    c[4]          # store via miss
    assert c.get(4) == 16


def test_get_returns_default_on_miss():
    c = BaseCache(func=squares)
    assert c.get(99, -1) == -1


def test_get_does_not_call_func_on_miss():
    c = BaseCache(func=squares)
    c.get(99, -1)
    assert c.call_count == 0


def test_get_does_not_store_on_miss():
    c = BaseCache(func=squares)
    c.get(99, -1)
    assert 99 not in c


def test_get_increments_read_count_on_hit():
    c = BaseCache(func=squares)
    c[3]
    c.get(3)
    assert c.read_count == 1


# ---------------------------------------------------------------------------
# prune()
# ---------------------------------------------------------------------------

def test_prune_keeps_n_largest_by_default():
    c = BaseCache(func=squares)
    for n in range(6):
        c[n]
    c.prune(3)
    assert set(c.keys()) == {3, 4, 5}


def test_prune_updates_largest_key():
    c = BaseCache(func=squares)
    for n in range(5):
        c[n]
    c.prune(2)
    assert c.largest_key == 4


def test_prune_updates_smallest_key():
    c = BaseCache(func=squares)
    for n in range(5):
        c[n]
    c.prune(2)
    assert c.smallest_key == 3


def test_prune_desc_keeps_n_smallest():
    c = BaseCache(func=squares)
    for n in range(6):
        c[n]
    c.prune(3, order='desc')
    assert set(c.keys()) == {0, 1, 2}


def test_prune_zero_clears_cache():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    c.prune(0)
    assert len(c) == 0
    assert c.smallest_key is None
    assert c.largest_key is None


def test_prune_invalid_order_raises():
    c = BaseCache(func=squares)
    c[1]
    with pytest.raises(ValueError):
        c.prune(1, order='sideways')


def test_prune_n_larger_than_size_keeps_all():
    c = BaseCache(func=squares)
    for n in range(3):
        c[n]
    c.prune(10)
    assert len(c) == 3


# ---------------------------------------------------------------------------
# maxsize — auto-prune on insert
# ---------------------------------------------------------------------------

def test_maxsize_enforced_on_auto_compute():
    c = BaseCache(func=squares, maxsize=3)
    for n in range(6):
        c[n]
    assert len(c) <= 3


def test_maxsize_enforced_on_manual_write():
    c = BaseCache(func=squares, maxsize=3)
    for n in range(3):
        c[n]
    c[99] = 9801
    assert len(c) <= 3


def test_maxsize_prune_keeps_largest_by_default():
    c = BaseCache(func=squares, maxsize=3)
    for n in range(5):
        c[n]
    # Default prune_key keeps max(size-1, 2) = 2 entries before inserting new one
    assert max(c.keys()) == 4


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_data():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    c.reset()
    assert len(c) == 0


def test_reset_clears_call_count():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    c.reset()
    assert c.call_count == 0


def test_reset_clears_read_count():
    c = BaseCache(func=squares)
    c[2]
    c[2]
    c.reset()
    assert c.read_count == 0


def test_reset_clears_key_range():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    c.reset()
    assert c.smallest_key is None
    assert c.largest_key is None


def test_reset_cache_usable_after_reset():
    c = BaseCache(func=squares)
    c[3]
    c.reset()
    assert c[3] == 9
    assert c.call_count == 1


# ---------------------------------------------------------------------------
# clear()
# ---------------------------------------------------------------------------

def test_clear_resets_key_range():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    c.clear()
    assert c.smallest_key is None
    assert c.largest_key is None


def test_clear_does_not_reset_statistics():
    c = BaseCache(func=squares)
    for n in range(3):
        c[n]
    c.clear()
    assert c.call_count == 3   # stats survive clear(); only reset() wipes them


# ---------------------------------------------------------------------------
# seed (constructor parameter)
# ---------------------------------------------------------------------------

def test_seed_populates_cache():
    c = BaseCache(func=squares, seed={0: 0, 1: 1, 2: 4})
    assert c[0] == 0
    assert c[1] == 1
    assert c[2] == 4


def test_seed_does_not_increment_statistics():
    c = BaseCache(func=squares, seed={5: 25})
    assert c.call_count == 0
    assert c.read_count == 0


def test_seed_updates_key_range():
    c = BaseCache(func=squares, seed={3: 9, 7: 49})
    assert c.smallest_key == 3
    assert c.largest_key == 7


def test_seed_hit_does_not_recompute():
    calls = []
    def f(n):
        calls.append(n)
        return n * n
    c = BaseCache(func=f, seed={4: 16})
    _ = c[4]   # should be a hit
    assert 4 not in calls


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

def test_copy_contains_same_data():
    c = BaseCache(func=squares)
    for n in range(4):
        c[n]
    cp = c.copy()
    for n in range(4):
        assert cp.data[n] == n * n


def test_copy_shares_same_func():
    c = BaseCache(func=squares)
    cp = c.copy()
    assert cp.func is squares


def test_copy_preserves_statistics():
    c = BaseCache(func=squares)
    c[2]; c[2]; c[3]
    cp = c.copy()
    assert cp.call_count == c.call_count
    assert cp.read_count == c.read_count


def test_copy_preserves_key_range():
    c = BaseCache(func=squares)
    for n in [1, 5, 3]:
        c[n]
    cp = c.copy()
    assert cp.smallest_key == 1
    assert cp.largest_key == 5


def test_copy_is_independent():
    c = BaseCache(func=squares)
    c[2]
    cp = c.copy()
    cp[9]
    assert 9 not in c


# ---------------------------------------------------------------------------
# stats property
# ---------------------------------------------------------------------------

def test_stats_returns_dict():
    c = BaseCache(func=squares)
    assert isinstance(c.stats, dict)


def test_stats_keys_present():
    c = BaseCache(func=squares)
    s = c.stats
    for key in ("func", "size", "calls", "reads", "smallest_key", "largest_key", "maxsize"):
        assert key in s


def test_stats_values_consistent():
    c = BaseCache(func=squares)
    c[3]; c[3]; c[7]
    s = c.stats
    assert s["calls"] == 2
    assert s["reads"] == 1
    assert s["size"] == 2
    assert s["smallest_key"] == 3
    assert s["largest_key"] == 7


# ---------------------------------------------------------------------------
# cache property (backward compat)
# ---------------------------------------------------------------------------

def test_cache_property_returns_self():
    c = BaseCache(func=squares)
    assert c.cache is c


# ---------------------------------------------------------------------------
# Blocked UserDict methods
# ---------------------------------------------------------------------------

def test_setdefault_raises():
    c = BaseCache(func=squares)
    with pytest.raises(NotImplementedError):
        c.setdefault(1, 0)


def test_update_raises():
    c = BaseCache(func=squares)
    with pytest.raises(NotImplementedError):
        c.update({1: 1})


def test_pop_raises():
    c = BaseCache(func=squares)
    c[3]
    with pytest.raises(NotImplementedError):
        c.pop(3)


def test_delitem_raises():
    c = BaseCache(func=squares)
    c[3]
    with pytest.raises(NotImplementedError):
        del c[3]


def test_popitem_raises():
    c = BaseCache(func=squares)
    c[1]
    with pytest.raises(NotImplementedError):
        c.popitem()


def test_or_raises():
    c = BaseCache(func=squares)
    with pytest.raises(NotImplementedError):
        _ = c | {1: 1}


def test_fromkeys_raises():
    with pytest.raises(NotImplementedError):
        BaseCache.fromkeys([1, 2], 0)


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

def test_repr_is_string():
    c = BaseCache(func=squares)
    assert isinstance(repr(c), str)


def test_repr_contains_func_name():
    c = BaseCache(func=squares)
    assert "squares" in repr(c)

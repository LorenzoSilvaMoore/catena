"""Tests for weak-reference caching semantics.

The changes tracked by the weakref refactor:
  - ``SimpleContinuedFraction._cached_inverse`` is now a
    ``weakref.ReferenceType[Self]`` instead of a hard object reference.
  - ``PeriodicSimpleContinuedFraction._cached_conjugate`` is likewise a
    weakref (replacing the old hard-reference ``_conjugate`` attribute).

What we verify here:
  1. The stored attribute is an actual ``weakref.ref``, not a hard reference.
  2. The symmetric back-link on the paired object is also a weakref.
  3. While the referent is alive the cache works (same identity returned).
  4. Once the referent is garbage-collected the weakref returns ``None``.
  5. After GC the *write-once guard* allows a re-set, so the next call
     recomputes a fresh result with the correct value.
  6. The guard still blocks overwriting while the referent is alive.
  7. Neither object in a paired (a, 1/a) or (a, conjugate(a)) relationship
     keeps the other alive via the cache (no hard cycle).
"""

import gc
import weakref

import pytest

from catena.catena import (
    FiniteSimpleContinuedFraction,
    PeriodicSimpleContinuedFraction,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _collect():
    """Run several GC passes to handle reference cycles."""
    for _ in range(3):
        gc.collect()


# ===========================================================================
# _cached_inverse — FiniteSimpleContinuedFraction
# ===========================================================================

def test_fscf_cached_inverse_stored_as_weakref():
    """_cached_inverse holds a weakref.ref, not a direct object reference."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)   # 22/7
    inv = scf.inverse()
    assert isinstance(scf._cached_inverse, weakref.ref)
    assert scf._cached_inverse() is inv


def test_fscf_cached_inverse_back_link_is_weakref():
    """The symmetric back-link on the inverse is also a weakref pointing to scf."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    inv = scf.inverse()
    assert isinstance(inv._cached_inverse, weakref.ref)
    assert inv._cached_inverse() is scf


def test_fscf_cached_inverse_returns_none_after_gc():
    """Dropping the only hard reference to the inverse makes the weakref go dead."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    inv = scf.inverse()
    ref = weakref.ref(inv)
    del inv
    _collect()
    assert ref() is None


def test_fscf_inverse_recomputes_after_gc():
    """After the cached inverse is collected, inverse() recomputes a fresh object."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)   # 22/7 → inverse 7/22
    inv1 = scf.inverse()
    ref = weakref.ref(inv1)
    del inv1
    _collect()
    assert ref() is None, "inv1 should have been collected"

    inv2 = scf.inverse()   # recomputed
    assert inv2 is not None
    assert inv2.terminal_convergent == (7, 22)


def test_fscf_inverse_write_once_guard_while_alive():
    """Overwriting _cached_inverse raises AttributeError while the referent is alive."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    inv = scf.inverse()
    with pytest.raises(AttributeError):
        scf._cached_inverse = weakref.ref(inv)


def test_fscf_inverse_pair_does_not_prevent_gc():
    """Neither scf nor inv keeps the other alive through the weak cache."""
    scf = FiniteSimpleContinuedFraction([7], integer_part=3)
    inv = scf.inverse()
    ref_scf = weakref.ref(scf)
    ref_inv = weakref.ref(inv)
    del scf, inv
    _collect()
    assert ref_scf() is None, "scf should have been collected"
    assert ref_inv() is None, "inv should have been collected"


# ===========================================================================
# _cached_inverse — PeriodicSimpleContinuedFraction
# ===========================================================================

def test_pscf_cached_inverse_stored_as_weakref():
    """_cached_inverse on PSCF holds a weakref.ref."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)   # √2
    inv = pscf.inverse()
    assert isinstance(pscf._cached_inverse, weakref.ref)
    assert pscf._cached_inverse() is inv


def test_pscf_cached_inverse_back_link_is_weakref():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    inv = pscf.inverse()
    assert isinstance(inv._cached_inverse, weakref.ref)
    assert inv._cached_inverse() is pscf


def test_pscf_cached_inverse_returns_none_after_gc():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    inv = pscf.inverse()
    ref = weakref.ref(inv)
    del inv
    _collect()
    assert ref() is None


def test_pscf_inverse_recomputes_after_gc():
    """After GC of the cached inverse, inverse() produces a new correct value."""
    from math import isclose, sqrt
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)   # √2
    inv1 = pscf.inverse()
    ref = weakref.ref(inv1)
    del inv1
    _collect()
    assert ref() is None, "inv1 should have been collected"

    inv2 = pscf.inverse()
    assert isclose(float(inv2), 1 / sqrt(2), rel_tol=1e-10)


def test_pscf_inverse_write_once_guard_while_alive():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    inv = pscf.inverse()
    with pytest.raises(AttributeError):
        pscf._cached_inverse = weakref.ref(inv)


def test_pscf_inverse_pair_does_not_prevent_gc():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    inv = pscf.inverse()
    ref_pscf = weakref.ref(pscf)
    ref_inv = weakref.ref(inv)
    del pscf, inv
    _collect()
    assert ref_pscf() is None, "pscf should have been collected"
    assert ref_inv() is None, "inv should have been collected"


# ===========================================================================
# _cached_conjugate — PeriodicSimpleContinuedFraction
# ===========================================================================

def test_pscf_cached_conjugate_stored_as_weakref():
    """_cached_conjugate holds a weakref.ref, not a hard reference."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)   # √2
    conj = pscf.conjugate()
    assert isinstance(pscf._cached_conjugate, weakref.ref)
    assert pscf._cached_conjugate() is conj


def test_pscf_cached_conjugate_back_link_is_weakref():
    """The symmetric back-link on the conjugate is a weakref pointing to pscf."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    conj = pscf.conjugate()
    assert isinstance(conj._cached_conjugate, weakref.ref)
    assert conj._cached_conjugate() is pscf


def test_pscf_cached_conjugate_returns_none_after_gc():
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    conj = pscf.conjugate()
    ref = weakref.ref(conj)
    del conj
    _collect()
    assert ref() is None


def test_pscf_conjugate_recomputes_after_gc():
    """After GC of the cached conjugate, conjugate() produces a new correct value."""
    from math import isclose, sqrt
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)   # √2
    conj1 = pscf.conjugate()
    ref = weakref.ref(conj1)
    del conj1
    _collect()
    assert ref() is None, "conj1 should have been collected"

    conj2 = pscf.conjugate()
    assert isclose(float(conj2), -sqrt(2), rel_tol=1e-10)


def test_pscf_conjugate_write_once_guard_while_alive():
    """Overwriting _cached_conjugate raises AttributeError while the referent is alive."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    conj = pscf.conjugate()
    with pytest.raises(AttributeError):
        pscf._cached_conjugate = weakref.ref(conj)


def test_pscf_conjugate_pair_does_not_prevent_gc():
    """Neither pscf nor its conjugate keeps the other alive through the weak cache."""
    pscf = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
    conj = pscf.conjugate()
    ref_pscf = weakref.ref(pscf)
    ref_conj = weakref.ref(conj)
    del pscf, conj
    _collect()
    assert ref_pscf() is None, "pscf should have been collected"
    assert ref_conj() is None, "conj should have been collected"

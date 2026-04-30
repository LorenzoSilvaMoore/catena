# Changelog

All notable changes to **catena** will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2025-07-27

Initial release of `catena`.  This is a ground-up rebuild of the earlier
prototype (`confrac`, v0.0.1–v0.2.0) with a stricter architecture, a proper
test suite, and no external dependencies.

### Added

#### Core types (`catena.catena`)

- `SimpleContinuedFraction` — infinite generative SCF $[a_0;\,a_1,a_2,\ldots]$
  backed by an arbitrary callable generator.
  - Memoised two-layer convergent engine: `tail_convergent(n)` computes the
    recurrence for the tail $[a_1;\ldots,a_{n+1}]$; `convergent(n)` lifts by
    $a_0$.
  - `shift(n)` / integer addition (`scf + k`, `k + scf`) — creates a new SCF
    view sharing the existing cache without recomputation.
  - Attribute freezing: `_generator` and `_cache_handler` are immutable after
    construction; reassignment raises `AttributeError`.

- `FiniteSimpleContinuedFraction(SimpleContinuedFraction)` — finite SCF
  $[a_0;\,a_1,\ldots,a_k]$ backed by a `FiniteGenerator`.
  - `partial_quotients` property returns the full tail as an immutable `tuple`.
  - `terminal_convergent` / `terminal_tail_convergent` — exact rational value
    of the finite expression.
  - Factory class methods:
    - `from_rational(r)` — accepts `fractions.Fraction`, `(p, q)` tuple, or `int`.
    - `from_float(f, max_denominator=None)` — converts a Python `float`.
    - `from_decimal(d)` — converts a finite decimal string (e.g. `"3.14"`).
  - Arithmetic:
    - `scf + int` — integer shift (inherited from `SimpleContinuedFraction`).
    - `scf + scf` — rational sum; returns a new `FiniteSimpleContinuedFraction`.
  - Numeric protocol: `__float__`, `__int__`, `__bool__`, `__len__`.
  - String protocol: `__str__`, `__repr__`.

#### Generator layer (`catena.generators`)

- `Generator` — validated callable wrapper ensuring $f(n) \in \mathbb{Z}_{>0}$
  for all $n \geq 0$.  Identity semantics via `__new__` prevent double-wrapping.
- `CachedGenerator(Generator)` — like `Generator` with per-index memoisation
  via `OrdinalCache` and `SetLightCache`.  Exposes `cache`, `cache_handler`,
  and `reset_cache()`.
- `FiniteGenerator(Generator)` — fixed-sequence generator.  Auto-selects the
  smallest unsigned `array.array` typecode (`B`/`H`/`I`/`L`/`Q`) that covers
  the value range; falls back to `tuple` for values exceeding 64-bit.  Provides
  `size`, `dtype`, `is_compact`, `min`, `max`, `start`, `end`, `view`, and the
  full sequence protocol (`__getitem__`, `__iter__`, `__len__`, `__contains__`).

#### Caching layer (`catena.cache`)

- `Cache(UserDict)` — append-only dictionary; raises `KeyError` if an existing
  key is written again.
- `OrdinalCache(Cache)` — restricts keys to integers; tracks `smallest_key` and
  `largest_key`.
- `CacheHandler` — owns a `Cache`, records `call_count` (misses) and
  `read_count` (hits).  Exposes `reset_cache()` and `prune_cache(n)`.  Protected
  internal attributes are guarded by a custom `__setattr__`.
- `SetCache` — decorator / decorator-factory memoising any callable; keys by
  `(args, frozenset(kwargs.items()))`.
- `SetLightCache` — lightweight single-argument variant of `SetCache`.

#### Mathematical library (`catena.mathlib`)

- `catena.mathlib.core`
  - Type aliases: `IntPair`, `IntTriplet`, `FloatAsStr`.
  - `get_sign`, `simplify`, `canonicalize`, `euclidean_step`, `quotent_sign`.

- `catena.mathlib.arithmetic`
  - `add_fractions` / `uadd_fractions` — GCD-based addition minimising
    intermediate magnitudes.
  - `multiply_fractions` / `umultiply_fractions` — cross-GCD multiplication.
  - `square_fraction` / `usquare_fraction`.
  - `sandwich_fraction` / `usandwich_fraction`.
  - Each operation has a tuple-accepting form and a `u`-prefixed unpacked form
    to reduce overhead in hot paths.

- `catena.mathlib.convert`
  - `from_rational_to_scf` — Euclidean-algorithm decomposition.
  - `from_float_to_rational`, `from_float_to_scf`.
  - `from_decimal_to_rational` — exact string parsing with simplification.
  - `Rational` type alias: `Fraction | tuple[int, int] | int`.

- `catena.mathlib.metric`
  - `product_digit_count` — log-sum digit count of a product (no actual
    multiplication).
  - `product_digit_count_high_precision` — `Decimal`-based variant.
  - `average_digit_count`.

#### String utilities (`catena.strings`)

- `safe_int_str(n, n_trailing=99)` — abbreviated repr for large integers,
  avoiding the PEP 678 integer-to-string conversion limit.
- `safe_full_int_str(n)` — full decimal string via chunked conversion for
  arbitrarily large integers.

#### Test suite (`testing/`)

- 275 tests across 9 test modules; all pass on Python 3.12+.
- `testing/bigints.py` — deterministic large-integer generation and binary
  store (`testing/store/*.dat`).
- `testing/conftest.py` — session-scoped fixture loading the precomputed store
  and providing on-the-fly generation for values not in the store.
- `testing/README.md` — documentation for the testing infrastructure.

---

> Previous development history is archived in `CHANGELOG.old.md`.

# Changelog

All notable changes to `confrac` are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.0] — 2025-02-23

### Added
- `FinateSimpleContinuedFraction` class: the first complete user-facing type representing a finite simple continued fraction stored as `(head, body)`.
  - Constructor accepts `(head, body)` directly, a fraction pair `frac=(p, q)`, or an iterable of coefficients.
  - `convergent(n)` method implementing the standard three-term recurrence relation $p_n = a_n p_{n-1} + p_{n-2}$, $q_n = a_n q_{n-1} + q_{n-2}$.
  - `convergent_as_float`, `convergent_as_decimal`, `convergent_as_string`, `convergent_as_digits`.
  - `aftermost_convergent` returning the full rational value.
  - Iterator variants: `iconvergents`, `iconvergents_as_float`, `iconvergents_as_string`, `iconvergents_as_digits`, `iconvergents_float_as_string`, `ifloat_values`, `idecimal_values`.
  - Immutable `head`, `body`, `cache_handler`, `size` attributes enforced via `__setattr__` override.
- `SetLightCache`: lightweight single-argument memoisation wrapper used for `convergent`.
- Version bumped to `0.2.0` in `_version.py`.

### Changed
- Cache infrastructure consolidated: `SetCache` now co-exists with `SetLightCache` for different call signatures.

---

## [0.1.1] — 2025-02-22

### Changed
- Checkpoint: intermediate work on `FinateSimpleContinuedFraction` construction and conversion methods.

---

## [0.1.0] — 2025-02-21

### Added
- `cache.py`: immutable caching infrastructure.
  - `Cache` — append-only `UserDict` raising `KeyError` on key mutation.
  - `CacheHandler` — immutable wrapper holding a `Cache` pointer and a call counter.
  - `SetCache` — general multi-argument memoisation wrapper.
  - `time_it` decorator and `wrap_set_cache` functional helper.
- `Method` class in `catena.py`: static arithmetic primitives.
  - `simplify`, `breakdown`, `euclid_breakdown`.
  - `sum_fracs`, `mul_fracs`, `square_frac`, `sandwich_fracs`.
  - `greedy_algorithm` (Sylvester / Egyptian fraction decomposition).
  - `compress_body` (coefficient sequence normalisation).
  - `log_prod`, `log_avg` (digit-count utilities).
- `StringMethod` class: `prefix_match` (binary search over sequences) and `string_divition` (long-division decimal string).
- `Convert` class: conversions from `(p, q)`, `Decimal`, and decimal strings to SCF coefficients, digit lists, and Egyptian fractions.
- `utils.py`: `get_sign`, `set_recurtion_depth`, `set_int_size`.

---

## [0.0.1] — 2025-02-20

### Added
- Initial repository setup, project skeleton.

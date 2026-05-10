# Changelog

All notable changes to **catena** will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- New subpackage `catena.numbers` with two modules:
  - `catena.numbers.constants` — module-level SCF constants for standard
    mathematical values:
    - `e` — Euler's number as a `SimpleContinuedFraction` with the known
      closed-form generator `a(n) = 2(k+1)` when `n ≡ 1 (mod 3)`, else `1`.
    - `phi`, `sqrt2`, `sqrt3`, `sqrt5` — purely-periodic
      `PeriodicSimpleContinuedFraction` instances with correct `integer_part`
      and `period`.
    - `metallic_mean(n)` — factory returning the *n*-th metallic mean
      `[n; (n)]`; satisfies `x² − nx − 1 = 0`.
  - `catena.numbers.randoms` — deterministic pseudo-random SCF generation via
    the Gauss-Kuzmin distribution:
    - `Seed` — stateful seed dispenser; `state` property advances via
      SHA-256 on each access, returning the previous raw bytes; `step` tracks
      how many times the state has been consumed; `__str__` always decodes
      the original UTF-8 `initial_state`.
    - `GaussKuzminSHA(seed)` — 53-bit SHA-256 uniform → Gauss-Kuzmin
      transform in O(1); callable by index, deterministic, seed-keyed.
    - `UniformSHAArbitrary(precision)` — multi-round SHA-256 hash chain
      producing a `Decimal` uniform in `[0, 1)` with `precision` significant
      digits.
    - `GaussKuzminSHAArbitrary(seed, precision)` — arbitrary-precision
      Gauss-Kuzmin callable built on `UniformSHAArbitrary`.
    - `RandomSCF` (ABC) — base class exposing six factory methods:
      `generator()`, `cached_generator()`, `finite_generator(size)`,
      `periodic_generator(period_size, pre_period_size)`, `scf(integer_part,
      memoised)`, `finite_scf(size, integer_part)`,
      `periodic_scf(period_size, pre_period, integer_part)`.
    - `GaussKuzminSCF(seed)` — `RandomSCF` backed by `GaussKuzminSHA`;
      each `__make_callable__` call consumes one `Seed.state` so successive
      calls on the same `Seed` produce independent callables.
    - `GaussKuzminArbitrarySCF(precision, seed)` — same pattern, backed by
      `GaussKuzminSHAArbitrary`.
    - Module-level `_SEED` — global default `Seed` instance used when no
      explicit seed is passed.

---

## [Unreleased] — prior commit

### Added

- `SimpleContinuedFraction.__repr__`: returns a detailed string including
  `generator`, `integer_part`, and `cache_handler` fields (distinct from
  `__str__`, which omits the cache handler).
- `FiniteSimpleContinuedFraction.__add__`: extended to accept `float`,
  `Fraction`, and `Decimal` in addition to the previously supported
  `FiniteSimpleContinuedFraction` and `int`.
- `FiniteSimpleContinuedFraction.__sub__`: new operator — delegates to
  `self + (-other)`.
- `FiniteSimpleContinuedFraction.__mul__`: new operator — supports
  multiplication by another `FiniteSimpleContinuedFraction`, `int`, `float`,
  `Fraction`, or `Decimal`; returns a new `FiniteSimpleContinuedFraction`.
- `FiniteSimpleContinuedFraction.__truediv__`: new operator — supports
  division by another `FiniteSimpleContinuedFraction`, `int`, `float`,
  `Fraction`, or `Decimal`; returns a new `FiniteSimpleContinuedFraction`.
- `FiniteSimpleContinuedFraction.__eq__`: compares by `terminal_convergent`
  so two SCFs with different internal representations of the same rational are
  considered equal; also handles `int`, `float`, and `Fraction`.
- `FiniteSimpleContinuedFraction.__hash__`: hashes the `terminal_convergent`
  tuple so equal SCFs have equal hashes and instances are usable as dict keys
  and in sets.
- `PeriodicSimpleContinuedFraction.__eq__`: compares by `quadratic_surd()`
  tuple; only defined for two `PeriodicSimpleContinuedFraction` instances.
- `PeriodicSimpleContinuedFraction.__hash__`: hashes the `quadratic_surd()`
  tuple; consistent with `__eq__`.

### Fixed

- `FiniteGenerator.insert`: dtype promotion now uses a `'Z'`-sentinel
  `max()` comparison so arrays with different compact typecodes (e.g. `'B'`
  and `'H'`) are both recast to the wider typecode before concatenation,
  preventing `TypeError` on mixed-dtype inserts.
- `PeriodicGenerator.insert`: refactored to delegate dtype handling entirely
  to `FiniteGenerator.insert` (chained calls), removing the duplicated dtype
  logic and the `'A'`-sentinel workaround.
- `FiniteSimpleContinuedFraction.__add__` / `__mul__` / `__truediv__`: `Decimal`
  values are now converted to `Fraction` before accessing `.numerator` /
  `.denominator`, fixing `AttributeError` on `Decimal` operands.
- `FiniteSimpleContinuedFraction.__eq__`: previous implementation compared
  `terminal_convergent` against the `(integer_part, pq_list)` tuple returned
  by `from_rational_to_scf`, always yielding `False`; now compares
  `Fraction(*self.terminal_convergent)` against the numeric value directly.

---

## [Unreleased] — prior commit

### Added

- `Generator.advance(n)`: returns a new generator whose *k*-th term equals the
  original's *(n+k)*-th term.  Raises `ValueError` for negative *n*; returns
  `self` for `n == 0`.  Return type follows `type(self)` so all subclasses
  inherit correct dispatch automatically.
- `Generator.insert(fg, at)`: inserts a `FiniteGenerator` at the given index,
  returning a new generator that splices the two sequences together.  Returns
  `self` when `fg` is empty.
- `Generator.prepend(fg)`: convenience alias for `insert(fg, at=0)`.
- `CachedGenerator.advance(n, copy_cache=False)`: override that optionally
  copies and re-indexes cache entries whose key ≥ *n* into the new generator
  (shifting keys by −*n*).
- `CachedGenerator.insert(fg, at, copy_cache=False)`: override that optionally
  copies cache entries; entries at indices < *at* are kept as-is; entries at
  indices ≥ *at* are shifted forward by `fg.size`.
- `FiniteGenerator.advance(n)`: slices the internal data array from *n*
  onward; raises `IndexError` if `n > size`.  Advancing exactly to `size`
  returns an empty `FiniteGenerator`.
- `FiniteGenerator.insert(fg, at)`: concatenates the underlying data arrays
  and selects the larger of the two dtypes; raises `IndexError` if
  `at > size`.
- `PeriodicGenerator.advance(n)`: exhausts the pre-period first, then rotates
  the period by `n % len(period)`.
- `PeriodicGenerator.insert(fg, at)`: inserts into the pre-period when
  `at ≤ len(pre_period)`; otherwise folds the relevant portion of the period
  into an extended pre-period while keeping the original period intact.
- `SimpleContinuedFraction.__neg__`: returns the additive inverse as a new SCF
  of the same type, using `advance` and `prepend`; two branches handle *a₁ > 1*
  and *a₁ = 1* separately.
- `FiniteSimpleContinuedFraction.__neg__`: delegates to `from_rational` for
  `size ≤ 2` (avoids accessing a potentially absent *a₂*); calls `super().__neg__()`
  for larger SCFs.
- `PeriodicSimpleContinuedFraction.__neg__`: trivial negation via the quadratic
  surd representation — maps *(P + √D) / Q* to *(P + √D) / (−Q)*.
- `PeriodicSimpleContinuedFraction.__init__`: accepts a `PeriodicGenerator`
  instance directly as the `period` argument, bypassing re-construction.

### Removed

- `Generator.cached` and `CachedGenerator.cached` attributes (use
  `isinstance(g, CachedGenerator)` to test for caching instead).

### Fixed

- `CachedGenerator`: passing a `CachedGenerator` instance to the constructor
  now returns the same object (identity short-circuit via `__new__` +
  `__init__` early-return guard) rather than wrapping it in a second layer.
- Removed stray debug `print` from `mathlib/convert.py`.

---

## [0.3.0] — 2026-05-07

### Added

- `SimpleContinuedFraction.__float__`: evaluates `convergent(50)` as a
  `float`.  The 50th-convergent denominator exhausts 64-bit float precision
  for all standard generators (worst case: Fibonacci denominators give error
  ≈ 1.5 × 10⁻²¹).
- `SimpleContinuedFraction.segment(n)`: returns a `FiniteSimpleContinuedFraction`
  of the first *n* body partial quotients with an independent convergent cache.
- `FiniteSimpleContinuedFraction.segment(n)` (override): `n < size` → independent
  copy; `n == size` → cache-sharing `shift(0)` clone; `n > size` → `IndexError`.
  Inherited automatically by `PeriodicSimpleContinuedFraction`.
- `catena.cache` re-exported from `catena/__init__.py` so `OrdinalCache`,
  `CacheHandler`, `SetLightCache`, and `SetCache` are accessible directly as
  `catena.cache.<Class>` without importing from the internal submodule.

### Fixed

- `SimpleContinuedFraction.inverse()`: negative integer part (`a_0 < 0`) now
  raises `ValueError` explicitly instead of silently constructing a malformed
  SCF with a negative value in a body slot (which violates `g: I → ℤ⁺`).
  The condition was tightened from a bare `else` to `elif a_0 > 0` with an
  explicit guard.

### Changed

- **`tail_convergent` recurrence seeds** shifted to match standard literature:
  `(h_{-2}, k_{-2}) = (1, 0)`, `(h_{-1}, k_{-1}) = (0, 1)`,
  giving `h_0 = 1`, `k_0 = a_1`.
- **`tail_convergent` implementation** rewritten from top-down recursion to an
  iterative forward fill that advances from `OrdinalCache.largest_key` to *n*.
  Stack depth is now O(1) for any *n*; `RecursionError` on large indices is no
  longer possible.  The frontier is clamped to `max(0, largest_key + 1)` to
  guard against stale seed entries corrupting the fill.

### Documentation

- **Theory paper v1.0.0** (`docs/theory/`) — first complete draft covering all
  implemented classes.  Sections added or substantially rewritten:
  - *Simple SCFs*: generator catenadef rewritten; `inverse` proposition fixed
    (`a_0 > 0` condition); integer-translation, shared-cache, and
    no-`to_decimal` remarks added.
  - *Finite SCFs*: dual-representation proposition, canonical-form remark,
    IEEE 754 remark, `to_decimal` catenadef, full properties subsection.
  - *Caching*: complete rewrite — cache primitives, memoisation decorators,
    generator-level caching decision guide, shared-cache and tail section.
  - *Periodic SCFs*: new section — two-generator data model, purely-periodic
    vs. eventually-periodic unification (single class, vacuous `g_pre`),
    inherited and deferred-algebraic methods subsection.
  - *Notation*: overhauled to a 3-column table (Symbol / `catena` attribute /
    Meaning) with `body` vs. `generator` disambiguation remark.
  - *Introduction*: ℕ/ℤ⁺ remark, `PeriodicSCF` deferral remark,
    `fractions.Fraction` worst-case clarification, stale function-notation
    bullets removed.
- GitHub Actions workflow (`.github/workflows/build-docs.yml`) compiles
  `main.tex` with `latexmk` + `biber` and deploys `catena-theory.pdf` to
  GitHub Pages on every push touching `docs/theory/`.
- README links to the hosted PDF.

---

## [0.2.0] — 2026-05-03

### Added

#### Quadratic-irrational support (`catena.catena`)

- `PeriodicSimpleContinuedFraction` — new methods for algebraic evaluation and
  manipulation of periodic SCFs as quadratic surds $(P + \sqrt{D})\,/\,Q$:
  - `quadratic_surd()` — derives $(P, Q, D)$ from the quadratic coefficients;
    detects which root the SCF represents by round-tripping through the
    conversion algorithm.  Cached write-once in `_quadratic_surd`.
  - `is_principal_surd()` / `is_conjugate_root()` — classify the root by the
    sign of $Q$.
  - `conjugate()` — returns the algebraic conjugate (the other root of the same
    quadratic); cached write-once in `_conjugate`; double application returns
    the original object.
  - `inverse()` (override) — inverts via the reversed quadratic
    $C x^2 + B x + A = 0$, selects the correct root based on
    `is_principal_surd()`, and caches write-once in `_inverse`.
  - `from_quadratic_surd(P, Q, D)` (classmethod) — constructs a
    `PeriodicSimpleContinuedFraction` directly from surd parameters.
  - `__float__` and `as_decimal()` — evaluate the surd exactly.
  - `__neg__` — negates by flipping the sign of $Q$.
  - `__setattr__` extended with freeze guards for `_quadratic_coefficients`,
    `_quadratic_surd`, and `_conjugate`.
  - `quadratic_coefficients()` now caches its result on first call.

- `SimpleContinuedFraction`:
  - `tail()` — returns a new instance sharing the generator and cache but with
    `integer_part = 0`.
  - `inverse()` — constructs the multiplicative inverse.  When $a_0 = 0$ the
    generator is shifted forward by one; otherwise $a_0$ is prepended and the
    generator shifts back.  Cached write-once in `_inverse`; calling `inverse()`
    twice returns the original object.
  - `__setattr__` extended to enforce write-once semantics on `_inverse`.

- `FiniteSimpleContinuedFraction`:
  - `inverse()` (override) — inverts the terminal convergent
    $(p, q) \to (q, p)$ and constructs the new finite SCF via
    `from_rational_to_scf`.  Raises `ZeroDivisionError` for the zero value.

#### New module: `catena.mathlib.quadratic`

- `_square_part_sqrt(D)` — largest $s$ such that $s^2 \mid D$.
- `simplify_quadratic_surd(P, Q, D)` — reduce by the common factor
  $g = \gcd(P,\,Q,\,\text{sqpart}(D))$; preserves signs.
- `normalize_quadratic_surd(P, Q, D)` — scale so that $Q \mid (D - P^2)$;
  required by the SCF expansion algorithm.
- `quadratic_roots_from_coefficients(A, B, C)` — both real roots of
  $Ax^2+Bx+C=0$ as `Decimal` values ($x_0 \geq x_1$), or `None` if $\Delta < 0$.
- `quadratic_surd_from_coefficients(A, B, C)` — canonical surd form $(P, Q, D)$
  with $Q > 0$, after GCD reduction.

#### New functions: `catena.mathlib.convert`

- `from_quadratic_surd_to_scf(P, Q, D)` — expands $(P + \sqrt{D})\,/\,Q$ into
  `(integer_part, pre_period, period)` using an integer-only Euclidean
  algorithm; avoids floating-point for the floor step.
- `from_quadratic_surd_to_conjugate_scf(P, Q, D)` — thin wrapper that negates
  both $P$ and $Q$ before delegating to the above.

#### Test suite

- 115 new tests; 541 total, all passing.
- `testing/test_math_quadratic.py` (new) — full coverage of `mathlib.quadratic`
  and the two new `convert` helpers: known values, structural invariants
  (Vieta's formulas, value preservation, divisibility condition), error cases.
- `testing/test_periodic_scf.py` — added sections for `quadratic_surd`,
  `is_principal_surd`/`is_conjugate_root`, `__float__`, `as_decimal`,
  `from_quadratic_surd`, `conjugate`, `inverse`, and `__neg__`.
- `testing/test_scf.py` — added sections for `tail()` and `inverse()`,
  including write-once protection and the double-inverse identity.
- `testing/test_finite_scf.py` — added `inverse()` tests with known rational
  values, double-inverse caching, and `ZeroDivisionError` for zero input.

### Changed

- `catena/generators.py` module docstring updated to reflect four generator
  types (was three).

### Documentation

- `README.md` — added "Why catena?" rationale section; added cache design
  rationale; added pointer to `CONTRIBUTING.md`.
- `CONTRIBUTING.md` (new) — development setup, test-running instructions, and
  code conventions.
- `testing/README.md` — clarified that `store/*.dat` and `store/*.hash` are
  not git-tracked.

---

## [0.1.0.post1] — 2026-04-30

### Changed

- Distribution renamed from `catena` to `catena-scf` on PyPI (`pip install catena-scf`);
  the import name `catena` is unchanged.
- Package description updated to "A Python library for simple continued fractions".
- Version bumped to `0.1.0.post1` to allow re-upload after the rename.

### Added

- `catena.__version__` — reads the installed version from package metadata via
  `importlib.metadata`; returns `None` when running from source without installing.
- `pyproject.toml`: sdist now excludes `docs/` and `testing/`.
- `requirements.txt`: pin `twine >= 6.2.0, < 7.0.0`.
- `.gitignore`: added `dist/`, `docs/theory/`, `gitdiff.txt`.

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

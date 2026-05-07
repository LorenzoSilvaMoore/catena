# catena

A pure-Python library for working with **simple continued fractions** (SCFs).

`catena` provides three main abstractions: a generative SCF driven by an
arbitrary callable, a finite SCF backed by a compact fixed sequence, and a
periodic SCF representing quadratic irrationals.  All three share a memoised
two-layer convergent engine and a common arithmetic interface.

The library has **zero dependencies** and requires Python ≥ 3.12.

A formal write-up of the theory and implementation decisions is available as a PDF:
**[catena — Architecture, Algorithm Decisions, and Formal Theory](https://lorenzosilvamoore.github.io/catena/catena-theory.pdf)**

---

## Mathematical background

A simple continued fraction expresses a number as

$$
a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{\ddots}}}
\;=\; [a_0;\, a_1, a_2, \ldots]
$$

where $a_0 \in \mathbb{Z}$ and $a_k \in \mathbb{Z}_{>0}$ for $k \geq 1$.
When the sequence is finite the expression represents a rational number exactly.

Convergents are the rational approximations obtained by truncating the expansion:

$$
\frac{p_n}{q_n} = [a_0;\, a_1, \ldots, a_n]
$$

They satisfy the two-term recurrence

$$
p_n = a_n p_{n-1} + p_{n-2}, \qquad q_n = a_n q_{n-1} + q_{n-2}
$$

and are best rational approximations to the value being expanded.

---

## Why catena?

Existing Python libraries for continued fractions tend to focus on the finite,
rational case.  For example,
[`continuedfractions`](https://continuedfractions.readthedocs.io/) is a
well-designed object-oriented library that extends `fractions.Fraction` to cover
finite SCFs and related objects such as Farey sequences and mediants — but its
scope is explicitly limited to rationals.  Many other packages take an even more
procedural approach, exposing functions that operate on lists of coefficients
rather than first-class objects.

`catena` starts from the general, countably infinite definition.  A
`SimpleContinuedFraction` is driven by a generator callable that produces
partial quotients on demand — so an infinite expansion like $\sqrt{2}$ or $e$
is represented by a small, fixed-size object regardless of how many convergents
you compute.  Convergents are memoised as they are requested; you pay only for
what you use, and the cache is shared transparently when the same tail is viewed
with a different integer part.

`catena` also does not subclass `fractions.Fraction`.  Convergents produced by
the two-term recurrence are guaranteed to be in lowest terms — consecutive
convergents satisfy $p_n q_{n-1} - p_{n-1} q_n = \pm 1$, so $\gcd(p_n, q_n) = 1$
always holds.  `fractions.Fraction` normalises every result through a GCD
reduction regardless, which means wrapping convergents in it would pay a cost
that buys nothing.  Instead, `catena` stores numerator/denominator pairs as
plain `(int, int)` tuples and implements only the arithmetic operations it
actually needs, with targeted GCD reductions where they are genuinely required
(e.g. when adding two finite SCFs).

The long-term goal is to build on this foundation a high-level API for concrete
applications of continued fraction theory.  The following are already
implemented or partially implemented:

- **Quadratic irrationals and periodic SCFs** — `PeriodicSimpleContinuedFraction`
  represents numbers of the form $(P + \sqrt{D})/Q$ as eventually-periodic
  expansions.  Provides `quadratic_surd()`, `conjugate()`, `inverse()`,
  `from_quadratic_surd()`, and `__float__` / `as_decimal()`.

Planned for future releases:

- **Best rational approximations** — direct extraction from the convergent sequence.
- **Pell's equation** — solutions via the periodic expansion of $\sqrt{D}$.
- **Farey sequences and mediants** — enumeration of rationals and their
  geometric interpretation as rational points in the plane.
- **Transcendental constants** — generalized continued fraction expansions for
  $e^x$, $\tanh(1/n)$, $\tan(n)$, Bessel functions, and related sequences.
- **Fibonacci-type sequences** — structural connections between convergents and
  linear recurrences.

---

## Installation

```bash
pip install catena-scf
```

The import name is `catena` (unchanged from the distribution name):

```python
import catena
```

**Development install** from the repository root:

```bash
pip install -e .
```

---

## Quick start

### Finite SCF from a rational number

```python
from catena import FiniteSimpleContinuedFraction

# 355/113  =  [3; 7, 16]
scf = FiniteSimpleContinuedFraction.from_rational((355, 113))

print(scf.integer_part)        # 3
print(scf.partial_quotients)   # (7, 16)
print(scf.terminal_convergent) # (355, 113)

# Successive convergents
scf.convergent(0)   # (22, 7)   — the classic 22/7 approximation
scf.convergent(1)   # (355, 113)
```

### Finite SCF from a float or decimal string

```python
import math

scf = FiniteSimpleContinuedFraction.from_float(math.pi, max_denominator=1000)
print(scf.terminal_convergent)   # (355, 113)

scf2 = FiniteSimpleContinuedFraction.from_decimal("3.14159265")
```

### Infinite (generative) SCF

```python
from catena import SimpleContinuedFraction

# Golden ratio  φ = [1; 1, 1, 1, ...]
phi = SimpleContinuedFraction(lambda n: 1, integer_part=1)

phi.tail_convergent(10)   # (89, 144) — consecutive Fibonacci numbers
phi.convergent(10)        # (233, 144)

# Shift the integer part without recomputing the cache
phi_shifted = phi + 2     # [3; 1, 1, 1, ...]  — shares phi's cache
```

### SCF arithmetic

```python
from catena import FiniteSimpleContinuedFraction

a = FiniteSimpleContinuedFraction.from_rational((1, 3))
b = FiniteSimpleContinuedFraction.from_rational((1, 6))

c = a + b                       # FiniteSimpleContinuedFraction for 1/2
c.terminal_convergent           # (1, 2)
float(c)                        # 0.5

# Multiplicative inverse
inv = a.inverse()               # FiniteSimpleContinuedFraction for 3/1
inv.terminal_convergent         # (3, 1)
inv.inverse() is a              # True — cached, returns original object
```

### Periodic SCF — quadratic irrationals

```python
from catena import PeriodicSimpleContinuedFraction

# √2 = [1; (2, 2, 2, ...)]
sqrt2 = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)

float(sqrt2)                    # 1.4142135623730951
sqrt2.quadratic_coefficients()  # (1, 0, -2)  →  x² - 2 = 0
sqrt2.quadratic_surd()          # (0, 1, 2)   →  (0 + √2) / 1

conj = sqrt2.conjugate()        # the other root: -√2
float(conj)                     # -1.4142135623730951
conj.conjugate() is sqrt2       # True

inv = sqrt2.inverse()           # 1/√2 = [0; 1, (2)]
float(inv)                      # 0.7071067811865476

# Construct directly from surd parameters (P + √D) / Q
phi = PeriodicSimpleContinuedFraction.from_quadratic_surd(1, 2, 5)
float(phi)                      # 1.618033988749895
```

---

## Project structure

```
catena/
├── __init__.py          # Public exports
├── catena.py            # SimpleContinuedFraction, FiniteSimpleContinuedFraction,
│                        #   PeriodicSimpleContinuedFraction
├── generators.py        # Generator, CachedGenerator, FiniteGenerator, PeriodicGenerator
├── cache.py             # Cache, OrdinalCache, CacheHandler, SetCache, SetLightCache
├── strings.py           # safe_int_str, safe_full_int_str
└── mathlib/
    ├── __init__.py      # Re-exports all submodules
    ├── core.py          # Type aliases, get_sign, simplify, canonicalize, euclidean_step
    ├── arithmetic.py    # add_fractions, multiply_fractions, square_fraction, sandwich_fraction
    ├── convert.py       # from_rational_to_scf, from_float_to_*, from_decimal_to_rational,
    │                    #   from_quadratic_surd_to_scf, from_quadratic_surd_to_conjugate_scf
    ├── quadratic.py     # simplify/normalize_quadratic_surd, quadratic_roots/surd_from_coefficients
    └── metric.py        # product_digit_count, average_digit_count

testing/
├── conftest.py              # Session fixtures, large-integer store management
├── bigints.py               # Deterministic large-integer generation and binary store
├── test_scf.py              # SimpleContinuedFraction tests
├── test_finite_scf.py       # FiniteSimpleContinuedFraction tests
├── test_periodic_scf.py     # PeriodicSimpleContinuedFraction tests
├── test_generators.py       # Generator / CachedGenerator / FiniteGenerator / PeriodicGenerator tests
├── test_cache.py            # Cache / OrdinalCache / CacheHandler / SetCache tests
├── test_math_core.py        # mathlib.core tests
├── test_math_arithmetic.py  # mathlib.arithmetic tests
├── test_math_quadratic.py   # mathlib.quadratic + convert surd helpers tests
├── test_math_metric.py      # mathlib.metric tests
└── test_strings.py          # strings tests
```

---

## API reference

### `catena.catena`

#### `SimpleContinuedFraction`

Represents an infinite SCF $[a_0;\, a_1, a_2, \ldots]$ driven by a callable generator.

```python
SimpleContinuedFraction(generator, integer_part=0)
```

| Member | Description |
|--------|-------------|
| `integer_part` | $a_0$; readable and writable |
| `generator` | The underlying `Generator` instance |
| `cache_handler` | `CacheHandler` managing the memoised convergents |
| `tail_convergent(n)` | $(h_n, k_n)$ for the tail $[a_1;\ldots,a_{n+1}]$; memoised |
| `convergent(n)` | $(a_0 k_n + h_n,\; k_n)$ — the full $n$-th convergent |
| `shift(n)` | New SCF with `integer_part + n`, sharing the same cache |
| `tail()` | New SCF with `integer_part = 0`, sharing the same generator and cache |
| `inverse()` | Multiplicative inverse $1/x$; result cached write-once in `_inverse` |
| `scf + k` / `k + scf` | Integer shift (delegates to `shift`) |

The attributes `_generator`, `_cache_handler`, and `tail_convergent` are frozen
after construction; any attempt to reassign them raises `AttributeError`.
`_inverse` is write-once: set by the first call to `inverse()` and immutable
thereafter.

#### `FiniteSimpleContinuedFraction`

Extends `SimpleContinuedFraction` with a fixed, indexable tail.

```python
FiniteSimpleContinuedFraction(partial_quotients, integer_part=0, dtype=None)
```

| Member | Description |
|--------|-------------|
| `partial_quotients` | Tail as an immutable tuple (materialises the full sequence) |
| `size` / `len(scf)` | Number of partial quotients |
| `terminal_convergent` | Last convergent — exact rational value of the SCF |
| `terminal_tail_convergent` | Last tail convergent |
| `to_decimal()` | Exact value as `decimal.Decimal` |
| `inverse()` | Multiplicative inverse; raises `ZeroDivisionError` for the zero value |
| `float(scf)` | Terminal convergent as Python `float` |
| `int(scf)` | `integer_part` |
| `bool(scf)` | `False` only when `integer_part == 0` and the tail is empty |
| `scf + scf` | Rational sum; returns a new `FiniteSimpleContinuedFraction` |

**Factory class methods:**

| Method | Input |
|--------|-------|
| `from_rational(r)` | `Fraction`, `(p, q)` tuple, or `int` |
| `from_float(f, max_denominator=None)` | Python `float` |
| `from_decimal(d)` | Finite decimal string, e.g. `"3.14"` |

---

#### `PeriodicSimpleContinuedFraction`

Represents an eventually-periodic SCF $[a_0;\, a_1, \ldots, a_k,\, \overline{b_1, \ldots, b_m}]$
corresponding to a quadratic irrational $(P + \sqrt{D})/Q$.

```python
PeriodicSimpleContinuedFraction(period, integer_part=0, pre_period=())
```

The `period` is a non-empty tuple of strictly positive integers; `pre_period`
(if given) is the finite non-repeating tail $[a_1, \ldots, a_k]$.

| Member | Description |
|--------|-------------|
| `period` | Repeating part as an immutable tuple |
| `pre_period` | Non-repeating tail prefix (empty tuple if purely periodic) |
| `quadratic_surd()` | Returns `(P, Q, D)` such that the SCF represents $(P + \sqrt{D})/Q$ |
| `quadratic_coefficients()` | Minimal polynomial coefficients $(A, B, C)$ with $Ax^2 + Bx + C = 0$ |
| `is_principal_surd()` | `True` when the surd satisfies $0 < x$ and $-1 < x' < 0$ (principal / reduced) |
| `is_conjugate_root()` | `True` when the surd is the conjugate of a principal surd |
| `conjugate()` | The conjugate surd $\hat{x} = (P - \sqrt{D})/Q$; result cached write-once |
| `inverse()` | Multiplicative inverse $1/x$; result cached write-once |
| `from_quadratic_surd(P, Q, D)` | Class method — construct from surd parameters directly |
| `float(scf)` | Decimal approximation via `as_decimal()` (50 significant digits by default) |
| `as_decimal(n_digits)` | Arbitrarily precise `Decimal` value |
| `-scf` | Negation; returns a new `PeriodicSimpleContinuedFraction` for $-x$ |

Key attributes (`_conjugate`, `_inverse`, `_quadratic_surd`, `_quadratic_coefficients`)
are write-once: computed on first access and frozen thereafter.

### `catena.generators`

| Class | Description |
|-------|-------------|
| `Generator(f)` | Validates that `f(n)` always returns a strictly positive `int`; avoids double-wrapping |
| `CachedGenerator(f)` | Like `Generator` but memoises results in an `OrdinalCache` |
| `FiniteGenerator(data, dtype=None)` | Fixed sequence; auto-selects the smallest unsigned `array` typecode (`B`/`H`/`I`/`L`/`Q`); falls back to `tuple` for values exceeding 64-bit range |
| `PeriodicGenerator(period, pre_period=())` | Repeating sequence; delegates to `FiniteGenerator` for each segment |

---

### `catena.cache`

`functools.lru_cache` / `functools.cache` bind the cache to a single function
with no public API to extract or share the underlying store.  `catena` needs
the cache to be an explicit, first-class object for three reasons:

- **Shareability.**  Two SCF instances with the same tail (e.g. `phi` and
  `phi + 2` after an integer shift) should share a single convergent cache.
  The same applies to an expensive recursive generator used by several SCFs —
  the computation should be paid once, not once per instance.
- **Pruning.**  `CacheHandler.prune_cache(n)` drops all entries below index
  `n`, letting callers free memory mid-computation without discarding the
  handler or its references.
- **Coherent reset.**  `CacheHandler.reset_cache()` clears the store while
  keeping the same handler object alive.  Because every SCF that shares a tail
  holds a reference to the same `CacheHandler`, a single reset is visible to
  all of them simultaneously — something that is impossible when the cache is
  private to each decorated function.

`CacheHandler` owns the underlying store and exposes it; `SetLightCache` and
`SetCache` are thin wrappers that delegate to it.

| Symbol | Description |
|--------|-------------|
| `Cache` | Append-only `UserDict`; raises `KeyError` if an existing key is overwritten |
| `OrdinalCache` | `Cache` restricted to integer keys; tracks `smallest_key` and `largest_key` |
| `CacheHandler` | Owns a `Cache`; records `call_count` (misses) and `read_count` (hits); supports `reset_cache()` and `prune_cache(n)` |
| `SetCache(func, cache_handler)` | Decorator/factory; keys by `(args, frozenset(kwargs))` |
| `SetLightCache(func, cache_handler)` | Lightweight variant for single-argument callables; keys by the argument directly |

---

### `catena.mathlib`

#### `core`

| Function | Description |
|----------|-------------|
| `get_sign(n)` | `1`, `-1`, or `0` |
| `simplify(p, q)` | Reduce fraction by $\gcd$; preserves signs |
| `canonicalize(p, q)` | `simplify` + ensure denominator is positive |
| `euclidean_step(p, q)` | Returns `(p//q, p%q, q)` — one step of the Euclidean algorithm |
| `quotent_sign(p, q)` | Sign of $p/q$ without division; `None` if $q = 0$ |

Type aliases: `IntPair = tuple[int, int]`, `IntTriplet = tuple[int, int, int]`.

#### `arithmetic`

| Function | Description |
|----------|-------------|
| `add_fractions(a, b)` | $a + b$ with GCD-based intermediate reduction |
| `multiply_fractions(a, b)` | $a \times b$ with cross-GCD reduction |
| `square_fraction(a)` | $a^2$ |
| `sandwich_fraction(a, b)` | $(p/q) \text{ sandwich } (r/s) = (ps, qr)$ |

Each function has an `u`-prefixed unpacked variant (e.g. `uadd_fractions(p, q, r, s)`) to avoid tuple construction overhead in hot paths.

#### `convert`

| Function | Description |
|----------|-------------|
| `from_rational_to_scf(r)` | `Rational` → `(a0, [a1, …])` via Euclidean algorithm |
| `from_float_to_rational(f, limit_denominator)` | `float` → `(p, q)` via `fractions.Fraction` |
| `from_float_to_scf(f, limit_denominator)` | Chains the two above |
| `from_decimal_to_rational(d)` | Finite decimal string → exact `(p, q)` in lowest terms |
| `from_quadratic_surd_to_scf(P, Q, D)` | $(P + \sqrt{D})/Q$ → `(a0, period, pre_period)` via integer-only Euclidean expansion |
| `from_quadratic_surd_to_conjugate_scf(P, Q, D)` | Conjugate surd $(-P + \sqrt{D})/(-Q)$ → same output format |

`Rational` alias: `Fraction | tuple[int, int] | int`.

#### `quadratic`

Pure-integer helpers for quadratic surds $(P + \sqrt{D})/Q$.

| Function | Description |
|----------|-------------|
| `simplify_quadratic_surd(P, Q, D)` | Divides $P$, $Q$ by $\gcd(P, Q)$ where the same factor divides $D$; returns `(P, Q, D)` |
| `normalize_quadratic_surd(P, Q, D)` | Full normalisation: simplify + ensure $Q > 0$ |
| `quadratic_roots_from_coefficients(A, B, C)` | Both roots of $Ax^2 + Bx + C = 0$ as `(P, Q, D)` pairs |
| `quadratic_surd_from_coefficients(A, B, C)` | The larger root of $Ax^2 + Bx + C = 0$ as a `(P, Q, D)` surd |

#### `metric`

| Function | Description |
|----------|-------------|
| `product_digit_count(arr)` | Total decimal digit count of $\prod arr$ (log-sum, no actual multiplication) |
| `product_digit_count_high_precision(arr)` | Same via `Decimal` for higher accuracy |
| `average_digit_count(arr)` | `product_digit_count(arr) / len(arr)` |

---

### `catena.strings`

| Function | Description |
|----------|-------------|
| `safe_int_str(n, n_trailing=99)` | Abbreviated repr for large integers, avoiding PEP 678 conversion limits |
| `safe_full_int_str(n)` | Full decimal string of arbitrarily large integers via chunked conversion |

---

## Design notes

**Zero dependencies.**  The library is pure Python and relies only on the
standard library (`fractions`, `decimal`, `array`, `collections`, `math`).

**Immutability by default.**  Core attributes of `SimpleContinuedFraction`,
`CacheHandler`, and related classes are frozen after construction.  Mutations
raise `AttributeError` early rather than silently producing wrong results.

**Two-layer convergent computation.**  `tail_convergent` computes the
recurrence for the tail $[a_1; a_2, \ldots]$ independently of $a_0$.  This
allows `shift` and integer addition to create new SCF views sharing a fully
populated cache without recomputation.  For periodic SCFs the same tail is
shared between an instance and its `inverse()` / `conjugate()` counterparts.

**Write-once inverse and conjugate.**  The first call to `inverse()` or
`conjugate()` on a `SimpleContinuedFraction` or `PeriodicSimpleContinuedFraction`
stores the result in a frozen attribute.  Subsequent calls return the cached
object directly, and the double-inverse / double-conjugate identity `x.inv().inv() is x`
holds by construction.

**Compact storage.**  `FiniteGenerator` automatically selects the smallest
unsigned `array.array` typecode that covers the value range, falling back to
a plain `tuple` only when values exceed the 64-bit ceiling.

---

## Running the tests

```bash
pytest testing/
```

The test suite uses a binary large-integer store (`testing/store/`) for
expensive pre-computed values.  It is rebuilt automatically when
`conftest._PRECOMPUTED` changes.

---

## Contributing

Contributions are welcome.  See [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines on setting up the development environment, running the test suite,
and the conventions used across the project.

---

## License

GPL-3.0-or-later

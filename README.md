# catena

A pure-Python library for working with **simple continued fractions** (SCFs).

`catena` provides three main abstractions: a generative SCF driven by an
arbitrary callable, a finite SCF backed by a compact fixed sequence, and a
periodic SCF representing quadratic irrationals.  All three share a memoised
two-layer convergent engine with a full arithmetic interface — including
negation, subtraction, multiplication, division, equality, and hashing for
finite SCFs, and equality / hashing for periodic SCFs.  The `catena.numbers`
subpackage provides named mathematical constants (`e`, `φ`, `√2`, …) and
deterministic Gauss-Kuzmin random SCF generators backed by SHA-256.

The library has **zero dependencies** and requires Python ≥ 3.12.

---

## Mathematical background

A simple continued fraction expresses a number as

```
        1
a₀ + ─────────────
          1
     a₁ + ────────
               1
          a₂ + ───
               ⋱
```

written compactly as `[a₀; a₁, a₂, …]`, where `a₀` is any integer and
`a₁, a₂, …` are strictly positive integers.
When the sequence is finite the expression represents a rational number exactly.

Convergents are the rational approximations obtained by truncating the expansion:

```
pₙ/qₙ  =  [a₀; a₁, …, aₙ]
```

They satisfy the two-term recurrence

```
pₙ = aₙ·pₙ₋₁ + pₙ₋₂,   qₙ = aₙ·qₙ₋₁ + qₙ₋₂
```

and are the best rational approximations to the value being expanded.

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
partial quotients on demand — so an infinite expansion like `√2` or `e`
is represented by a small, fixed-size object regardless of how many convergents
you compute.  Convergents are memoised as they are requested; you pay only for
what you use, and the cache is shared transparently when the same tail is viewed
with a different integer part.

`catena` also does not subclass `fractions.Fraction`.  Convergents produced by
the two-term recurrence are guaranteed to be in lowest terms — consecutive
convergents satisfy `pₙ·qₙ₋₁ − pₙ₋₁·qₙ = ±1`, so `gcd(pₙ, qₙ) = 1`
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
  represents numbers of the form `(P + √D) / Q` as eventually-periodic
  expansions.  Provides `quadratic_surd()`, `conjugate()`, `inverse()`,
  `from_quadratic_surd()`, and `__float__` / `as_decimal()`.
- **Generator manipulation** — all four generator types support `advance(n)`,
  `insert(fg, at)`, and `prepend(fg)` for slicing, splicing, and reordering
  partial-quotient sequences.  `CachedGenerator` variants optionally copy and
  re-index the memoised `BaseCache` across operations.
- **Full SCF arithmetic** — `FiniteSimpleContinuedFraction` supports `__neg__`,
  `__sub__`, `__mul__`, `__truediv__`, extended `__add__` (accepts `float`,
  `Fraction`, `Decimal`), `__eq__` (compares by exact rational value via
  `terminal_convergent`), and `__hash__`.  Periodic SCFs gain `__eq__` and
  `__hash__` via their `quadratic_surd()` triple.
- **Mathematical constants** — `catena.numbers.constants` provides ready-to-use
  SCF objects for `e`, `phi` (golden ratio), `sqrt2`, `sqrt3`, `sqrt5`, and a
  `metallic_mean(n)` factory for the entire metallic-mean family.
- **Deterministic random SCFs** — `catena.numbers.randoms` generates
  Gauss-Kuzmin-distributed partial quotients via a SHA-256 hash chain
  (`GaussKuzminSCF`, `GaussKuzminArbitrarySCF`).  A stateful `Seed` class
  ensures reproducibility and independence between successive callables.

Planned for future releases:

- **Best rational approximations** — direct extraction from the convergent sequence.
- **Pell's equation** — solutions via the periodic expansion of `√D`.
- **Farey sequences and mediants** — enumeration of rationals and their
  geometric interpretation as rational points in the plane.
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
print(scf2.terminal_convergent)  # (62831853, 20000000)
```

### Infinite (generative) SCF

```python
from catena import SimpleContinuedFraction

# Golden ratio  φ = [1; 1, 1, 1, ...]
phi = SimpleContinuedFraction(lambda n: 1, integer_part=1)

phi.tail_convergent(10)   # (89, 144) — exactly the same as the 10th convergent of [0; 1, 1, 1, ...]
phi.convergent(10)        # (233, 144) — 10th convergent of [1; 1, 1, 1, ...]

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
inv.inverse() is a              # True — cached reference, returns original object
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

### Generator manipulation

```python
from catena.generators import FiniteGenerator

fg = FiniteGenerator([3, 1, 4, 1, 5, 9])

# advance: skip the first n terms
list(fg.advance(2))              # [4, 1, 5, 9]

# insert: splice another FiniteGenerator at the given position
patch = FiniteGenerator([7, 7])
list(fg.insert(patch, at=1))    # [3, 7, 7, 1, 4, 1, 5, 9]

# prepend: shorthand for insert at 0
list(fg.prepend(patch))         # [7, 7, 3, 1, 4, 1, 5, 9]
```

### SCF arithmetic

```python
from catena import FiniteSimpleContinuedFraction
from fractions import Fraction

a = FiniteSimpleContinuedFraction.from_rational((3, 4))
b = FiniteSimpleContinuedFraction.from_rational((1, 4))

(a - b).terminal_convergent     # (1, 2)
(a * b).terminal_convergent     # (3, 16)
(a / b).terminal_convergent     # (3, 1)

# Operations with plain numbers
(a + 0.5).terminal_convergent   # (5, 4)

# Equality and hashing
a == Fraction(3, 4)             # True
len({a, b, a})                  # 2  — deduplicated via __hash__
```

### Mathematical constants

```python
from catena.numbers import constants

float(constants.e)              # 2.718281828459045
float(constants.phi)            # 1.618033988749895
float(constants.sqrt2)          # 1.4142135623730951

# Metallic means  [n; (n)]
float(constants.metallic_mean(2))    # 2.414213562373095  (silver mean)
float(constants.metallic_mean(3))    # 3.302775637731995  (bronze mean)
```

### Deterministic random SCFs

```python
from catena.numbers.randoms import GaussKuzminSCF, Seed

seed = Seed("my-experiment")
rng  = GaussKuzminSCF(seed)

# Factory methods produce different SCF types
scf  = rng.scf(integer_part=1)          # SimpleContinuedFraction
fsf  = rng.finite_scf(size=10)          # FiniteSimpleContinuedFraction, 10 quotients
pscf = rng.periodic_scf(period_size=4)  # PeriodicSimpleContinuedFraction

# Each factory call advances the seed — successive objects are independent
str(seed)    # Seed(initial_state=my-experiment, step=3)
```

---

## Project structure

```
catena/
├── __init__.py          # Public exports
├── catena.py            # SimpleContinuedFraction, FiniteSimpleContinuedFraction,
│                        #   PeriodicSimpleContinuedFraction
├── generators.py        # Generator, CachedGenerator, FiniteGenerator, PeriodicGenerator
├── cache.py             # BaseCache (self-computing append-only cache)
├── strings.py           # safe_int_str, safe_full_int_str
├── mathlib/
│   ├── __init__.py      # Re-exports all submodules
│   ├── core.py          # Type aliases, get_sign, simplify, canonicalize, euclidean_step
│   ├── arithmetic.py    # add_fractions, multiply_fractions, square_fraction, sandwich_fraction
│   ├── convert.py       # from_rational_to_scf, from_float_to_*, from_decimal_to_rational,
│   │                    #   from_quadratic_surd_to_scf, from_quadratic_surd_to_conjugate_scf
│   ├── quadratic.py     # simplify/normalize_quadratic_surd, quadratic_roots/surd_from_coefficients
│   └── metric.py        # product_digit_count, average_digit_count
└── numbers/
    ├── __init__.py      # Re-exports constants and randoms submodules
    ├── constants.py     # e, phi, sqrt2, sqrt3, sqrt5, metallic_mean(n)
    └── randoms.py       # Seed, GaussKuzminSHA, UniformSHAArbitrary,
                         #   GaussKuzminSHAArbitrary, RandomSCF,
                         #   GaussKuzminSCF, GaussKuzminArbitrarySCF

testing/
├── conftest.py                  # Session fixtures, large-integer store management
├── bigints.py                   # Deterministic large-integer generation and binary store
├── test_scf.py                  # SimpleContinuedFraction tests
├── test_finite_scf.py           # FiniteSimpleContinuedFraction tests
├── test_periodic_scf.py         # PeriodicSimpleContinuedFraction tests
├── test_generators.py           # Generator / CachedGenerator / FiniteGenerator / PeriodicGenerator tests
├── test_cache.py                # BaseCache tests
├── test_cache_weakrefs.py       # Weakref caching semantics: GC behaviour, recomputation, write-once guard
├── test_math_core.py            # mathlib.core tests
├── test_math_arithmetic.py      # mathlib.arithmetic tests
├── test_math_quadratic.py       # mathlib.quadratic + convert surd helpers tests
├── test_math_metric.py          # mathlib.metric tests
├── test_strings.py              # strings tests
├── test_numbers_constants.py    # catena.numbers.constants tests
└── test_numbers_randoms.py      # catena.numbers.randoms tests
```

---

## API reference

The full API reference and usage examples are hosted at:
**[lorenzosilvamoore.github.io/catena](https://lorenzosilvamoore.github.io/catena/)**

A formal write-up of the theory and implementation decisions is available as a PDF:
**[catena — Architecture, Algorithm Decisions, and Formal Theory](https://lorenzosilvamoore.github.io/catena/catena-theory.pdf)**

---

## Design notes

**Zero dependencies.**  The library is pure Python and relies only on the
standard library (`fractions`, `decimal`, `array`, `collections`, `math`).

**Immutability by default.**  Core attributes of `SimpleContinuedFraction`,
`BaseCache`, and related classes are frozen after construction.  Mutations
raise `AttributeError` early rather than silently producing wrong results.

**Two-layer convergent computation.**  `tail_convergent` computes the
recurrence for the tail $[a_1; a_2, \ldots]$ independently of $a_0$.  This
allows `shift` and integer addition to create new SCF views sharing a fully
populated cache without recomputation.  For periodic SCFs the same tail is
shared between an instance and its `inverse()` / `conjugate()` counterparts.

**Weakref-cached inverse and conjugate.**  The first call to `.inverse()` or
`.conjugate()` stores the result in a `weakref.ref` attribute.  Subsequent
calls return the live object directly if it is still reachable, or
transparently recompute and re-cache it otherwise.  The symmetric identity
`x.inverse().inverse() is x` holds while the intermediate object remains
reachable — the weakref prevents inverse/conjugate pairs from pinning each
other in memory.

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

Contributions are welcome.  See **[CONTRIBUTING.md](https://github.com/LorenzoSilvaMoore/catena/blob/main/CONTRIBUTING.md)** for
guidelines on setting up the development environment, running the test suite,
and the conventions used across the project.

---

## License

GPL-3.0-or-later

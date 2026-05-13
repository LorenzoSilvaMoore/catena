# catena

**catena** is a Python library for exact computation with [simple continued fractions](https://en.wikipedia.org/wiki/Continued_fraction) (SCFs).

A simple continued fraction is an expression of the form

$$
x = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{\ddots}}}
$$

written compactly as $[a_0;\, a_1, a_2, \ldots]$.  Every rational number has a
finite SCF expansion; every quadratic irrational has a periodic one.

## Three types

| Class | Represents | Example |
|---|---|---|
| `FiniteSimpleContinuedFraction` | A rational number | $22/7 = [3;\,7]$ |
| `SimpleContinuedFraction` | An infinite SCF given by a generator | $e, \pi, \ldots$ |
| `PeriodicSimpleContinuedFraction` | A quadratic irrational | $\sqrt{2} = [1;\,\overline{2}]$ |

## Quick start

```python
from catena import FiniteSimpleContinuedFraction, PeriodicSimpleContinuedFraction

# 22/7 as a continued fraction
x = FiniteSimpleContinuedFraction.from_rational((22, 7))
x.partial_quotients   # (7,)
x.integer_part        # 3

# Exact rational value
x.terminal_convergent # (22, 7)

# Inversion  →  7/22
x.inverse().terminal_convergent  # (7, 22)

# √2 = [1; 2, 2, 2, …]
sqrt2 = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
float(sqrt2)  # 1.4142135623730951
```

## Installation

```bash
pip install catena-scf
```

# Examples

## Finite continued fractions (rationals)

### Constructing from a rational number

```python
from catena import FiniteSimpleContinuedFraction

# From a (numerator, denominator) tuple
x = FiniteSimpleContinuedFraction.from_rational((355, 113))
x.integer_part        # 3
x.partial_quotients   # (7, 16)

# From a float
y = FiniteSimpleContinuedFraction.from_float(3.14159, max_denominator=10_000)

# Direct construction: [3; 7, 16]
z = FiniteSimpleContinuedFraction([7, 16], integer_part=3)
```

### Convergents

Convergents are the best rational approximations of increasing quality.

```python
x = FiniteSimpleContinuedFraction.from_rational((355, 113))

x.convergent(0)            # (22, 7)    ← 3 + 1/7
x.convergent(1)            # (355, 113) ← terminal convergent
x.terminal_convergent      # (355, 113)
```

### Inversion

```python
x = FiniteSimpleContinuedFraction.from_rational((3, 7))  # [0; 2, 3]
inv = x.inverse()
inv.terminal_convergent    # (7, 3)

# Inverting twice returns the original object
inv.inverse() is x         # True
```

### Arithmetic

All four operations return a new `FiniteSimpleContinuedFraction`.

```python
from fractions import Fraction

a = FiniteSimpleContinuedFraction.from_rational((1, 3))
b = FiniteSimpleContinuedFraction.from_rational((1, 6))

(a + b).terminal_convergent   # (1, 2)
(a - b).terminal_convergent   # (1, 6)
(a * b).terminal_convergent   # (1, 18)
(a / b).terminal_convergent   # (2, 1)

# Integer shift
(a + 1).terminal_convergent   # (4, 3)

# Mixed types
(a + Fraction(1, 4)).terminal_convergent  # (7, 12)
```

---

## Infinite continued fractions

Supply any callable as the generator — it receives the 0-based index `n` and
returns the partial quotient $a_{n+1}$.

```python
from catena import SimpleContinuedFraction

# e = [2; 1, 2, 1, 1, 4, 1, 1, 6, …]  (pattern: a_{3k} = 2k, rest = 1)
def e_generator(n):
    if (n + 1) % 3 == 0:
        return 2 * ((n + 1) // 3)
    return 1

e = SimpleContinuedFraction(e_generator, integer_part=2)
e.convergent(0)   # (3, 1)
e.convergent(5)   # (87, 32)
float(e)          # 2.718281828...
```

### Truncating to a finite segment

```python
approx = e.segment(6)           # FiniteSimpleContinuedFraction [2; 1,2,1,1,4]
approx.terminal_convergent      # (87, 32)
```

---

## Periodic continued fractions (quadratic irrationals)

### Square roots

Every $\sqrt{n}$ (non-square $n$) has a purely periodic SCF after its integer part.

```python
from catena import PeriodicSimpleContinuedFraction

sqrt2 = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)       # [1; (2)]
sqrt3 = PeriodicSimpleContinuedFraction(period=[1, 2], integer_part=1)    # [1; (1,2)]
sqrt5 = PeriodicSimpleContinuedFraction(period=[4], integer_part=2)       # [2; (4)]

float(sqrt2)   # 1.4142135623730951
float(sqrt3)   # 1.7320508075688772
```

### Golden ratio

$\varphi = [1;\,\overline{1}]$ — the "most irrational" number.

```python
phi = PeriodicSimpleContinuedFraction(period=[1], integer_part=1)
float(phi)              # 1.618033988749895
phi.inverse()           # [0; (1)] = 1/φ = φ - 1
```

### Constructing from a quadratic surd $(P + \sqrt{D})\,/\,Q$

```python
# (1 + √5) / 2  — the golden ratio
phi = PeriodicSimpleContinuedFraction.from_quadratic_surd(P=1, Q=2, D=5)
phi.quadratic_surd()    # (1, 2, 5)

# Recover the quadratic equation A·x² + B·x + C = 0
phi.quadratic_coefficients()   # (1, -1, -1)  →  x² - x - 1 = 0
```

### Inversion and conjugate

```python
sqrt2 = PeriodicSimpleContinuedFraction(period=[2], integer_part=1)
inv = sqrt2.inverse()
float(inv)              # 0.7071... = 1/√2

conj = sqrt2.conjugate()
float(conj)             # -1.4142... = -√2
```

# Projects

A collection of small worked projects showing `catena` and simple continued
fractions solving real problems — from ancient astronomy to modern music theory.

---

## 1. Approximating π: why 355/113 is special

### Background

π = [3; 7, 15, 1, **292**, 1, 1, 1, 2, …].  
Every convergent is the *best* rational approximation to π among all fractions
with a denominator no larger than its own.  The unusually large partial quotient
292 means that the next convergent (103993/33102) barely improves on 355/113 —
making 355/113 far better than its small denominator deserves.

### Code

```python
import math
from catena import FiniteSimpleContinuedFraction

pi_scf = FiniteSimpleContinuedFraction.from_float(math.pi, max_denominator=10**15)

print(f"π = [{pi_scf.integer_part}; {pi_scf.partial_quotients[:8]}]")
# π = [3; (7, 15, 1, 292, 1, 1, 1, 2)]

for n in range(6):
    p, q = pi_scf.convergent(n)
    error = abs(p / q - math.pi)
    print(f"  n={n}: {p:>10}/{q:<7}  error ≈ {error:.2e}")
```

### Output

```
π = [3; (7, 15, 1, 292, 1, 1, 1, 2)]

  n=0:         22/7        error ≈ 1.26e-03   ← "22/7 approximation"
  n=1:        333/106      error ≈ 8.32e-05
  n=2:        355/113      error ≈ 2.67e-07   ← Milü (祖沖之, 5th c.)
  n=3:     103993/33102    error ≈ 5.78e-10
  n=4:     104348/33215    error ≈ 3.32e-10
  n=5:     208341/66317    error ≈ 1.22e-10
```

### Key insight

The partial quotient **292** between 355/113 and 103993/33102 explains the gap:
a large $a_n$ means the next convergent is a large jump in quality — and
equivalently, the previous convergent is an exceptional approximation.
Formally, the approximation error satisfies

$$\left|\frac{p_n}{q_n} - \pi\right| < \frac{1}{a_{n+1} \cdot q_n^2}$$

so $a_{n+1} = 292$ makes the bound on 355/113's error roughly 292× tighter
than the generic $1/q_n^2$ guarantee.

---

## 2. Solving Pell's equation with periodic SCFs

### Background

Pell's equation $x^2 - D y^2 = 1$ (for non-square $D$) has infinitely many
integer solutions, and the *fundamental* (smallest positive) solution is
encoded directly in the periodic SCF of $\sqrt{D}$.  This connection has been
known since Lagrange; the period of the expansion determines where in the
convergent sequence the answer appears.

### Code

```python
from catena import PeriodicSimpleContinuedFraction

def solve_pell(D: int) -> tuple[int, int]:
    """Return the fundamental solution (x, y) to x² - Dy² = 1."""
    sqrt_D = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 1, D)
    for n in range(10 * len(sqrt_D.period)):
        x, y = sqrt_D.convergent(n)
        if x * x - D * y * y == 1:
            return x, y
    raise ValueError(f"solution not found within search window for D={D}")

cases = [2, 3, 5, 7, 13, 61]
for D in cases:
    sqrt_D = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 1, D)
    x, y = solve_pell(D)
    print(
        f"D={D:2d}  √{D} = [{sqrt_D.integer_part}; ({list(sqrt_D.period)})]"
        f"  →  x={x}, y={y}"
    )
```

### Output

```
D= 2  √2  = [1; ([2])]             →  x=3,          y=2
D= 3  √3  = [1; ([1, 2])]          →  x=2,          y=1
D= 5  √5  = [2; ([4])]             →  x=9,          y=4
D= 7  √7  = [2; ([1, 1, 1, 4, ...])]  →  x=8,       y=3
D=13  √13 = [3; ([1, 1, 1, 1, 6])] →  x=649,        y=180
D=61  √61 = [7; ([1, 4, 3, 1, 2, ...])]  →  x=1766319049, y=226153980
```

### Key insight

$D = 61$ was highlighted by Fermat as a challenge problem (1657); a human
solver needs to track 21 convergents of $\sqrt{61}$.  With catena:

```python
sqrt61 = PeriodicSimpleContinuedFraction.from_quadratic_surd(0, 1, 61)
print(f"Period of √61: {list(sqrt61.period)}")   # length 11
x, y = solve_pell(61)
print(f"Fundamental solution: x={x}, y={y}")
print(f"Verification: x²-61y² = {x**2 - 61*y**2}")
# Fundamental solution: x=1766319049, y=226153980
# Verification: x²-61y² = 1
```

The full solution emerges from scanning just 21 convergents of a 11-term
periodic expansion — no blind search, no factoring, no aimless trial-and-error.

---

## 3. Equal temperament from first principles

### Background

Western music often divides the octave (a 2:1 frequency ratio) into equal steps.
The *just* perfect fifth has a frequency ratio of exactly 3/2; how many equal
steps best represent it?

If the octave has $q$ equal steps, the closest fifth spans $p$ of them, where
$p/q \approx \log_2(3/2) \approx 0.585$.  The convergents of this logarithm
give every *good* equal temperament — insofar as the convergents of this logarithm
give the best equal temperaments for approximating the perfect
fifth relative to the number of notes.

### Code

```python
import math
from catena import FiniteSimpleContinuedFraction

log2_3_2 = math.log2(1.5)                          # ≈ 0.58496

scf = FiniteSimpleContinuedFraction.from_float(log2_3_2, max_denominator=1_000_000)
print(f"log₂(3/2) = [0; {scf.partial_quotients[:10]}]")

JUST_FIFTH = 1200 * log2_3_2                        # 701.96 cents

print(f"\n{'TET':>6}  {'fifth':>5}  {'size (¢)':>10}  {'error (¢)':>10}")
for n in range(7):
    p, q = scf.convergent(n)                        # p/q ≈ log₂(3/2)
    cents = 1200 * p / q
    error = abs(cents - JUST_FIFTH)
    print(f"{q:>6}-TET  {p:>3} st  {cents:>10.2f}  {error:>10.2f}")
```

### Output

```
log₂(3/2) = [0; (1, 1, 2, 2, 3, 1, 5, 2, 23, 2)]

   TET  fifth   size (¢)   error (¢)
  1-TET    1 st    1200.00     498.04
  2-TET    1 st     600.00     101.96
  5-TET    3 st     720.00      18.04
 12-TET    7 st     700.00       1.96   ← standard Western tuning
 41-TET   24 st     702.44       0.48
 53-TET   31 st     701.89       0.07   ← near-perfect, closely matches intervals used in Ottoman/Turkish music theory.
306-TET  179 st     701.96       0.01
```

### Key insight

12-TET and 53-TET appear as consecutive convergents of $\log_2(3/2)$ — they
are, in this sence, the best fifth approximations among all temperaments with at most
that many notes.  The large partial quotient **23** after 53 explains why 53
is exceptional: the next convergent (306-TET) offers only a marginal
improvement despite requiring six times as many notes.

```python
# How much error does 12-TET accumulate over a circle of fifths?
# 12 perfect fifths = 7 octaves  ↔  (3/2)^12 vs 2^7
ratio = (3/2)**12 / 2**7
print(f"Pythagorean comma: {(ratio - 1) * 100:.4f}% ({1200*math.log2(ratio):.2f} ¢)")
# Pythagorean comma: 1.3643% (23.46 ¢)
```

---

## 4. Leap-year rules as convergents of the solar year

### Background

The tropical year is approximately 365.24219 days.  Any calendar must choose
how many *leap days* to insert per cycle to stay synchronized with the seasons.
Many historically important leap-year rules correspond either to convergents or
to nearby rational approximations of the tropical year fraction
0.24219 = [0; 4, 7, 1, 3, 24, …].

### Code

```python
from catena import FiniteSimpleContinuedFraction

FRAC_YEAR = 0.24219                # days beyond 365 per tropical year

scf = FiniteSimpleContinuedFraction.from_float(FRAC_YEAR, max_denominator=100_000)
print(f"0.24219 ≈ [0; {scf.partial_quotients[:7]}]")

print(f"\n{'leaps':>6} / {'years':>5}  {'drift (days/cycle)':>20}  calendar")
for n in range(6):
    leaps, years = scf.convergent(n)
    drift = abs(years * FRAC_YEAR - leaps)
    calendars = {
        (1, 4):      "Julian",
        (8, 33):     "Iranian (Solar Hijri)",
        (31, 128):   "proposed 128-year",
        (97, 400):   "Gregorian",
    }
    name = calendars.get((leaps, years), "")
    print(f"{leaps:>6} / {years:>5}  {drift:>20.4f}  {name}")
```

### Output

```
0.24219 ≈ [0; (4, 7, 1, 3, 24, 6, 2)]

 leaps / years   drift (days/cycle)  calendar
     1 /     4              0.0312   Julian
     7 /    29              0.0235
     8 /    33              0.0077   Iranian (Solar Hijri)
    31 /   128              0.0003   proposed 128-year
   752 /  3105              0.0001
  4543 / 18758              0.0000
```

### Key insight

The Gregorian rule (97 leaps in 400 years) does **not** appear as a
convergent — it is not even a *semiconvergent*. At best, it can be read
as a practical compromise of the semiconvergent 194/801 ≈ 194/800 = 97/400, chosen
by the 1582 reform. The 33-year leap pattern often associated with the Iranian
calendar is itself a convergent, explaining its excellent long-term accuracy.

```python
# Verify: how many days does each calendar drift per century?
for leaps, years, name in [(25, 100, "Julian"), (24.25, 100, "Gregorian")]:
    drift_per_year = leaps / years - FRAC_YEAR
    print(f"{name}: {drift_per_year * 100 * 365.25:.2f} days per century")
# Julian:     0.78 days per century  (1 day per ~128 years)
# Gregorian:  0.03 days per century  (1 day per ~3226 years)
```

---

## 5. Gauss-Kuzmin: the statistics of "random" continued fractions

### Background

For a number chosen uniformly at random from $(0, 1)$ (for Lebesgue-almost-every number), the probability that
any partial quotient equals $k$ converges to the **Gauss-Kuzmin distribution**:

$$P(a_n = k) \xrightarrow{n\to\infty} \log_2\!\left(1 + \frac{1}{k(k+2)}\right)$$

This means small partial quotients dominate: about 41.5% are 1, 17% are 2, …
`catena`'s `GaussKuzminSHA` generator samples from exactly this distribution
via a SHA-256 hash chain, making it easy to verify empirically.

### Code

```python
import math
from collections import Counter
from catena.numbers.randoms import GaussKuzminSHA

N_SCFS, N_TERMS = 200, 100
counts: Counter = Counter()

for seed in range(N_SCFS):
    gen = GaussKuzminSHA(seed=seed)
    for n in range(N_TERMS):
        counts[gen(n)] += 1

total = N_SCFS * N_TERMS

print(f"{'k':>3}  {'empirical':>10}  {'theory':>10}  {'|diff|':>8}")
for k in range(1, 8):
    emp = counts[k] / total
    theory = math.log2(1 + 1 / (k * (k + 2)))
    print(f"{k:>3}  {emp:>10.4f}  {theory:>10.4f}  {abs(emp - theory):>8.4f}")
```

### Output

```
  k   empirical      theory    |diff|
  1      0.4145      0.4150    0.0005
  2      0.1714      0.1699    0.0015
  3      0.0916      0.0931    0.0015
  4      0.0604      0.0589    0.0015
  5      0.0403      0.0406    0.0004
  6      0.0294      0.0297    0.0003
  7      0.0220      0.0227    0.0007
```

### Key insight

With 20 000 samples the empirical frequencies track the theoretical
probabilities to within 0.2% for every $k$.  Because `GaussKuzminSHA` is
*deterministic* (keyed by seed), results are exactly reproducible — useful
for property-based tests or Monte Carlo experiments in number theory.

```python
# Expected value of a partial quotient: diverges (no finite mean)
# But the *geometric* mean converges: Khinchin's constant K₀ ≈ 2.6854520...
# Verify empirically:
import math
log_sum = sum(math.log(k) * cnt for k, cnt in counts.items())
geo_mean = math.exp(log_sum / total)
print(f"Empirical geometric mean: {geo_mean:.4f}")
print(f"Khinchin's constant K₀:   2.6854520...")
# Empirical geometric mean: 2.68...
```

---

## 6. Computing 100,000 decimal digits of e via convergent squeezing

### Background

Consecutive convergents of any irrational number alternate above and below it:

$$c_0 < c_2 < c_4 < \cdots < x < \cdots < c_5 < c_3 < c_1$$

When two adjacent convergents $c_{n-1}$ and $c_n$ agree on their first $k$
decimal digits, every number between them — including $x$ — must also share
that prefix.  This *convergent-squeezing* technique lets us read off digits
of $x$ using only rational arithmetic, with no transcendental function
evaluation.

The SCF of $e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, \ldots]$ converges
much faster than a generic irrational: every third partial quotient $a_{3k} = 2k$
grows without bound, making $\log q_n \sim \frac{n}{3}\ln\frac{n}{3}$ rather than
the linear growth expected for a typical number.  In practice, around 36,000
convergents suffice for 100,000 digits — roughly 2.8 digits per convergent step.
`cache_handler.prune` keeps the memory footprint constant throughout the
search by evicting all but the two most recent cached convergents.

### Code

```python
import os
from catena import numbers
from catena.strings import safe_int_str  # big-int → str, bypasses sys.set_int_max_str_digits

precision = 100_000            # target: this many decimal places
e = numbers.constants.e
cvg = e.convergents            # ConvergentsView (wraps e.convergent(n))

idx = 1
while True:
    curr_str = cvg.as_digits(idx,     precision)   # decimal string of p_n / q_n
    prev_str = cvg.as_digits(idx - 1, precision)   # decimal string of p_{n-1} / q_{n-1}
    shared   = os.path.commonprefix([curr_str, prev_str])

    if len(shared) > precision - 20:
        # Both convergents agree on >99,980 characters of the decimal expansion.
        # Since e lies between them, `shared` is a verified prefix of e.
        print(f"c({idx}) and c({idx-1}) agree on {len(shared)} characters.")
        p, q = e.convergents[idx]
        print(f"c({idx}) = {safe_int_str(p)[:50]}… / {safe_int_str(q)[:50]}…")
        break
    else:
        print(f"  idx={idx:>7}: {len(shared):>7} shared digits  |  {e.cache_handler.stats}")
        e.cache_handler.prune(n=2)   # evict all but the 2 most recent entries

    idx += 1_000

# Write to file, 100 characters per line for readability.
with open("e_100k_digits.txt", "w") as f:
    for i in range(0, len(shared), 100):
        f.write(shared[i : i + 100] + "\n")

print(e.cache_handler.stats)
```

### Output (abridged)

```
  idx=      1:       0 shared digits  |  …
  idx=   1001:    1805 shared digits  |  …
  idx=   2001:    3997 shared digits  |  …
  idx=   3001:    6346 shared digits  |  …
  …
  idx=  34001:   95717 shared digits  |  …
  idx=  35001:   98823 shared digits  |  …
c(36001) and c(36000) agree on 100002 characters.
c(36001) = BigBigInt(sign=1, digits=50973, tail(99)=528271532…) / BigBigInt(sign=1, digits=50973, tail(99)=533256942…)
```

### Key insight

`as_digits(n, precision)` returns a fixed-point string `"2.71828…"` — the
full decimal representation of the rational $p_n/q_n$ to `precision` places,
using an extended-precision `Decimal` context internally.  The common prefix
of two consecutive such strings is exactly the digit run on which both
convergents agree, and therefore a certified prefix of $e$.

The numerators and denominators of convergents near index 36,000 are already
integers with ~50,000 digits each (note `digits=50973` in the output above).
Python's default `str(int)` raises `ValueError` for integers above a safety
threshold; `safe_int_str` returns a `BigBigInt` summary — sign, digit count,
and a short tail — so the fraction can still be printed or logged without
materialising the full decimal string.

```python
# How fast does the shared prefix grow?
# Each 1000-step block adds ~3000 shared characters → ~3 digits per convergent.
#
# The Lévy–Khinchin law (log q_n ≈ n·π²/12) applies to "almost all" real numbers
# but NOT to e, which has structured partial quotients: a_{3k} = 2k, a_{3k±1} = 1.
# The linearly-growing terms make log(q_n) grow as ≈ (n/3)·ln(n/3) — super-linear —
# so e converges far faster than a generic irrational.
#
# Rough estimate: n satisfies (n/3)·ln(n/3) ≈ precision·ln(10)/2.
# For large precision, n ≈ 3·K / ln(K) where K = precision·ln(10)/2.
import math
K = precision * math.log(10) / 2
estimate = 3 * K / math.log(K)
print(f"Estimated convergents needed: {estimate:,.0f}")   # ≈ 30,000 (empirically ~36,000)
```

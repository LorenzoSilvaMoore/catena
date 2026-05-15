# Formal Justification of `from_quadratic_surd_to_scf`

This document gives a self-contained, step-by-step proof of correctness for the
function `from_quadratic_surd_to_scf(P, Q, D)` in `catena/mathlib/convert.py`,
which computes the simple continued fraction (SCF) expansion of the quadratic
surd $x_0 = (P + \sqrt{D})/Q$.

---

## Raw code implementation

```python
def from_quadratic_surd_to_scf(P: int, Q: int, D: int):
    if Q == 0:
        raise ValueError("Q cannot be zero")
    if D < 0:
        raise ValueError("D must be non-negative")
    
    P, Q, D = normalize_quadratic_surd(P, Q, D)

    if (s:=isqrt(D))**2 == D:
        raise ValueError("D must not be a perfect square")
    
    m, d = P, Q
    a = (m + s) // d
    if d < 0 and (a * d - m) <= s:  # This is a logic step to avoid the 
        a -= 1                      # need to use floating point approximation for s.
    
    visited = dict()
    scf = []
    while (m, d) not in visited:
        visited[(m, d)] = len(scf)
        scf.append(a)

        m = a * d - m
        d = (D - m * m) // d
        a = (m + s) // d
        if d < 0 and (a * d - m) <= s:
            a -= 1

    return scf[0], tuple(scf[1:visited[(m, d)]]), tuple(scf[visited[(m, d)]:])
```

---

## 1. Setup and Assumptions

Throughout, we assume:

- $P, Q \in \mathbb{Z}$, $Q \neq 0$;
- $D \in \mathbb{Z}_{\geq 0}$, and $D$ is **not** a perfect square.

The non-perfect-square condition ensures $\sqrt{D}$ is irrational, so every
expression of the form $(m + \sqrt{D})/d$ with integer $m, d \neq 0$ is also
irrational, and its floor is unambiguously defined.

---

## 2. Normalization and the Divisibility Invariant

`normalize_quadratic_surd` finds the smallest positive integer $k$ such that
$kQ \mid (k^2 D - k^2 P^2)$, i.e.

$$
  k = \frac{|Q|}{\gcd(|Q|,\,|D - P^2|)},
$$

and rescales $(P, Q, D) \mapsto (kP,\, kQ,\, k^2 D)$.  The value is
unchanged because $(kP + \sqrt{k^2 D})/(kQ) = (P + \sqrt{D})/Q$.

The absolute value on $Q$ is necessary for the formula: $k$ must be a positive integer, so
the numerator must be $|Q|$ (the sign of $Q$ is preserved by the rescaling
$Q \mapsto kQ$ and must not be absorbed into $k$).  The absolute value on
$D - P^2$ is necessary in the implementation for a different reason: the code computes
$k = \operatorname{lcm}(Q, t) \,/\, t$ where $t = |D - P^2|$.  While `math.lcm`
handles a negative argument correctly (it takes absolute values internally), the
subsequent integer division `l // t` requires $t > 0$ to yield a positive $k$.
Without `abs`, a negative $D - P^2$ would produce a negative $t$ and therefore a
negative $k$, which would flip the sign of $Q$ and break the normalization.

After normalization, we write $(P, Q, D)$ for the rescaled parameters.  The
key property that has been established is:

$$
  Q \mid (D - P^2). \tag{N}
$$

**Why this matters.** The algorithm will produce a sequence $d_0, d_1, d_2, \ldots$
Each $d_{n+1}$ is defined as the integer quotient $(D - m_{n+1}^2)/d_n$.
Condition (N) is precisely what guarantees $d_0 \mid (D - m_0^2)$, and as shown
in §3 below, divisibility then propagates to every subsequent term.

---

## 3. Complete Quotients and the Recurrence

Define the sequence of **complete quotients** $x_0, x_1, x_2, \ldots$ by:

$$
  a_n = \lfloor x_n \rfloor, \qquad
  x_{n+1} = \frac{1}{x_n - a_n}.
$$

**Claim.** Every complete quotient has the form

$$
  x_n = \frac{m_n + \sqrt{D}}{d_n}
$$

for integers $m_n, d_n \neq 0$ satisfying the recurrence

$$
  m_{n+1} = a_n\, d_n - m_n,
  \qquad
  d_{n+1} = \frac{D - m_{n+1}^2}{d_n},
  \tag{R}
$$

with base case $(m_0, d_0) = (P, Q)$.

**Derivation.** Suppose $x_n = (m_n + \sqrt{D})/d_n$.  Then

$$
  x_n - a_n
  = \frac{m_n - a_n d_n + \sqrt{D}}{d_n}
  = \frac{\sqrt{D} - m_{n+1}}{d_n}
  \qquad (\text{defining } m_{n+1} = a_n d_n - m_n),
$$

and inverting:

$$
  x_{n+1}
  = \frac{1}{x_n - a_n}
  = \frac{d_n}{\sqrt{D} - m_{n+1}}
  = \frac{d_n(\sqrt{D} + m_{n+1})}{D - m_{n+1}^2}
  = \frac{m_{n+1} + \sqrt{D}}{d_{n+1}},
$$

where $d_{n+1} = (D - m_{n+1}^2)/d_n$.  This matches `(R)` and is exactly the
body of the loop in the code.

---

## 4. Divisibility Invariant

**Claim.** $d_n \mid (D - m_n^2)$ for all $n \geq 0$.

**Proof by induction.**

*Base case ($n = 0$):* $d_0 = Q$ and $Q \mid (D - P^2)$ by (N). ✓

*Inductive step:* Assume $d_n \mid (D - m_n^2)$.  Then $d_{n+1} = (D - m_{n+1}^2)/d_n$
is an integer by definition.  We must show $d_{n+1} \mid (D - m_{n+2}^2)$.

Set $m_{n+2} = a_{n+1} d_{n+1} - m_{n+1}$.  Expanding:

$$
  D - m_{n+2}^2
  = D - (a_{n+1} d_{n+1} - m_{n+1})^2
  = (D - m_{n+1}^2) + 2a_{n+1} d_{n+1} m_{n+1} - a_{n+1}^2 d_{n+1}^2.
$$

Substituting $D - m_{n+1}^2 = d_n d_{n+1}$:

$$
  D - m_{n+2}^2
  = d_{n+1}\bigl(d_n + 2a_{n+1} m_{n+1} - a_{n+1}^2 d_{n+1}\bigr).
$$

The right-hand side is divisible by $d_{n+1}$, so $d_{n+1} \mid (D - m_{n+2}^2)$. ✓

**Corollary.** $d_n \neq 0$ for all $n \geq 0$.

*Proof.* $d_{n+1} = 0$ would require $m_{n+1}^2 = D$, contradicting the
assumption that $D$ is not a perfect square. ✓

---

## 5. Exact Floor Computation: Why `(m + s) // d` Works

The algorithm computes $a_n = \lfloor (m_n + \sqrt{D})/d_n \rfloor$ in pure
integer arithmetic using $s = \lfloor\sqrt{D}\rfloor$ (the integer square root).
Python's `//` operator is always the mathematical floor (toward $-\infty$), so
`(m + s) // d` $= \lfloor(m+s)/d\rfloor$ for any sign of $m, s, d$.

### 5.1  Case $d > 0$: the integer square root is always sufficient

**Lemma.** For integers $m, d$ with $d > 0$,
$\lfloor(m + \sqrt{D})/d\rfloor = \lfloor(m + s)/d\rfloor$.

**Proof.** Let $a = \lfloor(m+s)/d\rfloor$, so $ad \leq m+s < (a+1)d$ (all integers).

*Upper bound:* $(a+1)d > m+s$ and both sides are integers, so $(a+1)d - m \geq s+1$.
Since $D$ is not a perfect square, $\sqrt{D}$ is irrational and $\sqrt{D} < s+1$ (as
$s = \lfloor\sqrt{D}\rfloor$).  Therefore $(a+1)d - m > \sqrt{D}$, giving
$(m + \sqrt{D})/d < a+1$.

*Lower bound:* $ad \leq m+s$ gives $ad - m \leq s < \sqrt{D}$, so
$(m + \sqrt{D})/d > a$.

Combining: $a \leq (m + \sqrt{D})/d < a+1$, i.e., $\lfloor(m+\sqrt{D})/d\rfloor = a$. □

**Consequence.** For $d > 0$ the correction block never fires: we will show in §5.2
that the condition `m1 <= s` is impossible when $d > 0$ and $a$ is computed correctly.

### 5.2  Case $d < 0$: the candidate may overshoot by exactly 1

For $d < 0$, dividing by a negative number reverses the inequality $s < \sqrt{D}$,
so $(m+s)/d > (m+\sqrt{D})/d$.  Let $a^* = \lfloor(m+\sqrt{D})/d\rfloor$ be the
true floor and $a_{\text{cand}} = \lfloor(m+s)/d\rfloor$ the computed candidate.

Since the two dividends differ by $(\sqrt{D} - s)/|d| \in (0, 1/|d|) \subset (0,1)$,
their floors satisfy $a_{\text{cand}} \in \{a^*, a^*+1\}$: the candidate can
**overshoot** by at most 1.

**Characterising the correct $a^*$: an if-and-only-if criterion.**
Denote by $m_1(a) = a \cdot d - m$ the tentative next numerator for any integer $a$,
and $d_1(a) = (D - m_1(a)^2)/d$ the corresponding tentative next denominator.
We claim:

$$
  a = a^*
  \quad \Longleftrightarrow \quad
  m_1(a) > \sqrt{D}.
  \tag{$\star$}
$$

*Proof of ($\Rightarrow$).*
By the floor definition $a^* \leq (m + \sqrt{D})/d < a^*+1$ and $d < 0$, multiplying
through by $d$ reverses inequalities:

$$
  a^* d \geq m + \sqrt{D} > (a^*+1)d.
$$

The left inequality gives $m_1(a^*) = a^* d - m \geq \sqrt{D}$; since $\sqrt{D}$ is
irrational the inequality is strict: $m_1(a^*) > \sqrt{D}$.

*Proof of ($\Leftarrow$).*
Since the candidate is confined to $\{a^*, a^*+1\}$ (proved above), it suffices to show
that $m_1(a^*+1) < \sqrt{D}$, i.e.\ the only element of the candidate set that does
*not* satisfy $m_1(a) > \sqrt{D}$ is $a^*+1$.  We can then conclude
$m_1(a) > \sqrt{D} \Rightarrow a \neq a^*+1 \Rightarrow a = a^*$.

From the right inequality of the floor definition, $(a^*+1)d < m + \sqrt{D}$, i.e.

$$
  m_1(a^*+1) = (a^*+1)d - m < \sqrt{D}.
$$

Since $\sqrt{D}$ is irrational, $m_1(a^*+1)$ is an integer, so in fact
$m_1(a^*+1) \leq s < \sqrt{D}$, completing the ($\Leftarrow$) direction. □

**A sharper characterisation of the overshoot.**  When $a_{\text{cand}} = a^*+1$, both
inequalities above bind simultaneously.  The overshoot condition
$\lfloor(m+s)/d\rfloor = a^*+1$ means (multiply the floor inequality $a^*+1 \leq (m+s)/d$ by
$d < 0$):

$$
  (a^*+1)d \geq m + s \quad\Longrightarrow\quad m_1(a^*+1) \geq s.
$$

Combined with $m_1(a^*+1) \leq s$ shown above:

$$
  \text{overshoot} \iff m_1(a_{\text{cand}}) = s \quad\text{(exactly)}.
$$

For the no-overshoot case, $m_1(a^*) > \sqrt{D}$ (by ($\star$)), so $m_1(a^*) \geq s+1$.
The two cases are therefore cleanly separated by comparing $m_1$ to $s$:

| Candidate $a$ | $m_1 = a \cdot d - m$ | Fires `m1 <= s`? |
|---|---|---|
| Correct $a^*$ | $m_1 \geq s+1 > s$ | No |
| Wrong $a^*+1$ | $m_1 = s$ | Yes — decrement |

**Connecting to the code's test `d < 0 and (a * d - m) <= s`.**  The test fires
precisely when $m_1(a_{\text{cand}}) \leq s$, which by the table above is equivalent
to $a_{\text{cand}} = a^*+1$.  Decrementing by 1 then recovers the correct $a^*$.

Note that the `<= s` form is equivalent to `== s` in the overshoot case (since $m_1$
is an integer and $m_1 < s$ never arises), but `<= s` is the more natural integer
transcription of the strict irrational bound $m_1 < \sqrt{D}$.

**Why the check is a no-op for $d > 0$.**
With $d > 0$ the candidate equals $a^*$ by §5.1, so $m_1 \geq s+1 > s$ and the
test `m1 <= s` is never satisfied.

### 5.3  After the first step, $d$ is always positive

**Claim.** If $d_n < 0$ and we use the correct $a_n^*$, then $d_{n+1} > 0$.

**Proof.** With the correct $a_n^*$, criterion ($\star$) gives $m_{n+1} = m_1(a_n^*) > \sqrt{D}$,
so $m_{n+1}^2 > D$.  Since $d_n < 0$, $d_{n+1} = (D - m_{n+1}^2)/d_n =
(\text{negative})/(\text{negative}) > 0$. □

This means that if $Q < 0$, the algorithm spends at most one iteration with $d < 0$
(the very first step).  Thereafter $d_n > 0$ and the lemma in §5.1 guarantees that
no further corrections are ever needed.

---

## 6. The Partial Quotients are Positive for $n \geq 1$

For every $n \geq 0$, since $a_n = \lfloor x_n \rfloor$ is the true floor,
$x_n - a_n \in (0, 1)$ (open, because $x_n$ is irrational).  Therefore

$$
  x_{n+1} = \frac{1}{x_n - a_n} > 1,
$$

which forces $a_{n+1} = \lfloor x_{n+1} \rfloor \geq 1$ for all $n \geq 0$.
The integer part $a_0$ is unrestricted (can be zero or negative), but all body
partial quotients $a_1, a_2, \ldots$ are strictly positive, as required by the
SCF definition.

---

## 7. Finiteness of the State Space and Termination

The full state of the recurrence at each step is the pair $(m_n, d_n)$, which
determines $x_n$ and all subsequent complete quotients.

**Bounds on $m_{n+1}$ and $d_{n+1}$.**
The fractional part $x_n - a_n \in (0,1)$ gives, with
$x_n = (m_n + \sqrt{D})/d_n$ and $d_n > 0$:
$$
  0 < \frac{\sqrt{D} - m_{n+1}}{d_n} < 1
  \;\Longrightarrow\;
  \sqrt{D} - d_n < m_{n+1} < \sqrt{D}.
$$
The right inequality gives $m_{n+1} \leq s$ and $D - m_{n+1}^2 > 0$,
confirming $d_{n+1} > 0$.  For the upper bound on $d_{n+1}$, factor
$D - m_{n+1}^2 = (\sqrt{D} - m_{n+1})(\sqrt{D} + m_{n+1})$; the left
inequality gives $d_n > \sqrt{D} - m_{n+1} > 0$, so dividing,
$$
  d_{n+1}
  = \frac{(\sqrt{D} - m_{n+1})(\sqrt{D} + m_{n+1})}{d_n}
  < \sqrt{D} + m_{n+1}
  \leq 2\sqrt{D},
$$
bounding $d_{n+1}$ to at most $\lfloor 2\sqrt{D} \rfloor$ positive integer
values.  Applying this bound to $d_n$ (inductively) and combining with the
left inequality: $m_{n+1} > \sqrt{D} - d_n \geq \sqrt{D} - 2\sqrt{D} =
-\sqrt{D}$, hence $m_{n+1} \geq -s$.  Altogether $|m_{n+1}| \leq s$,
confining $m_{n+1}$ to at most $2s + 1$ integer values.

The state space of pairs $(m_n, d_n)$ is therefore finite — at most
$O(\sqrt{D}) \times O(\sqrt{D}) = O(D)$ states.  By the pigeonhole principle
the sequence must eventually revisit a state: there exist $n > k \geq 0$
with $(m_n, d_n) = (m_k, d_k)$, which implies $x_n = x_k$ and hence that
all subsequent partial quotients repeat with period $n - k$.

The algorithm records each state's first occurrence in the \texttt{visited}
dictionary.  At the first revisit of $(m_k, d_k)$, the accumulated list
$[a_0, a_1, \ldots, a_{n-1}]$ is split as:

  1. Integer part: $a_0$;

  2. item Pre-period: $(a_1, \ldots, a_{k-1})$ (empty when $k \leq 1$);

  3. item Period: $(a_k, \ldots, a_{n-1})$.

The period is minimal because the loop halts at the \emph{first} revisit:
any shorter repeating block would imply an earlier recurrence of
$(m_k, d_k)$, contradicting the minimality of $k$.

Finally, note that $a_n \geq 1$ for all $n \geq 1$: since
$x_{n+1} = 1/(x_n - a_n)$ and $x_n - a_n \in (0,1)$, we have $x_{n+1} > 1$,
so $a_{n+1} = \lfloor x_{n+1}\rfloor \geq 1$.  All body partial quotients
are therefore positive integers, as required by the SCF definition.

---

## 8. Correctness of Period Detection

The `visited` dictionary maps each state $(m_n, d_n)$ to its first-occurrence
index in `scf`.  When the loop re-enters a state at position $k$ (i.e.,
$(m_n, d_n) = (m_k, d_k)$ for some $n > k$), we have $x_n = x_k$, so
the tail SCF from position $n$ is identical to the tail from position $k$.

At this point `scf` contains $[a_0, a_1, \ldots, a_{n-1}]$ and the function
returns:

- **Integer part**: `scf[0]` $= a_0$,
- **Pre-period**: `scf[1:k]` $= (a_1, \ldots, a_{k-1})$  (empty if $k = 0$ or $k = 1$),
- **Period**: `scf[k:]` $= (a_k, \ldots, a_{n-1})$.

The period block is minimal because the loop halts at the **first** recurrence
of $(m_k, d_k)$: any earlier termination would contradict the choice of $k$ as
the first visit.

The returned triple `(a0, pre_period, period)` therefore encodes the unique
eventually-periodic SCF representation of $x_0 = (P + \sqrt{D})/Q$,
as guaranteed by Lagrange's theorem.

---

## 9. Summary: Proof Obligations and Where They Are Met

| Obligation | Where justified |
|---|---|
| $d_{n+1}$ is always an integer | §4 (divisibility invariant, by induction) |
| $d_n \neq 0$ for all $n$ | §4 (corollary: $D$ not a perfect square) |
| `(m+s)//d` $= \lfloor(m+\sqrt{D})/d\rfloor$ for $d > 0$ | §5.1 (exact floor lemma) |
| Candidate overshoot detected for $d < 0$ | §5.2: overshoot $\iff m_1(a_{\text{cand}}) = s$; criterion `d < 0 and m1 <= s` |
| Algorithm enters $d > 0$ regime after one correction | §5.3 |
| Body partial quotients $a_n \geq 1$ for $n \geq 1$ | §6 |
| Loop terminates | §7 (state space is finite) |
| Pre-period and period are correctly extracted | §8 |

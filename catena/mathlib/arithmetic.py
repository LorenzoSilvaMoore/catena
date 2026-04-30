
from .core import (
    IntPair,
    gcd
    )

def add_fractions(a: IntPair, b: IntPair) -> IntPair:
    """
    Adds two fractions represented as tuples of (numerator, denominator).
    Reduces intermediate values by first dividing out gcd(q, s) before
    multiplying, then simplifying the resulting numerator. It also has the
    side effect of returning a canonicalized result when the input fractions 
    are in their canonical form, since the denominator since the denominator
    is guaranteed to be positive.

    Args:
        a (IntPair): The first fraction as a tuple (numerator, denominator).
        b (IntPair): The second fraction as a tuple (numerator, denominator).

    Returns:
        IntPair: The result of the addition as a simplified fraction.
    """
    return uadd_fractions(*a, *b)


def uadd_fractions(p: int, q: int, r: int, s: int) -> IntPair:
    """
    Adds two fractions represented as tuples of (numerator, denominator).
    Reduces intermediate values by first dividing out gcd(q, s) before
    multiplying, then simplifying the resulting numerator. It also has the
    side effect of returning a canonicalized result when the input fractions 
    are in their canonical form, since the denominator since the denominator
    is guaranteed to be positive.

    Args:
        p (int): The numerator of the first fraction.
        q (int): The denominator of the first fraction.
        r (int): The numerator of the second fraction.
        s (int): The denominator of the second fraction.

    Returns:
        IntPair: The result of the addition as a simplified fraction.
    """
    g1 = gcd(q, s)
    q1, s1 = q // g1, s // g1
    num = p * s1 + r * q1
    g2 = gcd(num, g1)
    return num // g2, q1 * (s // g2)


def multiply_fractions(a: IntPair, b: IntPair) -> IntPair:
    """
    Multiplies two fractions represented as tuples of (numerator, denominator).
    Reduces intermediate values by first dividing out gcd(p, s) and gcd(r, q)
    before multiplying, then simplifying the resulting numerator. It also has
    the side effect of returning a canonicalized result, since the denominator 
    is guaranteed to be positive.

    Args:
        a (IntPair): The first fraction as a tuple (numerator, denominator).
        b (IntPair): The second fraction as a tuple (numerator, denominator).

    Returns:
        IntPair: The result of the multiplication as a simplified fraction.
    """
    return umultiply_fractions(*a, *b)


def umultiply_fractions(p: int, q: int, r: int, s: int) -> IntPair:
    """
    Multiplies two fractions represented as separate numerator and denominator integers.
    Reduces intermediate values by first dividing out gcd(p, s) and gcd(r, q)
    before multiplying, then simplifying the resulting numerator. It also has
    the side effect of returning a canonicalized result, since the denominator 
    is guaranteed to be positive.

    Args:
        p (int): The numerator of the first fraction.
        q (int): The denominator of the first fraction.
        r (int): The numerator of the second fraction.
        s (int): The denominator of the second fraction.

    Returns:
        IntPair: The result of the multiplication as a simplified fraction.
    """
    g1 = gcd(p, s)
    g2 = gcd(r, q)
    return (p // g1) * (r // g2), (q // g2) * (s // g1)


def square_fraction(a: IntPair) -> IntPair:
    """
    Squares a fraction represented as a tuple of (numerator, denominator).
    It assumes that the fraction is already in its simplest form, so it simply
    squares the numerator and denominator without further reduction.

    Args:
        a (IntPair): The fraction to be squared as a tuple (numerator, denominator).

    Returns:
        IntPair: The result of the squaring as a fraction.
    """
    return usquare_fraction(*a)


def usquare_fraction(p: int, q: int) -> IntPair:
    """
    Squares a fraction represented as separate numerator and denominator integers.
    It assumes that the fraction is already in its simplest form, so it simply
    squares the numerator and denominator without further reduction.

    Args:
        p (int): The numerator of the fraction.
        q (int): The denominator of the fraction.

    Returns:
        IntPair: The result of the squaring as a fraction.
    """
    return p * p, q * q


def sandwich_fraction(a: IntPair, b: IntPair) -> IntPair:
    """
    Computes the "sandwich" of two fractions represented as tuples of (numerator, denominator).
    The sandwich is defined as (p*s, q*r) for fractions (p/q) and (r/s).

    Args:
        a (IntPair): The first fraction as a tuple (numerator, denominator).
        b (IntPair): The second fraction as a tuple (numerator, denominator).

    Returns:
        IntPair: The result of the sandwich operation as a fraction.
    """
    return usandwich_fraction(*a, *b)


def usandwich_fraction(p: int, q: int, r: int, s: int) -> IntPair:
    """
    Computes the "sandwich" of two fractions represented as separate numerator and denominator integers.
    The sandwich is defined as (p*s, q*r) for fractions (p/q) and (r/s).

    Args:
        p (int): The numerator of the first fraction.
        q (int): The denominator of the first fraction.
        r (int): The numerator of the second fraction.
        s (int): The denominator of the second fraction.

    Returns:
        IntPair: The result of the sandwich operation as a fraction.
    """
    return umultiply_fractions(p, q, s, r)






# import timeit
# import random
# import statistics

# # def benchmark_add_fractions(
# #     n_samples: int = 200,
# #     n_repeat: int = 5,
# #     n_iter: int = 2000,
# #     bit_sizes: tuple[int, ...] = (8, 32, 64, 128, 1024),
# #     seed: int = 42,
# # ) -> None:
# #     rng = random.Random(seed)

# #     def rand_pair(bits: int) -> IntPair:
# #         lo, hi = 2 ** (bits - 1), 2**bits - 1
# #         return rng.randint(lo, hi), rng.randint(lo, hi)

# #     funcs = {"add_fractions": add_fractions, "add_fractions_2": add_fractions_2, "uadd_fractions": uadd_fractions}

# #     for bits in bit_sizes:
# #         pairs = [(rand_pair(bits), rand_pair(bits)) for _ in range(n_samples)]
# #         print(f"\n--- {bits}-bit operands ---")

# #         results: dict[str, list[float]] = {name: [] for name in funcs}

# #         for a, b in pairs:
# #             for name, fn in funcs.items():
# #                 if name == "uadd_fractions":
# #                     p, q, r, s = *a, *b
# #                     times = timeit.repeat(lambda fn=fn, p=p, q=q, r=r, s=s: fn(p, q, r, s), number=n_iter, repeat=n_repeat)
# #                 else:
# #                     times = timeit.repeat(lambda fn=fn, a=a, b=b: fn(a, b), number=n_iter, repeat=n_repeat)
# #                 results[name].append(min(times) / n_iter * 1e9)  # ns per call

# #         for name, times in results.items():
# #             print(
# #                 f"  {name:20s}  "
# #                 f"median={statistics.median(times):7.1f} ns  "
# #                 f"mean={statistics.mean(times):7.1f} ns  "
# #                 f"stdev={statistics.stdev(times):6.1f} ns  "
# #                 f"min={min(times):6.1f} ns  "
# #                 f"max={max(times):6.1f} ns"
# #             )

# #         medians = {name: statistics.median(t) for name, t in results.items()}
# #         winner, loser = sorted(medians, key=medians.get), sorted(medians, key=medians.get, reverse=True)
# #         speedup = medians[loser[0]] / medians[winner[0]]
# #         print(f"  => {winner[0]} is {speedup:.2f}x faster (by median)")


# def benchmark_multiply_fractions(
#     n_samples: int = 200,
#     n_repeat: int = 5,
#     n_iter: int = 2000,
#     bit_sizes: tuple[int, ...] = (8, 32, 64, 128, 1024),
#     seed: int = 42,
# ) -> None:
#     rng = random.Random(seed)

#     def rand_pair(bits: int) -> IntPair:
#         lo, hi = 2 ** (bits - 1), 2**bits - 1
#         return rng.randint(lo, hi), rng.randint(lo, hi)

#     funcs = {"multiply_fractions": multiply_fractions, "umultiply_fractions": umultiply_fractions}

#     for bits in bit_sizes:
#         pairs = [(rand_pair(bits), rand_pair(bits)) for _ in range(n_samples)]
#         print(f"\n--- {bits}-bit operands ---")

#         results: dict[str, list[float]] = {name: [] for name in funcs}

#         for a, b in pairs:
#             for name, fn in funcs.items():
#                 if name == "umultiply_fractions":
#                     p, q, r, s = *a, *b
#                     times = timeit.repeat(lambda fn=fn, p=p, q=q, r=r, s=s: fn(p, q, r, s), number=n_iter, repeat=n_repeat)
#                 else:
#                     times = timeit.repeat(lambda fn=fn, a=a, b=b: fn(a, b), number=n_iter, repeat=n_repeat)
#                 results[name].append(min(times) / n_iter * 1e9)  # ns per call

#         for name, times in results.items():
#             print(
#                 f"  {name:20s}  "
#                 f"median={statistics.median(times):7.1f} ns  "
#                 f"mean={statistics.mean(times):7.1f} ns  "
#                 f"stdev={statistics.stdev(times):6.1f} ns  "
#                 f"min={min(times):6.1f} ns  "
#                 f"max={max(times):6.1f} ns"
#             )

#         medians = {name: statistics.median(t) for name, t in results.items()}
#         winner, loser = sorted(medians, key=medians.get), sorted(medians, key=medians.get, reverse=True)
#         speedup = medians[loser[0]] / medians[winner[0]]
#         print(f"  => {winner[0]} is {speedup:.2f}x faster (by median)")

# # print("Benchmarking add_fractions vs add_fractions_2...")
# # benchmark_add_fractions()


# print("Benchmarking multiply_fractions vs multiply_fractions2...")
# benchmark_multiply_fractions()
from math import log10, ceil, floor

from typing import Sequence
from functools import reduce


  # ensure enough precision for large digit counts

def product_digit_count(arr: Sequence[int]) -> int:
    """
    Computes the total number of digits in the product of a sequence of positive integers.
    
    Args:
        arr (Sequence[int]): A sequence of positive integers.

    Returns:
        int: The total number of digits in the product of the sequence.
    """
    tot = 0.0
    for num in arr:
        tot += log10(num)
    
    return floor(tot + 1.0) #ceil(tot) + tot.is_integer() # Add 1 if tot is an integer, otherwise add 0


def product_digit_count_high_precision(arr: Sequence[int]) -> int:
    """
    Alternative (and much slower) implementation of product_digit_count using Decimal for high precision.
    
    Args:
        arr (Sequence[int]): A sequence of positive integers.
    Returns:
        int: The total number of digits in the product of the sequence.
    """
    from decimal import Decimal, getcontext
    getcontext().prec = 20
    
    tot = Decimal(0)
    for num in arr:
        tot += 0#Decimal(num).log10()

    return floor(tot + Decimal(1.0))


def average_digit_count(arr: Sequence[int]) -> float:
    """
    Computes the average number of digits in the product of a sequence of positive integers.
    
    Args:
        arr (Sequence[int]): A sequence of positive integers.

    Returns:
        float: The average number of digits in the product of the sequence.
    """
    return product_digit_count(arr) / len(arr)

# import timeit
# import random
# import statistics

# def benchmark_log_prod(
#     n_samples: int = 200,
#     n_repeat: int = 5,
#     n_iter: int = 2000,
#     seq_lengths: tuple[int, ...] = (4, 16, 64, 256),
#     bit_sizes: tuple[int, ...] = (8, 64, 256),
#     seed: int = 42,
# ) -> None:
#     rng = random.Random(seed)

#     funcs = {
#         "log_prod":          log_prod,
#         "log_prod2":         log_prod2,
#         "log_prod3":         log_prod3,
#         # "log_prod_reduce":   log_prod_reduce,
#         # "log_prod_reduce_2": log_prod_reduce_2,
#     }

#     for length in seq_lengths:
#         for bits in bit_sizes:
#             lo, hi = 2 ** (bits - 1), 2**bits - 1
#             seqs = [
#                 [rng.randint(lo, hi) for _ in range(length)]
#                 for _ in range(n_samples)
#             ]
#             print(f"\n--- length={length}, {bits}-bit elements ---")

#             results: dict[str, list[float]] = {name: [] for name in funcs}

#             for seq in seqs:
#                 for name, fn in funcs.items():
#                     times = timeit.repeat(
#                         lambda fn=fn, seq=seq: fn(seq),
#                         number=n_iter,
#                         repeat=n_repeat,
#                     )
#                     results[name].append(min(times) / n_iter * 1e9)  # ns per call

#             for name, times in results.items():
#                 print(
#                     f"  {name:22s}  "
#                     f"median={statistics.median(times):7.1f} ns  "
#                     f"mean={statistics.mean(times):7.1f} ns  "
#                     f"stdev={statistics.stdev(times):6.1f} ns  "
#                     f"min={min(times):6.1f} ns  "
#                     f"max={max(times):6.1f} ns"
#                 )

#             medians = {name: statistics.median(t) for name, t in results.items()}
#             winner = min(medians, key=medians.get)
#             loser  = max(medians, key=medians.get)
#             speedup = medians[loser] / medians[winner]
#             print(f"  => {winner} is {speedup:.2f}x faster than {loser} (by median)")


# print("Benchmarking log_prod variants...")
# # benchmark_log_prod(seq_lengths=[16], bit_sizes=[516, 1024])

# from testing.bigints import make_ints
# import time

# for n in range(4, 15):
#     print(f"Generating {n}-element sequences...", end="", flush=True)
#     # ints = make_ints(count=n, bits=65536*n, base_seed=1)
#     x = log10(2)
#     ints = [10**10] * n
#     ints = [_int + bias for _int, bias in zip(ints, range(-n//2, n//2))]  # make them distinct
#     ints = [round(k/x) for k in ints]  

#     print(f" Done")

#     t0 = time.perf_counter(); pd1 = product_digit_count(ints);   t1 = time.perf_counter()
#     t2 = time.perf_counter(); pd2 = product_digit_count_high_precision(ints); t3 = time.perf_counter()

#     print(f"  product_digit_count == product_digit_count_high_precision: {pd1 == pd2}")
#     print(f"  product_digit_count:   {pd1}  ({(t1-t0)*1000:.3f} ms)")
#     print(f"  product_digit_count_high_precision: {pd2}  ({(t3-t2)*1000:.3f} ms)")



from math import log10, floor
from decimal import Decimal, getcontext
import time





if __name__ == "__main__":
    # ---------- Core implementations ----------

    def product_digit_count_counter(counter):
        tot = 0.0
        for num, count in counter.items():
            tot += count * log10(num)
        return floor(tot + 1.0)


    def product_digit_count_counter_high_precision(counter):
        getcontext().prec = 50
        tot = Decimal(0)
        for num, count in counter.items():
            tot += Decimal(count) * Decimal(num).log10()
        return int(tot) + 1


    # ---------- Continued fraction machinery ----------

    def continued_fraction(x, max_terms=30):
        cf = []
        for _ in range(max_terms):
            a = int(x)
            cf.append(a)
            x -= a
            if x == 0:
                break
            x = 1 / x
        return cf


    def convergents(cf):
        p0, q0 = cf[0], 1
        yield p0, q0

        if len(cf) == 1:
            return

        p1 = cf[0]*cf[1] + 1
        q1 = cf[1]
        yield p1, q1

        for i in range(2, len(cf)):
            a = cf[i]
            p2 = a*p1 + p0
            q2 = a*q1 + q0
            yield p2, q2
            p0, q0 = p1, q1
            p1, q1 = p2, q2


    # ---------- Test runner ----------

    def run_test():
        x = log10(2)
        cf = continued_fraction(x, max_terms=30)

        print("Searching for dangerous convergent...\n")

        for p, q in convergents(cf):
            err = abs(q * x - p)
            print(f"q = {q:<12} error ≈ {err:.3e}")

            if err < 1e-13:
                print("\n🔥 Found dangerous case!\n")

                # Instead of [2]*q, use counter
                counter = {2: q}

                t0 = time.perf_counter()
                pd1 = product_digit_count_counter(counter)
                t1 = time.perf_counter()

                t2 = time.perf_counter()
                pd2 = product_digit_count_counter_high_precision(counter)
                t3 = time.perf_counter()

                print(f"Float result:        {pd1}")
                print(f"High precision:      {pd2}")
                print(f"Match:               {pd1 == pd2}")
                print()
                print(f"Float time:          {(t1 - t0)*1000:.6f} ms")
                print(f"High precision time: {(t3 - t2)*1000:.6f} ms")

                break
    run_test()


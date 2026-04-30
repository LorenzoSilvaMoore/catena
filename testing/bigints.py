"""Deterministic large-integer generation and binary storage for tests.

On-the-fly generation (no file I/O):

    from testing.bigints import make_int, make_neg_int, make_ints

    a = make_int(bits=33000, seed=0)    # exactly 33 000-bit integer
    b = make_int(digits=10000, seed=1)  # ~10 000 decimal digits
    c = make_neg_int(digits=5000, seed=2)
    many = make_ints(8, digits=10000)   # 8 distinct values, seeds 0..7

Pre-computed named store (for expensive values like 101**5001):

    from testing.bigints import save, load

    save({"big_101": 101**5001, "mersenne_127": 2**127 - 1})
    ints = load()           # -> {"big_101": ..., "mersenne_127": ...}
    n    = load()["big_101"]

The binary store uses int.to_bytes / int.from_bytes, so load is O(n-bytes),
much faster than parsing a decimal string for very large numbers.

The bigger the store files get, the slower the loading times become, so
consider splitting them into multiple files if needed. 
"""

from __future__ import annotations

from decimal import Decimal
import random
import struct
from pathlib import Path

_STORE_DIR = Path(__file__).parent / "store"
_STORE_PATH = _STORE_DIR / "bigints.dat"
_MAGIC = b"CATBIG\x01\x00"  # 8-byte magic + version


# ---------------------------------------------------------------------------
# On-the-fly deterministic generation
# ---------------------------------------------------------------------------

def make_int(
    *,
    bits: int | None = None,
    digits: int | None = None,
    seed: int = 0,
) -> int:
    """Return a deterministic positive integer.

    Provide *either* ``bits`` (exact bit-length) *or* ``digits`` (approximate
    decimal digit count).  The top bit is always set, guaranteeing the
    requested bit-width and preventing the integer from being shorter than
    expected.

    Parameters
    ----------
    bits:
        Exact bit-length of the result.
    digits:
        Target decimal digit count.  Internally converted to
        ``bits = ceil(digits × log₂10) + 1``.
    seed:
        RNG seed – same seed always gives the same integer.
    """
    if (bits is None) == (digits is None):
        raise ValueError("Provide exactly one of bits= or digits=")
    if digits is not None:
        bits = int(digits * Decimal('3.321928094887362347870319429489390175864831393024580612054756395815934776608625215850139743359370155')) + 1   # ≈ ceil(digits × log₂10)
    if bits < 1:
        raise ValueError("bits must be >= 1")

    rng = random.Random(seed)
    val = rng.getrandbits(bits)
    val |= 1 << (bits - 1)   # guarantee bit-length == bits
    return val


def make_neg_int(
    *,
    bits: int | None = None,
    digits: int | None = None,
    seed: int = 0,
) -> int:
    """Like :func:`make_int` but returns the negated value."""
    return -make_int(bits=bits, digits=digits, seed=seed)


def make_ints(
    count: int,
    *,
    bits: int | None = None,
    digits: int | None = None,
    base_seed: int = 0,
) -> list[int]:
    """Return *count* distinct deterministic positive integers.

    Uses seeds ``base_seed, base_seed+1, …, base_seed+count-1`` so that
    different calls with non-overlapping seed ranges never collide.
    """
    return [make_int(bits=bits, digits=digits, seed=base_seed + i) for i in range(count)]


# ---------------------------------------------------------------------------
# Binary store  (compact, fast load via int.from_bytes)
# ---------------------------------------------------------------------------
#
# File layout:
#   8 bytes   magic / version
#   4 bytes   uint32-LE  number of entries
#   per entry:
#     2 bytes   uint16-LE  len(name UTF-8)
#     N bytes   name
#     1 byte    int8  sign: 0 = non-negative, -1 = negative
#     4 bytes   uint32-LE  number of magnitude bytes
#     M bytes   magnitude, big-endian

def save(integers: dict[str, int], path: Path | str = _STORE_PATH) -> None:
    """Write *integers* to a compact binary store at *path*."""
    path = Path(path)
    with open(path, "wb") as f:
        f.write(_MAGIC)
        f.write(struct.pack("<I", len(integers)))
        for name, value in integers.items():
            name_bytes = name.encode("utf-8")
            sign: int = -1 if value < 0 else 0
            magnitude = abs(value)
            byte_len = (magnitude.bit_length() + 7) // 8 if magnitude else 1
            data = magnitude.to_bytes(byte_len, "big")

            f.write(struct.pack("<H", len(name_bytes)))
            f.write(name_bytes)
            f.write(struct.pack("b", sign))
            f.write(struct.pack("<I", len(data)))
            f.write(data)


def load(path: Path | str = _STORE_PATH) -> dict[str, int]:
    """Load all named integers from a binary store.

    Returns an empty dict if the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        return {}

    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != _MAGIC:
            raise ValueError(f"Unrecognised store file (bad magic): {path}")

        (count,) = struct.unpack("<I", f.read(4))
        result: dict[str, int] = {}
        for _ in range(count):
            (name_len,) = struct.unpack("<H", f.read(2))
            name = f.read(name_len).decode("utf-8")
            (sign,) = struct.unpack("b", f.read(1))
            (data_len,) = struct.unpack("<I", f.read(4))
            data = f.read(data_len)

            value = int.from_bytes(data, "big")
            if sign == -1:
                value = -value
            result[name] = value

    return result


def update_or_save(integers: dict[str, int], path: Path | str = _STORE_PATH) -> None:
    """Merge *integers* into the store at *path*, or create it if absent.

    Existing keys are overwritten; keys not present in *integers* are kept.
    Equivalent to ``save(load(path) | integers, path)`` but only loads when
    the file already exists.
    """
    path = Path(path)
    if path.exists():
        existing = load(path)
        existing.update(integers)
        save(existing, path)
    else:
        save(integers, path)


# ---------------------------------------------------------------------------
# Utility functions
def build_store_path(file_name: str = None) -> Path:
    """Return the path to the store file, optionally with a custom name."""
    if file_name is None:
        return _STORE_PATH
    else:
        return (_STORE_DIR / file_name).with_suffix(".dat")


# ---------------------------------------------------------------------------



def _main() -> None:
    """Example usage and load-vs-generation benchmark."""
    import time

    

    # ints = {
    #     "big_101": 101**5001,
    #     "mersenne_127": 2**127 - 1,
    #     "random_33000": make_int(bits=33000, seed=1),
    #     "random_10000_digits": make_int(digits=10000, seed=1),
    #     "neg_random_5000_digits": make_neg_int(digits=5000, seed=2),
    # }
    # save(ints)

    # for name, value in ints.items():
    #     print(f"{name}: {safe_int_str(value)}")

    # ------------------------------------------------------------------
    # Benchmark: binary load  vs  fresh generation
    # ------------------------------------------------------------------
    REPS = 100
    print(f"\n{'─' * 52}")
    print(f"{'key':<28}  {'load':>8}  {'gen':>8}  {'winner'}")
    print(f"{'─' * 52}")

    path = build_store_path("bigints_benchmark")

    bench_cases: list[tuple[str, dict]] = [
        ("big_101",             {"expr": lambda: 101**5001}),
        ("mersenne_127",        {"expr": lambda: 2**127 - 1}),
        ("random_33000",        {"expr": lambda: make_int(bits=33000, seed=1)}),
        ("random_1000000_digits", {"expr": lambda: make_int(digits=1000000, seed=1)}),
        ("neg_random_5000_digits", {"expr": lambda: make_neg_int(digits=5000, seed=2)}),
    ]

    ints = {
        name: cfg["expr"]() for name, cfg in bench_cases
    }
    save(ints, path)

    for name, cfg in bench_cases:
        # --- load ---
        t0 = time.perf_counter()
        for _ in range(REPS):
            load(path)[name]
        t_load = (time.perf_counter() - t0) / REPS * 1000  # ms per call

        # --- generate ---
        fn = cfg["expr"]
        t0 = time.perf_counter()
        for _ in range(REPS):
            fn()
        t_gen = (time.perf_counter() - t0) / REPS * 1000  # ms per call

        winner = "load" if t_load < t_gen else "gen "
        print(f"{name:<28}  {t_load:>7.2f}ms  {t_gen:>7.2f}ms  {winner}")

    print(f"{'─' * 52}")
    print("(times are averages over", REPS, "repetitions)\n\n")
    
    from catena.strings import safe_int_str
    
    for name, value in ints.items():
        print(f"{name}: {safe_int_str(value)}")

if __name__ == "__main__":
    _main()



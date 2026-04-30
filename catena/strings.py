from .mathlib.core import get_sign
from .mathlib.metric import product_digit_count

def safe_int_str(n: int, n_trailing: int = 99) -> str:
    """
    Returns a string representation of n without risking the integer-to-string
    conversion limit (PEP 678 / Python 3.11+).

    If abs(n) has fewer than 100 digits, the full decimal representation is
    returned.  Otherwise only the last *n_trailing* digits are returned,
    zero-padded and prefixed with "...".

    Args:
        n (int): The integer to represent.
        n_trailing (int): Number of trailing digits to show when n is large.
                          Must satisfy 1 <= n_trailing <= 99.
    """
    if not 1 <= n_trailing <= 99:
        raise ValueError(f"n_trailing must be between 1 and 99, got {n_trailing}")

    sign = get_sign(n)

    if sign == 0:
        return "0"

    abs_n = n * sign

    if (digits:=product_digit_count([abs_n])) < 100:
        return str(n)

    tail = abs_n % (10**n_trailing)
    return "BigBigInt(sign={sign}, digits={digits}, tail({n_trailing})={tail:0{n_trailing}d}, hash={hash})".format(sign=sign, digits=digits, tail=tail, n_trailing=n_trailing, hash=hash(n))

def safe_full_int_str(n: int) -> str:
    """
    Returns the full decimal representation of n as a string, without risking
    the integer-to-string conversion limit (PEP 678 / Python 3.11+).

    Args:
        n (int): The integer to represent.
    """
    txt = ''
    sign = get_sign(n)
    abs_n = n * sign

    if abs_n <= 9223372036854775797:
        return str(n)

    while abs_n:
        chunk = abs_n % (10**99)
        abs_n //= 10**99
        txt = f"{chunk:099d}" + txt

    txt = txt.lstrip('0') or '0'

    if sign < 0:
        txt = "-" + txt

    return txt
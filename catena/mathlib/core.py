from math import gcd, log10

type IntPair = tuple[int, int]
type IntTriplet = tuple[int, int, int]
type FloatAsStr = str

def get_sign(n: int) -> int:
    """
    Returns the sign of a number. 
    
    Args:
        n (int): The number to check.

    Returns:
        int: 1 if positive, -1 if negative, 0 if zero.
    """
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


def simplify(p: int, q: int) -> IntPair:
    """
    Simplifies a fraction by dividing both the numerator and denominator by their greatest common divisor (GCD).
    Signs are preserved:
        - If the numerator is negative, the simplified numerator will be negative.
        - If the denominator is negative, the simplified denominator will be negative.
        - If both are negative, both will be simplified to negative.

    Args:
        p (int): The numerator.
        q (int): The denominator.

    Returns:
        IntPair: A tuple containing the simplified numerator and denominator.
    """
    d = gcd(p, q)
    return p//d, q//d


def canonicalize(p: int, q: int) -> IntPair:
    """
    Canonicalizes a fraction by simplifying it and ensuring the denominator is positive.

    Args:
        p (int): The numerator.
        q (int): The denominator.

    Returns:
        IntPair: A tuple containing the canonicalized numerator and denominator.
    """
    simplified_p, simplified_q = simplify(p, q)
    if simplified_q < 0:
        return -simplified_p, -simplified_q
    return simplified_p, simplified_q


def euclidean_step(p: int, q: int) -> IntTriplet:
    """
    Breaks down a division operation into quotient, remainder, and divisor.
    
    Args:
        p (int): The dividend.
        q (int): The divisor.

    Returns:
        IntTriplet: A tuple containing the quotient, remainder, and divisor.
    """
    return p//q, p%q, q


def quotent_sign(p: int, q: int) -> int|None:
    """
    Returns the sign of the quotient of a and b without performing the division.
    
    Args:
        p (int): The numerator.
        q (int): The denominator.

    Returns:
        int: 1 if the quotient is positive, -1 if negative, 0 if zero, None if undefined (division by zero).
    """
    if q == 0:
        return None
    return get_sign(p) * get_sign(q)


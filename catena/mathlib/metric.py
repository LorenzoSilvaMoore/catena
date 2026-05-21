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

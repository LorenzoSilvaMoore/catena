"""
Generators for partial-quotient sequences used in continued fraction expansions.

This module provides three callable generator types:

- :class:`Generator` — a thin wrapper around any callable ``f: int -> int`` that
  validates its output (positive integer) on every call.
- :class:`CachedGenerator` — a ``Generator`` that memoises results in an
  :class:`~catena.cache.OrdinalCache` to avoid redundant computation.
- :class:`FiniteGenerator` — a ``Generator`` backed by a fixed sequence of
  integers stored as a compact :class:`array.array` (or a plain tuple for
  values exceeding the 64-bit range).

All three types share the same calling convention: ``generator(n)`` returns the
*n*-th partial quotient (0-indexed), which must always be a strictly positive
integer.
"""
from collections.abc import Callable, Collection, Sequence
from array import array

from math import gcd
from typing import Optional, Tuple

from .cache import Cache, CacheHandler, SetLightCache, OrdinalCache
from .strings import safe_int_str
from .mathlib.core import get_sign



class Generator(Callable):
    """
    A validated callable wrapper for partial-quotient generator functions.

    Wraps any callable ``f(n: int) -> int`` and enforces that every call
    returns a strictly positive integer.  If the wrapped object is already a
    :class:`Generator` instance, it is returned unchanged (see
    :meth:`__new__`).
    """

    def __init__(self, generator: Callable[[int], int]):
        """
        Initialises the generator wrapper.

        Args:
            generator (Callable[[int], int]): A callable that maps a
                non-negative index *n* to a strictly positive integer.

        Raises:
            TypeError: If ``generator`` is not callable.
        """
        if isinstance(generator, type(self)):
            return
        
        if not callable(generator):
            raise TypeError(f"Generator requires a callable, got {type(generator).__name__}.")

        self.cached = False
        self.generator = generator

    def __call__(self, n: int) -> int:
        """
        Calls the underlying generator and validates its output.

        Args:
            n (int): Non-negative index of the partial quotient to retrieve.

        Returns:
            int: The *n*-th partial quotient (strictly positive).

        Raises:
            ValueError: If ``n`` is negative, or if the generator returns a
                non-integer or a non-positive value.
        """
        if n < 0:
            raise ValueError(f"Input n must be non-negative, got {n}.")

        call_result = self.generator(n)
        if not isinstance(call_result, int):
            raise ValueError(f"Generator function must return an integer, got {type(call_result)}")
        
        if not call_result > 0:
            raise ValueError(f"Generator function must return a positive integer, got value {safe_int_str(call_result)}.")
        
        return call_result
    
    def __str__(self) -> str:
        return f"Generator(generator={self.generator.__name__})"
    
    def __new__(cls, generator, *args, **kwargs):
        """
        Returns the existing instance if ``generator`` is already a
        :class:`Generator`, avoiding unnecessary double-wrapping.
        """
        if isinstance(generator, cls):
            return generator
        return super().__new__(cls)
    


class CachedGenerator(Generator):
    """
    A :class:`Generator` that memoises results in an
    :class:`~catena.cache.OrdinalCache`.

    On the first call for a given index *n* the underlying function is invoked
    and its result stored; subsequent calls for the same *n* are served
    directly from the cache.
    """

    def __init__(self, generator: Callable[[int], int], *args, **kwargs):
        """
        Initialises the cached generator.

        Args:
            generator (Callable[[int], int]): A callable that maps a
                non-negative index *n* to a strictly positive integer.
        """
        super().__init__(generator=generator, *args, **kwargs)
        self.cached = True
        self._cache_handler = CacheHandler(OrdinalCache())
        self.generator = SetLightCache(func=generator, cache_handler=self._cache_handler)

    @property
    def cache(self) -> Cache:
        """The underlying :class:`~catena.cache.Cache` storing computed values."""
        return self._cache_handler.cache
    
    @property
    def cache_handler(self) -> CacheHandler:
        """The :class:`~catena.cache.CacheHandler` managing the cache lifecycle."""
        return self._cache_handler
    
    def reset_cache(self) -> None:
        """Clears all entries from the cache, freeing the memoised results."""
        self._cache_handler.reset_cache()

    def __str__(self) -> str:
        return f"CachedGenerator(generator={self.generator.func.__name__}, cached={self.cached}, cache_size={len(self.cache)})"
    


class FiniteGenerator(Generator):
    """
    A :class:`Generator` backed by a fixed sequence of positive integers.

    The sequence is stored as a compact :class:`array.array` using the
    smallest unsigned typecode whose range covers all values in ``data``
    (``B`` → 8-bit, ``H`` → 16-bit, ``I`` → 32-bit, ``L`` → 32/64-bit,
    ``Q`` → 64-bit).  If any value exceeds the 64-bit range the sequence
    falls back to an immutable :class:`tuple` and ``is_compact`` is
    ``False``.
    """

    _dtypes = tuple('BHILQ')  # unsigned typecodes, smallest to largest
    _bounds: dict[str, tuple[int, int]] = {
        code: (0, (1 << (array(code, []).itemsize * 8)) - 1) for code in _dtypes
    }

    def __new__(cls, data, dtype=None, *args, **kwargs):
        if isinstance(data, cls):
            return data
        return object.__new__(cls)

    def __init__(self, data: Sequence[int], dtype: str = None, *args, **kwargs):
        """
        Initialises the finite generator from a sequence of positive integers.

        Args:
            data (Sequence[int]): The sequence of strictly positive partial
                quotients.
            dtype (str, optional): Force a specific unsigned array typecode
                (one of ``'B'``, ``'H'``, ``'I'``, ``'L'``, ``'Q'``).  When
                ``None`` (default) the smallest fitting typecode is chosen
                automatically.

        Raises:
            TypeError: If ``data`` is not a :class:`~collections.abc.Sequence`.
            ValueError: If ``dtype`` is not a supported typecode, or if any
                value in ``data`` is not a strictly positive integer.
        """
        if isinstance(data, FiniteGenerator):
            return
        
        if not isinstance(data, Sequence) or not all(isinstance(x, int) for x in data):
            raise TypeError(f"data must be a Sequence of integers, got {type(data).__name__} with elements of type {set(type(x) for x in data)}")

        if dtype is not None and dtype not in self._dtypes:
            raise ValueError(f"Invalid dtype '{dtype}'. Supported dtypes are: {', '.join(self._dtypes)}.")

        if len(data) == 0:
            self._data = array(dtype or 'B', [])
            self._compact = True
            self._min = self._max = None
        elif dtype is not None:
            lo = min(data)
            if lo <= 0:
                raise ValueError(f"FiniteGenerator values must be positive integers, got {lo}.")
            self._data = array(dtype, data)
            self._compact = True
            self._min = lo
            self._max = max(data)
        else:
            lo, hi = min(data), max(data)

            if lo <= 0:
                raise ValueError(f"FiniteGenerator values must be positive integers, got {lo}.")

            # Find the smallest unsigned typecode whose range covers [lo, hi]
            for code in self._dtypes:
                _, hi_bound = self._bounds[code]
                if hi <= hi_bound:
                    self._data = array(code, data)
                    self._compact = True
                    self._min = lo
                    self._max = hi
                    break
            else:
                # Values exceed 64-bit range; fall back to tuple for arbitrary precision
                self._data = tuple(data)
                self._compact = False
                self._min = lo
                self._max = hi

        def _at(n: int) -> int:
            size = len(self._data)
            if n < 0 or n >= size:
                raise IndexError(f"Index must be between 0 and {size - 1}, got {n}.")
            return self._data[n]

        super().__init__(generator=_at, *args, **kwargs)

    @property
    def size(self) -> int:
        """Number of elements in the sequence."""
        return len(self._data)

    @property
    def dtype(self) -> str | None:
        """Array typecode used for compact storage, or ``None`` if arbitrary-precision."""
        return self._data.typecode if self._compact else None

    @property
    def is_compact(self) -> bool:
        """``True`` if the data is stored as an :class:`array.array`, ``False`` for tuple fallback."""
        return self._compact
    
    @property
    def min(self) -> int:
        """Smallest value in the sequence, or ``None`` if empty."""
        return self._min

    @property
    def max(self) -> int:
        """Largest value in the sequence, or ``None`` if empty."""
        return self._max
    
    @property
    def start(self) -> int:
        """First element of the sequence, or ``None`` if empty."""
        return self._data[0] if self.size > 0 else None
    
    @property
    def end(self) -> int:
        """Last element of the sequence, or ``None`` if empty."""
        return self._data[-1] if self.size > 0 else None

    def __getitem__(self, index: int) -> int:
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: int) -> bool:
        return item in self._data

    def __str__(self) -> str:
        return f"FiniteGenerator(size={self.size}, dtype={self.dtype or 'arbitrary'}, start={self.start}, end={self.end}, min={self.min}, max={self.max})"

    def __repr__(self):
        return f"FiniteGenerator[{self.dtype or 'arbitrary'} × {self.size}]"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FiniteGenerator):
            return NotImplemented
        return self.dtype == other.dtype and self._data == other._data

    @property
    def view(self) -> memoryview:
        """
        A read-only :class:`memoryview` over the underlying array buffer.

        Raises:
            TypeError: If the data is stored as a tuple (arbitrary-precision
                fallback) and a memoryview cannot be constructed.
        """
        if not self._compact:
            raise TypeError("Data uses arbitrary-precision integers; memoryview is not available.")
        return memoryview(self._data).toreadonly()
    

class PeriodicGenerator(Generator):
    """
    A :class:`Generator` that produces a periodic sequence of positive integers.

    The sequence is defined by a finite list of integers representing the
    pre-period followed by a finite list representing the period.
    For example, the simple continued fraction expansion of $(7+\\sqrt{10})/4$ is
    $[2; 1, 1, 5, 1, 1, 1, 24, 1, 1, 1, 5, \\ldots]$, where the integer part is $2$, the
    pre-period is $[1, 1]$, and the period is $[5, 1, 1, 1, 24, 1, 1, 1]$.
    """
    def __init__(self, period: Collection[int], pre_period: Collection[int] = (), dtypes: Optional[Tuple[str, str]] = None, *args, **kwargs):
        """
        Initialises the periodic generator.

        Args:
            period (Collection[int]): The finite sequence of positive integers
                representing the periodic part of the continued fraction.
            pre_period (Collection[int], optional): The finite sequence of positive
                integers representing the aperiodic pre-period (default: empty).
            dtypes (Tuple[str, str], optional): Force specific :class:`array.array` typecodes for compact storage of the
                period and pre-period respectively (each one of ``'B'``, ``'H'``, ``'I'``, ``'L'``, ``'Q'``).
                When ``None``, the smallest fitting typecode is chosen automatically. 
                    Note: (str, None) and (None, str) are also accepted to specify a typecode 
                    for only one of the two sequences.

        Raises:
            ValueError: If any value in ``period`` or ``pre_period`` is not a strictly
                positive integer.
        """
        if isinstance(period, PeriodicGenerator) and len(pre_period) == 0:
            return  # __new__ returned the existing instance; skip re-initialisation

        if dtypes is None:
            dtypes = (None, None)

        elif len(dtypes) != 2:
            raise ValueError(f"Expected a tuple of two typecodes for 'dtypes' but got {dtypes}")

        self._period = FiniteGenerator(period, dtype=dtypes[0])
        self._pre_period = FiniteGenerator(pre_period, dtype=dtypes[1])

        if len(self._pre_period) != 0:
            def _at(n: int) -> int:
                if n < len(self._pre_period):
                    return self._pre_period[n]
                else:
                    return self._period[(n - len(self._pre_period)) % len(self._period)]
        else:
            def _at(n: int) -> int:
                return self._period[n % len(self._period)]

        super().__init__(generator=_at, *args, **kwargs)

    @property
    def period(self) -> FiniteGenerator:
        """The finite sequence of positive integers representing the period."""
        return self._period
    
    @property
    def pre_period(self) -> FiniteGenerator:
        """The finite sequence of positive integers representing the aperiodic pre-period."""
        return self._pre_period
    

    def __str__(self) -> str:
        return f"PeriodicGenerator(period={self.period}, pre_period={self.pre_period})"
    
    def __repr__(self):
        return f"PeriodicGenerator(period={repr(self.period)}, pre_period={repr(self.pre_period)})"
    
    def __new__(cls, period, pre_period=(), *args, **kwargs):
        """
        Returns the existing instance if ``period`` is already a
        :class:`PeriodicGenerator` with no pre-period, avoiding unnecessary
        double-wrapping.
        """
        if isinstance(period, PeriodicGenerator) and len(pre_period) == 0:
            return period
        return object.__new__(cls)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PeriodicGenerator):
            return NotImplemented
        return self.period == other.period and self.pre_period == other.pre_period
    

    def quadratic_coefficients(self) -> tuple[int, int, int]:
        """
        Returns the coefficients of the corresponding quadratic polynomial.
        
        The quadratic polynomial is derived from the periodic part of the continued fraction expansion,
        and its roots correspond to the value of the infinite periodic continued fraction defined 
        by the period and the pre-period (with a_0 = 0). If a pre-period is present, the coefficients are 
        adjusted to account for it.
        
        Returns:
            tuple[int, int, int]: Coefficients (A, B, C) of the quadratic polynomial Ax^2 + Bx + C = 0, 
            where A > 0 and gcd(A, B, C) = 1.
        """
        cyclic_coefficients = self.cycle_quadratic_coefficients()
        if len(self.pre_period) == 0:
            return cyclic_coefficients
        
        from .catena import FiniteSimpleContinuedFraction
        k = len(self.pre_period)
        A, B, C = cyclic_coefficients
        scf = FiniteSimpleContinuedFraction(partial_quotients=self.pre_period)
        ck = scf.convergent(k-1)
        ck_minus_1 = scf.convergent(k-2)

        pk, qk = ck
        pk_minus_1, qk_minus_1 = ck_minus_1

        # Adjust coefficients to account for the pre-period
        A_new = A * qk**2 - B * qk * qk_minus_1 + C * qk_minus_1**2
        B_new = -2 * A * pk * qk + B * (pk * qk_minus_1 + pk_minus_1 * qk) - 2 * C * pk_minus_1 * qk_minus_1
        C_new = A * pk**2 - B * pk * pk_minus_1 + C * pk_minus_1**2

        quadratic_sign = get_sign(A_new)
        g = gcd(A_new, B_new, C_new)
        return (A_new // g) * quadratic_sign, (B_new // g) * quadratic_sign, (C_new // g) * quadratic_sign

    
    def cycle_quadratic_coefficients(self) -> tuple[int, int, int]:
        """
        Returns the coefficients of the corresponding quadratic polynomial for the period only.

        The quadratic polynomial is derived from the periodic part of the continued fraction expansion,
        and its roots correspond to the value of the infinite periodic continued fraction defined by 
        the period (with a_0 = 0).

        Returns:
            tuple[int, int, int]: Coefficients (A, B, C) of the quadratic polynomial Ax^2 + Bx + C = 0, 
            where A > 0 and gcd(A, B, C) = 1.
        """
        from .catena import FiniteSimpleContinuedFraction

        k = len(self.period)
        scf = FiniteSimpleContinuedFraction(partial_quotients=self.period)
        ck = scf.convergent(k-1)
        ck_minus_1 = scf.convergent(k-2)
        pk, qk = ck
        pk_minus_1, qk_minus_1 = ck_minus_1

        A = qk_minus_1
        B = qk - pk_minus_1
        C = -pk
        quadratic_sign = get_sign(A)
        g = gcd(A, B, C)
        return (A // g) * quadratic_sign, (B // g) * quadratic_sign, (C // g) * quadratic_sign
    
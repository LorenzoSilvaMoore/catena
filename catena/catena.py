"""
Core continued-fraction types.

This module exposes three public classes:

- :class:`SimpleContinuedFraction` — an infinite (or generative) simple
  continued fraction ``[a₀; a₁, a₂, …]`` where the partial quotients are
  produced on demand by a :class:`~catena.generators.Generator`.
  Convergents are memoised in a :class:`~catena.cache.BaseCache`.

- :class:`FiniteSimpleContinuedFraction` — a finite SCF backed by a fixed
  sequence of partial quotients stored in a
  :class:`~catena.generators.FiniteGenerator`.  Provides factory methods to
  construct instances directly from rationals, floats, or decimal strings,
  and a :meth:`~FiniteSimpleContinuedFraction.to_decimal` method for exact
  :class:`~decimal.Decimal` conversion.

- :class:`PeriodicSimpleContinuedFraction` — a periodic SCF
  ``[a₀; a₁, …, aₘ, (b₁, …, bₙ)]`` backed by a
  :class:`~catena.generators.PeriodicGenerator`.  Provides
  :meth:`~PeriodicSimpleContinuedFraction.quadratic_coefficients` to recover
  the quadratic equation satisfied by its value.

Convergent arithmetic
---------------------
The standard two-term recurrence is split into two layers:

* ``tail_convergent(n)`` — computes the *n*-th convergent of the tail
  ``[a₁; a₂, …, aₙ₊₁]``, returning ``(numerator, denominator)``.
  The sentinel cases ``n = -2`` and ``n = -1`` return the recurrence seeds
  ``(1, 0)`` and ``(0, 1)`` respectively.
* ``convergent(n)`` — lifts the tail convergent to the full SCF by
  incorporating the integer part ``a₀``.
"""
import weakref

from fractions import Fraction

from .cache import BaseCache

from typing import Callable, Self, Tuple, Optional, Union, cast, override, TYPE_CHECKING
from decimal import Decimal
from collections.abc import Sequence

from .generators import Generator, FiniteGenerator, PeriodicGenerator
from .views.convergents import ConvergentsView, FiniteConvergentView
import catena.mathlib as mathlib

# class Method:
    
#     @staticmethod
#     def greedy_algorithm(p: int, q: int):
#         sign = Method.sign(p, q)
#         p, q = Method.abs(p, q)
#         p, q = Method.simplify(p, q)
#         lst = []
#         while p != 1:
#             n = q//p + 1
#             lst.append(n * sign)
#             p, q = Method.simplify(p*n - q, q*n)
#         lst.append(q * sign)
#         return lst


# class StringMethod:
#     def prefix_match(str1: Sequence, str2: Sequence) -> Sequence:
#         """
#         Finds the longest common prefix of two sequences using binary search.

#         :param str1: First input sequence (e.g., string, list, tuple)
#         :param str2: Second input sequence
#         :return: Longest common prefix as a sequence of the same type as str1
#         """
#         left, right = 0, min(len(str1),len(str2))

#         while left <= right:
#             mid = (left + right) // 2
#             if str1[:mid] == str2[:mid]:
#                 left = mid + 1
#             else:
#                 right = mid - 1

#         return str1[:(left + right) // 2]

#     # Needs to be refactored.
#     @staticmethod
#     def string_divition(frac: IntPair, length: int=100, bs: int=100000):
#         sign = Method.sign(*frac)
#         sign_str = "-" if sign < 0 else ""
#         frac = Method.abs(*frac)
#         (h, p), q = Method.euclid_breakdown(*frac)
#         s = f"{sign_str}{h}."
#         if p == 0:
#             return s+"0"
#         extra = len(s)
#         for _ in range(length):
#             count = -1
#             breaksafe = bs
#             while p < q:
#                 breaksafe -= 1
#                 p, count = p*10, count + 1
#                 if breaksafe == 0:
#                     break
#             (h, p), q = Method.euclid_breakdown(p, q)
#             s += "0"*count + str(h)
#             if p == 0:
#                 return s
#             if len(s) > length + extra:
#                 return s[:length + extra]
#         return s
    
#     # @staticmethod
#     # def print_intersection(frac1, frac2, length=100):
#     #     if isinstance(frac1, tuple):
#     #         string1 = Method.string_divition(frac1, length)
#     #     else:
#     #         string1 = str(frac1)

#     #     if isinstance(frac2, tuple):
#     #         string2 = Method.string_divition(frac2, length)
#     #     else:
#     #         string2 = str(frac2)

#     #     inter = StringMethod.prefix_match(string1, string2)
#     #     index = len(inter)
        
#     #     print(Fore.GREEN + inter, end="")
#     #     print(Fore.WHITE + string1[index:])
#     #     print(Style.RESET_ALL, end="")

#     #     print(Fore.GREEN + inter, end="")
#     #     print(Fore.WHITE + string2[index:])
#     #     print(Style.RESET_ALL, end="")


class SimpleContinuedFraction:
    """
    An infinite simple continued fraction ``[a₀; a₁, a₂, …]``.

    The partial quotients ``a₁, a₂, …`` are supplied by a
    :class:`~catena.generators.Generator` callable.  The integer part
    ``a₀`` is stored separately as :attr:`integer_part`.

    Tail convergents are automatically memoised via
    :class:`~catena.cache.BaseCache` so repeated calls to
    :meth:`tail_convergent` or :meth:`convergent` with the same index are O(1)
    after the first computation.

    Attributes ``_generator`` and ``_tail_cache`` are
    frozen after construction; attempting to overwrite them raises
    :exc:`AttributeError`.
    """
    __slots__ = (
        "_generator",
        "_tail_cache",
        "_cached_inverse",
        "_integer_part",
        "__weakref__",
    )
    is_finite = False  # Sentinel value for type checking; overridden to True in FSCF
    _empty_cached_entry = lambda *args, **kwargs: None  # Sentinel for an empty cache entry

    if TYPE_CHECKING:
        _generator: Generator
        _tail_cache: BaseCache
        _cached_inverse: weakref.ReferenceType[Self]
        _integer_part: int
    

    def __init__(self, generator: Callable[[int], int], integer_part: int = 0):
        """
        Initialises the continued fraction.

        Args:
            generator (Callable[[int], int]): A callable (or
                :class:`~catena.generators.Generator`) that returns the *n*-th
                partial quotient ``aₙ₊₁`` (0-indexed; ``generator(0)`` gives
                ``a₁``).
            integer_part (int): The integer part ``a₀``.  Defaults to ``0``.

        Raises:
            TypeError: If ``generator`` is not callable.
            ValueError: If ``integer_part`` cannot be converted to ``int``.
        """
        if not isinstance(generator, Generator):  # Ensure it's a Generator instance
            generator = Generator(generator)
        try:
            self._integer_part = int(integer_part)
        except ValueError:
            raise ValueError(f"Expected an integer for '{self.__class__.__name__}.integer_part' but got {integer_part}")

        super().__setattr__("_generator", generator)
        super().__setattr__("_tail_cache", BaseCache(func=self._tail_convergent))
        super().__setattr__("_cached_inverse", self._empty_cached_entry) # Initialize the cached inverse as a weak reference to None
    
    def __setattr__(self, name, value):
        """
        Guards frozen attributes against reassignment after construction.

        ``_generator`` and ``_tail_cache`` are permanently frozen.
        ``_cached_inverse`` is write-once: it can be set exactly once
        (by :meth:`inverse`) and raises :exc:`AttributeError` on any
        subsequent assignment.

        Raises:
            AttributeError: If ``name`` is one of ``_generator`` or
                ``_tail_cache`` (always), or ``_cached_inverse`` after
                it has already been set.
        """
        if name in {"_generator", "_tail_cache"}:
            raise AttributeError(f"'{self.__class__.__name__}.{name}' is immutable and cannot be modified after initialization")
        if name == "_cached_inverse" and self._cached_inverse() is not None:
            raise AttributeError(f"'{self.__class__.__name__}._cached_inverse' is write-once and has already been set")
        super().__setattr__(name, value)

    @property
    def generator(self) -> Generator:
        """The :class:`~catena.generators.Generator` supplying partial quotients."""
        return self._generator
    
    @property
    def integer_part(self) -> int:
        """The integer part ``a₀`` of the continued fraction."""
        return self._integer_part
    
    @integer_part.setter
    def integer_part(self, n: int):
        """
        Sets the integer part.

        Raises:
            TypeError: If ``n`` is not an ``int``.
        """
        if not isinstance(n, int):
            raise TypeError(f"Expected {type(1)} for '{self.__class__.__name__}.integer_part' but got {type(n)}")
        self._integer_part = n

    @property
    def cache_handler(self) -> BaseCache:
        """The :class:`~catena.cache.BaseCache` managing the convergent cache."""
        return self._tail_cache
    
    @property
    def convergents(self) -> ConvergentsView:
        """
        A view of the convergents of the SCF.

        Delegates to :attr:`tail_convergent` and :attr:`convergent` for scalar lookups, and provides 
        additional type conversions for individual convergents.  Notably, slicing is not supported 
        on this view since it is intended for infinite SCFs; use a loop or list comprehension instead.  
        For finite SCFs, use :attr:`finite_convergents` instead, which additionally supports slicing 
        and iteration.
        """
        return ConvergentsView(self)
    
    @classmethod
    def _from_shared(cls, source: 'SimpleContinuedFraction', integer_part: int) -> Self:
        """
        Creates a new instance that shares the generator and tail cache of
        ``source``, but has a different ``integer_part``.

        Used internally by :meth:`shift` and :meth:`__add__` to avoid
        redundant cache allocations when only ``a₀`` changes.
        """
        inst = cls.__new__(cls)
        object.__setattr__(inst, '_generator', source._generator)
        object.__setattr__(inst, '_tail_cache', source._tail_cache)
        inst.integer_part = integer_part
        return inst

    def __str__(self):
        return f"SimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part})"

    def __repr__(self):
        return f"SimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part}, cache_handler={self.cache_handler})"

    def shift(self, n: int) -> Self:
        """
        Returns a new SCF with ``integer_part`` shifted by ``n``, sharing the
        same generator and convergent cache.

        Args:
            n (int): The amount to add to ``integer_part``.

        Returns:
            SimpleContinuedFraction: A new instance with
            ``integer_part = self.integer_part + n``.
        """
        return self._from_shared(self, self._integer_part + n)
    
    def tail(self) -> Self:
        """
        Returns the tail of the SCF, i.e. a new instance with the same
        generator and convergent cache, but with ``integer_part = 0``.

        The tail corresponds to the SCF obtained by removing the integer part
        ``a₀`` from the original SCF, i.e. if ``x = [a₀; a₁, a₂, …]``, then
        ``x.tail()`` is ``[0; a₁, a₂, …]``.
        """
        return self._from_shared(self, 0)

    def __int__(self) -> int:
        """Returns the integer part of the SCF."""
        return self.integer_part

    def __add__(self, n: int) -> Self:
        """
        Shifts the integer part by ``n`` (``scf + n``).

        Returns :data:`NotImplemented` if ``n`` is not an ``int``.
        """
        if not isinstance(n, int):
            return NotImplemented
        
        return self.shift(n)

    def __radd__(self, n: int) -> Self:
        """
        Shifts the integer part by ``n`` (``n + scf``).

        Returns :data:`NotImplemented` if ``n`` is not an ``int``.
        """
        return self.__add__(n)
    
    def __float__(self) -> float:
        """
        Converts the SCF to a float by evaluating the 50-th convergent.

        Note: This is a heuristic choice for a large enough convergent 
        to give good enough precision. 64-bit floats have a precision 
        of about 15-17 decimal digits, and the denominator of the 45-th 
        convergent is usually big enough to ensure that onwards there
        is no distinction between the convergents at float precision.
        """
        p, q = self.convergent(50)
        return p / q
    
    def __neg__(self) -> Self:
        """
        Returns the additive inverse of the SCF, i.e., a new SCF representing -x if self represents x.
        """
        n = - (self.integer_part + 1)
        a0 = self.generator(0)
        if a0 > 1:
            # If a₁ > 1, we need the fractional part to be [0; 1, a₁-1, a₂, a₃, …] to ensure the correct value after negation.
            new_generator = (
                self.generator
                .advance(1) # Skip a₁ to get to a₂
                .prepend(FiniteGenerator([1, a0 - 1])) # Prepend 1 and a₁ - 1 to the front of the tail
                )
            
        else:
            # If a₁ = 1, we need the fractional part to be [0; a₂ + 1, a₃, …] to ensure the correct value after negation.
            new_generator = (
                self.generator
                .advance(2) # Skip a₁ and a₂ (which is 1) to get to a₃
                .prepend(FiniteGenerator([self.generator(1) + 1])) # Prepend a₂ + 1 to the front of the tail
                )
        
        return type(self)(new_generator, integer_part=n)

    def tail_convergent(self, n: int) -> Tuple[int, int]:
        """
        Computes the *n*-th convergent of the tail ``[a₁; a₂, …, aₙ₊₁]``.

        Args:
            n (int): 0-indexed depth.  ``n=-2`` and ``n=-1`` return the
                recurrence seeds ``(1, 0)`` and ``(0, 1)`` respectively.

        Returns:
            tuple[int, int]: ``(numerator, denominator)`` of the tail
            convergent at depth ``n``.
        """
        return self._tail_cache[n]
    
    def _tail_convergent(self, n: int) -> Tuple[int, int]:
        """
        Computes the *n*-th convergent of the tail ``[a₁; a₂, …, aₙ₊₁]``.

        Uses the standard two-term recurrence::

            h₋₂ = 1,  k₋₂ = 0
            h₋₁ = 0,  k₋₁ = 1
            hₙ = aₙ₊₁·hₙ₋₁ + hₙ₋₂     (n ≥ 0, aₙ₊₁ = generator(n))
            kₙ = aₙ₊₁·kₙ₋₁ + kₙ₋₂

        In particular: ``h₀ = 1``, ``k₀ = a₁ = generator(0)``.

        Results are memoised by :class:`~catena.cache.BaseCache`.

        Args:
            n (int): 0-indexed depth.  ``n=-2`` and ``n=-1`` return the
                recurrence seeds ``(1, 0)`` and ``(0, 1)``; ``n=0`` gives
                ``(1, a₁)``; ``n=1`` gives ``(a₂, a₁·a₂ + 1)``; etc.

        Returns:
            tuple[int, int]: ``(numerator, denominator)`` of the tail
            convergent at depth ``n``.

        Raises:
            RecursionError: If ``n < -2`` (indicates a logic error in
                the recurrence).
        """
        if n < -2:
            raise RecursionError("A negative value has been reached at runtime")

        # Base cases — never cached; returned directly so they never enter the
        # BaseCache and do not distort the frontier (largest_key).
        if n == -2:
            return 1, 0  # h₋₂ = 1, k₋₂ = 0
        if n == -1:
            return 0, 1  # h₋₁ = 0, k₋₁ = 1
        
        if n == 0:
            return 1, self.generator(0)  # h₀ = 1, k₀ = a₁

        # Iterative fill: advance from the current cache frontier to n.
        # BaseCache.largest_key gives the highest index already stored,
        # so we only compute the truly missing entries — O(gap) work and
        # O(1) stack depth regardless of n.
        # Clamp start to 0: base-case seeds (n=-2, n=-1) are handled above
        # and never entered into the cache; guard against a stale frontier
        # sitting below 0 from a previous clear/prune.
        cache = self._tail_cache
        lk = cache.largest_key
        start = 0 if (lk is None or lk < 0) else lk + 1

        if start > n:
            # n is already cached; __getitem__ will have returned before
            # reaching _tail_convergent, but guard for direct calls.
            return cache[n]

        # Seed the two values needed to begin the loop.
        prev2 = self._tail_cache[start - 2]
        prev1 = self._tail_cache[start - 1]

        for i in range(start, n + 1):
            a = int(self.generator(i))
            curr = (a * prev1[0] + prev2[0], a * prev1[1] + prev2[1])
            if i < n:
                cache[i] = curr  # write intermediates directly; wrapper writes n
            prev2, prev1 = prev1, curr

        return prev1
        
    def convergent(self, n: int) -> Tuple[int, int]:
        """
        Computes the *n*-th convergent of the full SCF ``[a₀; a₁, …, aₙ₊₁]``.

        Lifts the result of :meth:`tail_convergent` by incorporating
        :attr:`integer_part` (``a₀``)::

            convergent(n) = (a₀·kₙ + hₙ,  kₙ)

        where ``(hₙ, kₙ) = tail_convergent(n)``.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            tuple[int, int]: ``(numerator, denominator)`` of the *n*-th
            convergent of the full SCF.
        """
        h, k = self.tail_convergent(n)
        return self.integer_part * k + h, k
    
    def inverse(self) -> Self:
        """
        Returns the multiplicative inverse of the SCF, i.e. ``1/scf``.

        Two cases arise from the standard inversion identity:

        - If ``a₀ = 0``: ``x = [0; a₁, a₂, …]``, so
          ``1/x = [a₁; a₂, a₃, …]`` — the inverse has
          ``integer_part = a₁`` and the generator is shifted forward by one.
        - If ``a₀ ≠ 0``: ``x = [a₀; a₁, a₂, …]``, so
          ``1/x = [0; a₀, a₁, a₂, …]`` — the inverse has
          ``integer_part = 0`` and the generator prepends ``a₀`` before
          delegating to the original generator shifted back by one.

        The result is cached in ``_cached_inverse`` (write-once) and the inverse's
        own ``_cached_inverse`` is set back to ``self``, so calling ``inverse()``
        twice returns the original object.

        Returns:
            SimpleContinuedFraction: The multiplicative inverse of this SCF.
        """
        if hasattr(self, '_cached_inverse') and self._cached_inverse() is not None: 
            return cast(Self, self._cached_inverse())
        
        if self.integer_part == 0:
            new_integer_part = self.generator(0)
            new_generator = self.generator.advance(1) #lambda n: self.generator(n + 1)
        elif self.integer_part > 0:
            new_integer_part = 0
            new_generator = self.generator.prepend(FiniteGenerator([self.integer_part])) #lambda n: self.generator(n - 1) if n > 0 else self.integer_part
        else:
            result = -(-self).inverse()
            self._cached_inverse = weakref.ref(result)
            result._cached_inverse = weakref.ref(self)
            return result
        
        result = type(self)(new_generator, integer_part=new_integer_part)
        self._cached_inverse = weakref.ref(result)
        result._cached_inverse = weakref.ref(self)   # Cache the inverse of the inverse as the original SCF
        return result            # Make .inverse idempotent pair-wise while avoiding unecessary cloning.
    
    def segment(self, n: int) -> 'FiniteSimpleContinuedFraction':
        """
        Returns a finite SCF segment of the first ``n`` partial quotients.

        The result is a :class:`FiniteSimpleContinuedFraction` with
        ``integer_part = self.integer_part`` and
        ``partial_quotients = (self.generator(0), self.generator(1), …, self.generator(n-1))``.

        Args:
            n (int): The number of partial quotients to include in the segment.

        Returns:
            FiniteSimpleContinuedFraction: A finite SCF segment of the first
            ``n`` partial quotients.
        """
        return FiniteSimpleContinuedFraction(partial_quotients=tuple(self.generator(i) for i in range(n)), integer_part=self.integer_part)
        
    
class FiniteSimpleContinuedFraction(SimpleContinuedFraction):
    """
    A finite simple continued fraction ``[a₀; a₁, …, aₖ]``.

    Extends :class:`SimpleContinuedFraction` with a fixed, indexable sequence
    of partial quotients stored in a
    :class:`~catena.generators.FiniteGenerator`.  Provides:

    * Sequence-like properties: :attr:`partial_quotients`, :attr:`size`,
      ``__len__``, ``__float__``, ``__int__``, ``__bool__``.
    * Terminal (last) convergent shorthands: :attr:`terminal_convergent`,
      :attr:`terminal_tail_convergent`.
    * Arithmetic: adding two finite SCFs produces a new one equal to their
      rational sum.
    * Factory class methods: :meth:`from_rational`, :meth:`from_float`,
      :meth:`from_decimal`.
    """
    __slots__ = ()
    is_finite = True

    def __init__(self, partial_quotients: Sequence[int]|FiniteGenerator, integer_part: int = 0, dtype: Optional[str] = None):
        """
        Initialises the finite SCF from a sequence of partial quotients.

        Args:
            partial_quotients (Sequence[int]): The partial quotients
                ``a₁, a₂, …, aₖ`` (all must be strictly positive).
            integer_part (int): The integer part ``a₀``.  Defaults to ``0``.
            dtype (str, optional): Force a specific
                :class:`array.array` typecode for compact storage (one of
                ``'B'``, ``'H'``, ``'I'``, ``'L'``, ``'Q'``).  When ``None``
                the smallest fitting typecode is chosen automatically.

        Raises:
            TypeError: If ``partial_quotients`` is not a sequence of integers.
        """
        if isinstance(partial_quotients, FiniteGenerator):
            generator = partial_quotients
            
        else:
            generator = FiniteGenerator(partial_quotients, dtype=dtype) # FiniteGenerator will validate the input sequence and dtype

        super().__init__(generator=generator, integer_part=integer_part)
    
    @property
    def generator(self) -> FiniteGenerator:
        """The :class:`~catena.generators.FiniteGenerator` holding the partial quotients."""
        return cast(FiniteGenerator, super().generator)

    @property
    def partial_quotients(self) -> Tuple[int, ...]:
        """
        The partial quotients ``(a₁, a₂, …, aₖ)`` as an immutable tuple.

        Warning: Accessing this property implies materialising the entire tail in memory
        to a tuple, which may be expensive for large SCFs. Use with caution. Consider using 
        the :attr:`generator` directly for index-based access to partial quotients without 
        materialising the whole sequence, or :attr:`generator.view()` for a memory-efficient 
        read-only view of the partial quotients.
        """
        return tuple(self.generator)
    
    @property
    def size(self) -> int:
        """Number of partial quotients (length of the tail, excluding ``a₀``)."""
        return len(self.generator)

    @property
    def terminal_convergent(self) -> Tuple[int, int]:
        """The last convergent ``convergent(size - 1)`` — the exact rational value of the SCF."""
        if self.size == 0:
            return self.integer_part, 1
        return self.convergent(self.size - 1)

    @property
    def terminal_tail_convergent(self) -> Tuple[int, int]:
        """The last tail convergent ``tail_convergent(size - 1)``."""
        return self.tail_convergent(self.size - 1)
    
    @override
    @property
    def convergents(self) -> FiniteConvergentView:
        """A view of the convergents of the finite SCF, supporting slicing and iteration."""
        return FiniteConvergentView(self)
    
    def __str__(self):
        return f"FiniteSimpleContinuedFraction(partial_quotients={self.partial_quotients}, integer_part={self.integer_part})"
    
    def __repr__(self):
        return f"FiniteSimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part}, cache_handler={self.cache_handler})"
    
    def __len__(self):
        """Returns :attr:`size` (number of partial quotients in the tail)."""
        return self.size
    
    def __add__(self, other):
        """
        Adds an integer or another :class:`FiniteSimpleContinuedFraction`.

        - ``scf + int`` — shifts :attr:`integer_part` (inherited behaviour).
        - ``scf + scf`` — computes the rational sum of both terminal
          convergents and returns a new :class:`FiniteSimpleContinuedFraction`
          equal to that sum.
        - ``scf + rational or decimal`` — computes the rational  sum of the terminal convergent and
            the rational (other than int), and returns a new :class:`FiniteSimpleContinuedFraction` equal to that sum.

        Returns :data:`NotImplemented` for unsupported types.
        """
        if isinstance(other, FiniteSimpleContinuedFraction):
            s = mathlib.arithmetic.add_fractions(
                self.terminal_convergent, 
                other.terminal_convergent
            )
            return FiniteSimpleContinuedFraction.from_rational(s)

        if isinstance(other, (float, Fraction, Decimal)):
            o = Fraction(other) if not isinstance(other, Fraction) else other
            s = mathlib.arithmetic.uadd_fractions(*self.terminal_convergent, o.numerator, o.denominator)
            return FiniteSimpleContinuedFraction.from_rational(s)
            
        return super().__add__(other) # if int, will shift the integer part; else will return NotImplemented

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        """
        Multiplies by an integer, another :class:`FiniteSimpleContinuedFraction`, or a rational/decimal.

        - ``scf * scf`` — computes the rational product of both terminal convergents and returns a new :class:`FiniteSimpleContinuedFraction`
          equal to that product.
        - ``scf * rational or decimal`` — computes the rational product of the terminal convergent and
            the rational (including int), and returns a new :class:`FiniteSimpleContinuedFraction` equal to that product.

        Returns :data:`NotImplemented` for unsupported types.
        """
        if isinstance(other, FiniteSimpleContinuedFraction):
            s = mathlib.arithmetic.multiply_fractions(
                self.terminal_convergent, 
                other.terminal_convergent
            )
            return FiniteSimpleContinuedFraction.from_rational(s)

        if isinstance(other, (int, float, Fraction, Decimal)):
            o = other if isinstance(other, (int, Fraction)) else Fraction(other)
            s = mathlib.arithmetic.umultiply_fractions(*self.terminal_convergent, o.numerator, o.denominator)
            return FiniteSimpleContinuedFraction.from_rational(s)

        return NotImplemented

    def __truediv__(self, other):
        """
        Divides by an integer, another :class:`FiniteSimpleContinuedFraction`, or a rational/decimal.

        - ``scf / int`` — scales the terminal convergent by the reciprocal of the integer.
        - ``scf / scf`` — computes the rational quotient of both terminal convergents and returns a new :class:`FiniteSimpleContinuedFraction`
          equal to that quotient.
        - ``scf / rational or decimal`` — computes the rational quotient of the terminal convergent and
            the rational (including int), and returns a new :class:`FiniteSimpleContinuedFraction` equal to that quotient.

        Returns :data:`NotImplemented` for unsupported types.
        """
        if isinstance(other, FiniteSimpleContinuedFraction):
            s = mathlib.arithmetic.sandwich_fraction(
                self.terminal_convergent, 
                other.terminal_convergent
            )
            return FiniteSimpleContinuedFraction.from_rational(s)

        if isinstance(other, (int, float, Fraction, Decimal)):
            o = other if isinstance(other, (int, Fraction)) else Fraction(other)
            s = mathlib.arithmetic.usandwich_fraction(*self.terminal_convergent, o.numerator, o.denominator)
            return FiniteSimpleContinuedFraction.from_rational(s)

        return NotImplemented

    def __float__(self) -> float:
        """Returns the value of the terminal convergent as a Python ``float``."""
        tc = self.terminal_convergent
        return tc[0]/tc[1]

    def to_decimal(self) -> Decimal:
        """Returns the exact rational value as a :class:`decimal.Decimal`.

        Python's :class:`~decimal.Decimal` constructor has no ``__decimal__``
        protocol (unlike :class:`float` which calls ``__float__``), so
        ``Decimal(scf)`` cannot work directly.  Call this method instead::

            d = scf.to_decimal()
        """
        tc = self.terminal_convergent
        return Decimal(tc[0])/Decimal(tc[1])

    def __bool__(self):
        """Returns ``False`` only when ``integer_part == 0`` and the tail is empty."""
        return self.integer_part != 0 or len(self) != 0

    def __eq__(self, value):
        """
        Equality comparison.

        - If ``value`` is a :class:`FiniteSimpleContinuedFraction`, compares
          their terminal convergents for equality (i.e. checks if they represent the same rational number).
        - If ``value`` is a any numeric type (e.g. ``int``, ``float``, ``Fraction``), converts it to 
        a rational and compares to the terminal convergent.
        - For other types, returns :data:`NotImplemented`.
        """
        # We are compelled to use terminal convergent for comparison, as the same rational number can have multiple SCF representations (e.g. [1; 2] = [1; 1, 1]).
        if isinstance(value, FiniteSimpleContinuedFraction):
            return self.terminal_convergent == value.terminal_convergent
        
        elif isinstance(value, (int, float, Fraction)):
            try:
                other_frac = value if isinstance(value, Fraction) else Fraction(value)
                return Fraction(*self.terminal_convergent) == other_frac
            except (ValueError, OverflowError):
                return NotImplemented
        else:
            return NotImplemented

    def __hash__(self):
        """Hashes the terminal convergent, so that equal SCFs have the same hash."""
        # array.array are unhashable, so we cannot hash the generator directly. 
        return hash(self.terminal_convergent)

    def __neg__(self):
        if self.size <= 2: # For general negation, we ned a1 and a2 to be accessible, so here we do it by hand.
            return FiniteSimpleContinuedFraction.from_rational(-Fraction(*self.terminal_convergent))
        
        return super().__neg__()  # Use the general negation logic from SimpleContinuedFraction for larger SCFs
    
    @classmethod
    def from_rational(cls, r: mathlib.convert.Rational) -> 'FiniteSimpleContinuedFraction':
        """
        Constructs a :class:`FiniteSimpleContinuedFraction` from a rational number.

        Args:
            r (Rational): A :class:`~fractions.Fraction`, a
                ``(numerator, denominator)`` tuple, or a plain ``int``.

        Returns:
            FiniteSimpleContinuedFraction: The exact SCF representation of ``r``.
        """
        integer_part, partial_quotients = mathlib.convert.from_rational_to_scf(r)
        return cls(partial_quotients=partial_quotients, integer_part=integer_part)
    
    @classmethod
    def from_float(cls, f: float, max_denominator: Optional[int] = None) -> 'FiniteSimpleContinuedFraction':
        """
        Constructs a :class:`FiniteSimpleContinuedFraction` from a float.

        Args:
            f (float): The floating-point value to convert.
            max_denominator (int, optional): If provided, the rational
                approximation is bounded by this denominator via
                :meth:`~fractions.Fraction.limit_denominator`.

        Returns:
            FiniteSimpleContinuedFraction: The SCF of the rational
            approximation of ``f``.
        """
        r = mathlib.convert.from_float_to_rational(f, max_denominator)
        return cls.from_rational(r)
    
    @classmethod
    def from_decimal(cls, d: str) -> 'FiniteSimpleContinuedFraction':
        """
        Constructs a :class:`FiniteSimpleContinuedFraction` from a decimal string.

        Args:
            d (str): A finite decimal string (e.g. ``"3.14159"`` or ``"42"``).

        Returns:
            FiniteSimpleContinuedFraction: The exact SCF of the rational
            number represented by ``d``.

        Raises:
            ValueError: If ``d`` is not a string or not a finite decimal.
        """
        r = mathlib.convert.from_decimal_to_rational(d)
        return cls.from_rational(r)
    
    @override
    def inverse(self) -> 'FiniteSimpleContinuedFraction':
        """
        Returns the multiplicative inverse of the finite SCF, i.e. ``1/scf``.

        The result is a new :class:`FiniteSimpleContinuedFraction` whose
        terminal convergent is the reciprocal of this SCF's terminal
        convergent.

        Returns:
            FiniteSimpleContinuedFraction: The multiplicative inverse of this
            finite SCF.
        """
        if hasattr(self, '_cached_inverse') and self._cached_inverse() is not None:
            return cast(Self, self._cached_inverse())
        
        if self.size == 0 and self.integer_part == 0:
            raise ZeroDivisionError("Cannot invert a zero value")
        
        inv = super().inverse()
        # Seed inv's terminal tail convergent from self's cache to avoid
        # recomputing the full recurrence when inv.terminal_convergent is
        # called later.  Only runs when self's cache already reaches the
        # terminal entry (largest_key == size - 1).
        if self.cache_handler.largest_key == self.size - 1:
            if self.integer_part == 0 and self.size > 0:
                # inv = [a₁; a₂, …, aₙ]  (advance by 1, inv.size = n-1)
                # inv.tail_convergent(n-2) = (k_{n-1} - a₁·h_{n-1},  h_{n-1})
                ttc = self.tail_convergent(self.size - 1)   # free – already cached
                a1 = self.generator(0)
                inv.cache_handler[inv.size - 1] = (ttc[1] - a1 * ttc[0], ttc[0])
            elif self.integer_part > 0 and self.size > 0:
                # inv = [0; a₀, a₁, …, aₙ]  (prepend a₀, inv.size = n+1)
                # inv.tail_convergent(n) = (k_{n-1},  h_{n-1})  = (tc[1], tc[0])
                tc = self.terminal_convergent               # free – already cached
                inv.cache_handler[inv.size - 1] = (tc[1], tc[0])

        else:
            pass # for the negative case, the logic -(-self).inverse() passes the paths above as well.

        return inv  # Use the general inversion logic from SimpleContinuedFraction, which will handle caching and inverse of inverse correctly. The terminal convergent will be inverted correctly by the logic in SimpleContinuedFraction.inverse().
    
    @override
    def segment(self, n: int) -> 'FiniteSimpleContinuedFraction':
        """
        Returns a segment of the first ``n`` partial quotients.

        For a finite SCF, this is effectively a truncation.  The result is a
        new :class:`FiniteSimpleContinuedFraction` with
        ``integer_part = self.integer_part`` and
        ``partial_quotients = (self.generator(0), self.generator(1), …, self.generator(n-1))``.

        Args:
            n (int): The number of partial quotients to include in the segment.
                If ``n >= size``, the entire SCF is returned without truncation.

        Returns:
            FiniteSimpleContinuedFraction: A finite SCF segment of the first
            ``n`` partial quotients.

        Raises:
            IndexError: If ``n`` exceeds the size of the finite SCF.
        """
        if n > self.size:
            raise IndexError(f"Segment length n={n} exceeds the size of the finite SCF (size={self.size})")
        
        if n == self.size:
            return self.shift(0)  # Return a new instance with the same content to ensure immutability of the original SCF
        
        return super().segment(n)


class PeriodicSimpleContinuedFraction(SimpleContinuedFraction):
    """
    A periodic simple continued fraction ``[a₀; a₁, …, aₘ, (b₁, …, bₙ)]``.

    Extends :class:`SimpleContinuedFraction` with two fixed sequences of
    partial quotients stored in
    :class:`~catena.generators.FiniteGenerator` instances: the non-repeating
    prefix ``[a₁, …, aₘ]`` (the *pre-period*) and the repeating period
    ``(b₁, …, bₙ)``.  All :class:`SimpleContinuedFraction` methods
    (``convergent``, ``tail_convergent``, ``tail``, ``segment``, ``shift``,
    ``__add__``) are inherited unchanged.  Additional members:

    * Structure: :attr:`non_repeating_part`, :attr:`period`.
    * Numeric: ``__float__`` (overridden; uses algebraic formula directly),
      ``__neg__``, :meth:`as_decimal`.
    * Factory: :meth:`from_quadratic_surd`.
    * Algebraic (justification deferred): :meth:`quadratic_coefficients`,
      :meth:`quadratic_surd`, :meth:`is_principal_surd`,
      :meth:`is_conjugate_root`, :meth:`inverse` (overridden),
      :meth:`conjugate`.
    """
    __slots__ = ('_quadratic_coefficients', '_quadratic_surd', '_cached_conjugate')

    if TYPE_CHECKING:
        _quadratic_coefficients: Tuple[int, int, int]
        _quadratic_surd: Tuple[int, int, int]
        _cached_conjugate: weakref.ReferenceType['PeriodicSimpleContinuedFraction']

    def __init__(self, period: Union[Sequence[int], 'PeriodicGenerator'], pre_period: Sequence[int] = (), integer_part: int = 0, dtypes: Tuple[Optional[str], Optional[str]] = (None, None)):
        """
        Initialises the periodic SCF from non-repeating and repeating parts.

        Args:
            period (Sequence[int] | PeriodicGenerator): The repeating partial quotients
                ``b₁, b₂, …, bₙ`` (all must be strictly positive). If a ``PeriodicGenerator`` 
                is provided, its period and pre-period are used directly and the ``pre_period`` 
                and ``dtypes`` arguments are ignored.
            pre_period (Sequence[int], optional): The non-repeating partial
                quotients ``a₁, a₂, …, aₘ`` (all must be strictly positive).  
                Defaults to an empty sequence (i.e. no pre-period).
            integer_part (int): The integer part ``a₀``.  Defaults to ``0``.
            dtypes (Tuple[Optional[str], Optional[str]], optional): Force specific
                :class:`array.array` typecodes for compact storage of the
                period and pre-period respectively (each one of ``'B'``, ``'H'``, ``'I'``, ``'L'``, ``'Q'``).
                When ``None``, the smallest fitting typecode is chosen automatically. 
                    Note: (str, None) and (None, str) are also accepted to specify a typecode 
                    for only one of the two sequences.
        """

        if isinstance(period, PeriodicGenerator):
            generator = period
        else:
        
            generator = PeriodicGenerator(period=period, pre_period=pre_period, dtypes=dtypes)

        super().__setattr__('_cached_conjugate', self._empty_cached_entry)
        super().__init__(generator=generator, integer_part=integer_part)

    def __setattr__(self, name, value):
        if name in {"_quadratic_coefficients", "_quadratic_surd", "_cached_conjugate"} and hasattr(self, name):
            current = getattr(self, name)
            # Allow overwrite if still the sentinel or if the weakref has been collected
            if current is not self._empty_cached_entry and (not callable(current) or current() is not None):
                raise AttributeError(f"'{self.__class__.__name__}.{name}' is write-once and has already been set")
        
        super().__setattr__(name, value)

    @property
    def generator(self) -> PeriodicGenerator:
        """The :class:`~catena.generators.PeriodicGenerator` holding the partial quotients."""
        return cast(PeriodicGenerator, super().generator)
    
    @property
    def non_repeating_part(self) -> Tuple[int, ...]:
        """The non-repeating partial quotients ``(a₁, a₂, …, aₘ)`` as an immutable tuple."""
        return tuple(self.generator.pre_period)
    
    @property
    def period(self) -> Tuple[int, ...]:
        """The repeating partial quotients ``(b₁, b₂, …, bₙ)`` as an immutable tuple."""
        return tuple(self.generator.period)
    
    def __str__(self) -> str:
        return f"PeriodicSimpleContinuedFraction(non_repeating_part={self.non_repeating_part}, period={self.period}, integer_part={self.integer_part})"
    
    def __repr__(self) -> str:
        return f"PeriodicSimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part}, cache_handler={self.cache_handler})"
    
    def __float__(self) -> float:
        """Returns the value of the SCF as a Python ``float``."""
        P, Q, D = self.quadratic_surd()
        return (P + D**0.5)/Q
    
    @override
    def __neg__(self):
        """Returns the additive inverse of the SCF, i.e., a new SCF representing -x if self represents x."""
        # The special case of periodic SCFs allows to define a negation operation trivially.
        # If the value of the SCF is (P + √D)/Q, then its negation is (-P - √D)/Q,
        # or what is the same, (P + √D)/(-Q).
        P, Q, D = self.quadratic_surd()
        negated_surd = (P, -Q, D)
        return self.from_quadratic_surd(*negated_surd)

    def __eq__(self, other):
        """
        Equality comparison.

        Only defined for another :class:`PeriodicSimpleContinuedFraction`.
        """
        if not isinstance(other, PeriodicSimpleContinuedFraction):
            return NotImplemented
        
        return self.quadratic_surd() == other.quadratic_surd()
    
    def __hash__(self):
        """Hashes the quadratic surd parameters, so that equal SCFs have the same hash."""
        return hash(self.quadratic_surd())

    def as_decimal(self) -> Decimal:
        """Returns the value of the SCF as a :class:`decimal.Decimal`."""
        P, Q, D = self.quadratic_surd()
        return (Decimal(P) + Decimal(D).sqrt())/Decimal(Q)

    @classmethod
    def from_quadratic_surd(cls, P: int, Q: int, D: int) -> Self:
        """
        Constructs a :class:`PeriodicSimpleContinuedFraction` from the parameters of a quadratic surd.

        The value of the SCF is expressed as (P + √D)/Q where P, Q, D are integers satisfying:

            A = Q/2
            B = -P
            C = (P² - D)/4
        """
        _int, pre_period, period = mathlib.convert.from_quadratic_surd_to_scf(P, Q, D)
        return cls(pre_period=pre_period, period=period, integer_part=_int)
    
    def quadratic_coefficients(self) -> Tuple[int, int, int]:
        """
        As any periodic SCF represents a quadratic irrational, this method
        computes the coefficients (A, B, C) of the quadratic equation
        A·x² + B·x + C = 0 satisfied by the value of this periodic SCF.

        Returns:
            tuple[int, int, int]: The coefficients (A, B, C) of the
            quadratic equation.
        """
        if hasattr(self, '_quadratic_coefficients'):
            return self._quadratic_coefficients
        
        A, B, C = self.generator.quadratic_coefficients()
        if self.integer_part != 0:
            # If a₀ is not zero, we need to adjust the coefficients to account for the shift in the value of the SCF.
            # Say x is the SCF of intrest, and let y = x - a₀, where y satisfies the quadratic equation
            # A·y² + B·y + C = 0. Substituting y = x - a₀:
            # A·(x - a₀)² + B·(x - a₀) + C = 0
            # Expanding this gives:
            # A·(x² - 2·a₀·x + a₀²) + B·x - B·a₀ + C = 0
            # -> A·x² + (B - 2·A·a₀)·x + (A·a₀² - B·a₀ + C) = 0

            # Since for us A is garanteed to be positive, we can directly use it without worrying about the sign.
            # Likewiese, gdc(A, B, C) = 1, so we don't need to worry about simplifying the coefficients.

            A_adj = A
            B_adj = B - 2 * A * self.integer_part
            C_adj = C - B * self.integer_part + A * self.integer_part ** 2
            self._quadratic_coefficients = (A_adj, B_adj, C_adj)
            return A_adj, B_adj, C_adj
        
        self._quadratic_coefficients = (A, B, C)
        return A, B, C

    def quadratic_surd(self) -> Tuple[int, int, int]:
        """
        Computes the (P, Q, D) parameters of the quadratic surd representation
        of this periodic SCF.

        The value of the SCF can be expressed as (P + √D)/Q where P, Q, D are
        integers computed from the quadratic coefficients A, B, C as follows:

            P = -B
            D = B**2 - 4*A*C
            Q = 2*A

        Returns:
            tuple[int, int, int]: The parameters (P, Q, D) of the
            quadratic surd representation.
        """
        if hasattr(self, '_quadratic_surd'):
            return self._quadratic_surd
        
        A, B, C = self.quadratic_coefficients()
        coefs = mathlib.quadratic.quadratic_surd_from_coefficients(A, B, C)
        if coefs is None:
            raise ValueError("The quadratic coefficients do not correspond to a valid quadratic surd (discriminant must be non-square and positive)")
        
        P, Q, D = coefs

        _int, pre_period, period = mathlib.convert.from_quadratic_surd_to_scf(P, Q, D)
        if self.integer_part == _int and self.non_repeating_part == pre_period and self.period == period:
            # If the original SCF is already in the normalized surd form, we can directly return the surd parameters without worrying about the sign.
            self._quadratic_surd = (P, Q, D)
            return self._quadratic_surd
        else:
            # Otherwise, the original SCF is itself the conjugate of the normalized surd form, so we need to negate the surd parameters to get the correct value.
            self._quadratic_surd = (-P, -Q, D)
            return self._quadratic_surd

    @override
    def inverse(self) -> Self:
        """
        Returns the multiplicative inverse of the periodic SCF, i.e. ``1/scf``.

        The result is a new :class:`PeriodicSimpleContinuedFraction` whose
        value is the reciprocal of this SCF's value.

        Returns:
            PeriodicSimpleContinuedFraction: The multiplicative inverse of this
            periodic SCF.
        """
        if hasattr(self, '_cached_inverse') and self._cached_inverse() is not None:
            return cast(Self, self._cached_inverse())
        
        _, _, C = self.quadratic_coefficients()
        if C == 0:
            raise ZeroDivisionError("Cannot invert a zero value (rational root)")

        P, Q, D = self.quadratic_surd()
        if Q > 0: # Principal surd case
            self._cached_inverse = weakref.ref(type(self).from_quadratic_surd(-Q * P, -(P**2 - D), D * Q**2))
        else: # Conjugate surd case
            self._cached_inverse = weakref.ref(type(self).from_quadratic_surd(Q * P, (P**2 - D), D * Q**2))

        cast(Self, self._cached_inverse())._cached_inverse = weakref.ref(self)  # Cache the inverse of the inverse as the original SCF
        return cast(Self, self._cached_inverse())

    def is_principal_surd(self) -> bool:
        """
        Checks if the value of this periodic SCF is the principal root of its quadratic equation.

        The principal root of A·x² + B·x + C = 0 is the one with the positive square root in the surd representation (P + √D)/Q. 
        If the value of this SCF corresponds to the negative square root (P - √D)/Q, then it is not the principal surd.

        Returns:
            bool: True if this SCF is the principal surd, False otherwise.
        """
        _, Q, _ = self.quadratic_surd()
        return Q > 0

    def is_conjugate_root(self) -> bool:
        """
        Checks if the value of this periodic SCF is the conjugate root of its quadratic equation.

        The conjugate root of A·x² + B·x + C = 0 is the one with the negative square root in the surd representation (P - √D)/Q. 
        If the value of this SCF corresponds to the positive square root (P + √D)/Q, then it is not the conjugate root.

        Returns:
            bool: True if this SCF is the conjugate root, False otherwise.
        """
        _, Q, _ = self.quadratic_surd()
        return Q < 0

    def conjugate(self) -> 'PeriodicSimpleContinuedFraction':
        """
        Returns the algebraic conjugate of the periodic SCF.

        The algebraic conjugate of a root of A·x² + B·x + C = 0 is the other root of the same equation.
        If the roots are x₁ = (P + √D)/Q and x₂ = (P - √D)/Q, then the conjugate is x₂.

        Returns:
            PeriodicSimpleContinuedFraction: The algebraic conjugate of this
            periodic SCF.
        """
        if hasattr(self, '_cached_conjugate') and self._cached_conjugate() is not None:
            return cast(Self, self._cached_conjugate())

        P, Q, D = self.quadratic_surd()
        P_conj, Q_conj = -P, -Q
        result = type(self).from_quadratic_surd(P_conj, Q_conj, D)
        self._cached_conjugate = weakref.ref(result)
        result._cached_conjugate = weakref.ref(self)

        return result
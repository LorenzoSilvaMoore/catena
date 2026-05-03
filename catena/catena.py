"""
Core continued-fraction types.

This module exposes three public classes:

- :class:`SimpleContinuedFraction` — an infinite (or generative) simple
  continued fraction ``[a₀; a₁, a₂, …]`` where the partial quotients are
  produced on demand by a :class:`~catena.generators.Generator`.
  Convergents are memoised in an :class:`~catena.cache.OrdinalCache`.

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

from .cache import OrdinalCache, CacheHandler, SetLightCache

from typing import Callable, Tuple, Optional, override
from decimal import Decimal
from collections.abc import Sequence

from .generators import Generator, FiniteGenerator, PeriodicGenerator
import catena.mathlib as mathlib

# IntPair = tuple[int, int]
# IntTriplet = tuple[int, int, int]
# FloatAsStr = str

# CacheHandler = Any
# Cache = Any
# SetCache = Any

# def get_sign(n: int) -> int:
#     if n > 0:
#         return 1
#     elif n < 0:
#         return -1
#     else:
#         return 0

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
    
#     @staticmethod
#     def compress_body(body: Sequence[int]) -> list[int]:
#         compressed = []
#         i, l = 0, len(body)
#         while i < l:
#             if i < l - 1 and body[i] == 0 and body[i + 1] == 0:
#                 i += 2 
#             else:
#                 compressed.append(body[i])
#                 i += 1

#         if len(compressed) > 2 and compressed[-1]==1:
#             compressed[-2] += 1
#             return compressed[:-1]
#         return compressed


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



# class FinateSimpleContinuedFraction:
#     def __init__(self, head: int = 0, body: Iterable[int] = None, frac: Optional[IntPair] = None):
#         if isinstance(head, Iterable):
#             frac = tuple(head)

#         if frac is not None:
#             head, body = Convert.from_rational_to_scf(*frac)
#         else:
#             if not body:
#                 body = (1,)

#         super().__setattr__("_head", int(head)) 
#         super().__setattr__("_body", tuple(body))
#         super().__setattr__("_cache_handler", CacheHandler(Cache()))
#         super().__setattr__("_size", len(self.body))
#         self._str_length = 256
#         self._head = int(head)

#         self.convergent = SetLightCache(self.cache_handler, self._convergent)
    
#     @property
#     def head(self) -> int:
#         return self._head
    
#     @head.setter
#     def head(self, n: int):
#         if not isinstance(n, int):
#             raise TypeError(f"Expected {type(1)} for '{self.__class__.__name__}.head' but got {type(n)}")
#         self._head = n

#     @property
#     def str_length(self) -> int:
#         return self._str_length
    
#     @str_length.setter
#     def str_length(self, n: int):
#         if not isinstance(n, int):
#             raise TypeError(f"Expected {type(1)} for '{self.__class__.__name__}.str_length' but got {type(n)}")
#         self._str_length = n
    
#     @property
#     def body(self) -> tuple:
#         return self._body
    
#     @property
#     def cache_handler(self) -> CacheHandler:
#         return self._cache_handler
    
#     @property
#     def cache(self) -> Cache:
#         return self._cache_handler.cache
    
#     @property
#     def size(self) -> int:
#         return self._size

#     def __setattr__(self, key, value):
#         if key in {"_body", "_cache_handler", "_size"}:
#             raise AttributeError(f"'{self.__class__.__name__}.{key}' is immutable and cannot be modified after initialization")
#         super().__setattr__(key, value)

#     def __len__(self):
#         return self.size+1
    
#     def _convergent(self, n: int) -> IntPair:
#         if n >= self.size:
#             n = self.size - 1
#             return self.convergent(n)
#         if n < 0:
#             raise RecursionError("A negative value has been reached at runtime")

#         if n == 0:
#             p, q = 1, self.body[0]
#         elif n == 1:
#             p, q = self.body[1], self.body[0] * self.body[1] + 1
#         else:
#             m1, m2, a = self.convergent(n-1), self.convergent(n-2), int(self.body[n])
#             p, q = m1[0] * a + m2[0], m1[1] * a + m2[1]

#         return (p, q)
    
#     def aftermost_convergent(self) -> IntPair:
#         return self.convergent(self.size - 1)
    
#     def convergent_as_float(self, n: Optional[int]=None) -> IntPair:
#         if n is None:
#             n = self.size - 1

#         convergent = self.convergent(n)
#         return convergent[0] + self.head * convergent[1], convergent[1]
    
#     def convergent_as_digits(self, n: Optional[int]=None, d: Optional[int]=None) -> float:
#         if n is None:
#             n = self.size - 1
#         if d is None:
#             d = getcontext().prec

#         try:
#             p, q = self.convergent(n)
#             with localcontext() as ctx:
#                 ctx.prec = d + 5
#                 decimal_value = Decimal(p)/Decimal(q)
#                 decimal_str = str(decimal_value).replace('.', '')[:d]
#             return tuple(map(int, list(decimal_str)))
#         except ZeroDivisionError:
#             warnings.warn("A division by zero has been attemped at run time")
#             return 0.0
    
#     def convergent_as_decimal(self, n: Optional[int]=None) -> float:
#         if n is None:
#             n = self.size - 1

#         try:
#             p, q = self.convergent(n)
#             return Decimal(p)/Decimal(q)
#         except ZeroDivisionError:
#             warnings.warn("A division by zero has been attemped at run time")
#             return 0.0
    
#     def convergent_as_string(self, n: Optional[int]=None, length: Optional[int]=None):
#         if n is None:
#             n = self.size - 1

#         if length is None:
#             length=self.str_length

#         return StringMethod.string_divition(self.convergent(n), length=length)
    
#     def convergent_float_as_string(self, n: Optional[int]=None, length: Optional[int]=None):
#         if n is None:
#             n = self.size - 1

#         if length is None:
#             length=self.str_length
            
#         return StringMethod.string_divition(self.convergent_as_float(n), length=length)

#     def float_value(self, n: Optional[int]=None):
#         if n is None:
#             n = self.size - 1

#         return self.head + Method.devide(*self.convergent(n))
    
#     def decimal_value(self, n: Optional[int]=None):
#         if n is None:
#             n = self.size - 1

#         return Decimal(self.head) + self.convergent_as_decimal(n)
    
#     def denominator_length(self, n: Optional[int]=None):
#         if n is None:
#             n = self.size - 1

#         return int(log10(self.convergent(n)[1]))+1
    
#     def iconvergents(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1
            
#         for i in range(start, stop, step):
#             yield self.convergent(i)

#     def iaftermost_convergents(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1

#         for i in range(start, stop, step):
#             yield self.aftermost_convergent(i)

#     def iconvergents_as_float(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1

#         for i in range(start, stop, step):
#             yield self.convergent_as_float(i)

#     def iconvergents_as_digits(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None, d: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1

#         for i in range(start, stop, step):
#             yield self.convergent_as_digits(i, d)

#     def iconvergents_as_string(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None, length: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1
#         if length is None:
#             length=self.str_length

#         for i in range(start, stop, step):
#             yield StringMethod.string_divition(self.convergent(i), length=length)

#     def iconvergents_float_as_string(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None, length: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1
#         if length is None:
#             length=self.str_length

#         for i in range(start, stop, step):
#             yield StringMethod.string_divition(self.convergent_as_float(i), length=length)

#     def ifloat_values(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None):
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1

#         for i in range(start, stop, step):
#             yield self.head + Method.devide(*self.convergent(i))
    
#     def idecimal_values(self, start: int=0, stop: Optional[int]=None, step: Optional[int]=None):
#         if n is None:
#             n = self.size - 1
#         if stop is None:
#             stop = self.size
#         if step is None:
#             step = 1

#         for i in range(start, stop, step):
#             yield Decimal(self.head) + self.convergent_as_decimal(i)


class SimpleContinuedFraction:
    """
    An infinite simple continued fraction ``[a₀; a₁, a₂, …]``.

    The partial quotients ``a₁, a₂, …`` are supplied by a
    :class:`~catena.generators.Generator` callable.  The integer part
    ``a₀`` is stored separately as :attr:`integer_part`.

    Tail convergents are automatically memoised via
    :class:`~catena.cache.SetLightCache` so repeated calls to
    :meth:`tail_convergent` or :meth:`convergent` with the same index are O(1)
    after the first computation.

    Attributes ``_generator``, ``_cache_handler``, and ``tail_convergent`` are
    frozen after construction; attempting to overwrite them raises
    :exc:`AttributeError`.
    """

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
        super().__setattr__("_cache_handler", CacheHandler(OrdinalCache()))
        super().__setattr__("tail_convergent", SetLightCache(self.tail_convergent, self.cache_handler))
    
    def __setattr__(self, name, value):
        """
        Guards frozen attributes against reassignment after construction.

        ``_generator``, ``_cache_handler``, and ``tail_convergent`` are
        permanently frozen.  ``_inverse`` is write-once: it can be set
        exactly once (by :meth:`inverse`) and raises :exc:`AttributeError`
        on any subsequent assignment.

        Raises:
            AttributeError: If ``name`` is one of ``_generator``,
                ``_cache_handler``, or ``tail_convergent`` (always), or
                ``_inverse`` after it has already been set.
        """
        if name in {"_generator", "_cache_handler", "tail_convergent"}:
            raise AttributeError(f"'{self.__class__.__name__}.{name}' is immutable and cannot be modified after initialization")
        if name == "_inverse" and hasattr(self, "_inverse"):
            raise AttributeError(f"'{self.__class__.__name__}._inverse' is write-once and has already been set")
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
    def cache_handler(self) -> CacheHandler:
        """The :class:`~catena.cache.CacheHandler` managing the convergent cache."""
        return self._cache_handler
    
    @classmethod
    def _from_shared(cls, source: 'SimpleContinuedFraction', integer_part: int) -> 'SimpleContinuedFraction':
        """
        Creates a new instance that shares the generator and tail cache of
        ``source``, but has a different ``integer_part``.

        Used internally by :meth:`shift` and :meth:`__add__` to avoid
        redundant cache allocations when only ``a₀`` changes.
        """
        inst = cls.__new__(cls)
        object.__setattr__(inst, '_generator', source._generator)
        object.__setattr__(inst, '_cache_handler', source._cache_handler)
        object.__setattr__(inst, 'tail_convergent', source.tail_convergent)
        inst._integer_part = integer_part
        return inst

    def __str__(self):
        return f"SimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part})"

    def shift(self, n: int) -> 'SimpleContinuedFraction':
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
    
    def tail(self) -> 'SimpleContinuedFraction':
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

    def __add__(self, n: int) -> 'SimpleContinuedFraction':
        """
        Shifts the integer part by ``n`` (``scf + n``).

        Returns :data:`NotImplemented` if ``n`` is not an ``int``.
        """
        if not isinstance(n, int):
            return NotImplemented
        return self.shift(n)

    def __radd__(self, n: int) -> 'SimpleContinuedFraction':
        """
        Shifts the integer part by ``n`` (``n + scf``).

        Returns :data:`NotImplemented` if ``n`` is not an ``int``.
        """
        if not isinstance(n, int):
            return NotImplemented
        return self.shift(n)
    
    def tail_convergent(self, n: int) -> Tuple[int, int]:
        """
        Computes the *n*-th convergent of the tail ``[a₁; a₂, …, aₙ₊₁]``.

        Uses the standard two-term recurrence::

            h₋₁ = 1,  h₀ = a₁
            k₋₁ = 0,  k₀ = 1          (implicit via base cases below)
            hₙ = aₙ₊₁·hₙ₋₁ + hₙ₋₂
            kₙ = aₙ₊₁·kₙ₋₁ + kₙ₋₂

        Results are memoised by :class:`~catena.cache.SetLightCache`.

        Args:
            n (int): 0-indexed depth.  ``n=0`` gives the first convergent
                ``1/a₁``; ``n=1`` gives ``a₂/(a₁·a₂ + 1)``; etc.

        Returns:
            tuple[int, int]: ``(numerator, denominator)`` of the tail
            convergent at depth ``n``.

        Raises:
            RecursionError: If ``n < -2`` (indicates a logic error in
                the recurrence).
        """
        if n < -2:
            raise RecursionError("A negative value has been reached at runtime")
        
        if n == -2:
            return 1, 0  # h₋₂ = 0, k₋₂ = 1
        
        if n == -1:
            return 0, 1  # h₋₁ = 1, k₋₁ = 0
        
        if n == 0:
            return 1, self.generator(0)
        
        elif n == 1:
            return self.generator(1), self.generator(0) * self.generator(1) + 1
        
        else:
            m1, m2, a = self.tail_convergent(n-1), self.tail_convergent(n-2), int(self.generator(n))
            return m1[0] * a + m2[0], m1[1] * a + m2[1]
        
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
    
    def inverse(self) -> 'SimpleContinuedFraction':
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

        The result is cached in ``_inverse`` (write-once) and the inverse's
        own ``_inverse`` is set back to ``self``, so calling ``inverse()``
        twice returns the original object.

        Returns:
            SimpleContinuedFraction: The multiplicative inverse of this SCF.
        """
        if hasattr(self, '_inverse'): 
            return self._inverse
        
        if self.integer_part == 0:
            new_integer_part = self.generator(0)
            new_generator = lambda n: self.generator(n + 1)
        else:
            new_integer_part = 0
            new_generator = lambda n: self.generator(n - 1) if n > 0 else self.integer_part

        self._inverse = SimpleContinuedFraction(generator=new_generator, integer_part=new_integer_part)
        self._inverse._inverse = self   # Cache the inverse of the inverse as the original SCF
        return self._inverse            # Make .inverse idempotent pair-wise while avoiding unecessary cloning.
        
    
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
        return super().generator

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

        Returns :data:`NotImplemented` for unsupported types.
        """
        if isinstance(other, FiniteSimpleContinuedFraction):
            tc1 = self.terminal_convergent
            tc2 = other.terminal_convergent

            s = mathlib.arithmetic.add_fractions(tc1, tc2)
            return FiniteSimpleContinuedFraction.from_rational(s)
        
        return super().__add__(other)
    
    def __float__(self):
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
        if hasattr(self, '_inverse'):
            return self._inverse
        
        tc = self.terminal_convergent
        if tc[0] == 0:
            raise ZeroDivisionError("Cannot invert a zero value")
        
        r = mathlib.convert.from_rational_to_scf((tc[1], tc[0]))  # Invert the terminal convergent
        self._inverse = FiniteSimpleContinuedFraction(partial_quotients=r[1], integer_part=r[0]) # This is necessary to have all internal attributes properly set for the inverse.
        self._inverse._inverse = self 
        return self._inverse


class PeriodicSimpleContinuedFraction(SimpleContinuedFraction):
    """
    A periodic simple continued fraction ``[a₀; a₁, …, aₘ, (b₁, …, bₙ)]``.

    Extends :class:`SimpleContinuedFraction` with two fixed sequences of
    partial quotients stored in
    :class:`~catena.generators.FiniteGenerator` instances: the non-repeating
    prefix ``[a₁, …, aₘ]`` and the repeating period ``(b₁, …, bₙ)``.  Provides:

    * Sequence-like properties: :attr:`non_repeating_part`, :attr:`period`,
      :attr:`period_length`, ``__len__``, ``__float__``, ``__int__``, ``__bool__``.
    * Terminal convergent shorthands: :attr:`period_convergent`,
      :attr:`period_tail_convergent`.
    * Factory class methods: :meth:`from_rational`, :meth:`from_float`,
      :meth:`from_decimal`.
    """

    def __init__(self, period: Sequence[int], pre_period: Optional[Sequence[int]] = [], integer_part: int = 0, dtypes: Optional[Tuple[str, str]] = None):
        """
        Initialises the periodic SCF from non-repeating and repeating parts.

        Args:
            pre_period (Sequence[int], optional): The non-repeating partial
                quotients ``a₁, a₂, …, aₘ`` (all must be strictly positive).
            period (Sequence[int]): The repeating partial quotients
                ``b₁, b₂, …, bₙ`` (all must be strictly positive).
            integer_part (int): The integer part ``a₀``.  Defaults to ``0``.
            dtypes (Tuple[str, str], optional): Force specific
                :class:`array.array` typecodes for compact storage of the
                period and pre-period respectively (each one of ``'B'``, ``'H'``, ``'I'``, ``'L'``, ``'Q'``).
                When ``None``, the smallest fitting typecode is chosen automatically. 
                    Note: (str, None) and (None, str) are also accepted to specify a typecode 
                    for only one of the two sequences.
        """

        if dtypes is None:
            dtypes = (None, None)

        if len(dtypes) != 2:
            raise ValueError(f"Expected a tuple of two typecodes for 'dtypes' but got {dtypes}")
        
        generator = PeriodicGenerator(period=period, pre_period=pre_period, dtypes=dtypes)
        super().__init__(generator=generator, integer_part=integer_part)

    def __setattr__(self, name, value):
        if name in {"_quadratic_coefficients", "_quadratic_surd", "_conjugate"} and hasattr(self, name):
            raise AttributeError(f"'{self.__class__.__name__}.{name}' is immutable and cannot be modified after it has been set")
        super().__setattr__(name, value)

    @property
    def generator(self) -> PeriodicGenerator:
        """The :class:`~catena.generators.PeriodicGenerator` holding the partial quotients."""
        return super().generator
    
    @property
    def non_repeating_part(self) -> Tuple[int, ...]:
        """The non-repeating partial quotients ``(a₁, a₂, …, aₘ)`` as an immutable tuple."""
        return tuple(self.generator.pre_period)
    
    @property
    def period(self) -> Tuple[int, ...]:
        """The repeating partial quotients ``(b₁, b₂, …, bₙ)`` as an immutable tuple."""
        return tuple(self.generator.period)
    
    def __str__(self):
        return f"PeriodicSimpleContinuedFraction(non_repeating_part={self.non_repeating_part}, period={self.period}, integer_part={self.integer_part})"
    
    def __repr__(self):
        return f"PeriodicSimpleContinuedFraction(generator={self.generator}, integer_part={self.integer_part}, cache_handler={self.cache_handler})"
    
    def __float__(self):
        """Returns the value of the SCF as a Python ``float``."""
        P, Q, D = self.quadratic_surd()
        return (P + D**0.5)/Q
    
    def __neg__(self):
        """Returns the negation of the SCF, i.e. ``-scf``."""
        # The special case of periodic SCFs allows to define a negation operation trivially.
        # If the value of the SCF is (P + √D)/Q, then its negation is (-P - √D)/Q,
        # or what is the same, (P + √D)/(-Q).
        P, Q, D = self.quadratic_surd()
        negated_surd = (P, -Q, D)
        return self.from_quadratic_surd(*negated_surd)

    def as_decimal(self) -> Decimal:
        """Returns the value of the SCF as a :class:`decimal.Decimal`."""
        P, Q, D = self.quadratic_surd()
        return (Decimal(P) + Decimal(D).sqrt())/Decimal(Q)

    @classmethod
    def from_quadratic_surd(cls, P: int, Q: int, D: int) -> 'PeriodicSimpleContinuedFraction':
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
        P, Q, D = mathlib.quadratic.quadratic_surd_from_coefficients(A, B, C)

        _int, pre_period, period = mathlib.convert.from_quadratic_surd_to_scf(P, Q, D)
        if self.integer_part == _int and self.non_repeating_part == pre_period and self.period == period:
            # If the original SCF is already in the normalized surd form, we can directly return the surd parameters without worrying about the sign.
            self._quadratic_surd = (P, Q, D)
            return self._quadratic_surd
        else:
            # Otherwise, the original SCF is itself the conjugate of the normalized surd form, so we need to negate the surd parameters to get the correct value.
            self._quadratic_surd = (-P, -Q, D)
            return self._quadratic_surd

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

    @override
    def inverse(self) -> 'PeriodicSimpleContinuedFraction':
        """
        Returns the multiplicative inverse of the periodic SCF, i.e. ``1/scf``.

        The result is a new :class:`PeriodicSimpleContinuedFraction` whose
        value is the reciprocal of this SCF's value.

        Returns:
            PeriodicSimpleContinuedFraction: The multiplicative inverse of this
            periodic SCF.
        """
        if hasattr(self, '_inverse'):
            return self._inverse
        
        _, _, C = self.quadratic_coefficients()
        if C == 0:
            raise ZeroDivisionError("Cannot invert a zero value (rational root)")

        P, Q, D = self.quadratic_surd()
        if Q > 0: # Principal surd case
            self._inverse = PeriodicSimpleContinuedFraction.from_quadratic_surd(-Q * P, -(P**2 - D), D * Q**2)
        else: # Conjugate surd case
            self._inverse = PeriodicSimpleContinuedFraction.from_quadratic_surd(Q * P, (P**2 - D), D * Q**2)

        self._inverse._inverse = self  # Cache the inverse of the inverse as the original SCF
        return self._inverse

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
        if hasattr(self, '_conjugate'):
            return self._conjugate

        P, Q, D = self.quadratic_surd()
        P_conj, Q_conj = -P, -Q
        self._conjugate = PeriodicSimpleContinuedFraction.from_quadratic_surd(P_conj, Q_conj, D)
        self._conjugate._conjugate = self

        return self._conjugate

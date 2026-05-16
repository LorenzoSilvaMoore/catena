

"""
Convergent view classes for simple continued fractions.

This module provides two accessor classes that expose convergent utilities
under a dedicated ``scf.convergents`` sub-namespace, keeping the main SCF
class lean while remaining discoverable via tab-completion:

- :class:`ConvergentsView` — point-access and scalar queries for infinite
  (or generative) :class:`~catena.catena.SimpleContinuedFraction` instances.
- :class:`FiniteConvergentView` — extends :class:`ConvergentsView` with
  iteration, slicing, and bulk lazy sequences for
  :class:`~catena.catena.FiniteSimpleContinuedFraction` instances.

Both classes are lightweight wrappers (``__slots__``) that hold a single
reference to the underlying SCF; they perform no computation themselves.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ..catena import SimpleContinuedFraction

from collections.abc import Iterator, Callable

T = TypeVar('T')

from decimal import Decimal, localcontext
from fractions import Fraction
from math import log10


class ConvergentsView:
    """
    Accessor for point-wise convergent queries on a
    :class:`~catena.catena.SimpleContinuedFraction`.

    Obtained via ``scf.convergents``.  Exposes scalar lookups and type
    conversions for individual convergents without polluting the main SCF
    namespace.  All methods delegate to
    :meth:`~catena.catena.SimpleContinuedFraction.convergent`, which is
    memoised, so repeated calls at the same index are O(1).

    This class is intended for infinite (generative) SCFs.  For finite SCFs,
    use :class:`FiniteConvergentView`, which additionally supports iteration,
    slicing, and bulk lazy sequences.
    """
    __slots__ = ('_scf',)

    def __init__(self, scf: 'SimpleContinuedFraction'):
        """
        Initialises the view.

        Args:
            scf (SimpleContinuedFraction): The SCF instance to wrap.
        """
        object.__setattr__(self, '_scf', scf)

    def __getitem__(self, n: int) -> tuple[int, int]:
        """
        Returns the *n*-th convergent ``(pₙ, qₙ)`` of the SCF.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            tuple[int, int]: ``(numerator, denominator)`` of the *n*-th
            convergent.

        Raises:
            TypeError: If ``n`` is a slice (slicing requires a finite bound;
                use a loop or list comprehension instead).
        """
        if isinstance(n, slice):
            raise TypeError(
                "Slicing is not supported on an infinite SCF view. "
                "Use a loop or list comprehension instead."
            )
        return self._scf.convergent(n)

    def as_decimal(self, n: int) -> Decimal:
        """
        Returns the *n*-th convergent as an exact :class:`~decimal.Decimal`.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            Decimal: Exact rational value ``pₙ / qₙ``.
        """
        p, q = self._scf.convergent(n)
        return Decimal(p) / Decimal(q)

    def as_float(self, n: int) -> float:
        """
        Returns the *n*-th convergent as a Python :class:`float`.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            float: Floating-point approximation of ``pₙ / qₙ``.
        """
        p, q = self._scf.convergent(n)
        return p / q

    def as_fraction(self, n: int) -> Fraction:
        """
        Returns the *n*-th convergent as a :class:`~fractions.Fraction`.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            Fraction: Exact rational value ``pₙ / qₙ``.
        """
        p, q = self._scf.convergent(n)
        return Fraction(p, q)

    def as_digits(self, n: int, digits: int) -> str:
        """
        Returns the *n*-th convergent as a fixed-point decimal string.

        Uses an extended-precision :class:`~decimal.Decimal` context
        internally to avoid rounding artefacts in the last digit.

        Args:
            n (int): 0-indexed convergent depth.
            digits (int): Number of decimal places in the output string.

        Returns:
            str: The value ``pₙ / qₙ`` formatted to ``digits`` decimal places.
        """
        p, q = self._scf.convergent(n)
        with localcontext() as ctx:
            ctx.prec = digits + 10
            decimal_value = Decimal(p) / Decimal(q)
            return format(decimal_value, f'.{digits}f')

    def numerator_length(self, n: int) -> int:
        """
        Returns the number of decimal digits in the numerator of the *n*-th
        convergent.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            int: ``⌊log₁₀ pₙ⌋ + 1``, or ``1`` when ``pₙ ≤ 0``.
        """
        p, _ = self._scf.convergent(n)
        return int(log10(p)) + 1 if p > 0 else 1

    def denominator_length(self, n: int) -> int:
        """
        Returns the number of decimal digits in the denominator of the *n*-th
        convergent.

        Args:
            n (int): 0-indexed convergent depth.

        Returns:
            int: ``⌊log₁₀ qₙ⌋ + 1``, or ``1`` when ``qₙ ≤ 0``.
        """
        _, q = self._scf.convergent(n)
        return int(log10(q)) + 1 if q > 0 else 1


class FiniteConvergentView(ConvergentsView):
    """
    Accessor for convergent queries on a
    :class:`~catena.catena.FiniteSimpleContinuedFraction`.


    Extends :class:`ConvergentsView` with sequence-like access (iteration,
    negative indexing, slicing) and a family of bulk lazy generators via
    :meth:`apply`.

    All bulk methods return lazy :class:`~collections.abc.Iterator` objects;
    computation is deferred until the caller iterates, and the caller may
    stop early without evaluating the full sequence.
    """
    __slots__ = ()

    def __getitem__(self, n: int | slice) -> tuple[int, int] | list[tuple[int, int]]:
        """
        Returns the *n*-th convergent, or a list of convergents for a slice.

        Args:
            n (int | slice): A 0-indexed convergent depth, a negative index
                (counted from the terminal convergent), or a :class:`slice`.

        Returns:
            tuple[int, int]: ``(pₙ, qₙ)`` for integer ``n``.
            list[tuple[int, int]]: Convergents in the slice range.
        """
        if isinstance(n, slice):
            return [self._scf.convergent(i) for i in range(*n.indices(self._scf.size))]
        if n < 0:
            n += self._scf.size
        return self._scf.convergent(n)

    def __iter__(self) -> Iterator[tuple[int, int]]:
        """Yields all convergents ``(pₙ, qₙ)`` from ``n = 0`` to ``size - 1``."""
        for i in range(len(self)):
            yield self._scf.convergent(i)

    def __len__(self) -> int:
        """Returns the number of convergents (equal to ``scf.size``)."""
        return self._scf.size

    def apply(self, f: Callable[[int, int], T]) -> Iterator[T]:
        """
        Lazily applies ``f(p, q)`` to each convergent ``(p, q)`` in order.

        Nothing is computed until the caller iterates the result; the caller
        may stop at any point without evaluating the remaining convergents.
        This method also serves as an escape hatch for custom per-convergent
        metrics not covered by the named helper methods.

        Args:
            f (Callable[[int, int], T]): A function that takes a numerator
                ``p`` and denominator ``q`` and returns a value of type ``T``.

        Returns:
            Iterator[T]: A lazy iterator of ``f(pₙ, qₙ)`` for each ``n``.

        Example::

            # custom metric: parity of the denominator
            scf.convergents.apply(lambda _, q: q % 2)
        """
        return (f(p, q) for p, q in self)

    def as_decimals(self) -> Iterator[Decimal]:
        """
        Lazily yields each convergent as an exact :class:`~decimal.Decimal`.

        Returns:
            Iterator[Decimal]: ``pₙ / qₙ`` as a :class:`~decimal.Decimal`
            for each ``n``.
        """
        return self.apply(lambda p, q: Decimal(p) / Decimal(q))

    def as_floats(self) -> Iterator[float]:
        """
        Lazily yields each convergent as a Python :class:`float`.

        Returns:
            Iterator[float]: ``pₙ / qₙ`` as a :class:`float` for each ``n``.
        """
        return self.apply(lambda p, q: p / q)

    def as_fractions(self) -> Iterator[Fraction]:
        """
        Lazily yields each convergent as a :class:`~fractions.Fraction`.

        Returns:
            Iterator[Fraction]: ``pₙ / qₙ`` as a :class:`~fractions.Fraction`
            for each ``n``.
        """
        return self.apply(Fraction)

    def numerators(self) -> Iterator[int]:
        """
        Lazily yields the numerator of each convergent in order.

        Returns:
            Iterator[int]: ``pₙ`` for each ``n``.
        """
        return self.apply(lambda p, _: p)

    def denominators(self) -> Iterator[int]:
        """
        Lazily yields the denominator of each convergent in order.

        Returns:
            Iterator[int]: ``qₙ`` for each ``n``.
        """
        return self.apply(lambda _, q: q)

    def numerators_lengths(self) -> Iterator[int]:
        """
        Lazily yields the number of decimal digits in each numerator.

        Returns:
            Iterator[int]: ``⌊log₁₀ pₙ⌋ + 1`` (or ``1`` when ``pₙ ≤ 0``)
            for each ``n``.
        """
        return self.apply(lambda p, _: int(log10(p)) + 1 if p > 0 else 1)

    def denominators_lengths(self) -> Iterator[int]:
        """
        Lazily yields the number of decimal digits in each denominator.

        Returns:
            Iterator[int]: ``⌊log₁₀ qₙ⌋ + 1`` (or ``1`` when ``qₙ ≤ 0``)
            for each ``n``.
        """
        return self.apply(lambda _, q: int(log10(q)) + 1 if q > 0 else 1)
    

    

    

    
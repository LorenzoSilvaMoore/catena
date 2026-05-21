"""
Caching primitives for memoising partial-quotient generator calls.

This module provides:

- :class:`Cache` — an immutable-key :class:`~collections.UserDict` that
  prevents accidental overwriting of stored results.
- :class:`OrdinalCache` — a :class:`Cache` specialised for integer keys,
  tracking the smallest and largest key seen.
- :class:`CacheHandler` — a bookkeeping wrapper that owns a :class:`Cache`
  instance and records call/read statistics.
- :func:`SetCache` — a decorator / decorator-factory that memoises a
  function using arbitrary ``(args, kwargs)`` keys.
- :func:`SetLightCache` — a lighter variant of :func:`SetCache` for
  single-argument functions, using the argument directly as the cache key.
"""
from __future__ import annotations

import heapq

from typing import Any, Callable, Optional, override
from collections import UserDict

class BaseCache(UserDict):
    """
    A self-computing, append-only cache that unifies the roles of the old
    :class:`OrdinalCache` and :class:`CacheHandler` into a single object.

    On a cache *miss*, the bound function ``func`` is called automatically
    and the result stored; on a *hit*, the stored value is returned directly.
    Both paths are counted separately via :attr:`call_count` and
    :attr:`read_count`.  Integer keys additionally maintain :attr:`smallest_key`
    and :attr:`largest_key` without iterating the dictionary.

    Stored entries are *immutable*: attempting to overwrite an existing key
    raises :exc:`KeyError`.  The mutating :class:`~collections.UserDict`
    methods (``pop``, ``popitem``, ``__delitem__``, ``update``, ``setdefault``,
    ``fromkeys``, ``__or__``) are disabled and raise
    :exc:`NotImplementedError`.  Use :meth:`prune` or :meth:`reset` to
    reduce the cache size.

    When ``maxsize`` is set, :meth:`prune` is called automatically before
    each new insertion that would exceed the limit, using ``prune_key`` to
    determine how many entries to retain.

    Note:
        ``func`` must accept a single argument; the argument itself is used
        as the cache key.

    Warning:
        This class is experimental.  Its interface is subject to change
        without notice.
    """
    def __init__(self, *args: Any, func: Callable, maxsize: Optional[int] = None, prune_key: Optional[Callable[[int], tuple[int, Optional[str]]]] = None, seed: Optional[dict] = None, **kwargs: Any) -> None:
        """
        Initialises the cache.

        Args:
            func (Callable): The single-argument function whose results are
                memoised.  Called automatically on a cache miss.
            maxsize (int, optional): Maximum number of entries before an
                automatic :meth:`prune` is triggered.  ``None`` means
                unlimited.  Must be a strictly positive integer or ``None``.
            prune_key (Callable[[int], tuple], optional): A callable that
                receives the current ``maxsize`` and returns a tuple of
                positional arguments forwarded to :meth:`prune`.  Defaults
                to ``lambda k: (max(k - 1, 2),)``, which retains the
                ``max(maxsize - 1, 2)`` largest-keyed entries.
            seed (dict, optional): Pre-computed ``{key: value}`` pairs to
                load into the cache at construction time.  Entries are
                inserted directly into the underlying store without
                incrementing :attr:`call_count` or :attr:`read_count`.
                Subsequent reads of seeded keys are counted as normal hits.
                ``maxsize`` is not enforced against the seed.
            *args: Forwarded to :class:`~collections.UserDict`.
            **kwargs: Forwarded to :class:`~collections.UserDict`.

        Raises:
            ValueError: If ``maxsize`` is not a strictly positive integer or
                ``None``.
        """
        super().__init__(*args, **kwargs)
        self._func = func
        self._func_name = func.__name__ if hasattr(func, "__name__") else repr(func)
        self._read_count = 0
        self._call_count = 0
        self._write_count = 0 # As oposed to read_count and call_count, this counts all writes including those from seeding and pruning, not just misses.
        self._smallest_key = float('inf')
        self._largest_key = float('-inf')
        self._maxsize = maxsize
        self._prune_key = prune_key if prune_key is not None else (lambda k: (max(k - 1, 2), None))
        if self._maxsize is not None and (not isinstance(self._maxsize, int) or self._maxsize <= 0):
            raise ValueError(f"BaseCache maxsize must be a positive integer or None, got {self._maxsize!r}")
        if seed:
            for key, value in seed.items():
                self.data[key] = value
                if isinstance(key, int):
                    if key < self._smallest_key:
                        self._smallest_key = key
                    if key > self._largest_key:
                        self._largest_key = key

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Stores ``value`` under ``key``.

        If ``maxsize`` is set and the cache is at capacity, :meth:`prune` is
        called first to make room.  Integer keys update :attr:`smallest_key`
        and :attr:`largest_key` automatically.

        Args:
            key: The cache key.
            value: The value to store.

        Raises:
            KeyError: If ``key`` already exists (entries are immutable).
        """
        if key in self.data:
            raise KeyError(f"Cache key '{key}' is immutable and cannot be modified.")
        
        if self._maxsize is not None and len(self.data) >= self._maxsize:
            self.prune(*self._prune_key(self._maxsize))

        if isinstance(key, int):
            if key < self._smallest_key:
                self._smallest_key = key
            if key > self._largest_key:
                self._largest_key = key

        self._write_count += 1
        super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        """
        Returns the cached value for ``key``, computing and storing it on a miss.

        A *hit* (key already in the cache) increments :attr:`read_count`.
        A *miss* delegates to :meth:`__missing__`, which calls ``func``,
        stores the result, and increments :attr:`call_count`.

        Args:
            key: The cache key.

        Returns:
            The cached (or freshly computed) value for ``key``.
        """
        if key in self.data:
            self._read_count += 1
            return self.data[key]
        return self.__missing__(key)

    def __missing__(self, key: Any) -> Any:
        """
        Called by :meth:`__getitem__` on a cache miss.

        Invokes ``func(key)``, stores the result via :meth:`__setitem__`
        (which enforces ``maxsize`` and updates the key-range trackers), and
        increments :attr:`call_count`.

        Args:
            key: The missing cache key.

        Returns:
            The computed value ``func(key)``.
        """
        self._call_count += 1
        result = self._func(key)
        self[key] = result
        return result
    
    def __repr__(self):
        """
        Returns a concise string representation showing the bound function,
        call/read counts, and current size.
        """
        return f"BaseCache(func={self.func_name}, calls={self.call_count}, reads={self.read_count}, size={len(self)})"
    
    @property
    def func(self):
        """The function whose results are being cached."""
        return self._func
    
    @property
    def func_name(self):
        """The name of the cached function, if available."""
        return self._func_name
    
    @property
    def read_count(self):
        """Number of cache hits since initialisation."""
        return self._read_count

    @property
    def write_count(self):
        """Number of cache writes since initialisation."""
        return self._write_count
    
    @property
    def call_count(self):
        """Number of cache misses (underlying function calls) since initialisation."""
        return self._call_count
    
    @property
    def smallest_key(self):
        """The smallest key stored so far, or ``None`` if the cache is empty."""
        if not self.data:
            return None
        return self._smallest_key if self._smallest_key != float('inf') else None
    
    @property
    def largest_key(self):
        """The largest key stored so far, or ``None`` if the cache is empty."""
        if not self.data:
            return None
        return self._largest_key if self._largest_key != float('-inf') else None
    
    @property
    def maxsize(self):
        """The maximum size of the cache, or ``None`` if unlimited."""
        return self._maxsize
    
    @property
    def stats(self):
        """A summary of the cache's current statistics as a dictionary."""
        return {
            "func": self.func_name,
            "size": len(self),
            "calls": self.call_count,
            "reads": self.read_count,
            "writes": self._write_count, 
            "smallest_key": self.smallest_key,
            "largest_key": self.largest_key,
            "maxsize": self.maxsize,
            "prune_key": self._prune_key(self.maxsize) if self._maxsize is not None else None
        }
    
    @property
    def cache(self):
        """Returns self for backward compatibility."""
        return self
    
    def prune(self, n: int = 2, order: Optional[str] = 'asc'):
        """
        Retains only the ``n`` largest-keyed entries, discarding the rest.

        Args:
            n (int): Number of entries to keep.  Defaults to ``2``.
            order (str): Whether to keep the entries with the
                largest keys (``'asc'``) or smallest keys (``'desc'``).
                Defaults to ``'asc'``.

        Raises:
            ValueError: If ``order`` is not 'asc' or 'desc'.
        """
        if n <= 0:
            self.clear()
            return
        
        if order is None:
             order = 'asc'

        if order == 'asc':
            keys_to_keep = heapq.nlargest(n, self.data)
            new_data = {k: self.data[k] for k in keys_to_keep}
            self.clear()
            self.data.update(new_data)
        elif order == 'desc':
            keys_to_keep = heapq.nsmallest(n, self.data)
            new_data = {k: self.data[k] for k in keys_to_keep}
            self.clear()
            self.data.update(new_data)
        else:
            raise ValueError(f"Invalid prune order: {order!r}. Expected 'asc' or 'desc'.")
        
        if new_data:
            self._smallest_key = min(new_data)
            self._largest_key = max(new_data)
    
    def reset(self):
        """
        Clears all cached entries and resets :attr:`call_count`,
        :attr:`read_count`, :attr:`smallest_key`, and :attr:`largest_key`
        to their initial values.

        The bound ``func`` and ``maxsize`` are preserved.
        """
        self.clear()
        self._read_count = 0
        self._call_count = 0

    @override
    def clear(self):
        """
        Clears all cached entries and resets :attr:`smallest_key` and
        :attr:`largest_key`, but *preserves* :attr:`call_count` and
        :attr:`read_count`.

        To reset statistics as well, use :meth:`reset`.
        """
        self.data.clear()
        self._smallest_key = float('inf')
        self._largest_key = float('-inf')

    @override
    def copy(self) -> BaseCache:
        """
        Returns a shallow copy of the cache.

        The new instance shares the same ``func``, ``maxsize``, and
        ``prune_key``, and carries over the current data, statistics
        (:attr:`call_count`, :attr:`read_count`), and key-range sentinels
        (:attr:`smallest_key`, :attr:`largest_key`).

        Returns:
            BaseCache: A new :class:`BaseCache` instance with the same state.
        """
        new_cache = BaseCache(func=self.func, maxsize=self.maxsize, prune_key=self._prune_key)
        new_cache.data = self.data.copy()
        new_cache._read_count = self._read_count
        new_cache._call_count = self._call_count
        new_cache._smallest_key = self._smallest_key
        new_cache._largest_key = self._largest_key
        return new_cache
    
    @override
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Returns the cached value for ``key``, or ``default`` on a miss.

        Unlike :meth:`__getitem__`, a missing key does *not* trigger a call
        to ``func`` and is *not* stored.  A hit increments :attr:`read_count`.

        Args:
            key: The cache key to look up.
            default: Value to return when ``key`` is absent.  Defaults to
                ``None``.

        Returns:
            The stored value, or ``default`` if the key is not in the cache.
        """
        if key in self.data:
            self._read_count += 1
            return self.data[key]
        return default
    
    @override
    def setdefault(self, key, default=None):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("setdefault is not supported by BaseCache due to immutability guarantees. Use direct assignment instead.")
    
    @override
    def update(self, *args, **kwargs):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("update is not supported by BaseCache due to immutability guarantees. Use direct assignment instead.")
    
    @override
    def pop(self, key, *args):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("pop is not supported by BaseCache due to immutability guarantees. Use prune() to remove entries instead.")
    
    @classmethod
    @override
    def fromkeys(cls, iterable, value=None):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("fromkeys is not supported by BaseCache due to construnction requirements. Create a new instance and assign values directly instead.")
    
    @override
    def __delitem__(self, key):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("Deletion of individual keys is not supported by BaseCache due to immutability guarantees. Use prune() to remove entries instead.")
    
    @override
    def popitem(self):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("popitem is not supported by BaseCache due to immutability guarantees. Use prune() to remove entries instead.")
    
    @override
    def __or__(self, other):
        """
        Not supported.  Raises :exc:`NotImplementedError`.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("Merging of BaseCache instances is not supported due to immutability guarantees. Create a new instance and assign values directly instead.")

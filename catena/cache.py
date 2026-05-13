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
import heapq
import warnings

from typing import Callable
from collections import UserDict


class Cache(UserDict):
    """
    An append-only dictionary whose entries are immutable once written.

    Inherits from :class:`~collections.UserDict`.  Any attempt to overwrite
    an existing key raises a :exc:`KeyError`, making stored results safe
    against accidental mutation.
    """

    def __setitem__(self, key, value):
        """
        Stores ``value`` under ``key``, raising :exc:`KeyError` if the key
        already exists.
        """
        if key in self.data:
            raise KeyError(f"Cache key '{key}' is immutable and cannot be modified.")
        super().__setitem__(key, value)

    def __repr__(self):
        return f"Cache({super().__len__()})[{super().__repr__()}]"
    
class OrdinalCache(Cache):
    """
    A :class:`Cache` restricted to integer keys that tracks the key range.

    In addition to the immutability guarantee of :class:`Cache`, this
    subclass enforces integer-only keys and maintains :attr:`smallest_key`
    and :attr:`largest_key` attributes so callers can inspect the covered
    range without iterating the dictionary.
    """

    def __init__(self, *args: object, maxsize: int | None = None, **kwargs: object):
        """
        Initialises the ordinal cache.

        Args:
            *args: Forwarded to :class:`~collections.UserDict`.
            maxsize (int | None): Reserved for future capacity limiting;
                accepted but not yet enforced.  Must be an integer or
                ``None``.
            **kwargs: Forwarded to :class:`~collections.UserDict`.

        Raises:
            TypeError: If ``maxsize`` is neither an integer nor ``None``.
        """
        self._smallest_key = float('inf')
        self._largest_key = float('-inf')
        if not isinstance(maxsize, (int, type(None))):
            raise TypeError(f"OrdinalCache maxsize must be an integer or None, got {type(maxsize).__name__}")

        super().__init__(*args, **kwargs)

    @property
    def smallest_key(self):
        """The smallest integer key stored so far, or ``None`` if the cache is empty."""
        if not self.data:
            return None
        return self._smallest_key
    
    @property
    def largest_key(self):
        """The largest integer key stored so far, or ``None`` if the cache is empty."""
        if not self.data:
            return None
        return self._largest_key

    def __setitem__(self, key, value):
        """
        Stores ``value`` under the integer ``key`` and updates the tracked range.

        Raises:
            TypeError: If ``key`` is not an integer.
            KeyError: If ``key`` already exists (inherited from :class:`Cache`).
        """
        if not isinstance(key, int):
            raise TypeError(f"OrdinalCache keys must be integers, got {type(key).__name__}")
        
        super().__setitem__(key, value)

        if key < self._smallest_key:
            self._smallest_key = key
        if key > self._largest_key:
            self._largest_key = key

class CacheHandler:
    """
    Bookkeeping wrapper that owns a :class:`Cache` and records usage statistics.

    Tracks the number of *calls* (cache misses, i.e. the underlying function
    was invoked) and *reads* (cache hits, i.e. a stored result was returned)
    since the handler was created or last reset.  The internal ``_cache``,
    ``_call_count``, and ``_read_count`` attributes are protected against
    direct assignment via a custom :meth:`__setattr__`.
    """

    def __init__(self, cache_pointer: Cache):
        """
        Initialises the handler with a given cache instance.

        Args:
            cache_pointer (Cache): The cache object to manage.
        """
        self._set_cache(cache_pointer)
        super().__setattr__("_call_count", 0)
        super().__setattr__("_read_count", 0)

    @property
    def cache(self) -> Cache:
        """The :class:`Cache` instance managed by this handler."""
        return self._cache
    
    @property
    def call_count(self) -> int:
        """Total number of cache misses (underlying function invocations) since initialisation or last reset."""
        return self._call_count
    
    @property
    def read_count(self) -> int:
        """Total number of cache hits (stored-result retrievals) since initialisation or last reset."""
        return self._read_count

    def reset_cache(self) -> None:
        """Replaces the current cache with a fresh, empty instance of the same type."""
        self._set_cache(self.cache.__class__())

    def prune_cache(self, n: int = 2) -> None:
        """
        Retains only the ``n`` largest-keyed entries, discarding the rest.

        For :class:`OrdinalCache` instances the *n* numerically largest keys
        are kept.  For generic :class:`Cache` instances the first element of
        each key tuple is used for comparison.

        Args:
            n (int): Number of entries to keep.  Defaults to ``2``.
        """
        if isinstance(self.cache, OrdinalCache):
            keys = heapq.nlargest(n, self.cache)
        else:
            keys = heapq.nlargest(n, self.cache, key=lambda x: x[0][0])
        self._set_cache(self.cache.__class__({k: self.cache[k] for k in keys}))

    def _set_cache(self, cache_pointer: Cache) -> None:
        """Replaces the internal cache reference, bypassing the attribute guard."""
        super().__setattr__("_cache", cache_pointer)

    def _tick_call_count(self) -> None:
        """Increments the call counter by one."""
        super().__setattr__("_call_count", self.call_count+1)

    def _tick_read_count(self) -> None:
        """Increments the read counter by one."""
        super().__setattr__("_read_count", self.read_count+1)

    def __setattr__(self, key, value):
        """
        Guards private attributes against external assignment.

        Raises:
            AttributeError: If ``key`` is one of the protected internal
                attributes (``_cache``, ``_call_count``, ``_read_count``).
        """
        if key in {"_cache", "_call_count", "_read_count"}:
            raise AttributeError(f"'{self.__class__.__name__}.{key}' is private and cannot be directly modified after initialization")
        super().__setattr__(key, value)

    def __repr__(self):
        return f"CacheHandler[{id(self)}] -> Cache[{id(self.cache)}] | Calls: {self.call_count}, Reads: {self.read_count}, Size: {len(self.cache)}"
    

def SetCache(func: Callable = None, cache_handler: CacheHandler = None) -> Callable:
    """
    Decorator / decorator-factory that memoises a function using a
    :class:`CacheHandler`.

    Results are keyed by ``(args, frozenset(kwargs.items()))`` so that calls
    with different positional or keyword arguments are cached independently.

    Can be used in two ways::

        @SetCache
        def f(*args, **kwargs): ...

        @SetCache(cache_handler=my_handler)
        def f(*args, **kwargs): ...

    Args:
        func (Callable, optional): The function to wrap.  When provided
            directly the decorator is applied immediately; when ``None`` a
            decorator factory is returned.
        cache_handler (CacheHandler, optional): An existing handler to use.
            A new one backed by a plain :class:`Cache` is created if not
            supplied.

    Returns:
        Callable: The wrapped function (or a decorator if ``func`` is ``None``).
    """
    if cache_handler is None:
        cache_handler = CacheHandler(Cache())

    def decorator(f):
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache_handler.cache:
                cache_handler._tick_read_count()
                return cache_handler.cache[key]
            cache_handler._tick_call_count()
            result = f(*args, **kwargs)
            cache_handler.cache[key] = result
            return result
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def SetLightCache(func: Callable = None, cache_handler: CacheHandler = None) -> Callable:
    """
    A lighter variant of :func:`SetCache` for single-argument functions.

    Uses the sole argument directly as the cache key instead of building a
    ``(args, kwargs)`` tuple, which avoids the overhead of tuple construction
    and ``frozenset`` hashing for the common case of integer-indexed
    generators.

    Can be used in two ways::

        @SetLightCache
        def f(n): ...

        @SetLightCache(cache_handler=my_handler)
        def f(n): ...

    Args:
        func (Callable, optional): The single-argument function to wrap.
        cache_handler (CacheHandler, optional): An existing handler to use.
            A new one backed by a plain :class:`Cache` is created if not
            supplied.

    Returns:
        Callable: The wrapped function (or a decorator if ``func`` is ``None``).
    """
    if cache_handler is None:
        cache_handler = CacheHandler(Cache())

    def decorator(f):
        def wrapper(arg):
            if arg in cache_handler.cache:
                cache_handler._tick_read_count()
                return cache_handler.cache[arg]
            cache_handler._tick_call_count()
            result = f(arg)
            cache_handler.cache[arg] = result
            return result
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
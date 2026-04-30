import catena.cache as cache_module

def test_cache_empty_creation():
    """Test that a Cache can be created and is initially empty."""
    c = cache_module.Cache()
    assert len(c) == 0

def test_cache_set_and_get():
    """Test setting and getting values in a Cache."""
    c = cache_module.Cache()
    c['a'] = 1
    c['b'] = 2
    assert c['a'] == 1
    assert c['b'] == 2
    assert len(c) == 2

def test_cache_inmutability():
    """Test that a Cache key cannot be modified once set."""
    c = cache_module.Cache()
    c['a'] = 1
    try:
        c['a'] = 2
        assert False, "Expected an exception when trying to modify an existing key"
    except KeyError:
        pass

def test_ordinal_cache():
    """Test that an OrdinalCache can be created and behaves correctly."""
    oc = cache_module.OrdinalCache()
    oc[1] = 'one'
    oc[3] = 'three'
    oc[2] = 'two'
    assert oc.smallest_key == 1
    assert oc.largest_key == 3
    assert oc[1] == 'one'
    assert oc[2] == 'two'
    assert oc[3] == 'three'

def test_ordinal_cache2():
    """Test that an OrdinalCache can be created with initial values and behaves correctly."""
    oc = cache_module.OrdinalCache((
        (5, 'five'),
        (2, 'two'),
        (8, 'eight'),
    ))

    assert oc.smallest_key == 2
    assert oc.largest_key == 8
    assert oc[5] == 'five'
    assert oc[2] == 'two'
    assert oc[8] == 'eight'

def test_ordinal_cache_empty():
    """Test that an empty OrdinalCache has None for smallest and largest keys."""
    oc = cache_module.OrdinalCache()
    assert oc.smallest_key is None
    assert oc.largest_key is None

def test_ordinal_cache_single_element():
    """Test that an OrdinalCache with a single element has correct smallest and largest keys."""
    oc = cache_module.OrdinalCache()
    oc[1] = 'one'
    assert oc.smallest_key == 1
    assert oc.largest_key == 1

def test_ordinal_cache_non_integer_key():
    """Test that an OrdinalCache raises an exception when a non-integer key is used."""
    oc = cache_module.OrdinalCache()
    try:
        oc['a'] = 'not an integer'
        assert False, "Expected an exception when trying to set a non-integer key"
    except TypeError:
        pass

def test_ordinal_cache_inmutability():
    """Test that an OrdinalCache key cannot be modified once set."""
    oc = cache_module.OrdinalCache()
    oc[1] = 'one'
    try:
        oc[1] = 'uno'
        assert False, "Expected an exception when trying to modify an existing key"
    except KeyError:
        pass




def test_cache_handler():
    """Test that a CacheHandler can be created and behaves correctly."""
    c = cache_module.Cache()
    handler = cache_module.CacheHandler(c)
    assert handler.cache is c
    assert handler.call_count == 0
    assert handler.read_count == 0

def test_cache_handler_reset():
    """Test that the reset_cache method of CacheHandler works correctly."""
    c = cache_module.Cache()
    handler = cache_module.CacheHandler(c)
    handler.cache['a'] = 1
    handler.reset_cache()
    assert len(handler.cache) == 0
    assert isinstance(handler.cache, cache_module.Cache)

    c2 = cache_module.OrdinalCache()
    handler2 = cache_module.CacheHandler(c2)
    handler2.cache[1] = 'one'
    handler2.reset_cache()
    assert len(handler2.cache) == 0
    assert isinstance(handler2.cache, cache_module.OrdinalCache)

def test_cache_handler_prune():
    """Test that the prune_cache method of CacheHandler works correctly."""
    c = cache_module.Cache()
    handler = cache_module.CacheHandler(c)
    handler.cache['a'] = 1
    handler.cache['b'] = 2
    handler.cache['c'] = 3
    handler.prune_cache(n=2)
    assert len(handler.cache) == 2
    assert 'a' not in handler.cache
    assert 'b' in handler.cache
    assert 'c' in handler.cache
    assert isinstance(handler.cache, cache_module.Cache)

def test_cache_handler_prune_no_removal():
    """Test that the prune_cache method of CacheHandler does not remove items if n is greater than the cache size."""
    c = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(c)
    handler.cache[1] = 'one'
    handler.cache[2] = 'two'
    handler.prune_cache(n=3)
    assert len(handler.cache) == 2
    assert 1 in handler.cache
    assert 2 in handler.cache
    assert isinstance(handler.cache, cache_module.OrdinalCache)

def test_cache_handler_inmutability():
    """Test that the CacheHandler does not allow modification of the cache pointer."""
    c = cache_module.Cache()
    handler = cache_module.CacheHandler(c)
    try:
        handler.cache = cache_module.Cache()
        assert False, "Expected an exception when trying to modify the cache pointer"
    except AttributeError:
        pass

    try:
        handler._cache = cache_module.Cache()
        assert False, "Expected an exception when trying to modify the _cache attribute directly"
    except AttributeError:
        pass

    try:
        handler._call_count = 1
        assert False, "Expected an exception when trying to modify the _call_count attribute directly"
    except AttributeError:
        pass

    try:
        handler._read_count = 1
        assert False, "Expected an exception when trying to modify the _read_count attribute directly"
    except AttributeError:
        pass   


def test_cache_handler_call_and_read_counts():
    """Test that the call_count and read_count properties of CacheHandler work correctly."""
    c = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(c)
    func = cache_module.SetLightCache(lambda x: x*2, handler)
    assert handler.call_count == 0
    assert handler.read_count == 0

    assert func(2) == 4
    assert handler.call_count == 1
    assert handler.read_count == 0

    assert func(2) == 4
    assert handler.call_count == 1
    assert handler.read_count == 1

    handler.reset_cache()
    assert handler.call_count == 1
    assert handler.read_count == 1

    assert func(2) == 4
    assert handler.call_count == 2
    assert handler.read_count == 1


def test_cache_handler_with_fibonacci():
    """Test that the CacheHandler works correctly with a Fibonacci function."""
    c = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(c)

    @cache_module.SetLightCache(cache_handler=handler)
    def fib(n):
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)

    assert fib(100) == 354224848179261915075
    assert handler.call_count == 101  # fib(0) to fib(100) are called
    assert handler.read_count == 98   # fib(2) to fib(100) are read from cache
    
    assert fib(50) == 12586269025
    assert handler.call_count == 101  # No new calls, all results are cached
    assert handler.read_count == 99   # fib(50) is read from cache

    assert handler.cache.smallest_key == 0
    assert handler.cache.largest_key == 100


# ---------------------------------------------------------------------------
# Cache — missing key and membership
# ---------------------------------------------------------------------------

def test_cache_missing_key_raises():
    c = cache_module.Cache()
    try:
        _ = c['missing']
        assert False, "Expected KeyError for missing key"
    except KeyError:
        pass

def test_cache_contains():
    c = cache_module.Cache()
    c['x'] = 42
    assert 'x' in c
    assert 'y' not in c


# ---------------------------------------------------------------------------
# OrdinalCache — maxsize validation and initializer bounds
# ---------------------------------------------------------------------------

def test_ordinal_cache_maxsize_invalid_type():
    try:
        cache_module.OrdinalCache(maxsize='big')
        assert False, "Expected TypeError for non-int maxsize"
    except TypeError:
        pass

def test_ordinal_cache_init_with_dict_updates_bounds():
    oc = cache_module.OrdinalCache({3: 'three', 1: 'one', 7: 'seven'})
    assert oc.smallest_key == 1
    assert oc.largest_key == 7

def test_ordinal_cache_negative_keys():
    oc = cache_module.OrdinalCache()
    oc[-5] = 'minus five'
    oc[10] = 'ten'
    assert oc.smallest_key == -5
    assert oc.largest_key == 10


# ---------------------------------------------------------------------------
# CacheHandler — prune on OrdinalCache
# ---------------------------------------------------------------------------

def test_cache_handler_prune_ordinal_removes_smallest():
    oc = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(oc)
    for i in range(1, 6):
        handler.cache[i] = i * 10
    # keep 2 largest: 4, 5
    handler.prune_cache(n=2)
    assert len(handler.cache) == 2
    assert 1 not in handler.cache
    assert 2 not in handler.cache
    assert 3 not in handler.cache
    assert 4 in handler.cache
    assert 5 in handler.cache

def test_cache_handler_prune_ordinal_updates_bounds():
    oc = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(oc)
    for i in range(1, 6):
        handler.cache[i] = i * 10
    handler.prune_cache(n=2)
    assert handler.cache.smallest_key == 4
    assert handler.cache.largest_key == 5

def test_cache_handler_prune_to_zero():
    oc = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(oc)
    handler.cache[1] = 'one'
    handler.cache[2] = 'two'
    handler.prune_cache(n=0)
    assert len(handler.cache) == 0
    assert isinstance(handler.cache, cache_module.OrdinalCache)

def test_cache_handler_reset_clears_ordinal_bounds():
    oc = cache_module.OrdinalCache()
    handler = cache_module.CacheHandler(oc)
    handler.cache[3] = 'three'
    handler.cache[7] = 'seven'
    assert handler.cache.smallest_key == 3
    assert handler.cache.largest_key == 7
    handler.reset_cache()
    assert handler.cache.smallest_key is None
    assert handler.cache.largest_key is None


# ---------------------------------------------------------------------------
# SetCache — untested entirely
# ---------------------------------------------------------------------------

def test_set_cache_basic():
    handler = cache_module.CacheHandler(cache_module.Cache())
    func = cache_module.SetCache(lambda x: x * 3, handler)
    assert func(4) == 12
    assert handler.call_count == 1
    assert handler.read_count == 0
    assert func(4) == 12
    assert handler.call_count == 1
    assert handler.read_count == 1

def test_set_cache_kwargs_are_part_of_key():
    handler = cache_module.CacheHandler(cache_module.Cache())
    func = cache_module.SetCache(lambda x, y=1: x + y, handler)
    assert func(2, y=3) == 5
    assert handler.call_count == 1
    # same positional arg, different kwarg — must be a cache miss
    assert func(2, y=4) == 6
    assert handler.call_count == 2
    # repeat call — cache hit
    assert func(2, y=3) == 5
    assert handler.read_count == 1

def test_set_cache_as_decorator():
    handler = cache_module.CacheHandler(cache_module.Cache())

    @cache_module.SetCache
    def square(x):
        return x * x

    assert square(5) == 25
    assert square(5) == 25

def test_set_cache_as_decorator_factory():
    handler = cache_module.CacheHandler(cache_module.Cache())

    @cache_module.SetCache(cache_handler=handler)
    def cube(x):
        return x ** 3

    assert cube(3) == 27
    assert handler.call_count == 1
    assert cube(3) == 27
    assert handler.read_count == 1

def test_set_cache_auto_creates_handler():
    # When no handler is provided, SetCache creates its own — must not raise
    func = cache_module.SetCache(lambda x: x + 1)
    assert func(10) == 11
    assert func(10) == 11  # should hit cache silently


# ---------------------------------------------------------------------------
# SetLightCache — auto handler and decorator factory form
# ---------------------------------------------------------------------------

def test_set_light_cache_auto_creates_handler():
    func = cache_module.SetLightCache(lambda x: x * 2)
    assert func(5) == 10
    assert func(5) == 10  # should hit cache silently

def test_set_light_cache_as_decorator_factory():
    handler = cache_module.CacheHandler(cache_module.OrdinalCache())

    @cache_module.SetLightCache(cache_handler=handler)
    def double(x):
        return x * 2

    assert double(7) == 14
    assert handler.call_count == 1
    assert double(7) == 14
    assert handler.read_count == 1
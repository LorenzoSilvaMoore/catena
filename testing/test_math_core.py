import catena.mathlib.core as math_core


def test_get_sign():
    """Test the get_sign function with various inputs."""
    assert math_core.get_sign(10) == 1
    assert math_core.get_sign(-5) == -1
    assert math_core.get_sign(0) == 0

    for a in [-10, 0, 10]:
        for b in [-10, 1, 10]:
            assert math_core.get_sign(a) * math_core.get_sign(b) == math_core.get_sign(a*b)


def test_simplify():
    """Test the simplify function with various inputs."""
    assert math_core.simplify(10, 5) == (2, 1)
    assert math_core.simplify(15, 25) == (3, 5)
    assert math_core.simplify(7, 3) == (7, 3)
    assert math_core.simplify(0, 5) == (0, 1)
    assert math_core.simplify(40, 0) == (1, 0)


def test_simplify_negative():
    """Test the simplify function with negative inputs."""
    assert math_core.simplify(-10, 5) == (-2, 1)
    assert math_core.simplify(15, -25) == (3, -5)
    assert math_core.simplify(-7, -3) == (-7, -3)
    assert math_core.simplify(0, -5) == (0, -1)
    assert math_core.simplify(-40, 0) == (-1, 0)


def test_canonicalize():
    """Test the canonicalize function with various inputs."""
    assert math_core.canonicalize(10, 5) == (2, 1)
    assert math_core.canonicalize(15, -25) == (-3, 5)
    assert math_core.canonicalize(-7, -3) == (7, 3)
    assert math_core.canonicalize(0, -5) == (0, 1)
    assert math_core.canonicalize(-40, 0) == (-1, 0)
    assert math_core.canonicalize(-10, 5) == (-2, 1)


def test_euclidean_step():
    """Test the euclidean_step function with various inputs."""
    assert math_core.euclidean_step(10, 3) == (3, 1, 3)
    assert math_core.euclidean_step(15, 4) == (3, 3, 4)
    assert math_core.euclidean_step(7, 2) == (3, 1, 2)
    assert math_core.euclidean_step(0, 5) == (0, 0, 5)
    assert math_core.euclidean_step(-21, 5) == (-5, 4, 5)
    
    try:
        math_core.euclidean_step(40, 0)
        assert False, "Expected ZeroDivisionError"
    except ZeroDivisionError:
        pass  # Expected exception


def test_quotent_sign():
    """Test the quotent_sign function with various inputs."""
    assert math_core.quotent_sign(10, 5) == 1
    assert math_core.quotent_sign(-15, 25) == -1
    assert math_core.quotent_sign(-7, -3) == 1
    assert math_core.quotent_sign(0, -5) == 0
    assert math_core.quotent_sign(-40, 0) is None
    assert math_core.quotent_sign(-10, 5) == -1





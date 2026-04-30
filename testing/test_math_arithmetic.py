from catena.mathlib.arithmetic import (
    add_fractions,
    uadd_fractions,
    multiply_fractions,
    umultiply_fractions,
    square_fraction,
    usquare_fraction,
    sandwich_fraction,
    usandwich_fraction,
)


def test_add_fractions():
    """Test the add_fractions function with various inputs."""
    # simplified inputs garantee simplified outputs
    # unsimplified inputs may or may not produce simplified outputs, but should always produce correct results
    assert add_fractions((1, 2), (1, 3)) == (5, 6)
    assert add_fractions((1, 4), (1, 4)) == (1, 2)
    assert add_fractions((2, 3), (1, 6)) == (5, 6)
    assert add_fractions((0, 1), (1, 5)) == (1, 5)
    assert add_fractions((-1, 2), (1, 2)) == (0, 1)
    assert add_fractions((-1, 2), (-1, 2)) == (-1, 1)
    assert add_fractions((1, 1), (2, 6)) == (8, 6) # Note: This test checks that the function returns the correct unsimplified result, which is expected behavior for add_fractions.

def test_uadd_fractions():
    """Test the uadd_fractions function with various inputs."""
    assert uadd_fractions(1, 2, 1, 3) == (5, 6)
    assert uadd_fractions(1, 4, 1, 4) == (1, 2)
    assert uadd_fractions(2, 3, 1, 6) == (5, 6)
    assert uadd_fractions(0, 1, 1, 5) == (1, 5)
    assert uadd_fractions(-1, 2, 1, 2) == (0, 1)
    assert uadd_fractions(-1, 2, -1, 2) == (-1, 1)
    assert uadd_fractions(1, 1, 2, 6) == (8, 6)

def test_uadd_fractions_against_add_fractions():
    """Test that uadd_fractions produces the same results as add_fractions."""
    test_cases = [
        ((1, 2), (1, 3)),
        ((1, 4), (1, 4)),
        ((2, 3), (1, 6)),
        ((0, 1), (1, 5)),
        ((-1, 2), (1, 2)),
        ((-1, 2), (-1, 2)),
        ((0, 1), (2, 6)),
    ]
    
    for a, b in test_cases:
        assert uadd_fractions(*a, *b) == add_fractions(a, b)


def test_multiply_fractions():
    """Test the multiply_fractions function with various inputs."""
    # simplified inputs garantee simplified outputs
    # unsimplified inputs may or may not produce simplified outputs, but should always produce correct results
    assert multiply_fractions((1, 2), (1, 3)) == (1, 6)
    assert multiply_fractions((1, 4), (1, 4)) == (1, 16)
    assert multiply_fractions((2, 3), (1, 6)) == (1, 9)
    assert multiply_fractions((0, 1), (1, 5)) == (0, 1)
    assert multiply_fractions((-1, 2), (1, 2)) == (-1, 4)
    assert multiply_fractions((-1, 2), (-1, 2)) == (1, 4)
    assert multiply_fractions((1, 3), (2, 6)) == (2, 18)
    assert multiply_fractions((2, 4), (12, 16)) == (3, 8)


def test_umultiply_fractions():
    """Test the umultiply_fractions function with various inputs."""
    assert umultiply_fractions(1, 2, 1, 3) == (1, 6)
    assert umultiply_fractions(1, 4, 1, 4) == (1, 16)
    assert umultiply_fractions(2, 3, 1, 6) == (1, 9)
    assert umultiply_fractions(0, 1, 1, 5) == (0, 1)
    assert umultiply_fractions(-1, 2, 1, 2) == (-1, 4)
    assert umultiply_fractions(-1, 2, -1, 2) == (1, 4)
    assert umultiply_fractions(1, 3, 2, 6) == (2, 18)
    assert umultiply_fractions(2, 4, 12, 16) == (3, 8)


def test_umultiply_fractions_against_multiply_fractions():
    """Test that umultiply_fractions produces the same results as multiply_fractions."""
    test_cases = [
        ((1, 2), (1, 3)),
        ((1, 4), (1, 4)),
        ((2, 3), (1, 6)),
        ((0, 1), (1, 5)),
        ((-1, 2), (1, 2)),
        ((-1, 2), (-1, 2)),
        ((1, 3), (2, 6)),
        ((2, 4), (12, 16)),
    ]
    
    for a, b in test_cases:
        assert umultiply_fractions(*a, *b) == multiply_fractions(a, b)


def test_square_fraction():
    """Test the square_fraction function with various inputs."""
    assert square_fraction((1, 2)) == (1, 4)
    assert square_fraction((3, 4)) == (9, 16)
    assert square_fraction((-1, 2)) == (1, 4)
    assert square_fraction((0, 1)) == (0, 1)
    assert square_fraction((2, 3)) == (4, 9)
    assert square_fraction((5, 1)) == (25, 1)
    assert square_fraction((5, 25)) == (25, 625)


def test_usquare_fraction():
    """Test the usquare_fraction function with various inputs."""
    assert usquare_fraction(1, 2) == (1, 4)
    assert usquare_fraction(3, 4) == (9, 16)
    assert usquare_fraction(-1, 2) == (1, 4)
    assert usquare_fraction(0, 1) == (0, 1)
    assert usquare_fraction(2, 3) == (4, 9)
    assert usquare_fraction(5, 1) == (25, 1)
    assert usquare_fraction(5, 25) == (25, 625)


def test_usandwich_fraction():
    """Test the usandwich_fraction function with various inputs."""
    assert usandwich_fraction(1, 2, 3, 4) == (2, 3)
    assert usandwich_fraction(2, 3, 4, 5) == (5, 6)
    assert usandwich_fraction(-1, 2, 3, 4) == (-2, 3)
    assert usandwich_fraction(1, 2, -3, 4) == (2, -3)
    assert usandwich_fraction(-1, 2, -3, 4) == (-2, -3)
    assert usandwich_fraction(1, -2, -3, 4) == (2, 3)
    assert usandwich_fraction(0, 1, 3, 4) == (0, 1)


def test_sandwich_fraction():
    """Test the sandwich_fraction function with various inputs."""
    assert sandwich_fraction((1, 2), (3, 4)) == (2, 3)
    assert sandwich_fraction((2, 3), (4, 5)) == (5, 6)
    assert sandwich_fraction((-1, 2), (3, 4)) == (-2, 3)
    assert sandwich_fraction((1, 2), (-3, 4)) == (2, -3)
    assert sandwich_fraction((-1, 2), (-3, 4)) == (-2, -3)
    assert sandwich_fraction((1, -2), (-3, 4)) == (2, 3)
    assert sandwich_fraction((0, 1), (3, 4)) == (0, 1)
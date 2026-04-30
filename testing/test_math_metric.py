from catena.mathlib.metric import product_digit_count, average_digit_count

from functools import reduce

from testing.bigints import load, build_store_path

def test_product_digit_count():
    """Test the product_digit_count function with various inputs."""
    assert product_digit_count([1, 2, 3]) == 1
    assert product_digit_count([10, 100, 1000]) == 7
    assert product_digit_count([123, 456, 789]) == 8
    assert product_digit_count([2, 5, 10]) == 3
    assert product_digit_count([1]) == 1

    loaded = load(build_store_path("random_math_metric_product_digit_count"))
    big_ints = [loaded[f"random_1000000_digits{i}"] for i in range(1, 4)]

    assert product_digit_count(big_ints) == 3000001
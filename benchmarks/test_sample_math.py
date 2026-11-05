import pytest
from benchmarks.sample_math import calculate_discount, find_median

def test_calculate_discount_standard():
    assert calculate_discount(100.0, 20.0) == 80.0

def test_calculate_discount_zero_discount():
    assert calculate_discount(50.0, 0.0) == 50.0

def test_find_median_unsorted_odd():
    assert find_median([5, 1, 3]) == 3.0

def test_find_median_unsorted_even():
    assert find_median([10, 2, 8, 4]) == 6.0

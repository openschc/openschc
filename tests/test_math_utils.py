from src.math_utils import divide
import pytest


def test_divide_positive_numbers() -> None:
    """Test that divide returns the correct result when given two numbers."""
    assert divide(1, 2) == 0.5


def test_divide_negative_numbers() -> None:
    """
    Test that divide returns the correct result when given a positive and
    a negative number.
    """
    assert divide(5, -2) == -2.5
    assert divide(-2, 5) == -0.4
    
def test_divide_by_zero() -> None:
    """Test that divide raises a ZeroDivisionError when the denominator is zero."""
    with pytest.raises(ZeroDivisionError, match="You can't divide by zero!"):
        divide(1, 0)
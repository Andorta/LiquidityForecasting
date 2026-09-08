import pytest

from liquidity_forecasting.allocation import (
    allocate_funds_by_shortfall,
)


def test_allocate_all_required_funding_when_funds_are_sufficient():
    result = allocate_funds_by_shortfall(
        {"EUR": 100.0, "USD": 50.0},
        available_funds=200.0,
    )

    assert result == {
        "EUR": 100.0,
        "USD": 50.0,
    }


def test_allocate_funds_proportionally_when_funds_are_limited():
    result = allocate_funds_by_shortfall(
        {"EUR": 100.0, "USD": 50.0},
        available_funds=60.0,
    )

    assert result["EUR"] == pytest.approx(40.0)
    assert result["USD"] == pytest.approx(20.0)


def test_allocate_zero_when_there_are_no_shortfalls():
    result = allocate_funds_by_shortfall(
        {"EUR": 0.0, "USD": 0.0},
        available_funds=100.0,
    )

    assert result == {
        "EUR": 0.0,
        "USD": 0.0,
    }


def test_reject_negative_available_funds():
    with pytest.raises(ValueError, match="cannot be negative"):
        allocate_funds_by_shortfall(
            {"EUR": 100.0},
            available_funds=-1.0,
        )


def test_reject_negative_shortfall():
    with pytest.raises(ValueError, match="cannot be negative"):
        allocate_funds_by_shortfall(
            {"EUR": -10.0},
            available_funds=100.0,
        )
import pandas as pd
import pytest

from liquidity_forecasting.balances import project_balances


def test_project_balances_accumulates_net_cashflows():
    dates = pd.date_range("2025-01-01", periods=3, freq="D")
    forecasts = {
        "EUR": pd.Series([10.0, -20.0, 5.0], index=dates),
        "USD": pd.Series([-5.0, 15.0, -10.0], index=dates),
    }
    opening_balances = {
        "EUR": 100.0,
        "USD": 200.0,
    }

    result = project_balances(opening_balances, forecasts)

    expected = pd.DataFrame(
        {
            "EUR": [110.0, 90.0, 95.0],
            "USD": [195.0, 210.0, 200.0],
        },
        index=dates,
    )
    expected.index.name = "Date"

    pd.testing.assert_frame_equal(result, expected)


def test_project_balances_rejects_missing_opening_balance():
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    forecasts = {
        "EUR": pd.Series([10.0, -5.0], index=dates),
    }

    with pytest.raises(ValueError, match="missing for currency 'EUR'"):
        project_balances({}, forecasts)


def test_project_balances_rejects_empty_forecasts():
    with pytest.raises(ValueError, match="At least one"):
        project_balances({"EUR": 100.0}, {})
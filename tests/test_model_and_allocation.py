import numpy as np
import pandas as pd

from liquidity_forecasting.data import load_cashflow_data, preprocess_data
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.allocation import optimize_allocation


def test_forecast_currency_produces_expected_horizon_without_nans():
    """Forecast should return a series of the requested length with no missing values."""
    df = preprocess_data(load_cashflow_data())
    horizon = 14

    forecast = forecast_currency(df, "EUR", periods=horizon)

    assert len(forecast) == horizon
    assert isinstance(forecast, (pd.Series, np.ndarray))
    # convert to series to check NaNs easily
    s = pd.Series(forecast)
    assert s.isna().sum() == 0


def test_optimize_allocation_sums_to_one_and_is_positive():
    """Optimized allocations should form a valid probability distribution."""
    df = preprocess_data(load_cashflow_data())
    horizon = 7

    forecasts = {
        ccy: forecast_currency(df, ccy, periods=horizon)
        for ccy in df.columns
    }

    allocations = optimize_allocation(forecasts)

    # all currencies from forecasts should be present
    assert set(allocations.keys()) == set(forecasts.keys())

    # allocations should be positive and sum to 1 (within numerical tolerance)
    values = np.array(list(allocations.values()))
    assert np.all(values > 0)
    assert np.isclose(values.sum(), 1.0, atol=1e-6)


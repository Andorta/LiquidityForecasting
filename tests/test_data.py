import pandas as pd

from liquidity_forecasting.data import load_cashflow_data, preprocess_data


def test_load_cashflow_data_default_shape():
    """Data loader should return a non-empty daily time series with expected currencies."""
    df = load_cashflow_data()
    # basic structure
    assert isinstance(df.index, pd.DatetimeIndex)
    assert not df.empty
    # by default we expect 6 currencies
    assert set(df.columns) == {"EUR", "USD", "JPY", "BRL", "INR", "AUD"}


def test_preprocess_data_forward_fills_missing_values():
    """Preprocessing should forward-fill missing values."""
    df = load_cashflow_data().copy()

    # introduce a missing value in the middle
    df.iloc[10, 0] = None
    # pandas converts None to NaN for numeric dtypes
    assert pd.isna(df.iloc[10, 0])

    processed = preprocess_data(df)

    # after preprocessing, there should be no NaNs in the data
    assert not processed.isna().any().any()
    # and the introduced NaN should have been forward-filled
    assert processed.iloc[10, 0] == processed.iloc[9, 0]


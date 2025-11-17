import pandas as pd
import numpy as np

def load_cashflow_data(
    start="2022-01-01",
    end="2025-01-01",
    currencies=None,
    seed=42
):
    """
    Simulate daily cumulative cashflows for multiple currencies.
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start, end=end, freq="D")
    if currencies is None:
        currencies = ['EUR', 'USD', 'JPY', 'BRL', 'INR', 'AUD']

    data = {
        currency: np.cumsum(np.random.randn(len(dates)) * 100)
        for currency in currencies
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.ffill()

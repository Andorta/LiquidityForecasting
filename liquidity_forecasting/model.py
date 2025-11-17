import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def forecast_currency(
    df: pd.DataFrame,
    currency: str,
    periods: int = 30,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal: tuple[int, int, int, int] = (1, 1, 1, 7),
):
    """
    Fit a SARIMAX model for a single currency and forecast future values.

    Parameters
    ----------
    df : pd.DataFrame
        Historical cashflow data with a DatetimeIndex and one column per currency.
    currency : str
        Currency column to model.
    periods : int
        Number of days to forecast.
    order : tuple[int, int, int]
        Non-seasonal ARIMA (p, d, q) order.
    seasonal : tuple[int, int, int, int]
        Seasonal (P, D, Q, s) order.

    Returns
    -------
    pd.Series
        Forecasted values for the given horizon.
    """
    series = df[currency]

    model = SARIMAX(series, order=order, seasonal_order=seasonal)
    results = model.fit(disp=False)
    forecast = results.forecast(steps=periods)

    # Ensure we return a pandas Series (tests also accept np.ndarray, but this is clearer)
    if not isinstance(forecast, pd.Series):
        forecast = pd.Series(forecast)

    return forecast

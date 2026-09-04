import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def forecast_currency(
    df: pd.DataFrame,
    currency: str,
    periods: int = 30,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal: tuple[int, int, int, int] = (1, 1, 1, 7),
) -> pd.Series:
    """Fit a SARIMAX model and forecast daily values for one currency."""
    series = df[currency]

    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal,
    )
    results = model.fit(disp=False)

    forecast_values = results.forecast(steps=periods)

    future_index = pd.date_range(
        start=series.index.max() + pd.Timedelta(days=1),
        periods=periods,
        freq="D",
    )

    return pd.Series(
        pd.Series(forecast_values).to_numpy(),
        index=future_index,
        name=currency,
    )

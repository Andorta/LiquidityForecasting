from dataclasses import dataclass
import warnings

import pandas as pd
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.statespace.sarimax import SARIMAX


@dataclass(frozen=True)
class ForecastResult:
    mean: pd.Series
    lower: pd.Series
    upper: pd.Series
    converged: bool


def forecast_currency_with_intervals(
    df: pd.DataFrame,
    currency: str,
    periods: int = 30,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal: tuple[int, int, int, int] = (1, 1, 1, 7),
    alpha: float = 0.05,
) -> ForecastResult:
    """Fit SARIMAX and return forecasts with prediction intervals."""
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between zero and one.")

    series = df[currency]

    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always", ConvergenceWarning)

        model = SARIMAX(
            series,
            order=order,
            seasonal_order=seasonal,
        )
        fitted_model = model.fit(disp=False)

    convergence_warning = any(
        issubclass(warning.category, ConvergenceWarning)
        for warning in captured_warnings
    )

    converged = bool(
        fitted_model.mle_retvals.get(
            "converged",
            not convergence_warning,
        )
    )

    prediction = fitted_model.get_forecast(steps=periods)
    confidence_intervals = prediction.conf_int(alpha=alpha)

    future_index = pd.date_range(
        start=series.index.max() + pd.Timedelta(days=1),
        periods=periods,
        freq="D",
    )

    mean = pd.Series(
        prediction.predicted_mean.to_numpy(),
        index=future_index,
        name=currency,
    )
    lower = pd.Series(
        confidence_intervals.iloc[:, 0].to_numpy(),
        index=future_index,
        name=currency,
    )
    upper = pd.Series(
        confidence_intervals.iloc[:, 1].to_numpy(),
        index=future_index,
        name=currency,
    )

    return ForecastResult(
        mean=mean,
        lower=lower,
        upper=upper,
        converged=converged,
    )


def forecast_currency(
    df: pd.DataFrame,
    currency: str,
    periods: int = 30,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal: tuple[int, int, int, int] = (1, 1, 1, 7),
) -> pd.Series:
    """Return the mean SARIMAX forecast for one currency."""
    result = forecast_currency_with_intervals(
        df=df,
        currency=currency,
        periods=periods,
        order=order,
        seasonal=seasonal,
    )

    return result.mean
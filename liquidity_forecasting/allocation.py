import numpy as np
import pandas as pd
from typing import Dict, Mapping


def optimize_allocation(forecasts: Dict[str, pd.Series]) -> Dict[str, float]:
    """
    Compute a simple allocation based on total absolute forecasted cashflows.

    Parameters
    ----------
    forecasts : dict
        Mapping from currency code to forecast series/array.

    Returns
    -------
    dict
        Mapping from currency code to allocation weight (summing to 1.0).
    """
    totals = {}
    for ccy, fc in forecasts.items():
        # Convert to Series for consistent handling
        s = pd.Series(fc)
        totals[ccy] = float(np.abs(s).sum())

    grand_total = sum(totals.values())
    if grand_total == 0:
        # Edge case: if everything is zero, allocate equally
        n = len(totals)
        return {ccy: 1.0 / n for ccy in totals}

    allocations = {ccy: total / grand_total for ccy, total in totals.items()}
    return allocations

def allocate_funds_by_shortfall(
    shortfalls_in_base_currency: Mapping[str, float],
    available_funds: float,
) -> Dict[str, float]:
    """Allocate available funds proportionally to liquidity shortfalls."""
    if not shortfalls_in_base_currency:
        raise ValueError("At least one liquidity shortfall is required.")

    if available_funds < 0:
        raise ValueError("Available funds cannot be negative.")

    normalized_shortfalls = {
        currency: float(shortfall)
        for currency, shortfall in shortfalls_in_base_currency.items()
    }

    negative_currencies = [
        currency
        for currency, shortfall in normalized_shortfalls.items()
        if shortfall < 0
    ]

    if negative_currencies:
        invalid = ", ".join(negative_currencies)
        raise ValueError(
            f"Liquidity shortfalls cannot be negative for: {invalid}."
        )

    total_shortfall = sum(normalized_shortfalls.values())

    if total_shortfall == 0 or available_funds == 0:
        return {
            currency: 0.0
            for currency in normalized_shortfalls
        }

    funding_ratio = min(
        1.0,
        float(available_funds) / total_shortfall,
    )

    return {
        currency: shortfall * funding_ratio
        for currency, shortfall in normalized_shortfalls.items()
    }
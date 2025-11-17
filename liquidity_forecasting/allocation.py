import numpy as np
import pandas as pd
from typing import Dict


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

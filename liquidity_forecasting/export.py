import pandas as pd


def save_to_excel(
    cashflows,
    forecasts,
    allocations,
    filename="output.xlsx",
    projected_balances=None,
):
    """Export liquidity analysis results to an Excel workbook."""
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        cashflows.to_excel(
            writer,
            sheet_name="Historical_Cashflows",
        )

        forecast_data = pd.DataFrame(forecasts)
        forecast_data.index.name = "Forecast_Date"
        forecast_data.to_excel(
            writer,
            sheet_name="Forecasts",
        )

        if projected_balances is not None:
            projected_balances.to_excel(
                writer,
                sheet_name="Projected_Balances",
            )

        allocation_data = pd.DataFrame.from_dict(
            allocations,
            orient="index",
            columns=["Allocation"],
        )
        allocation_data["Allocation"] *= 100
        allocation_data.to_excel(
            writer,
            sheet_name="Allocation",
        )
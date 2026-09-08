import pandas as pd

from liquidity_forecasting.fx import BASE_CURRENCY


def save_to_excel(
    cashflows,
    forecasts,
    funding_recommendations,
    filename="output.xlsx",
    projected_balances=None,
    liquidity_shortfalls=None,
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

        if liquidity_shortfalls is not None:
            liquidity_shortfalls.to_excel(
                writer,
                sheet_name="Liquidity_Shortfalls",
            )

        funding_data = pd.DataFrame.from_dict(
            funding_recommendations,
            orient="index",
            columns=[
                f"Recommended Funding ({BASE_CURRENCY})"
            ],
        )
        funding_data.index.name = "Currency"
        funding_data.to_excel(
            writer,
            sheet_name="Funding_Recommendations",
        )
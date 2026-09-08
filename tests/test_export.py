from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from liquidity_forecasting.export import save_to_excel


def test_excel_export_contains_expected_sheets():
    historical_index = pd.date_range(
        "2025-01-01",
        periods=3,
        freq="D",
    )
    forecast_index = pd.date_range(
        "2025-01-04",
        periods=2,
        freq="D",
    )

    cashflows = pd.DataFrame(
        {"EUR": [100.0, -50.0, 25.0]},
        index=historical_index,
    )
    forecasts = {
        "EUR": pd.Series(
            [20.0, -10.0],
            index=forecast_index,
        )
    }
    projected_balances = pd.DataFrame(
        {"EUR": [1_020.0, 1_010.0]},
        index=forecast_index,
    )
    funding_recommendations = {"EUR": 1_000.0}

    output = BytesIO()

    save_to_excel(
        cashflows,
        forecasts,
        funding_recommendations,
        filename=output,
        projected_balances=projected_balances,
    )

    output.seek(0)

    with ZipFile(output) as workbook:
        workbook_xml = workbook.read(
            "xl/workbook.xml"
        ).decode("utf-8")

    assert "Historical_Cashflows" in workbook_xml
    assert "Forecasts" in workbook_xml
    assert "Projected_Balances" in workbook_xml
    assert "Funding_Recommendations" in workbook_xml
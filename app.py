from io import BytesIO

import pandas as pd
import streamlit as st

from liquidity_forecasting.allocation import optimize_allocation
from liquidity_forecasting.balances import (
    DEFAULT_MINIMUM_BUFFERS,
    DEFAULT_OPENING_BALANCES,
    calculate_liquidity_shortfalls,
    project_balances,
)
from liquidity_forecasting.data import (
    generate_sample_cashflows,
    preprocess_data,
)
from liquidity_forecasting.export import save_to_excel
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.validation import validate_cashflow_data


st.set_page_config(
    page_title="Liquidity Forecasting Dashboard",
    layout="wide",
)

st.title("Liquidity Forecasting & Fund Allocation Dashboard")


# Data input
st.sidebar.header("Data Options")

use_simulated = st.sidebar.checkbox(
    "Use simulated sample data",
    value=True,
)

if use_simulated:
    df = generate_sample_cashflows()
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload Cashflow File",
        type=["csv", "xlsx"],
    )

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(
                uploaded_file,
                parse_dates=[0],
                index_col=0,
            )
        else:
            df = pd.read_excel(
                uploaded_file,
                parse_dates=[0],
                index_col=0,
            )
    else:
        st.warning("Upload a file or enable simulated data.")
        st.stop()

try:
    df = preprocess_data(df)
    validate_cashflow_data(df)
except (TypeError, ValueError) as error:
    st.error(f"Invalid cashflow data: {error}")
    st.stop()

st.subheader("Historical Net Cashflows")
st.line_chart(df)


# Forecast settings
st.sidebar.header("Forecast Settings")

horizon = st.sidebar.slider(
    "Forecast horizon (days)",
    min_value=7,
    max_value=90,
    value=30,
)

currencies = st.sidebar.multiselect(
    "Select currencies",
    df.columns.tolist(),
    default=df.columns.tolist(),
)

if not currencies:
    st.warning("Select at least one currency.")
    st.stop()


# Opening balances
st.sidebar.header("Opening Balances")

opening_balances = {}

for currency in currencies:
    default_balance = DEFAULT_OPENING_BALANCES.get(
        currency,
        100_000.0,
    )

    opening_balances[currency] = st.sidebar.number_input(
        f"{currency} opening balance",
        min_value=0.0,
        value=float(default_balance),
        step=max(float(default_balance) * 0.05, 1_000.0),
    )


# Minimum liquidity buffers
st.sidebar.header("Minimum Liquidity Buffers")

minimum_buffers = {}

for currency in currencies:
    default_buffer = DEFAULT_MINIMUM_BUFFERS.get(
        currency,
        20_000.0,
    )

    minimum_buffers[currency] = st.sidebar.number_input(
        f"{currency} minimum buffer",
        min_value=0.0,
        value=float(default_buffer),
        step=max(float(default_buffer) * 0.05, 500.0),
    )


# Forecast computation
st.subheader(f"Forecasts for Next {horizon} Days")

forecasts = {
    currency: forecast_currency(
        df,
        currency,
        periods=horizon,
    )
    for currency in currencies
}

projected_balances = project_balances(
    opening_balances,
    forecasts,
)

shortfalls = calculate_liquidity_shortfalls(
    projected_balances,
    minimum_buffers,
)


# Forecast charts
for currency in currencies:
    st.write(f"### {currency} Forecast")

    historical = df[currency].iloc[-60:]
    combined = pd.concat(
        [historical, forecasts[currency]]
    )

    st.line_chart(combined)


# Projected balances
st.subheader("Projected Cash Balances")

st.caption(
    "Projected balances equal the opening balance plus "
    "cumulative forecast net cashflows."
)

st.line_chart(projected_balances)

liquidity_summary = pd.DataFrame(
    {
        "Opening Balance": pd.Series(opening_balances),
        "Minimum Buffer": pd.Series(minimum_buffers),
        "Minimum Projected Balance": projected_balances.min(),
        "Maximum Shortfall": shortfalls.max(),
    }
)

st.dataframe(
    liquidity_summary.style.format("{:,.2f}")
)

currencies_at_risk = liquidity_summary[
    liquidity_summary["Maximum Shortfall"] > 0
].index.tolist()

if currencies_at_risk:
    st.warning(
        "Projected buffer breach for: "
        + ", ".join(currencies_at_risk)
    )
else:
    st.success(
        "No projected liquidity-buffer breaches "
        "during the forecast period."
    )


# Temporary allocation heuristic
st.subheader("Current Heuristic Allocation")

st.caption(
    "This allocation is an interim heuristic. It will be replaced "
    "with FX-normalized constrained optimization."
)

allocations = optimize_allocation(forecasts)

allocation_data = pd.DataFrame.from_dict(
    allocations,
    orient="index",
    columns=["Allocation"],
)
allocation_data["Allocation %"] = (
    allocation_data["Allocation"] * 100
)

st.dataframe(
    allocation_data.style.format(
        {"Allocation %": "{:.2f}"}
    )
)


# Excel download
buffer = BytesIO()

save_to_excel(
    df,
    forecasts,
    allocations,
    filename=buffer,
    projected_balances=projected_balances,
)

buffer.seek(0)

st.download_button(
    label="Download Excel Output",
    data=buffer,
    file_name="liquidity_forecast_output.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
)
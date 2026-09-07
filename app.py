import streamlit as st
import pandas as pd

from liquidity_forecasting.data import (
    generate_sample_cashflows,
    preprocess_data,
)
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.allocation import optimize_allocation
from liquidity_forecasting.export import save_to_excel
from liquidity_forecasting.validation import validate_cashflow_data

from io import BytesIO

from liquidity_forecasting.balances import (
    DEFAULT_OPENING_BALANCES,
    project_balances,
)

# ---------------------------
# Streamlit App Config
# ---------------------------
st.set_page_config(
    page_title="Liquidity Forecasting Dashboard",
    layout="wide",
)

st.title("Liquidity Forecasting & Fund Allocation Dashboard")


# ---------------------------
# Data Input Section
# ---------------------------
st.sidebar.header("Data Options")

use_simulated = st.sidebar.checkbox("Use simulated sample data", value=True)

if use_simulated:
    df = generate_sample_cashflows()
else:
    uploaded_file = st.sidebar.file_uploader("Upload Cashflow File", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file, parse_dates=[0], index_col=0)
        else:
            df = pd.read_excel(uploaded_file, parse_dates=[0], index_col=0)
    else:
        st.warning("Upload a file or enable simulated data.")
        st.stop()

try:
    df = preprocess_data(df)
    validate_cashflow_data(df)
except (TypeError, ValueError) as error:
    st.error(f"Invalid cashflow data: {error}")
    st.stop()

st.subheader("Historical Cashflows")
st.line_chart(df)


# ---------------------------
# Forecast Settings
# ---------------------------
st.sidebar.header("Forecast Settings")

horizon = st.sidebar.slider("Forecast horizon (days)", min_value=7, max_value=90, value=30)

currencies = st.sidebar.multiselect(
    "Select currencies", df.columns.tolist(), default=df.columns.tolist()
)

if not currencies:
    st.warning("Select at least one currency.")
    st.stop()

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


# ---------------------------
# Forecast Computation
# ---------------------------
st.subheader(f"Forecasts for Next {horizon} Days")

forecasts = {}
for ccy in currencies:
    forecasts[ccy] = forecast_currency(df, ccy, periods=horizon)

projected_balances = project_balances(
    opening_balances,
    forecasts,
)

# Display forecast charts
for ccy in currencies:
    st.write(f"### {ccy} Forecast")

    historical = df[ccy].iloc[-60:]
    combined = pd.concat([historical, forecasts[ccy]])

    st.line_chart(combined)

st.subheader("Projected Cash Balances")

st.caption(
    "Projected balances are calculated from the opening balance "
    "plus cumulative forecast net cashflows."
)

st.line_chart(projected_balances)

minimum_balances = pd.DataFrame(
    {
        "Minimum Projected Balance": projected_balances.min(),
    }
)

st.dataframe(
    minimum_balances.style.format(
        {"Minimum Projected Balance": "{:,.2f}"}
    )
)

# ---------------------------
# Allocation Optimization
# ---------------------------
st.subheader("Optimized Allocation")

allocations = optimize_allocation(forecasts)

alloc_df = pd.DataFrame.from_dict(allocations, orient="index", columns=["Allocation"])
alloc_df["Allocation %"] = alloc_df["Allocation"] * 100

st.dataframe(alloc_df.style.format({"Allocation %": "{:.2f}"}))


# ---------------------------
# Download Excel Output
# ---------------------------
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
    label="📥 Download Excel Output",
    data=buffer,
    file_name="liquidity_forecast_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

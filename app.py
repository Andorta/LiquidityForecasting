import streamlit as st
import pandas as pd

from liquidity_forecasting.data import load_cashflow_data, preprocess_data
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.allocation import optimize_allocation
from liquidity_forecasting.export import save_to_excel

from io import BytesIO


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
    df = load_cashflow_data()
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

df = preprocess_data(df)

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


# ---------------------------
# Forecast Computation
# ---------------------------
st.subheader(f"Forecasts for Next {horizon} Days")

forecasts = {}
for ccy in currencies:
    forecasts[ccy] = forecast_currency(df, ccy, periods=horizon)

# Display forecast charts
for ccy in currencies:
    st.write(f"### {ccy} Forecast")

    historical = df[ccy].iloc[-60:]
    future_index = pd.date_range(
        start=df.index[-1] + pd.Timedelta(days=1),
        periods=horizon
    )
    combined = pd.concat(
        [historical, pd.Series(forecasts[ccy].values, index=future_index)]
    )

    st.line_chart(combined)


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
save_to_excel(df, forecasts, allocations, filename=buffer)
buffer.seek(0)

st.download_button(
    label="📥 Download Excel Output",
    data=buffer,
    file_name="liquidity_forecast_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

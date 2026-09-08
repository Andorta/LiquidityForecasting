from io import BytesIO

import pandas as pd
import streamlit as st

from liquidity_forecasting.allocation import (
    allocate_funds_by_shortfall,
)
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
from liquidity_forecasting.fx import (
    BASE_CURRENCY,
    DEFAULT_FX_TO_EUR,
    convert_frame_to_base_currency,
)
from liquidity_forecasting.evaluation import (
    rolling_backtest_currency,
    summarize_backtest_results,
)
from liquidity_forecasting.export import save_to_excel
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.validation import validate_cashflow_data


st.set_page_config(
    page_title="Liquidity Forecasting Dashboard",
    layout="wide",
)
@st.cache_data(show_spinner=False)
def run_cached_backtest(data, currency, horizon, folds):
    return rolling_backtest_currency(
        data,
        currency,
        forecast_currency,
        horizon=horizon,
        folds=folds,
        season_length=7,
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
st.sidebar.header(f"FX Rates to {BASE_CURRENCY}")

st.sidebar.caption(
    f"Each rate represents the value of one unit "
    f"of local currency in {BASE_CURRENCY}."
)

fx_rates = {}

for currency in currencies:
    default_rate = DEFAULT_FX_TO_EUR.get(currency, 1.0)

    fx_rates[currency] = st.sidebar.number_input(
        f"1 {currency} in {BASE_CURRENCY}",
        min_value=0.000001,
        value=float(default_rate),
        format="%.6f",
        disabled=(currency == BASE_CURRENCY),
    )

    minimum_buffers[currency] = st.sidebar.number_input(
        f"{currency} minimum buffer",
        min_value=0.0,
        value=float(default_buffer),
        step=max(float(default_buffer) * 0.05, 500.0),
    )
st.sidebar.header("Central Funding")

available_funds = st.sidebar.number_input(
    f"Available central funds ({BASE_CURRENCY})",
    min_value=0.0,
    value=100_000.0,
    step=5_000.0,
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

shortfalls_in_base_currency = convert_frame_to_base_currency(
    shortfalls,
    fx_rates,
)

maximum_shortfalls_in_base = (
    shortfalls_in_base_currency.max()
)
funding_recommendations = allocate_funds_by_shortfall(
    maximum_shortfalls_in_base.to_dict(),
    available_funds,
)

recommended_funding = pd.Series(
    funding_recommendations,
    dtype=float,
)

remaining_shortfalls = (
    maximum_shortfalls_in_base - recommended_funding
).clip(lower=0)

recommended_funding_local = pd.Series(
    {
        currency: amount / fx_rates[currency]
        for currency, amount in funding_recommendations.items()
    }
)

# Forecast charts
for currency in currencies:
    st.write(f"### {currency} Forecast")

    historical = df[currency].iloc[-60:]
    combined = pd.concat(
        [historical, forecasts[currency]]
    )

    st.line_chart(combined)

st.subheader("Forecast Model Evaluation")

evaluation_currency = st.selectbox(
    "Currency to evaluate",
    currencies,
)

if st.button("Run backtest"):
    with st.spinner(
        f"Backtesting {evaluation_currency}. "
        "This may take a little while..."
    ):
        backtest_results = run_cached_backtest(
            df,
            evaluation_currency,
            horizon=7,
            folds=3,
        )

    backtest_summary = summarize_backtest_results(
        backtest_results
    )

    st.dataframe(
        backtest_summary.style.format(
            {
                "MAE": "{:,.2f}",
                "MASE": "{:.3f}",
            }
        )
    )

    sarimax_mase = backtest_summary.loc[
        backtest_summary["Model"] == "SARIMAX",
        "MASE",
    ].iloc[0]

    naive_mase = backtest_summary.loc[
        backtest_summary["Model"] == "Seasonal Naive",
        "MASE",
    ].iloc[0]

    if sarimax_mase < naive_mase:
        st.success(
            "SARIMAX outperformed the seasonal-naive baseline "
            "during this backtest."
        )
    else:
        st.warning(
            "SARIMAX did not outperform the seasonal-naive "
            "baseline. The simpler model may be preferable."
        )

    with st.expander("View individual backtest folds"):
        st.dataframe(backtest_results)

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
        "Maximum Shortfall (Local)": shortfalls.max(),
        f"Maximum Shortfall ({BASE_CURRENCY})": (
            maximum_shortfalls_in_base
        ),
    }
)

st.dataframe(
    liquidity_summary.style.format("{:,.2f}")
)

currencies_at_risk = liquidity_summary[
    liquidity_summary["Maximum Shortfall (Local)"] > 0
].index.tolist()

st.dataframe(
    liquidity_summary.style.format("{:,.2f}")
)

currencies_at_risk = liquidity_summary[
    liquidity_summary["Maximum Shortfall (Local)"] > 0
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
# Funding recommendations
st.subheader("Funding Recommendations")

st.caption(
    f"Recommendations are allocated according to maximum "
    f"liquidity shortfalls after conversion to {BASE_CURRENCY}."
)

funding_summary = pd.DataFrame(
    {
        f"Maximum Shortfall ({BASE_CURRENCY})": (
            maximum_shortfalls_in_base
        ),
        f"Recommended Funding ({BASE_CURRENCY})": (
            recommended_funding
        ),
        "Recommended Funding (Local)": (
            recommended_funding_local
        ),
        f"Remaining Shortfall ({BASE_CURRENCY})": (
            remaining_shortfalls
        ),
    }
)

st.dataframe(
    funding_summary.style.format("{:,.2f}")
)

total_required = maximum_shortfalls_in_base.sum()
total_recommended = recommended_funding.sum()
total_remaining = remaining_shortfalls.sum()

metric_columns = st.columns(3)

metric_columns[0].metric(
    f"Required ({BASE_CURRENCY})",
    f"{total_required:,.2f}",
)
metric_columns[1].metric(
    f"Recommended ({BASE_CURRENCY})",
    f"{total_recommended:,.2f}",
)
metric_columns[2].metric(
    f"Unfunded ({BASE_CURRENCY})",
    f"{total_remaining:,.2f}",
)

if total_remaining > 0:
    st.warning(
        "Available central funds do not cover all projected shortfalls."
    )

# Excel download
buffer = BytesIO()

save_to_excel(
    df,
    forecasts,
    funding_recommendations,
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
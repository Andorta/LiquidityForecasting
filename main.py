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
from liquidity_forecasting.export import save_to_excel
from liquidity_forecasting.fx import (
    BASE_CURRENCY,
    DEFAULT_FX_TO_EUR,
    convert_frame_to_base_currency,
)
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.plotting import plot_forecasts
from liquidity_forecasting.validation import validate_cashflow_data


def main():
    cashflows = generate_sample_cashflows()
    cashflows = preprocess_data(cashflows)
    validate_cashflow_data(cashflows)

    forecasts = {
        currency: forecast_currency(cashflows, currency)
        for currency in cashflows.columns
    }

    opening_balances = {
        currency: DEFAULT_OPENING_BALANCES[currency]
        for currency in forecasts
    }

    minimum_buffers = {
        currency: DEFAULT_MINIMUM_BUFFERS[currency]
        for currency in forecasts
    }

    fx_rates = {
        currency: DEFAULT_FX_TO_EUR[currency]
        for currency in forecasts
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

    available_funds = 100_000.0

    funding_recommendations = allocate_funds_by_shortfall(
        maximum_shortfalls_in_base.to_dict(),
        available_funds,
    )

    print("Projected minimum balances:")
    for currency, balance in projected_balances.min().items():
        print(f"{currency}: {balance:,.2f}")

    print(
        f"\nMaximum liquidity shortfalls in {BASE_CURRENCY}:"
    )
    for currency, shortfall in maximum_shortfalls_in_base.items():
        print(f"{currency}: {shortfall:,.2f}")

    print(
        f"\nRecommended funding in {BASE_CURRENCY} "
        f"(available: {available_funds:,.2f}):"
    )
    for currency, amount in funding_recommendations.items():
        print(f"{currency}: {amount:,.2f}")

    save_to_excel(
        cashflows,
        forecasts,
        funding_recommendations,
        projected_balances=projected_balances,
        liquidity_shortfalls=shortfalls,
    )

    plot_forecasts(cashflows, forecasts)


if __name__ == "__main__":
    main()
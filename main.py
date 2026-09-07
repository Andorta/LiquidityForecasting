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

    projected_balances = project_balances(
        opening_balances,
        forecasts,
    )

    minimum_buffers = {
        currency: DEFAULT_MINIMUM_BUFFERS[currency]
        for currency in forecasts
    }

    shortfalls = calculate_liquidity_shortfalls(
        projected_balances,
        minimum_buffers,
    )

    print("Projected minimum balances:")
    for currency, balance in projected_balances.min().items():
        print(f"{currency}: {balance:,.2f}")

    print("\nMaximum liquidity shortfalls:")
    for currency, shortfall in shortfalls.max().items():
        print(f"{currency}: {shortfall:,.2f}")

    allocations = optimize_allocation(forecasts)

    print("\nCurrent heuristic allocation:")
    for currency, percentage in allocations.items():
        print(f"{currency}: {percentage * 100:.2f}%")

    save_to_excel(
        cashflows,
        forecasts,
        allocations,
        projected_balances=projected_balances,
        liquidity_shortfalls=shortfalls,
    )

    plot_forecasts(cashflows, forecasts)


if __name__ == "__main__":
    main()
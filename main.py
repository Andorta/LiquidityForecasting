from liquidity_forecasting.data import load_cashflow_data, preprocess_data
from liquidity_forecasting.model import forecast_currency
from liquidity_forecasting.allocation import optimize_allocation
from liquidity_forecasting.plotting import plot_forecasts
from liquidity_forecasting.export import save_to_excel

def main():
    df = load_cashflow_data()
    df = preprocess_data(df)

    forecasts = {
        currency: forecast_currency(df, currency)
        for currency in df.columns
    }

    allocations = optimize_allocation(forecasts)

    print("Optimized Allocation:")
    for c, pct in allocations.items():
        print(f"{c}: {pct*100:.2f}%")

    save_to_excel(df, forecasts, allocations)
    plot_forecasts(df, forecasts)

if __name__ == "__main__":
    main()

# liquidity forecasting app for funds allocation

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import StandardScaler
import datetime
import warnings
warnings.filterwarnings("ignore")

# Simulates daily cashflow data
def load_cashflow_data():

    # Simulated sample data for 6 currencies
    dates = pd.date_range(start="2022-01-01", end="2025-01-01", freq='D')
    currencies = ['EUR', 'USD', 'JPY', 'BRL', 'INR', 'AUD']
    data = {
        currency: np.cumsum(np.random.randn(len(dates)) * 100) for currency in currencies
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df

# Preprocessing function to handle missing values

def preprocess_data(df):
    df = df.fillna(method='ffill')
    return df

# This is the forecasting function using SARIMA
def forecast_currency(df, currency, periods=30):
    model = SARIMAX(df[currency], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    
    results = model.fit(disp=False)
    forecast = results.forecast(steps=periods)
    return forecast

# Fund Allocation Optimization

def optimize_allocation(forecasts):

    total_forecast = sum([abs(forecast.sum()) for forecast in forecasts.values()])
    allocations = {
        currency: abs(forecast.sum()) / total_forecast for currency, forecast in forecasts.items()
    }
    return allocations

# Plot forecasts
def plot_forecasts(original_df, forecasts):
    for currency, forecast in forecasts.items():
        plt.figure(figsize=(10, 4))
        plt.plot(original_df[currency].iloc[-60:], label='Historical')
        plt.plot(pd.date_range(start=original_df.index[-1] + pd.Timedelta(days=1), periods=len(forecast)), forecast, label='Forecast')
        plt.title(f"Cash Flow Forecast - {currency}")
        plt.legend()
        plt.tight_layout()
        plt.show()

# The following is the main function to tie everything together
def main():
    df = load_cashflow_data()
    df = preprocess_data(df)

    forecasts = {}
    for currency in df.columns:
        forecast = forecast_currency(df, currency)
        forecasts[currency] = forecast

    allocations = optimize_allocation(forecasts)

    print("\nOptimized Fund Allocation (Next 30 days):")
    for currency, allocation in allocations.items():
        print(f"{currency}: {allocation * 100:.2f}%")

    # Saves outputs to Excel
    save_to_excel(df, forecasts, allocations)

    plot_forecasts(df, forecasts)
  
def save_to_excel(df, forecasts, allocations, filename='liquidity_forecast_output.xlsx'):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Save historical data
        df.to_excel(writer, sheet_name='Historical_Cashflow')
        
        # This saves forecast data
        forecast_df = pd.DataFrame(forecasts)
        forecast_df.index.name = 'Forecast_Date'
        forecast_df.to_excel(writer, sheet_name='Forecasts')
        
        # This saves allocation summary
        alloc_df = pd.DataFrame.from_dict(allocations, orient='index', columns=['Allocation_Percent'])
        alloc_df['Allocation_Percent'] *= 100
        alloc_df.index.name = 'Currency'
        alloc_df.to_excel(writer, sheet_name='Optimized_Allocation')
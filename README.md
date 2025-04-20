# LiquidityForecasting

This Python-based application provides a liquidity monitoring solution for treasury teams, leveraging time-series forecastingin order to be able to predict cash flow trends and optimize fund allocation sor several currencies.

# Overview

- Enable proactive treasury decisions by forecasting account cash flow across 6 currencies: `EUR`, `USD`, `JPY`, `BRL`, `INR`, and `AUD`.
- Designed for the treasury department to manage multi-currency accounts to improve liquidity planning.

# Methods used

  - Uses `SARIMA` models to forecast 30-day trends per currency
  - Applies a simple fund allocation optimization based on predicted movements
  - Outputs results in a structured Excel file for reporting or integration
 
# Features included

- Time-series forecasting with `SARIMAX`
- Multi-currency support
- Excel export with:
  - Historical cash flow
  - 30-day forecasts
  - Optimized fund allocations
-  Visualization of forecast trends using `matplotlib`


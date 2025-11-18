# Liquidity Forecasting & Fund Allocation Platform

![CI](https://github.com/Andorta/LiquidityForecasting/actions/workflows/ci.yml/badge.svg)

A production-style Python project for forecasting **30-day multi-currency liquidity** and generating **optimal fund allocation** across currencies using SARIMAX time-series models.

Built with:
- **Python**
- **Pandas / NumPy**
- **SARIMAX (statsmodels)**
- **Streamlit (Dashboard)**
- **ExcelWriter for reporting**
- **PyTest (Unit Tests)**
- **GitHub Actions (CI)**
- **Docker (optional)**

---

## 🚀 Project Overview

This project simulates and forecasts daily cashflows for multiple currencies (EUR, USD, JPY, BRL, INR, AUD), then optimizes capital allocation based on predicted liquidity needs.

It includes:

### ✔ Forecasting  
SARIMAX models generate 30-day forecasts for each currency.

### ✔ Fund Allocation  
Allocations computed using forecast magnitudes (probability-like weights).

### ✔ Dashboard  
A Streamlit interface allowing users to:
- view historical data  
- plot future liquidity forecasts  
- export reports  
- view allocation results  

### ✔ Automation Outputs  
Exports:
- Historical data  
- Forecast data  
- Allocation summary  

to Excel using **xlsxwriter**.

---

## 🏗 Project Structure
liquidity-forecasting/
├── liquidity_forecasting/
│ ├── data.py
│ ├── model.py
│ ├── allocation.py
│ ├── export.py
│ ├── plotting.py
│ └── init.py
├── tests/
│ ├── test_data.py
│ ├── test_model_and_allocation.py
├── app.py
├── main.py
├── requirements.txt
└── README.md

---

## ⚙️ Installation

### 1. Clone the repository 

(bash)
git clone https://github.com/Andorta/LiquidityForecasting.git
cd LiquidityForecasting

### 2. Install dependencies
(bash)
python3 -m pip install -r requirements.txt

---

🔄 Continuous Integration

GitHub Actions automatically runs:

dependency installation

test suite (pytest)

Python version matrix (3.9 & 3.11)

Workflow file: .github/workflows/ci.yml

📌 Future Improvements

Add SQL database ingestion

Add Docker image with production-ready Streamlit app

Hyperparameter tuning for SARIMAX

Stress-testing and scenario modelling

👤 Author

Andorta

Feel free to open issues or contribute!


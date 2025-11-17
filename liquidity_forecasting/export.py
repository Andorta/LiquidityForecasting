import pandas as pd

def save_to_excel(df, forecasts, allocations, filename="output.xlsx"):
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Historical")

        f_df = pd.DataFrame(forecasts)
        f_df.index.name = "Forecast_Date"
        f_df.to_excel(writer, sheet_name="Forecasts")

        alloc = pd.DataFrame.from_dict(
            allocations, orient="index", columns=["Allocation"]
        )
        alloc["Allocation"] *= 100
        alloc.to_excel(writer, sheet_name="Allocation")

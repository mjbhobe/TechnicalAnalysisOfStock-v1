"""
data.py - functions to download data from Yahoo! Finance
    at various intervals.

Author: Manish Bhobe
My experiments with Python, ML and Generative AI.
Code is meant for illustration purposes ONLY. Use at your own risk!
Author is not liable for any damages arising from direct/indirect use of this code.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def download_stock_data(symbol: str, end_date: str = None, years: int = 5):

    def __download_data(_symbol: str, _start_date: str, _end_date: str, _interval: str):
        RENAMED_COLS = ["Close", "High", "Low", "Open", "Volume"]
        COLS = ["Open", "High", "Low", "Close", "Volume"]

        df = yf.download(
            _symbol,
            start=_start_date,
            end=_end_date,
            interval=_interval,
            auto_adjust=True,
            progress=False,
        )
        df.columns = RENAMED_COLS
        df = df[COLS]
        return df

    if end_date is None:
        end_dt = datetime.today()
    else:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    start_date = end_dt - timedelta(days=years * 365)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_dt.strftime("%Y-%m-%d")

    # download data at various intervals
    monthly_df = __download_data(symbol, start_date_str, end_date_str, "1mo")
    weekly_df = __download_data(symbol, start_date_str, end_date_str, "1wk")
    daily_df = __download_data(symbol, start_date_str, end_date_str, "1d")

    return monthly_df, weekly_df, daily_df


if __name__ == "__main__":
    from rich import print
    from rich.console import Console

    console = Console()

    monthly, weekly, daily = download_stock_data("RELIANCE.NS")
    console.print("\n[green]Monthly download:[/green]\n")
    print(monthly.head(5))
    print(monthly.tail(5))
    print("--" * 80)
    console.print("\n[green]Weekly download:[/green]\n")
    print(weekly.head(5))
    print(weekly.tail(5))
    print("--" * 80)
    console.print("\n[green]Daily download:[/green]\n")
    print(daily.head(5))
    print(daily.tail(5))
    print("--" * 80)

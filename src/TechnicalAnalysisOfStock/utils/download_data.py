"""
data.py - functions to download data from Yahoo! Finance
    at various intervals.

Author: Manish Bhobe
My experiments with Python, ML and Generative AI.
Code is meant for illustration purposes ONLY. Use at your own risk!
Author is not liable for any damages arising from direct/indirect use of this code.
"""

from typing import Literal
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import utils.technical_indicators as ta


def download_stock_data_and_tai(
    symbol: str,
    start_date: str,
    end_date: str,
):
    # downlods
    df = yf.download(
        symbol,
        start_date,
        end_date,
        progress=False,
        auto_adjust=True,
    )
    RENAMED_COLS = ["Close", "High", "Low", "Open", "Volume"]
    COLS = ["Open", "High", "Low", "Close", "Volume"]

    df.columns = RENAMED_COLS
    df = df[COLS]

    # calculate the indicators
    # EMAs & VWAP
    df["EMA5"] = ta.ema(df["Close"], span=5)
    df["EMA13"] = ta.ema(df["Close"], span=13)
    df["EMA26"] = ta.ema(df["Close"], span=26)
    df["EMA50"] = ta.ema(df["Close"], span=50)
    df["EMA200"] = ta.ema(df["Close"], span=200)
    df["VWAP"] = ta.vwap(df)
    # Bollinger Bands
    sma_line, upper_bb, lower_bb = ta.bollinger_bands(df["Close"])
    df["BB_SMA"] = sma_line
    df["BB_Upper"] = upper_bb
    df["BB_Lower"] = lower_bb
    # MACD & Histogram
    macd_line, signal_line, histogram = ta.macd(df["Close"])
    df["MACD"] = macd_line
    df["MACD_Signal"] = signal_line
    df["MACD_Histo"] = histogram
    # RSI
    df["RSI"] = ta.rsi(df["Close"])
    # Stochastic
    stoch_perc_k, stoch_perc_d = ta.stochastic(df)
    df["Stoch_K"] = stoch_perc_k
    df["Stoch_D"] = stoch_perc_d
    # ADX
    adx_line, adx_plus_di, adx_minus_di = ta.adx(df)
    df["ADX"] = adx_line
    df["ADX_Plus_Di"] = adx_plus_di
    df["ADX_Minus_Di"] = adx_minus_di

    return df


def download_stock_data_and_indicators2(
    symbol: str, end_date: str = None, years: int = 5
):
    """download 3 stock price series for 5 years at daily, weekly and monthly and appends
    following technical indicators to each price series

    """

    def __append_ta_indicators(prices_ohlc: pd.DataFrame):
        # append EMA5, 13, 23, 50, 200
        prices_ohlc["EMA5"] = ta.ema(prices_ohlc["Close"], span=5)
        prices_ohlc["EMA13"] = ta.ema(prices_ohlc["Close"], span=13)
        prices_ohlc["EMA23"] = ta.ema(prices_ohlc["Close"], span=23)
        prices_ohlc["EMA50"] = ta.ema(prices_ohlc["Close"], span=50)
        prices_ohlc["EMA200"] = ta.ema(prices_ohlc["Close"], span=200)
        # append bollinger bands & SMA
        sma_line, upper_bb, lower_bb = ta.bollinger_bands(prices_ohlc["Close"])
        prices_ohlc["BB_SMA"] = sma_line
        prices_ohlc["BB_Upper"] = upper_bb
        prices_ohlc["BB_Lower"] = lower_bb
        # append MACD + signal + histogram
        macd_line, signal_line, histogram = ta.macd(prices_ohlc["Close"])
        prices_ohlc["MACD"] = macd_line
        prices_ohlc["MACD_Signal"] = signal_line
        prices_ohlc["MACD_Histo"] = histogram
        # append RSI
        prices_ohlc["RSI"] = ta.rsi(prices_ohlc["Close"])
        # append Stochastic
        stoch_perc_k, stoch_perc_d = ta.stochastic(prices_ohlc)
        prices_ohlc["Stoch_K"] = stoch_perc_k
        prices_ohlc["Stoch_D"] = stoch_perc_d
        # append ADX
        adx_line, adx_plus_di, adx_minus_di = ta.adx(prices_ohlc)
        prices_ohlc["ADX"] = adx_line
        prices_ohlc["ADX_Plus_Di"] = adx_plus_di
        prices_ohlc["ADX_Minus_Di"] = adx_minus_di

    monthly_df, weekly_df, daily_df = download_stock_data(symbol, end_date, years)
    __append_ta_indicators(monthly_df)
    __append_ta_indicators(weekly_df)
    __append_ta_indicators(daily_df)
    return monthly_df, weekly_df, daily_df


if __name__ == "__main__":
    from rich import print
    from rich.console import Console

    console = Console()

    monthly, weekly, daily = download_stock_data_and_indicators("RELIANCE.NS")
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

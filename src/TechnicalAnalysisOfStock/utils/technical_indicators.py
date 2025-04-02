"""
technical_indicators.py - functions to calculate various technical indicators
    such as EMA, bollinger bands, ADX etc.

Author: Manish Bhobe
My experiments with Python, ML and Generative AI.
Code is meant for illustration purposes ONLY. Use at your own risk!
Author is not liable for any damages arising from direct/indirect use of this code.
"""

import pandas as pd
from typing import Tuple


def ema(prices: pd.Series, span: int = 5) -> pd.Series:
    """calculate exponential moving average for a prices series

    Args:
       prices (pd.Series) - pandas series (usually closing prices)
       span (int) [optional, default=5] - the span for which EMA is desired

    Returns:
       calculated ema for span as a pd.Series object
    """
    return prices.ewm(span=span, adjust=False).mean()


def sma(prices: pd.Series, window: int = 50) -> pd.Series:
    """calculate simple moving average for a prices series

    Args:
       prices (pd.Series) - pandas series (usually closing prices)
       window (int) [optional, default=50] - the window for which SMA is desired
    """
    return prices.rolling(window=window).mean()


def vwap(prices: pd.DataFrame) -> pd.Series:
    vwap_values = (prices["Close"] * prices["Volume"]).cumsum() / prices[
        "Volume"
    ].cumsum()
    return vwap_values


def bollinger_bands(
    prices: pd.Series, window: int = 20, num_std: int = 2
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """calculate sma & upper + lower bollinger bands for a prices series

    Args:
        prices (pd.Series) - pandas series (usually closing prices)
        window (int) [optional, default=20] - window for calculating rolling mean for SMA line
        num_std (int) [optional, default=2] - # of standard deviations from SMA line to determine upper
            & lower bollinger bands

    Returns:
        a tuple of 3 pd.Series = (sma line, upper bollinger band, lower bollinger band)
    """

    sma_line = prices.rolling(window).mean()
    std = prices.rolling(window).std()

    upper_band = sma_line + (num_std * std)
    lower_band = sma_line - (num_std * std)

    return sma_line, upper_band, lower_band


def macd(
    prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """calculate sma & upper + lower bollinger bands for a prices series

    Args:
        prices (pd.Series) - pandas series (usually closing prices)
        fast (int) [optional, default=12] - short-term EMA that reacts quickly to price changes.
            It's more sensitive and follows price closely.
        slow (int) [optional, default=26] - longer-term EMA that reacts slower to price changes.
            Smooths out the price trend.
        signal (int) [optional, default=9] - EMA period of the macd line itself.

        The MACD line is calculated as fast EMA - slow EMA
        When MACD line crosses above signal line -> trend is usually bullish
        When MACD line crosses below signal line -> trend is usually bearish

    Returns:
        a tuple of 3 pd.Series = (macd, signal line and histogram)
        histogram is calculated ad macd - signal line
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """calculate RSI on a prices series for a given period
    The RSI (Relative Strength Index) is a classic momentum oscillator that tells you
    whether a stock is overbought, oversold, or trending strongly.

    Args:
        prices (pd.Series) - pandas series (usually closing prices)
        period (int) [optional, default = 14] - is the number of past time intervals
            (e.g., days, hours, minutes) used to average gains and losses.
            If prices is a weekly series and periods = 14, it means 14 weeks
            Similarly for a daily prices series, period = 14 means 14 days.

        Short term traders usually use period = 5 or 9 and long term traders use period=14

    Returns:
        The RSI line (a pd.Series object)
        NOTE: when plotting RAI, we also plot the upper & lower threshold values. If RSI falls
        above upper threshold, it indicates stock is overbought and if it falls below lower threshold
        it usually means stock is oversold. These threshold are fixed values, usally (70,30) or (80, 20)
    """

    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    # NOTE: RSI line is normalized between 0-100
    rsi_line = 100 - (100 / (1 + rs))

    return rsi_line


def stochastic(prices_ohlc: pd.DataFrame, k_window: int = 14, d_window: int = 3):
    """
    The Stochastic Oscillator is a popular momentum indicator that compares a
    stock’s closing price to its price range over a given period.
        - It measures where the current closing price is relative to
          the high-low range over a certain number of periods.
        - It helps identify overbought and oversold conditions, and possible reversals.

    Args:
        prices_ohlc (pd.DataFrame) [NOT pd.Series] - the OHLC prices dataframe
        k_window (int) [optional, default = 14]
        d_window (int) [optional, default = 3]

    """
    assert (
        "Open" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Open' prices column!"
    assert (
        "High" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'High' prices column!"
    assert (
        "Low" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Low' prices column!"
    assert (
        "Close" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Close' column!"

    low_min = prices_ohlc["Low"].rolling(window=k_window).min()
    high_max = prices_ohlc["High"].rolling(window=k_window).max()

    percent_k = 100 * (prices_ohlc["Close"] - low_min) / (high_max - low_min)
    percent_d = percent_k.rolling(window=d_window).mean()

    return percent_k, percent_d


def adx(prices_ohlc: pd.DataFrame, period: int = 14):
    """
    Calculate the Directional Movement Index (DMI) and ADX for a given DataFrame.
    It helps traders determine if a trend exists and direction & strength of trend.
        - If +DI > -DI - uptrend
        - If +DI < -DI - downtrend
        - If ADX is rising (> 20-25), trend is gaining strength
        - If ADX < 20, weak or no trend

    Args:
        df (pd.DataFrame) - the OHLC prices dataframe
        period (int) [optional, default 14] - the lookback period

    Returns:
        Tuple of pd.Series objects = (ADX line, +DI line and -DI line)
    """

    assert (
        "Open" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Open' prices column!"
    assert (
        "High" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'High' prices column!"
    assert (
        "Low" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Low' prices column!"
    assert (
        "Close" in prices_ohlc.columns
    ), "FATAL: prices dataframe does not have a 'Close' column!"

    high = prices_ohlc["High"]
    low = prices_ohlc["Low"]
    close = prices_ohlc["Close"]

    plus_dm = high.diff()
    minus_dm = low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift()))
    tr3 = pd.DataFrame(abs(low - close.shift()))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = abs(100 * (minus_dm.rolling(window=period).mean() / atr))

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx_line = dx.rolling(window=period).mean()

    return adx_line, plus_di, minus_di

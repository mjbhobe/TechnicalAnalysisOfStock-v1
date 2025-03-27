"""
indicators.py - functions to calculate various technical indicators
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

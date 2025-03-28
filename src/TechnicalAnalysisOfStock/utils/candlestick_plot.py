"""
candlestick_plot.py - creates a plotly candlestick plot with indicators
    as chosen by the user.

Author: Manish Bhobé

My experiments with Python, ML and Generative AI.
Code is meant for illustration purposes ONLY. Use at your own risk!
Author is not liable for any damages arising from direct/indirect use of this code.
"""
from typing import List, Optional
import pandas as pd

import plotly.graph_objs as go
from plotly.subplots import make_subplots


def plot_technical_chart(
    symbol: str,
    df : pd.DataFrame,
    ema_lines : Optional[List[int]] = [5, 13, 26, 50, 200],
    show_bollinger_bands : bool = True,
    show_macd : bool = False,
    show_stochastic : bool = False,
    show_rsi : bool = False,
    show_adx : bool = False,
):
    """
    Plot the technical chart with the given data and indicators.
    Plot is divided into 5 subplots as folows:
        - Candle stick plot showing OHLC (and optionally EMA lines + Bollinger Bands) [OHLC Always shown]
        - MACD plot (optional) - will show MACD, Signal Line and Histogram
        - RSI plot (optional) - will show RSI line and overbought/oversold lines
        - DMI plot (optional) - will show the ADX line, +DI and -DI

    Args:
        symbol (str) - stock symbol fo
        df (pd.DataFrame) - the stock prices + indicators dataframe
        ema_lines (List[int] | None) - list of EMA lines to show None (to not show any EMA lines)
            default value = [5, 13, 26, 50, 200], but you can pass a sublist with any of these values
        show_bollinger_bands (bool) - whether to show bollinger bands or not (default=True)
        show_macd (bool) - whether to show MACD or not (default=True)
    """
    
    allowed_ema_values = {5, 13, 26, 50, 200}
    if ema_lines is not None:
        if not set(ema_lines).issubset(allowed_ema_values):
            raise ValueError(f"ema_lines must be a subset of {allowed_ema_values}")

    # build subplot titles
    subplot_titles = ["Candlestick Plot"]
    if show_macd: subplot_titles.append("MACD")
    if show_stochastic: subplot_titles.append("Stochastic")
    if show_rsi: subplot_titles.append("RSI")
    if show_adx: subplot_titles.append("DMI")
    
    row_heights = [
        [1.0],                  # if only candlestick shown
        [0.7, 0.3],             # for 2 subplots (candlestick + any 1 of MACD, Stoch, RSI, DMI)
        [0.6, 0.2, 0.2],        # for 3 subplots (candlestick + any 2 of MACD, Stoch, RSI, DMI)
        [0.5, 0.2, 0.2, 0.1],   # for 4 subplots (candlestick + any 3 of MACD, Stoch, RSI, DMI)
        [0.4, 0.2, 0.2, 0.1, 0.1],   # for 5 subplots (candlestick + all of of MACD, Stoch, RSI, DMI)
    ]
    num_rows = len(subplot_titles)

    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights[num_rows - 1],
        subplot_titles=tuple(subplot_titles),
    )

    # Candlestick 
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlesticks",
        ),
        row=1,
        col=1,
    )

    if ema_lines is not None:
        # overlay EMA lines on candlestick
        ema_colors = {
            "EMA5"  : "green",
            "EMA13" : "blue",
            "EMA26" : "gray",
            "EMA50" : "magenta",
            "EMA200": "purple",
        }

        for value in ema_lines:
            ema_name = f"EMA{value}"
            ema_color = ema_colors[ema_name]
            ema_width = 4 if ema_name in ["EMA50", "EMA200"] else 2

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[ema_name],
                    mode="lines",
                    name=ema_name,
                    line=dict(color=ema_color, width=ema_width),
                ),
                row=1,
                col=1,
            )

    if show_bollinger_bands:
        # overlay Bollinger bands on candlestick chart
        # BB SMA line
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df["BB_SMA"], 
                name="", 
                line=dict(color="red")
            ),
            row=1,
            col=1,
        )
        # 1. Add shaded area between upper and lower band
        fig.add_trace(go.Scatter(
            x=df.index.tolist() + df.index[::-1].tolist(),  # upper x then reversed lower x
            y=df["BB_Upper"].tolist() + df["BB_Lower"][::-1].tolist(),  # upper y then reversed lower y
            fill='toself',
            fillcolor='rgba(0, 255, 255, 0.3)',  # cyan with 30% opacity
            line=dict(color='rgba(255,255,255,0)'),  # invisible border line
            hoverinfo="skip",
            showlegend=False,
            name=""
        ))
        # BB Upper band
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"], 
                mode="lines",
                name="",
                line=dict(color="cyan"),
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        # Lower BB Band
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Lower"], 
                mode="lines",
                name="",
                line=dict(color="cyan"),
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    """
    # ADX
    fig.add_trace(
        go.Scatter(x=df.index, y=adx, name="ADX", line=dict(color="orange")),
        row=1,
        col=1,
    )





    # MACD + Signal + Histogram
    fig.add_trace(
        go.Scatter(
            x=df.index, y=macd_dict["macd"], name="MACD", line=dict(color="blue")
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd_dict["signal"],
            name="Signal Line",
            line=dict(color="orange"),
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=df.index, y=macd_dict["hist"], name="Histogram", marker_color="gray"),
        row=3,
        col=1,
    )

    # Stochastic Oscillator
    fig.add_trace(
        go.Scatter(
            x=df.index, y=stochastic_dict["%K"], name="%K", line=dict(color="green")
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=stochastic_dict["%D"], name="%D", line=dict(color="purple")
        ),
        row=4,
        col=1,
    )

    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=rsi, name="RSI", line=dict(color="blue")), row=5, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=[70] * len(df),
            name="Overbought (70)",
            line=dict(color="red", dash="dash"),
        ),
        row=5,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=[30] * len(df),
            name="Oversold (30)",
            line=dict(color="green", dash="dash"),
        ),
        row=5,
        col=1,
    )
    """

    # show the last 30 periods to begin with
    if len(df.index) > 30:
        start_idx = df.index[-30]
        end_idx = df.index[-1]

        fig.update_layout(
            height=1000, 
            xaxis=dict(
                range=[start_idx, end_idx],
                fixedrange=False,  # allow zoom/pan
            ),
            title=f"Plot for {symbol}", 
            showlegend=True, 
            xaxis_rangeslider_visible=True,   # make scrollable
        )
    return fig

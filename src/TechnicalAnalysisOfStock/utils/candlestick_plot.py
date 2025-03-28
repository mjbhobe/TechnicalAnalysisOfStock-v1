"""
candlestick_plot.py - creates a plotly candlestick plot with indicators
    as chosen by the user.

Author: Manish Bhobé

My experiments with Python, ML and Generative AI.
Code is meant for illustration purposes ONLY. Use at your own risk!
Author is not liable for any damages arising from direct/indirect use of this code.
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots


def plot_technical_chart(
    df, ema_dict, bollinger_dict, macd_dict, stochastic_dict, rsi, adx, title="Chart"
):
    """
    Plot the technical chart with the given data and indicators.
    Plot is divided into 5 subplots as folows:
        - Candle stick plot showing OHLC (and optionally EMA lines + Bollinger Bands) [Always shown]
        - MACD plot (optional) - will show MACD, Signal Line and Histogram
        - RSI plot (optional) - will show RSI line and overbought/oversold lines
        - DMI plot (optional) - will show the ADX line, +DI and -DI

    Args:
        df (pd.DataFrame) - the stock prices + indicators dataframe
        ema_lines (List[int] | None) - list of EMA lines to show None (to not show any EMA lines)
            default value = [5, 13, 26, 50, 200], but you can pass a sublist with any of these values
        bollinger_bands (bool) - whether to show bollinger bands or not (default=True)
        macd (bool) - whether to show MACD or not (default=True)
    """
    fig = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.1, 0.5, 0.2, 0.1, 0.1],
        subplot_titles=(
            "ADX",
            "Price with EMAs & Bollinger Bands",
            "MACD",
            "Stochastic Oscillator",
            "RSI",
        ),
    )

    # ADX
    fig.add_trace(
        go.Scatter(x=df.index, y=adx, name="ADX", line=dict(color="orange")),
        row=1,
        col=1,
    )

    # Candlestick + EMAs + Bollinger
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlesticks",
        ),
        row=2,
        col=1,
    )

    for name, ema in ema_dict.items():
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=ema,
                mode="lines",
                name=f"EMA {name}",
                line=ema_dict[name]["style"],
            ),
            row=2,
            col=1,
        )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=df.index, y=bollinger_dict["sma"], name="SMA 20", line=dict(color="red")
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=bollinger_dict["upper"],
            name="Upper Band",
            line=dict(color="cyan"),
            opacity=0.5,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=bollinger_dict["lower"],
            name="Lower Band",
            line=dict(color="cyan"),
            fill="tonexty",
            opacity=0.2,
        ),
        row=2,
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

    fig.update_layout(
        height=1000, title=title, showlegend=True, xaxis_rangeslider_visible=False
    )
    return fig

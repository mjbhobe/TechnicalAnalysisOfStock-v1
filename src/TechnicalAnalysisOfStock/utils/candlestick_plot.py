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

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_technical_chart(
    symbol: str,
    df: pd.DataFrame,
    ema_lines: Optional[List[int]] = [5, 13, 26, 50, 200],
    show_bollinger_bands: bool = True,
    show_macd: bool = False,
    show_stochastic: bool = False,
    show_rsi: bool = False,
    show_adx: bool = False,
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
    if show_macd:
        subplot_titles.append("MACD")
    if show_stochastic:
        subplot_titles.append("Stochastic")
    if show_rsi:
        subplot_titles.append("RSI")
    if show_adx:
        subplot_titles.append("DMI")

    row_heights = [
        [1.0],  # if only candlestick shown
        [0.7, 0.3],  # for 2 subplots (candlestick + any 1 of MACD, Stoch, RSI, DMI)
        [
            0.6,
            0.2,
            0.2,
        ],  # for 3 subplots (candlestick + any 2 of MACD, Stoch, RSI, DMI)
        [
            0.5,
            0.2,
            0.2,
            0.1,
        ],  # for 4 subplots (candlestick + any 3 of MACD, Stoch, RSI, DMI)
        [
            0.4,
            0.2,
            0.2,
            0.1,
            0.1,
        ],  # for 5 subplots (candlestick + all of of MACD, Stoch, RSI, DMI)
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
            "EMA5": "green",
            "EMA13": "blue",
            "EMA26": "gray",
            "EMA50": "magenta",
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
            go.Scatter(x=df.index, y=df["BB_SMA"], name="", line=dict(color="red")),
            row=1,
            col=1,
        )
        # 1. Add shaded area between upper and lower band
        fig.add_trace(
            go.Scatter(
                x=df.index.tolist()
                + df.index[::-1].tolist(),  # upper x then reversed lower x
                y=df["BB_Upper"].tolist()
                + df["BB_Lower"][::-1].tolist(),  # upper y then reversed lower y
                fill="toself",
                fillcolor="rgba(0, 255, 255, 0.3)",  # cyan with 30% opacity
                line=dict(color="rgba(255,255,255,0)"),  # invisible border line
                hoverinfo="skip",
                showlegend=False,
                name="",
            )
        )
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
    if len(df.index) > 20:
        start_idx = df.index[-20]
        end_idx = df.index[-1]

        fig.update_layout(
            height=1000,
            xaxis=dict(
                range=[start_idx, end_idx],
                fixedrange=False,  # allow zoom/pan
            ),
            title=f"Plot for {symbol}",
            showlegend=True,
            xaxis_rangeslider_visible=True,  # make scrollable
        )
    return fig


def plot_full_technical_chart_plotly(df, symbol="TCS.NS"):
    """
    Generate a clean, professional technical analysis chart using Plotly.
    - Fixes overlapping zoom slider
    - Shows all subplots without gaps
    - Minimizes zoom slider height
    - Removes unnecessary whitespace
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.002,  # reduce space between rows
        # row_heights=[0.08, 0.42, 0.15, 0.12, 0.12, 0.11],
        row_heights=[0.70, 0.30],
        subplot_titles=[
            # "ADX (+DI, -DI)",
            f"{symbol} OHLC + EMAs + Bollinger Bands",
            # "MACD",
            # "Stochastic Oscillator",
            # "RSI",
            "Volume",
        ],
    )

    # # ADX
    # fig.add_trace(
    #     go.Scatter(x=df.index, y=df["ADX"], name="ADX", line=dict(color="black")),
    #     row=1,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df.index, y=df["ADX_Plus_Di"], name="+DI", line=dict(color="green")
    #     ),
    #     row=1,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df.index, y=df["ADX_Minus_Di"], name="-DI", line=dict(color="red")
    #     ),
    #     row=1,
    #     col=1,
    # )

    # Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick",
            increasing_line_color="rgb(49,130,117)",
            decreasing_line_color="rgb(242,54,69)",
        ),
        row=1,
        col=1,
    )

    # EMAs
    ema_colors = {
        "EMA5": "green",
        "EMA13": "blue",
        "EMA26": "gray",
        "EMA50": "pink",
        "EMA200": "purple",
    }
    line_widths = {"EMA5": 1, "EMA13": 1, "EMA26": 1, "EMA50": 2.5, "EMA200": 3}
    for ema in ema_colors:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[ema],
                name=ema,
                line=dict(color=ema_colors[ema], width=line_widths[ema]),
            ),
            row=1,
            col=1,
        )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Upper"],
            name="Upper Band",
            line=dict(color="rgb(12,50,153)", width=1),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Lower"],
            name="Lower Band",
            line=dict(color="rgb(12,50,153)", width=1),
            fill="tonexty",
            fillcolor="rgba(12,50,153,0.15)",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_SMA"],
            name="Bollinger SMA",
            line=dict(color="red", width=1),
        ),
        row=1,
        col=1,
    )

    # # MACD
    # fig.add_trace(
    #     go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="blue")),
    #     row=3,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df.index, y=df["MACD_Signal"], name="Signal", line=dict(color="orange")
    #     ),
    #     row=3,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Bar(
    #         x=df.index,
    #         y=df["MACD_Histo"],
    #         name="MACD Histogram",
    #         marker_color="gray",
    #     ),
    #     row=3,
    #     col=1,
    # )

    # # Stochastic
    # fig.add_trace(
    #     go.Scatter(x=df.index, y=df["Stoch_K"], name="%K", line=dict(color="blue")),
    #     row=4,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Scatter(x=df.index, y=df["Stoch_D"], name="%D", line=dict(color="red")),
    #     row=4,
    #     col=1,
    # )
    # fig.add_shape(
    #     type="rect",
    #     x0=df.index[0],
    #     x1=df.index[-1],
    #     y0=20,
    #     y1=80,
    #     xref="x4",
    #     yref="y4",
    #     fillcolor="pink",
    #     opacity=0.2,
    #     layer="below",
    #     line_width=0,
    # )

    # # RSI
    # fig.add_trace(
    #     go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="purple")),
    #     row=5,
    #     col=1,
    # )
    # fig.add_shape(
    #     type="rect",
    #     x0=df.index[0],
    #     x1=df.index[-1],
    #     y0=30,
    #     y1=60,
    #     xref="x5",
    #     yref="y5",
    #     fillcolor="pink",
    #     opacity=0.2,
    #     layer="below",
    #     line_width=0,
    # )
    # fig.add_shape(
    #     type="line",
    #     x0=df.index[0],
    #     x1=df.index[-1],
    #     y0=40,
    #     y1=40,
    #     xref="x5",
    #     yref="y5",
    #     line=dict(color="black", dash="dash"),
    # )

    # Volume
    volume_colors = [
        (
            "rgba(49,130,117,0.35)"
            if df["Close"].iloc[i] >= df["Open"].iloc[i]
            else "rgba(242,54,69,0.35)"
        )
        for i in range(len(df))
    ]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color=volume_colors,
            opacity=1,
        ),
        row=2,
        col=1,
    )

    # Configure layout
    fig.update_layout(
        title=f"{symbol} - Full Technical Chart",
        height=1000,
        margin=dict(t=40, b=30, l=20, r=20),
        xaxis_rangeslider=dict(visible=True, thickness=0.03),  # slim slider
        showlegend=True,
    )

    # @see:
    fig.update_xaxes(rangeslider_thickness=0.1)

    return fig


# Re-run after code execution environment was reset


def plot_tradingview_style_chart(
    df: pd.DataFrame,
    symbol: str = "TCS.NS",
    indicators: List[str] = ["ohlc"],
):
    """
    Generate a TradingView-style plotly chart:
    - Scrollable X-axis with auto-rescaling Y-axis
    - Optional technical indicators as overlays or subplots
    - White background and custom color styling
    """
    if indicators is None:
        indicators = []

    show_volume = "volume" in indicators
    show_macd = "macd" in indicators
    show_stoch = "stochastic" in indicators
    show_rsi = "rsi" in indicators
    show_adx = "adx" in indicators

    # Map subplot order
    plot_rows = ["adx", "ohlc", "macd", "stochastic", "rsi"]
    active_rows = [
        row
        for row in plot_rows
        if (
            (row == "adx" and show_adx)
            or (row == "macd" and show_macd)
            or (row == "stochastic" and show_stoch)
            or (row == "rsi" and show_rsi)
            or row == "ohlc"
        )
    ]

    row_map = {name: i + 1 for i, name in enumerate(active_rows)}
    row_heights = {
        "adx": 0.1,
        "ohlc": 0.45,
        "macd": 0.15,
        "stochastic": 0.15,
        "rsi": 0.15,
    }

    subplot_heights = [row_heights[name] for name in active_rows]

    fig = make_subplots(
        rows=len(active_rows),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.005,
        row_heights=subplot_heights,
        subplot_titles=[f"{symbol} - {row.upper()}" for row in active_rows],
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="rgb(49,130,117)",
            decreasing_line_color="rgb(242,54,69)",
            name="Candlestick",
        ),
        row=row_map["ohlc"],
        col=1,
    )

    # EMAs
    ema_colors = {
        "EMA5": "green",
        "EMA13": "blue",
        "EMA26": "gray",
        "EMA50": "pink",
        "EMA200": "purple",
    }
    for ema, color in ema_colors.items():
        if ema.lower() in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[ema.upper()],
                    name=ema,
                    line=dict(
                        color=color, width=4 if ema in ["EMA50", "EMA200"] else 2
                    ),
                ),
                row=row_map["ohlc"],
                col=1,
            )

    # Bollinger Bands
    if "bollinger" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"],
                name="Upper Band",
                line=dict(color="rgb(12,50,153)", width=2),
            ),
            row=row_map["ohlc"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Lower"],
                name="Lower Band",
                line=dict(color="rgb(12,50,153)", width=2),
                fill="tonexty",
                fillcolor="rgba(12,50,153,0.20)",
            ),
            row=row_map["ohlc"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_SMA"],
                name="Bollinger SMA",
                line=dict(color="red", width=1),
            ),
            row=row_map["ohlc"],
            col=1,
        )

    # Volume
    if show_volume:
        volume_colors = [
            (
                "rgba(49,130,117,0.35)"
                if df["Close"].iloc[i] >= df["Open"].iloc[i]
                else "rgba(242,54,69,0.35)"
            )
            for i in range(len(df))
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                marker_color=volume_colors,
                opacity=1,
            ),
            row=row_map["ohlc"],
            col=1,
        )

    # ADX
    if show_adx:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["ADX"], name="ADX", line=dict(color="black")),
            row=row_map["adx"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["ADX_Plus_Di"], name="+DI", line=dict(color="green")
            ),
            row=row_map["adx"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["ADX_Minus_Di"], name="-DI", line=dict(color="red")
            ),
            row=row_map["adx"],
            col=1,
        )

    # MACD
    if show_macd:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="blue")),
            row=row_map["macd"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD_Signal"],
                name="Signal",
                line=dict(color="orange"),
            ),
            row=row_map["macd"],
            col=1,
        )
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["MACD_Histo"],
                name="MACD Histogram",
                marker_color="gray",
            ),
            row=row_map["macd"],
            col=1,
        )

    # Stochastic
    if show_stoch:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stoch_K"],
                name="%K",
                line=dict(color="blue"),
            ),
            row=row_map["stochastic"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stoch_D"],
                name="%D",
                line=dict(color="red"),
            ),
            row=row_map["stochastic"],
            col=1,
        )
        fig.add_shape(
            type="rect",
            x0=df.index[0],
            x1=df.index[-1],
            y0=20,
            y1=80,
            xref=f'x{row_map["stochastic"]}',
            yref=f'y{row_map["stochastic"]}',
            fillcolor="pink",
            opacity=0.2,
            layer="below",
            line_width=0,
        )

    # RSI
    if show_rsi:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="purple")),
            row=row_map["rsi"],
            col=1,
        )
        fig.add_shape(
            type="rect",
            x0=df.index[0],
            x1=df.index[-1],
            y0=30,
            y1=60,
            xref=f'x{row_map["rsi"]}',
            yref=f'y{row_map["rsi"]}',
            fillcolor="pink",
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        fig.add_shape(
            type="line",
            x0=df.index[0],
            x1=df.index[-1],
            y0=40,
            y1=40,
            xref=f'x{row_map["rsi"]}',
            yref=f'y{row_map["rsi"]}',
            line=dict(color="black", dash="dash"),
        )

    # Layout
    fig.update_layout(
        height=1000,
        margin=dict(t=40, b=30, l=40, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(240,240,240)",
            layer="below traces",
            rangeslider=dict(visible=True, thickness=0.03),
            rangeselector=dict(
                buttons=[
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(step="all"),
                ]
            ),
            type="date",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(240,240,240)",
            layer="below traces",
            autorange=True,
        ),
        showlegend=True,
    )

    return fig

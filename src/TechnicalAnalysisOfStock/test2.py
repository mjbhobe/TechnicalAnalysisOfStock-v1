import streamlit as st
import pandas as pd


def technical_chart_app(df, symbol="TCS.NS"):
    """
    Streamlit App for displaying a fully interactive technical analysis chart.
    Features:
    - Toggle indicators
    - Show/hide overlays
    - Export as PNG
    - Tabs for future multi-symbol support
    """
    st.set_page_config(layout="wide")
    st.title(f"{symbol} - Interactive Technical Chart")

    # Sidebar controls
    st.sidebar.header("Chart Settings")

    show_ema = st.sidebar.multiselect(
        "Show EMAs",
        options=["EMA5", "EMA13", "EMA26", "EMA50", "EMA200"],
        default=["EMA5", "EMA13", "EMA26", "EMA50", "EMA200"],
    )

    show_indicators = st.sidebar.multiselect(
        "Show Technical Indicators",
        options=["ADX", "MACD", "Stochastic", "RSI", "Volume", "Bollinger Bands"],
        default=["ADX", "MACD", "Stochastic", "RSI", "Volume", "Bollinger Bands"],
    )

    download_png = st.sidebar.button("📷 Export Chart as PNG")

    # Dynamic plot construction
    fig = generate_dynamic_plot(df, symbol, show_ema, show_indicators)

    # Show chart
    st.plotly_chart(fig, use_container_width=True)

    # PNG Export
    if download_png:
        fig.write_image("technical_chart.png", format="png", width=1600, height=950)
        with open("technical_chart.png", "rb") as file:
            st.download_button(
                label="Download Chart as PNG",
                data=file,
                file_name=f"{symbol}_technical_chart.png",
                mime="image/png",
            )


def generate_dynamic_plot(df, symbol, show_ema, show_indicators):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    include_adx = "ADX" in show_indicators
    include_macd = "MACD" in show_indicators
    include_stochastic = "Stochastic" in show_indicators
    include_rsi = "RSI" in show_indicators
    include_volume = "Volume" in show_indicators
    include_bollinger = "Bollinger Bands" in show_indicators

    rows = sum(
        [include_adx, 1, include_macd, include_stochastic, include_rsi, include_volume]
    )
    row_heights = []
    subplot_titles = []
    row_index = 1
    row_map = {}

    if include_adx:
        row_map["adx"] = row_index
        row_heights.append(0.08)
        subplot_titles.append("ADX (+DI, -DI)")
        row_index += 1

    row_map["price"] = row_index
    row_heights.append(0.42)
    subplot_titles.append(f"{symbol} OHLC + EMAs + Bollinger Bands")
    row_index += 1

    if include_macd:
        row_map["macd"] = row_index
        row_heights.append(0.14)
        subplot_titles.append("MACD")
        row_index += 1

    if include_stochastic:
        row_map["stoch"] = row_index
        row_heights.append(0.12)
        subplot_titles.append("Stochastic Oscillator")
        row_index += 1

    if include_rsi:
        row_map["rsi"] = row_index
        row_heights.append(0.12)
        subplot_titles.append("RSI")
        row_index += 1

    if include_volume:
        row_map["volume"] = row_index
        row_heights.append(0.12)
        subplot_titles.append("Volume")
        row_index += 1

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.005,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    # ADX
    if include_adx:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["DMI"], name="ADX", line=dict(color="black")),
            row=row_map["adx"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["DMI_Plus_D"], name="+DI", line=dict(color="green")
            ),
            row=row_map["adx"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["DMI_Minus_D"], name="-DI", line=dict(color="red")
            ),
            row=row_map["adx"],
            col=1,
        )

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
        row=row_map["price"],
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
    for ema in show_ema:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[ema],
                name=ema,
                line=dict(color=ema_colors[ema], width=line_widths[ema]),
            ),
            row=row_map["price"],
            col=1,
        )

    if include_bollinger:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Bollinger_Upper_Band"],
                name="Upper Band",
                line=dict(color="rgb(12,50,153)", width=1),
            ),
            row=row_map["price"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Bollinger_Lower_Band"],
                name="Lower Band",
                line=dict(color="rgb(12,50,153)", width=1),
                fill="tonexty",
                fillcolor="rgba(12,50,153,0.65)",
            ),
            row=row_map["price"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Bollinger_Signal_Line"],
                name="Bollinger SMA",
                line=dict(color="red", width=1),
            ),
            row=row_map["price"],
            col=1,
        )

    # MACD
    if include_macd:
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
                y=df["MACD_Histogram"],
                name="MACD Histogram",
                marker_color="gray",
            ),
            row=row_map["macd"],
            col=1,
        )

    # Stochastic
    if include_stochastic:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stochastic_Percent_K"],
                name="%K",
                line=dict(color="blue"),
            ),
            row=row_map["stoch"],
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stochastic_Percent_D"],
                name="%D",
                line=dict(color="red"),
            ),
            row=row_map["stoch"],
            col=1,
        )
        fig.add_shape(
            type="rect",
            x0=df.index[0],
            x1=df.index[-1],
            y0=20,
            y1=80,
            xref=f'x{row_map["stoch"]}',
            yref=f'y{row_map["stoch"]}',
            fillcolor="pink",
            opacity=0.2,
            layer="below",
            line_width=0,
        )

    # RSI
    if include_rsi:
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

    # Volume
    if include_volume:
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
            row=row_map["volume"],
            col=1,
        )

    fig.update_layout(
        height=950,
        margin=dict(t=40, b=30, l=20, r=20),
        xaxis_rangeslider=dict(visible=True, thickness=0.03),
        showlegend=True,
    )

    return fig

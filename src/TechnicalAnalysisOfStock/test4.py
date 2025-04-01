import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from io import BytesIO
from PIL import Image
import google.generativeai as genai
import os

from utils.download_data import download_stock_data_and_tai

# Configure Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


# Function to validate stock symbol
def validate_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if info and info["regularMarketPrice"]:
            return True, info["shortName"]
        else:
            return False, "Invalid symbol or no data found."
    except Exception as e:
        return False, f"An error occurred: {e}"


# Function to fetch stock data
def fetch_stock_data(symbol, periods):
    data = {}
    for period in periods:
        data[period] = download_stock_data_and_tai(symbol, period)
        # if period == "Daily":
        #     df = yf.download(symbol, period="1d")
        # elif period == "Monthly":
        #     df = yf.download(symbol, period="1mo")
        # elif period == "Yearly":
        #     df = yf.download(symbol, period="1y")
        # else:
        #     continue
        # data[period] = df
    return data


# Function to plot the chart
def plot_stock_chart(df, symbol, indicators):
    fig = go.Figure()

    # OHLC + EMAs + Bollinger Bands + Volume (Row 1)
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            yaxis="y1",
        )
    )
    if "EMA5" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA5"],
                mode="lines",
                name="EMA 5",
                line=dict(color="green"),
                yaxis="y1",
            )
        )
    if "EMA13" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA13"],
                mode="lines",
                name="EMA 13",
                line=dict(color="blue"),
                yaxis="y1",
            )
        )
    if "EMA26" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA26"],
                mode="lines",
                name="EMA 26",
                line=dict(color="gray"),
                yaxis="y1",
            )
        )
    if "EMA50" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                mode="lines",
                name="EMA 50",
                line=dict(color="pink", width=2),
                yaxis="y1",
            )
        )
    if "EMA200" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA200"],
                mode="lines",
                name="EMA 200",
                line=dict(color="purple", width=2),
                yaxis="y1",
            )
        )
    if "Bollinger Bands" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"],
                mode="lines",
                name="Bollinger Upper",
                line=dict(color="rgb(12, 50, 153)"),
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Lower"],
                mode="lines",
                name="Bollinger Lower",
                line=dict(color="rgb(12, 50, 153)"),
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_SMA"],
                mode="lines",
                name="Bollinger SMA",
                line=dict(color="red"),
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BB_Upper"],
                fill="tonexty",
                fillcolor="rgba(12, 50, 153, 0.35)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                yaxis="y1",
            )
        )
    if "Volume" in indicators:
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                yaxis="y2",
                marker_color=[
                    "rgb(49, 130, 117)" if v >= 0 else "rgb(242, 54, 69)"
                    for v in df["Volume"].diff().fillna(0)
                ],
                opacity=0.35,
            )
        )

    # MACD (Row 2)
    if "MACD" in indicators:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD", yaxis="y3")
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD_Signal"],
                mode="lines",
                name="MACD Signal",
                yaxis="y3",
            )
        )
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["MACD_Histo"],
                name="MACD Histogram",
                yaxis="y3",
                marker_color=["green" if v >= 0 else "red" for v in df["MACD_Histo"]],
            )
        )

    # RSI (Row 3)
    if "RSI" in indicators:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI", yaxis="y4")
        )
        fig.add_shape(
            type="rect",
            xref="x",
            yref="y4",
            x0=df.index.min(),
            y0=30,
            x1=df.index.max(),
            y1=60,
            fillcolor="pink",
            opacity=0.3,
            layer="below",
            line_width=0,
        )
        fig.add_hline(y=40, line_dash="dash", line_color="pink", yaxis="y4")

    # Stochastic (Row 4)
    if "Stochastic" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stoch_K"],
                mode="lines",
                name="Stochastic %K",
                yaxis="y5",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Stoch_D"],
                mode="lines",
                name="Stochastic %D",
                yaxis="y5",
            )
        )
        fig.add_shape(
            type="rect",
            xref="x",
            yref="y5",
            x0=df.index.min(),
            y0=20,
            x1=df.index.max(),
            y1=80,
            fillcolor="pink",
            opacity=0.3,
            layer="below",
            line_width=0,
        )

    # ADX/DMI (Row 5)
    if "ADX/DMI" in indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["ADX"],
                mode="lines",
                name="ADX",
                yaxis="y6",
                line=dict(color="black"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["ADX_Plus_Di"],
                mode="lines",
                name="+DI",
                yaxis="y6",
                line=dict(color="green"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["ADX_Minus_Di"],
                mode="lines",
                name="-DI",
                yaxis="y6",
                line=dict(color="red"),
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{symbol} Stock Chart",
        xaxis_rangeslider_visible=False,
        yaxis1=dict(title="Price", domain=[0.7, 1], side="right"),
        yaxis2=dict(
            title="Volume", overlaying="y1", side="left", position=0, domain=[0.7, 1]
        ),
        yaxis3=dict(title="MACD", domain=[0.5, 0.68], side="right"),
        yaxis4=dict(title="RSI", domain=[0.3, 0.48], side="right"),
        yaxis5=dict(title="Stochastic", domain=[0.1, 0.28], side="right"),
        yaxis6=dict(title="ADX/DMI", domain=[0, 0.08], side="right"),
        yaxis_title_standoff=15,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(rangeslider=dict(visible=True, thickness=0.01), domain=[0, 0.95]),
        # yaxis_range_slider=dict(visible=True, thickness=0.01),
    )

    return fig


# Function to generate recommendation using Gemini
def generate_recommendation(images):
    model = genai.GenerativeModel("gemini-pro-vision")
    prompt = "Analyze the provided stock charts and provide observations on each chart. Then, give an overall recommendation on where you see the stock price moving."
    response = model.generate_content([prompt] + images)
    return response.text


# Streamlit app
def main():
    st.sidebar.title("Stock Chart Analysis")

    symbol = st.sidebar.text_input("Enter Stock Symbol", "AAPL")
    if st.sidebar.button("Validate"):
        valid, message = validate_symbol(symbol)
        if valid:
            st.sidebar.success(f"Symbol {symbol} validated. Company Name: {message}")
        else:
            st.sidebar.error(message)

    periods = st.sidebar.multiselect(
        "Select Time Periods", ["Daily", "Monthly", "Yearly"], default=["Daily"]
    )

    indicators = st.sidebar.multiselect(
        "Select Indicators",
        [
            "EMA5",
            "EMA13",
            "EMA26",
            "EMA50",
            "EMA200",
            "Bollinger Bands",
            "Volume",
            "MACD",
            "Stochastic",
            "RSI",
            "ADX/DMI",
        ],
    )

    if st.sidebar.button("Generate Charts"):
        if not periods:
            st.sidebar.error("Please select at least one time period.")
        else:
            data = fetch_stock_data(symbol, periods)
            for period, df in data.items():
                st.subheader(f"{symbol} Stock Chart ({period})")
                fig = plot_stock_chart(df, symbol, indicators)
                st.plotly_chart(fig, use_container_width=True)

            generate_recommendation_button = st.button(
                "Generate Recommendation", disabled=False if data else True
            )
            if generate_recommendation_button:
                images = []
                for period, df in data.items():
                    fig = plot_stock_chart(df, symbol, indicators)
                    img_bytes = fig.to_image(format="png")
                    img = Image.open(BytesIO(img_bytes))
                    images.append(img)
                recommendation = generate_recommendation(images)
                st.write(recommendation)


if __name__ == "__main__":
    main()

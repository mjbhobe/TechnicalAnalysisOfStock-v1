# Libraries
from dotenv import load_dotenv
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import tempfile
import os
import json
from datetime import datetime, timedelta

import utils.technical_indicators as ta
from utils.download_data import download_stock_data_and_tai

# Configure the API key - IMPORTANT: Use Streamlit secrets or environment variables for security
# For now, using hardcoded API key - REPLACE WITH YOUR ACTUAL API KEY SECURELY
load_dotenv()  # Load environment variables from .env file
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Select the Gemini model - using 'gemini-2.0-flash' as a general-purpose model
MODEL_NAME = "gemini-2.0-flash"  # or other model
gen_model = genai.GenerativeModel(MODEL_NAME)

# Set up Streamlit app
st.set_page_config(layout="wide")
st.title("AI-Powered Technical Stock Analysis Dashboard")
st.sidebar.header("Configuration")

# Input for multiple stock tickers (comma-separated)
tickers_input = st.sidebar.text_input(
    "Enter Stock Tickers (comma-separated):", "TCS.NS,RELIANCE.NS,HDFCBANK.NS"
)
# Parse tickers by stripping extra whitespace and splitting on commas
tickers = [
    ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()
]

# set date intervals -  end date is today & start date is 1 years back
end_date_default = datetime.today()
start_date_default = end_date_default - timedelta(days=365)
start_date = st.sidebar.date_input("Start Date", value=start_date_default)
end_date = st.sidebar.date_input("End Date", value=end_date_default)

# Technical indicators selection (applied to every ticker)
st.sidebar.subheader("Technical Indicators")
indicators = st.sidebar.multiselect(
    "Select Indicators:",
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
        "VWAP",
    ],
    default=["Bollinger Bands", "Volume"],
)

# Button to fetch data for all tickers
if st.sidebar.button("Fetch Data"):
    stock_data = {}
    for ticker in tickers:
        # Download data for each ticker using yfinance
        df = yf.download(
            ticker,
            start_date,
            end_date,
            progress=False,
            auto_adjust=True,
        )
        if not df.empty:
            stock_data[ticker] = df
        else:
            st.warning(f"No data found for {ticker}.")

        # add indicators chosen by user
        for indicator in indicators:
            if indicator == "EMA5":
                df["EMA5"] = ta.ema(df["Close"], span=5)
            if indicator == "EMA13":
                df["EMA13"] = ta.ema(df["Close"], span=13)
            if indicator == "EMA26":
                df["EMA26"] = ta.ema(df["Close"], span=26)
            if indicator == "EMA50":
                df["EMA50"] = ta.ema(df["Close"], span=50)
            if indicator == "EMA200":
                df["EMA200"] = ta.ema(df["Close"], span=200)
            if indicator == "VWAP":
                df["VWAP"] = ta.vwap(df)
            if indicator == "Bollinger Bands":
                sma_line, upper_bb, lower_bb = ta.bollinger_bands(df["Close"])
                df["BB_SMA"] = sma_line
                df["BB_Upper"] = upper_bb
                df["BB_Lower"] = lower_bb
            if indicator == "MACD":
                macd_line, signal_line, histogram = ta.macd(df["Close"])
                df["MACD"] = macd_line
                df["MACD_Signal"] = signal_line
                df["MACD_Histo"] = histogram
            if indicator == "RSI":
                df["RSI"] = ta.rsi(df["Close"])
            if indicator == "Stochastic":
                stoch_perc_k, stoch_perc_d = ta.stochastic(df)
                df["Stoch_K"] = stoch_perc_k
                df["Stoch_D"] = stoch_perc_d
            if indicator == "ADX":
                adx_line, adx_plus_di, adx_minus_di = ta.adx(df)
                df["ADX"] = adx_line
                df["ADX_Plus_Di"] = adx_plus_di
                df["ADX_Minus_Di"] = adx_minus_di

    st.session_state["stock_data"] = stock_data
    st.success("Stock data loaded successfully for: " + ", ".join(stock_data.keys()))

# Ensure we have data to analyze
if "stock_data" in st.session_state and st.session_state["stock_data"]:

    # Define a function to build chart, call the Gemini API and return structured result
    def plot_chart(ticker, df):
        # Build candlestick chart for the given ticker's data

        # chart layout will be like this
        #   candlesticks with (optionally) following indicators - EMA5, 13, 26, 50, 200, VWAP, BB
        #   volume
        #   macd
        #   stochastic
        #   rsi
        #   adx

        subplot_titles = ["Candlesticks"]

        if "Volume" in indicators:
            subplot_titles.append("Volume")
        if "MACD" in indicators:
            subplot_titles.append("MACD")
        if "Stochastic" in indicators:
            subplot_titles.append("Stochastic")
        if "RSI" in indicators:
            subplot_titles.append("Stochastic")
        if "ADX/DMI" in indicators:
            subplot_titles.append("ADX/DMI")

        # adjust row heights depending on # of subplots
        # there can be candlesticks + upto 5 subplots
        # fmt: off
        row_heights = [
            [1.0],                  # only candlesticks
            [0.7, 0.3],             # candlestick & 1 more
            [0.6, 0.2, 0.2],
            [0.5, 0.2, 0.2, 0.1],
            [0.4, 0.2, 0.2, 0.1, 0.1],
            [0.4, 0.2, 0.1, 0.1, 0.1, 0.1],
        ]  # fmt: on
        num_rows = len(subplot_titles)

        fig = go.Figure()

        fig = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=row_heights[num_rows - 1],
            subplot_titles=tuple(subplot_titles),
        )

        # add candlesticks (always shown)
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

        ema_colors = {
            "EMA5": "green",
            "EMA13": "blue",
            "EMA26": "gray",
            "EMA50": "magenta",
            "EMA200": "purple",
            "VWAP": "brown",
        }

        for ema, color in ema_colors.items():
            if ema in indicators:
                ema_width = 2 if ema in ["EMA50", "EMA200", "VWAP"] else 1
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ema],
                        mode="lines",
                        name=ema,
                        line=dict(color=color, width=ema_width),
                    ),
                    row=1,
                    col=1,
                )

        if "Bollinger Bands" in indicators:
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
                    fillcolor="rgba(0, 255, 255, 0.20)",  # cyan with 30% opacity
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

        if "Volume" in indicators:
            # volume_colors = [
            #     (
            #         # "rgba(49,130,117,0.35)"
            #         # if df["Close"].iloc[i] >= df["Open"].iloc[i]
            #         # else "rgba(242,54,69,0.35)"
            #         "rgb(49, 130, 117)" if v >= 0 else "rgb(242, 54, 69)"
            #         for v in df["Volume"].diff().fillna(0)
            #     )
            #     #  for i in range(len(df))
            # ]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["Volume"],
                    name="Volume",
                    marker_color=[
                        "rgb(49, 130, 117)" if v >= 0 else "rgb(242, 54, 69)"
                        for v in df["Volume"].diff().fillna(0).values.ravel()
                    ],
                    opacity=0.30,
                ),
                row=2,
                col=1,
            )

        # # Add selected technical indicators
        # def add_indicator(indicator):
        #     if indicator == "20-Day SMA":
        #         sma = data["Close"].rolling(window=20).mean()
        #         fig.add_trace(
        #             go.Scatter(x=data.index, y=sma, mode="lines", name="SMA (20)")
        #         )
        #     elif indicator == "20-Day EMA":
        #         ema = data["Close"].ewm(span=20).mean()
        #         fig.add_trace(
        #             go.Scatter(x=data.index, y=ema, mode="lines", name="EMA (20)")
        #         )
        #     elif indicator == "20-Day Bollinger Bands":
        #         sma = data["Close"].rolling(window=20).mean()
        #         std = data["Close"].rolling(window=20).std()
        #         bb_upper = sma + 2 * std
        #         bb_lower = sma - 2 * std
        #         fig.add_trace(
        #             go.Scatter(x=data.index, y=bb_upper, mode="lines", name="BB Upper")
        #         )
        #         fig.add_trace(
        #             go.Scatter(x=data.index, y=bb_lower, mode="lines", name="BB Lower")
        #         )
        #     elif indicator == "VWAP":
        #         data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data[
        #             "Volume"
        #         ].cumsum()
        #         fig.add_trace(
        #             go.Scatter(x=data.index, y=data["VWAP"], mode="lines", name="VWAP")
        #         )

        # for ind in indicators:
        #     add_indicator(ind)
        # fig.update_layout(xaxis_rangeslider_visible=False)

        # # Save chart as temporary PNG file and read image bytes
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        #     fig.write_image(tmpfile.name)
        #     tmpfile_path = tmpfile.name
        # with open(tmpfile_path, "rb") as f:
        #     image_bytes = f.read()
        # os.remove(tmpfile_path)

        # # Create an image Part
        # image_part = {"data": image_bytes, "mime_type": "image/png"}

        # # Updated prompt asking for a detailed justification of technical analysis and a recommendation.
        # analysis_prompt = (
        #     f"You are a Stock Trader specializing in Technical Analysis at a top financial institution. "
        #     f"Analyze the stock chart for {ticker} based on its candlestick chart and the displayed technical indicators. "
        #     f"Provide a detailed justification of your analysis, explaining what patterns, signals, and trends you observe. "
        #     f"Then, based solely on the chart, provide a recommendation from the following options: "
        #     f"'Strong Buy', 'Buy', 'Weak Buy', 'Hold', 'Weak Sell', 'Sell', or 'Strong Sell'. "
        #     f"Return your output as a JSON object with two keys: 'action' and 'justification'."
        # )

        # # Call the Gemini API with text and image input - Roles added: "user" for both text and image
        # contents = [
        #     {
        #         "role": "user",
        #         "parts": [analysis_prompt],
        #     },  # Text prompt with role "user"
        #     {"role": "user", "parts": [image_part]},  # Image part with role "user"
        # ]

        # response = gen_model.generate_content(
        #     contents=contents  # Pass the restructured 'contents' with roles
        # )

        # try:
        #     # Attempt to parse JSON from the response text
        #     result_text = response.text
        #     # Find the start and end of the JSON object within the text (if Gemini includes extra text)
        #     json_start_index = result_text.find("{")
        #     json_end_index = (
        #         result_text.rfind("}") + 1
        #     )  # +1 to include the closing brace
        #     if json_start_index != -1 and json_end_index > json_start_index:
        #         json_string = result_text[json_start_index:json_end_index]
        #         result = json.loads(json_string)
        #     else:
        #         raise ValueError("No valid JSON object found in the response")

        # except json.JSONDecodeError as e:
        #     result = {
        #         "action": "Error",
        #         "justification": f"JSON Parsing error: {e}. Raw response text: {response.text}",
        #     }
        # except ValueError as ve:
        #     result = {
        #         "action": "Error",
        #         "justification": f"Value Error: {ve}. Raw response text: {response.text}",
        #     }
        # except Exception as e:
        #     result = {
        #         "action": "Error",
        #         "justification": f"General Error: {e}. Raw response text: {response.text}",
        #     }

        return fig

    def plot_technical_chart(ticker, df, indicators):
        fig = go.Figure()

        # OHLC + EMAs + Bollinger Bands + Volume (Row 1)

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlesticks",
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
                    fill="tonexty",
                    fillcolor="rgba(12, 50, 153, 0.25)",
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
            # fig.add_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df["BB_Upper"],
            #         fill="tonexty",
            #         fillcolor="rgba(12, 50, 153, 0.25)",
            #         line=dict(color="rgba(0,0,0,0)"),
            #         showlegend=False,
            #         yaxis="y1",
            #     )
            # )
        if "Volume" in indicators:
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["Volume"],
                    name="Volume",
                    yaxis="y2",
                    marker_color=[
                        "rgb(49, 130, 117)" if v >= 0 else "rgb(242, 54, 69)"
                        for v in df["Volume"].diff().fillna(0).values.ravel()
                    ],
                    opacity=0.35,
                )
            )

        # MACD (Row 2)
        if "MACD" in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df["MACD"], mode="lines", name="MACD", yaxis="y3"
                )
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
                    marker_color=[
                        "green" if v >= 0 else "red" for v in df["MACD_Histo"]
                    ],
                )
            )

        # RSI (Row 3)
        if "RSI" in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df["RSI"], mode="lines", name="RSI", yaxis="y4"
                )
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
            title=f"{ticker} Technical Chart",
            height=1000,
            xaxis_rangeslider_visible=False,
            yaxis1=dict(title="Price", domain=[0.7, 1], side="right"),
            yaxis2=dict(
                title="Volume",
                overlaying="y1",
                side="left",
                position=0,
                domain=[0.7, 1],
            ),
            yaxis3=dict(title="MACD", domain=[0.5, 0.68], side="right"),
            yaxis4=dict(title="RSI", domain=[0.3, 0.48], side="right"),
            yaxis5=dict(title="Stochastic", domain=[0.1, 0.28], side="right"),
            yaxis6=dict(title="ADX/DMI", domain=[0, 0.08], side="right"),
            yaxis_title_standoff=15,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.01), domain=[0, 0.95]
            ),
            # yaxis_range_slider=dict(visible=True, thickness=0.01),
        )

        return fig

    # Create tabs: first tab for overall summary, subsequent tabs per ticker
    tab_names = ["Overall Summary"] + list(st.session_state["stock_data"].keys())
    tabs = st.tabs(tab_names)

    # List to store overall results
    overall_results = []

    # Process each ticker and populate results
    for i, ticker in enumerate(st.session_state["stock_data"]):
        data = st.session_state["stock_data"][ticker]
        fig = plot_chart(ticker, data)
        with tabs[i + 1]:
            st.subheader(f"Analysis for {ticker}")
            st.plotly_chart(fig)
            st.write("**LLM analysis will appear here!**")

        # # Analyze ticker: get chart figure and structured output result
        # fig, result = analyze_ticker(ticker, data)
        # overall_results.append(
        #     {"Stock": ticker, "Recommendation": result.get("action", "N/A")}
        # )
        # # In each ticker-specific tab, display the chart and detailed justification
        # with tabs[i + 1]:
        #     st.subheader(f"Analysis for {ticker}")
        #     st.plotly_chart(fig)
        #     st.write("**Detailed Justification:**")
        #     st.write(result.get("justification", "No justification provided."))

    # In the Overall Summary tab, display a table of all results
    with tabs[0]:
        st.subheader("Overall Structured Recommendations")
        st.write("Under construction")
        # df_summary = pd.DataFrame(overall_results)
        # st.table(df_summary)
else:
    st.info("Please fetch stock data using the sidebar.")

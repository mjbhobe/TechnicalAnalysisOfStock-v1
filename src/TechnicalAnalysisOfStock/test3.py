import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
from rich import print
from TechnicalAnalysisOfStock.utils.download_data import download_stock_data_and_tai

# # Load data
# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
# )
stock_symbol = "TCS.NS"
_, _, df = download_stock_data_and_tai(stock_symbol)
# df.columns = [col.replace("AAPL.", "") for col in df.columns]
print(df.tail())

# Create figure
fig = go.Figure()

# show candlestick & volume in 2 row plot

# fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.High)))

fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.002,  # reduce space between rows
    # row_heights=[0.08, 0.42, 0.15, 0.12, 0.12, 0.11],
    row_heights=[0.70, 0.30],
    # subplot_titles=[
    #     # "ADX (+DI, -DI)",
    #     f"{symbol} OHLC + EMAs + Bollinger Bands",
    #     # "MACD",
    #     # "Stochastic Oscillator",
    #     # "RSI",
    #     "Volume",
    # ],
)

# Candlesticks
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        # name="Candlestick",
        increasing_line_color="rgb(49,130,117)",
        decreasing_line_color="rgb(242,54,69)",
    ),
    row=1,
    col=1,
)

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
        # name="Volume",
        marker_color=volume_colors,
        opacity=1,
    ),
    row=2,
    col=1,
)

# Set title
fig.update_layout(title_text=f"Technical chart for {stock_symbol}")

# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    # dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
        # rangeslider=dict(visible=True),
        type="date",
    ),
    xaxis2_rangeslider=dict(visible=True, thickness=0.02),
)

# This is the line you must add before showing the plot
# The rangeslider now has a height that is 40% of the total plot area height
fig.update_xaxes(rangeslider_thickness=0.02)

fig.show()

import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pathlib

import utils.technical_indicators as ta
from utils.download_data import download_stock_data_and_tai

from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Span, BoxAnnotation, Band
from bokeh.models.tools import WheelZoomTool, PanTool

# set date intervals -  end date is today & start date is 1 years back
num_years = 1
end_date = datetime.today()
start_date = end_date - timedelta(days=num_years * 365)
ticker = "TCS.NS"
df = yf.download(
    ticker,
    start=start_date.strftime("%Y-%m-%d"),
    end=end_date.strftime("%Y-%m-%d"),
    progress=False,
    auto_adjust=True,
    group_by="ticker",
)
# above call returns a multi-index dataframe, following call flattens multi-index columns
df.columns = [
    col[1] if isinstance(col, tuple) and col[1] else col[0] for col in df.columns
]

df["EMA5"] = ta.ema(df["Close"], span=5)
df["EMA13"] = ta.ema(df["Close"], span=13)
df["EMA26"] = ta.ema(df["Close"], span=26)
df["EMA50"] = ta.ema(df["Close"], span=50)
df["EMA200"] = ta.ema(df["Close"], span=200)
df["VWAP"] = ta.vwap(df)

sma_line, upper_bb, lower_bb = ta.bollinger_bands(df["Close"])
df["BB_SMA"] = sma_line
df["BB_Upper"] = upper_bb
df["BB_Lower"] = lower_bb

macd_line, signal_line, histogram = ta.macd(df["Close"])
df["MACD"] = macd_line
df["MACD_Signal"] = signal_line
df["MACD_Histo"] = histogram
df["RSI"] = ta.rsi(df["Close"])

stoch_perc_k, stoch_perc_d = ta.stochastic(df)
df["Stoch_K"] = stoch_perc_k
df["Stoch_D"] = stoch_perc_d

adx_line, adx_plus_di, adx_minus_di = ta.adx(df)
df["ADX"] = adx_line
df["ADX_Plus_Di"] = adx_plus_di
df["ADX_Minus_Di"] = adx_minus_di

# Fixing: move Volume to separate plot below candlesticks
output_file_path = pathlib.Path(__file__).parent / "bokeh_plot.html"
output_file(str(output_file_path))

TOOLS = "xpan,xwheel_zoom,reset"
w = 12 * 60 * 60 * 1000

# Update DataFrame with color fields
df["vol_color"] = [
    "#49A27F" if c >= o else "#F23645" for c, o in zip(df["Close"], df["Open"])
]
df["macd_color"] = ["#49A27F" if val >= 0 else "#F23645" for val in df["MACD_Histo"]]
df["datetime"] = df.index
source = ColumnDataSource(df)

# P1: Candlestick chart
p1 = figure(
    x_axis_type="datetime",
    height=300,
    title="Candlestick with EMA and VWAP",
    tools=TOOLS,
)
inc = df["Close"] > df["Open"]
dec = df["Open"] > df["Close"]
# p1.segment('datetime', 'High', 'datetime', 'Low', color="black", source=source)
# p1.vbar(df['datetime'][inc], w, df['Open'][inc], df['Close'][inc], fill_color="#49A27F", line_color="#49A27F")
# p1.vbar(df['datetime'][dec], w, df['Open'][dec], df['Close'][dec], fill_color="#F23645", line_color="#F23645")

# Rising candles (green)
p1.segment(
    df["datetime"][inc],
    df["High"][inc],
    df["datetime"][inc],
    df["Low"][inc],
    color="#49A27F",
)

# Falling candles (red)
p1.segment(
    df["datetime"][dec],
    df["High"][dec],
    df["datetime"][dec],
    df["Low"][dec],
    color="#F23645",
)

# Rising candles (green)
p1.vbar(
    df["datetime"][inc],
    w,
    df["Open"][inc],
    df["Close"][inc],
    fill_color="#49A27F",
    line_color="#49A27F",
)

# Falling candles (red)
p1.vbar(
    df["datetime"][dec],
    w,
    df["Open"][dec],
    df["Close"][dec],
    fill_color="#F23645",
    line_color="#F23645",
)

for ema, color in [
    ("EMA5", "green"),
    ("EMA13", "blue"),
    ("EMA26", "gray"),
    ("EMA50", "pink"),
    ("EMA200", "purple"),
]:
    p1.line(
        "datetime",
        ema,
        source=source,
        line_width=2 if ema in ["EMA50", "EMA200"] else 1,
        color=color,
        legend_label=ema,
    )
p1.line("datetime", "VWAP", source=source, line_width=2.5, color="brown")

# add bollinger bands
band = Band(
    base="datetime",
    lower="BB_Lower",
    upper="BB_Upper",
    source=source,
    level="underlay",
    fill_alpha=0.25,
    line_width=2,
    line_color="#006064",
    fill_color="#006064",
)
p1.add_layout(band)
p1.line(
    "date", "BB_SMA", source=source, color="red", line_width=1.5, legend_label="BB SMA"
)

p1.ygrid.grid_line_color = "lightgray"
p1.xgrid.grid_line_color = "lightgray"
# p1.add_tools(WheelZoomTool(), PanTool())
p1.toolbar.logo = None
p1.toolbar_location = None

# P1.5: Volume chart (separate plot)
p1_vol = figure(
    x_range=p1.x_range, height=150, title="Volume", tools=TOOLS, y_axis_location="right"
)
p1_vol.vbar(
    x="datetime",
    top="Volume",
    width=w,
    source=source,
    fill_alpha=0.25,
    fill_color="vol_color",
    line_color=None,
)
p1_vol.ygrid.grid_line_color = "lightgray"
p1_vol.xgrid.grid_line_color = "lightgray"
# p1_vol.add_tools(WheelZoomTool(), PanTool())
p1_vol.toolbar.logo = None
p1_vol.toolbar_location = None

# legend
p1.legend.location = "top_left"
p1.legend.label_text_font_size = "8pt"

# zoom & PAN controls
p1.toolbar_location = "above"
p1.toolbar.active_scroll = p1.select_one(WheelZoomTool)
p1.toolbar.active_drag = p1.select_one(PanTool)

p1_vol.toolbar_location = "above"
p1_vol.toolbar.active_scroll = p1_vol.select_one(WheelZoomTool)
p1_vol.toolbar.active_drag = p1_vol.select_one(PanTool)


# P2: MACD
p2 = figure(x_range=p1.x_range, height=200, title="MACD", tools=TOOLS)
p2.line("datetime", "MACD", source=source, color="blue")
p2.line("datetime", "MACD_Signal", source=source, color="red")
p2.vbar(
    x="datetime",
    top="MACD_Histo",
    width=w,
    source=source,
    fill_alpha=0.25,
    fill_color="macd_color",
    line_color=None,
)
p2.ygrid.grid_line_color = "lightgray"

# P3: Stochastic
p3 = figure(x_range=p1.x_range, height=200, title="Stochastic Oscillator", tools=TOOLS)
p3.line("datetime", "Stoch_K", source=source, color="blue")
p3.line("datetime", "Stoch_D", source=source, color="red")
p3.add_layout(BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color="pink"))
for y in [20, 80]:
    p3.add_layout(
        Span(location=y, dimension="width", line_color="lightgray", line_dash="dashed")
    )
p3.ygrid.grid_line_color = "lightgray"

# P4: RSI
p4 = figure(x_range=p1.x_range, height=200, title="RSI", tools=TOOLS)
p4.line("datetime", "RSI", source=source, color="black")
p4.add_layout(BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color="pink"))
for y in [20, 80]:
    p4.add_layout(
        Span(location=y, dimension="width", line_color="lightgray", line_dash="dashed")
    )
p4.ygrid.grid_line_color = "lightgray"

# P5: ADX
p5 = figure(x_range=p1.x_range, height=200, title="ADX", tools=TOOLS)
p5.line("datetime", "ADX", source=source, color="black")
p5.line("datetime", "ADX_Plus_Di", source=source, color="green")
p5.line("datetime", "ADX_Minus_Di", source=source, color="red")
p5.ygrid.grid_line_color = "lightgray"

# hide all x-axis except the last one
p2.xaxis.visible = False
p3.xaxis.visible = False
p4.xaxis.visible = False
p1_vol.xaxis.visible = False
p1.xaxis.visible = False

from bokeh.models import DatetimeTickFormatter

# format the axis to show date-times
p5.xaxis.formatter = DatetimeTickFormatter(
    days="%d-%b", months="%d-%b", years="%d-%b", hours="%d-%b", minutes="%d-%b"
)


# display the bokeh plot
from bokeh.plotting import show

show(column(p1, p1_vol, p2, p3, p4, p5, sizing_mode="stretch_both"))

# Combine and export
# from bokeh.io.export import export_png
# # save(column(p1, p1_vol, p2, p3, p4, p5))
# export_png(column(p1, p1_vol, p2, p3, p4, p5))

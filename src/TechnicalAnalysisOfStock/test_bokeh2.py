import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Band, Range1d, Span, BoxAnnotation
from bokeh.io import output_notebook
from bokeh.models.tools import WheelZoomTool

import utils.technical_indicators as ta

# output_notebook()

def plot_stock_dashboard(stock_df: pd.DataFrame):
    df = stock_df.copy()
    df.reset_index(inplace=True)
    df['date'] = pd.to_datetime(df['datetime'])
    source = ColumnDataSource(df)

    TOOLS = "pan,wheel_zoom,reset"
    shared_x_range = Range1d(start=df['date'].min(), end=df['date'].max())

    # Candlestick + EMA + VWAP + BB
    p1 = figure(x_axis_type="datetime", height=400, tools=TOOLS, x_range=shared_x_range, background_fill_color="white")
    inc = df['Close'] > df['Open']
    dec = df['Close'] <= df['Open']

    p1.segment('date', 'High', 'date', 'Low', source=source, color="black")
    p1.vbar(df['date'][inc], width=0.6, top=df['Close'][inc], bottom=df['Open'][inc], fill_color="#49A27F", line_color="#49A27F")
    p1.vbar(df['date'][dec], width=0.6, top=df['Close'][dec], bottom=df['Open'][dec], fill_color="#F23645", line_color="#F23645")

    # EMA lines
    p1.line('date', 'EMA5', source=source, line_width=1, color="green", legend_label="EMA5")
    p1.line('date', 'EMA13', source=source, line_width=1, color="blue", legend_label="EMA13")
    p1.line('date', 'EMA26', source=source, line_width=1, color="gray", legend_label="EMA26")
    p1.line('date', 'EMA50', source=source, line_width=2.5, color="pink", legend_label="EMA50")
    p1.line('date', 'EMA200', source=source, line_width=2.5, color="purple", legend_label="EMA200")
    p1.line('date', 'VWAP', source=source, line_width=2.5, color="brown", legend_label="VWAP")

    # Bollinger Bands
    band = Band(base='date', lower='BB_Lower', upper='BB_Upper', source=source, level='underlay',
                fill_alpha=0.65, line_width=2, line_color="#006064", fill_color="#006064")
    p1.add_layout(band)
    p1.line('date', 'BB_SMA', source=source, color="red", line_width=1.5, legend_label="BB SMA")

    # Volume
    p2 = figure(x_axis_type="datetime", height=180, tools=TOOLS, x_range=p1.x_range, background_fill_color="white")
    p2.vbar(df['date'][inc], width=0.6, top=df['Volume'][inc], fill_alpha=0.25, fill_color="green")
    p2.vbar(df['date'][dec], width=0.6, top=df['Volume'][dec], fill_alpha=0.25, fill_color="red")

    # MACD
    p3 = figure(x_axis_type="datetime", height=180, tools=TOOLS, x_range=p1.x_range, background_fill_color="white")
    p3.line('date', 'MACD', source=source, color="blue", legend_label="MACD")
    p3.line('date', 'MACD_Signal', source=source, color="red", legend_label="Signal")
    p3.vbar(x='date', top='MACD_Histo', width=0.6,
            fill_color=["green" if val > 0 else "red" for val in df['MACD_Histo']],
            fill_alpha=0.25, source=source)

    # Stochastic Oscillator
    p4 = figure(x_axis_type="datetime", height=180, tools=TOOLS, x_range=p1.x_range, background_fill_color="white")
    p4.line('date', 'Stoch_K', source=source, color="blue", legend_label="%K")
    p4.line('date', 'Stock_D', source=source, color="red", legend_label="%D")
    stoch_box = BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color="pink")
    p4.add_layout(stoch_box)
    p4.add_layout(Span(location=80, dimension='width', line_dash='dashed', line_color='lightgray'))
    p4.add_layout(Span(location=20, dimension='width', line_dash='dashed', line_color='lightgray'))

    # RSI
    p5 = figure(x_axis_type="datetime", height=180, tools=TOOLS, x_range=p1.x_range, background_fill_color="white")
    p5.line('date', 'RSI', source=source, color="purple", legend_label="RSI")
    rsi_box = BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color="pink")
    p5.add_layout(rsi_box)

    # ADX
    p6 = figure(x_axis_type="datetime", height=180, tools=TOOLS, x_range=p1.x_range, background_fill_color="white")
    p6.line('date', 'ADX', source=source, color="black", legend_label="ADX")
    p6.line('date', 'ADX_Plus_Di', source=source, color="green", legend_label="+DI")
    p6.line('date', 'ADX_Minus_Di', source=source, color="red", legend_label="-DI")

    for p in [p1, p2, p3, p4, p5, p6]:
        p.grid.grid_line_color = "#e0e0e0"
        p.xaxis.visible = False
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)

    p6.xaxis.visible = True

    layout = gridplot([[p1], [p2], [p3], [p4], [p5], [p6]], toolbar_location="above", merge_tools=True)
    show(layout)

# download the dataset & prepare the dataframe
num_years = 1
end_date = datetime.today()
start_date = end_date - timedelta(days=num_years*365)
ticker = "TCS.NS"
stock_df = yf.download(
    ticker,
    start=start_date.strftime('%Y-%m-%d'),
    end=end_date.strftime('%Y-%m-%d'),
    progress=False,
    auto_adjust=True,
    group_by='ticker',
)
# above call returns a multi-index dataframe, following call flattens multi-index columns
stock_df.columns = [
    col[1] if isinstance(col, tuple) and col[1] else col[0]
    for col in stock_df.columns
]

stock_df["EMA5"] = ta.ema(stock_df["Close"], span=5)
stock_df["EMA13"] = ta.ema(stock_df["Close"], span=13)
stock_df["EMA26"] = ta.ema(stock_df["Close"], span=26)
stock_df["EMA50"] = ta.ema(stock_df["Close"], span=50)
stock_df["EMA200"] = ta.ema(stock_df["Close"], span=200)
stock_df["VWAP"] = ta.vwap(stock_df)

sma_line, upper_bb, lower_bb = ta.bollinger_bands(stock_df["Close"])
stock_df["BB_SMA"] = sma_line
stock_df["BB_Upper"] = upper_bb
stock_df["BB_Lower"] = lower_bb

macd_line, signal_line, histogram = ta.macd(stock_df["Close"])
stock_df["MACD"] = macd_line
stock_df["MACD_Signal"] = signal_line
stock_df["MACD_Histo"] = histogram
stock_df["RSI"] = ta.rsi(stock_df["Close"])

stoch_perc_k, stoch_perc_d = ta.stochastic(stock_df)
stock_df["Stoch_K"] = stoch_perc_k
stock_df["Stoch_D"] = stoch_perc_d

adx_line, adx_plus_di, adx_minus_di = ta.adx(stock_df)
stock_df["ADX"] = adx_line
stock_df["ADX_Plus_Di"] = adx_plus_di
stock_df["ADX_Minus_Di"] = adx_minus_di

# Fixing: move Volume to separate plot below candlesticks
# output_file_path = pathlib.Path(__file__).parent / "bokeh_plot.html"
# output_file(str(output_file_path))

# TOOLS = "xpan,xwheel_zoom,reset"
# w = 12 * 60 * 60 * 1000

# Update DataFrame with color fields
stock_df['vol_color'] = ['#49A27F' if c >= o else '#F23645' for c, o in zip(stock_df['Close'], stock_df['Open'])]
stock_df['macd_color'] = ['#49A27F' if val >= 0 else '#F23645' for val in stock_df['MACD_Histo']]
stock_df["datetime"] = stock_df.index

plot_stock_dashboard(stock_df)
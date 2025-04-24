## --------------- Plotly Code ----------------- ##

## Plotly

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Generate dummy stock data
np.random.seed(0)
date_range = pd.date_range(start='2023-01-01', periods=100, freq='D')
df = pd.DataFrame(index=date_range)
df['Open'] = np.random.uniform(100, 200, size=100)
df['High'] = df['Open'] + np.random.uniform(0, 10, size=100)
df['Low'] = df['Open'] - np.random.uniform(0, 10, size=100)
df['Close'] = df['Open'] + np.random.uniform(-5, 5, size=100)
df['Volume'] = np.random.randint(100000, 500000, size=100)
df['BB_Upper'] = df['Close'] + 10
df['BB_Lower'] = df['Close'] - 10
df['BB_SMA'] = df['Close']
for span in [5, 13, 26, 50, 200]:
    df[f'EMA{span}'] = df['Close'].ewm(span=span).mean()
df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
df['MACD'] = df['EMA12'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
df['MACD_Histo'] = df['MACD'] - df['MACD_Signal']
df['RSI'] = 50 + 10 * np.sin(np.linspace(0, 6.28, 100))
df['Stoch_K'] = 50 + 30 * np.sin(np.linspace(0, 6.28, 100))
df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
df['ADX'] = 20 + 10 * np.abs(np.sin(np.linspace(0, 6.28, 100)))
df['ADX_Plus_Di'] = 25 + 5 * np.sin(np.linspace(0, 6.28, 100))
df['ADX_Minus_Di'] = 25 - 5 * np.sin(np.linspace(0, 6.28, 100))

# Create subplots
fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                    row_heights=[0.35, 0.15, 0.15, 0.15, 0.2],
                    subplot_titles=('Price Chart', 'MACD', 'Stochastic Oscillator', 'RSI', 'ADX'))

# Row 1: Candlestick + EMAs + VWAP + Volume
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                             low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
ema_colors = {5: 'green', 13: 'blue', 26: 'gray', 50: 'pink', 200: 'purple'}
for span in [5, 13, 26, 50, 200]:
    fig.add_trace(go.Scatter(x=df.index, y=df[f'EMA{span}'], mode='lines',
                             line=dict(width=3 if span in [50, 200] else 1, color=ema_colors[span]),
                             name=f'EMA{span}'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines',
                         line=dict(width=3, color='brown'), name='VWAP'), row=1, col=1)
colors = np.where(df['Close'] >= df['Open'], 'rgba(0,200,0,0.25)', 'rgba(200,0,0,0.25)')
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume',
                     marker_color=colors, showlegend=False), row=1, col=1)

# Row 2: MACD
fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='Signal', line=dict(color='red')), row=2, col=1)
macd_hist_colors = np.where(df['MACD_Histo'] >= 0, 'rgba(0,200,0,0.25)', 'rgba(200,0,0,0.25)')
fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histo'], name='Histogram', marker_color=macd_hist_colors), row=2, col=1)

# Row 3: Stochastic
fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_K'], mode='lines', name='%K', line=dict(color='blue')), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_D'], mode='lines', name='%D', line=dict(color='red')), row=3, col=1)
fig.add_shape(type='rect', x0=df.index[0], x1=df.index[-1], y0=20, y1=80,
              fillcolor='pink', opacity=0.2, line_width=0, row=3, col=1)
for level in [20, 80]:
    fig.add_trace(go.Scatter(x=[df.index[0], df.index[-1]], y=[level, level],
                             mode='lines', line=dict(color='lightgray', dash='dash'), showlegend=False), row=3, col=1)

# Row 4: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='black')), row=4, col=1)
fig.add_shape(type='rect', x0=df.index[0], x1=df.index[-1], y0=20, y1=80,
              fillcolor='pink', opacity=0.2, line_width=0, row=4, col=1)
for level in [20, 80]:
    fig.add_trace(go.Scatter(x=[df.index[0], df.index[-1]], y=[level, level],
                             mode='lines', line=dict(color='lightgray', dash='dash'), showlegend=False), row=4, col=1)

# Row 5: ADX
fig.add_trace(go.Scatter(x=df.index, y=df['ADX'], mode='lines', name='ADX', line=dict(color='black')), row=5, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['ADX_Plus_Di'], mode='lines', name='+DI', line=dict(color='green')), row=5, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['ADX_Minus_Di'], mode='lines', name='-DI', line=dict(color='red')), row=5, col=1)

# Update layout for better aesthetics
fig.update_layout(
    title='TradingView-style Multi-Indicator Stock Chart',
    template='plotly_white',
    height=1200,
    showlegend=False,
    xaxis_rangeslider_visible=False,
)

# Light grid
for i in range(1, 6):
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray', row=i, col=1)

# Hide modebar
import plotly.offline as pyo
import plotly.io as pio
pio.renderers.default = 'iframe'
pyo.plot(fig, config={'displayModeBar': False}, auto_open=False, filename='/mnt/data/tradingview_plotly.html')

"/mnt/data/tradingview_plotly.html"


## ----------------------- Bokeh version ---------------------------
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Span, BoxAnnotation
from bokeh.models.tools import WheelZoomTool, PanTool

# Fixing: move Volume to separate plot below candlesticks

output_file("/mnt/data/tradingview_bokeh_fixed.html")

TOOLS = "xpan,xwheel_zoom,reset"
w = 12 * 60 * 60 * 1000

# Update DataFrame with color fields
df['vol_color'] = ['#49A27F' if c >= o else '#F23645' for c, o in zip(df['Close'], df['Open'])]
df['macd_color'] = ['#49A27F' if val >= 0 else '#F23645' for val in df['MACD_Histo']]
df["datetime"] = df.index
source = ColumnDataSource(df)

# P1: Candlestick chart
p1 = figure(x_axis_type="datetime", height=300, title="Candlestick with EMA and VWAP", tools=TOOLS)
inc = df['Close'] > df['Open']
dec = df['Open'] > df['Close']
p1.segment('datetime', 'High', 'datetime', 'Low', color="black", source=source)
p1.vbar(df['datetime'][inc], w, df['Open'][inc], df['Close'][inc], fill_color="#49A27F", line_color="black")
p1.vbar(df['datetime'][dec], w, df['Open'][dec], df['Close'][dec], fill_color="#F23645", line_color="black")
for ema, color in [('EMA5', 'green'), ('EMA13', 'blue'), ('EMA26', 'gray'), ('EMA50', 'pink'), ('EMA200', 'purple')]:
    p1.line('datetime', ema, source=source, line_width=2 if ema in ['EMA50', 'EMA200'] else 1, color=color)
p1.line('datetime', 'VWAP', source=source, line_width=2.5, color='brown')
p1.ygrid.grid_line_color = "lightgray"
p1.xgrid.grid_line_color = "lightgray"
p1.add_tools(WheelZoomTool(), PanTool())
p1.toolbar.logo = None
p1.toolbar_location = None

# P1.5: Volume chart (separate plot)
p1_vol = figure(x_range=p1.x_range, height=150, title="Volume", tools=TOOLS, y_axis_location="right")
p1_vol.vbar(x='datetime', top='Volume', width=w, source=source, fill_alpha=0.25,
            fill_color='vol_color', line_color=None)
p1_vol.ygrid.grid_line_color = "lightgray"
p1_vol.xgrid.grid_line_color = "lightgray"
p1_vol.add_tools(WheelZoomTool(), PanTool())
p1_vol.toolbar.logo = None
p1_vol.toolbar_location = None

# P2: MACD
p2 = figure(x_range=p1.x_range, height=200, title="MACD", tools=TOOLS)
p2.line('datetime', 'MACD', source=source, color="blue")
p2.line('datetime', 'MACD_Signal', source=source, color="red")
p2.vbar(x='datetime', top='MACD_Histo', width=w, source=source, fill_alpha=0.25,
        fill_color='macd_color', line_color=None)
p2.ygrid.grid_line_color = "lightgray"

# P3: Stochastic
p3 = figure(x_range=p1.x_range, height=200, title="Stochastic Oscillator", tools=TOOLS)
p3.line('datetime', 'Stoch_K', source=source, color="blue")
p3.line('datetime', 'Stoch_D', source=source, color="red")
p3.add_layout(BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color='pink'))
for y in [20, 80]:
    p3.add_layout(Span(location=y, dimension='width', line_color='lightgray', line_dash='dashed'))
p3.ygrid.grid_line_color = "lightgray"

# P4: RSI
p4 = figure(x_range=p1.x_range, height=200, title="RSI", tools=TOOLS)
p4.line('datetime', 'RSI', source=source, color="black")
p4.add_layout(BoxAnnotation(top=80, bottom=20, fill_alpha=0.2, fill_color='pink'))
for y in [20, 80]:
    p4.add_layout(Span(location=y, dimension='width', line_color='lightgray', line_dash='dashed'))
p4.ygrid.grid_line_color = "lightgray"

# P5: ADX
p5 = figure(x_range=p1.x_range, height=200, title="ADX", tools=TOOLS)
p5.line('datetime', 'ADX', source=source, color="black")
p5.line('datetime', 'ADX_Plus_Di', source=source, color="green")
p5.line('datetime', 'ADX_Minus_Di', source=source, color="red")
p5.ygrid.grid_line_color = "lightgray"

# Combine and export
save(column(p1, p1_vol, p2, p3, p4, p5))

"/mnt/data/tradingview_bokeh_fixed.html"

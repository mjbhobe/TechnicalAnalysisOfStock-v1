import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Reuse the plotting function from earlier
def validate_symbol(symbol):
    try:
        info = yf.Ticker(symbol).info
        return 'shortName' in info
    except Exception:
        return False

def download_stock_data(symbol, periods):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5*365)
    datasets = {}
    for p in periods:
        interval = {'Daily': '1d', 'Monthly': '1mo', 'Yearly': '3mo'}[p]
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        if not data.empty:
            datasets[p] = data
    return datasets

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📈 Technical Chart & Recommendation (Powered by Gemini)")

# Sidebar
st.sidebar.header("Chart Configuration")
symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., TCS.NS)", value="TCS.NS")
validate_clicked = st.sidebar.button("✅ Validate Symbol")
symbol_valid = False

if validate_clicked:
    if validate_symbol(symbol):
        st.sidebar.success("Valid symbol ✔️")
        symbol_valid = True
    else:
        st.sidebar.error("Invalid symbol ❌")

selected_intervals = st.sidebar.multiselect(
    "Select Timeframes", ["Daily", "Monthly", "Yearly"], default=["Daily"]
)

indicator_options = ["EMA5", "EMA13", "EMA26", "EMA50", "EMA200", "MACD", "Stochastic", "RSI", "ADX"]
selected_indicators = st.sidebar.multiselect("Select Indicators", indicator_options)

generate_chart_clicked = st.sidebar.button("📊 Generate Charts")

if generate_chart_clicked:
    if not selected_intervals:
        st.sidebar.warning("Please select at least one timeframe")
    else:
        data_dict = download_stock_data(symbol, selected_intervals)
        if not data_dict:
            st.error("No data found for the selected timeframe.")
        else:
            st.session_state.generated_charts = []
            st.subheader(f"📉 Charts for {symbol}")
            for timeframe, df in data_dict.items():
                df = df.dropna().copy()
                df.index.name = "Date"
                df["Volume"] = df["Volume"].fillna(0)
                # Add fake indicator columns for demo (replace with real calc)
                for ind in selected_indicators:
                    df[ind] = df["Close"].rolling(14).mean()
                fig = plot_tradingview_style_chart(df, symbol=symbol, indicators=[i.lower() for i in selected_indicators])
                st.plotly_chart(fig, use_container_width=True)
                st.session_state.generated_charts.append((timeframe, fig))
            st.session_state.show_gemini = True

# Button for Gemini recommendation
if "show_gemini" in st.session_state and st.session_state.show_gemini:
    if st.button("🔮 Generate Recommendation"):
        for idx, (timeframe, fig) in enumerate(st.session_state.generated_charts):
            image_file = f"chart_{timeframe}.png"
            fig.write_image(image_file, width=1400, height=800)
            st.image(image_file, caption=f"{timeframe} Chart", use_column_width=True)

        st.info("Gemini-powered chart analysis will be here... [To be implemented]")

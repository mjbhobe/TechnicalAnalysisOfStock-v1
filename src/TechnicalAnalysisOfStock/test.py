from rich.console import Console
from rich import print
import yfinance as yf
from agno.utils.log import logger

from utils.download_data import download_stock_data_and_tai
from utils.candlestick_plot import (
    plot_technical_chart,
    plot_full_technical_chart_plotly,
    plot_tradingview_style_chart,
)

console = Console()


def is_valid_stock_symbol(symbol: str) -> bool:
    try:
        ticker = yf.Ticker(symbol.upper())
        # try to get info, should raise exception if invalid
        _ = ticker.info
        return True
    except Exception as e:
        logger.fatal(f"ERROR: {symbol.upper()} is not a valid stock symbol.")
        return False


# monthly, weekly, daily = download_stock_data_and_tai("RELIANCE.NS")
# console.print("[green] Prices[/green]")
# # NOTE: head() may display NaN values for most metrics!
# print(daily.head())
# console.print(f"[red]{'-'*80}[/red]")
# print(daily.tail())


# while True:
#     stock_symbol = console.input(
#         "[green]Enter stock symbol (as on Yahoo! Finance):[/green] "
#     )
#     stock_symbol = stock_symbol.strip().upper()
#     if not is_valid_stock_symbol(stock_symbol):
#         console.print(f"[red]{stock_symbol} does not appear to be a valid symbol!")
#         continue
#     if stock_symbol.lower() in ["bye", "quit", "exit"]:
#         break

#     monthly, weekly, daily = download_stock_data_and_tai(stock_symbol)
#     # console.print("[green] Prices[/green]")
#     # console.print("[yellow]Daily[/yellow]")
#     # # NOTE: head() may display NaN values for most metrics!
#     # console.print(f"[red]{'-' * 40}[/red]")
#     # print(daily.head())
#     # console.print(f"[pink]{'-' * 40}[/pink]")
#     # print(daily.tail())
#     # console.print("\n[yellow]Weekly[/yellow]")
#     # console.print(f"[red]{'-' * 40}[/red]")
#     # print(weekly.head())
#     # console.print(f"[pink]{'-' * 40}[/pink]")
#     # print(weekly.tail())
#     # console.print("\n[yellow]Monthly[/yellow]")
#     # console.print(f"[red]{'-' * 40}[/red]")
#     # print(monthly.head())
#     # console.print(f"[pink]{'-' * 40}[/pink]")
#     # print(monthly.tail())

#     # fig = plot_technical_chart(stock_symbol, daily)

stock_symbol = "TCS.NS"
monthly, weekly, daily = download_stock_data_and_tai(stock_symbol)
indicators = [
    "ohlc",
    # "volume",
    "ema5",
    "ema13",
    "ema26",
    "ema50",
    "ema200",
    "bollinger",
    "adx",
]
fig = plot_tradingview_style_chart(
    daily,
    stock_symbol,
    indicators=indicators,
)
fig.show()

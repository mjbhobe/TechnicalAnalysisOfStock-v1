from rich.console import Console
from rich import print
import pandas as pd
import utils
import utils.indicators as ta

console = Console()

_, _, daily = utils.download_stock_data("RELIANCE.NS")
# console.print("[green]Daily data:[/green]")
# console.print("[blue]head()[/blue]")
# print(daily.head())
# console.print("\n[yellow]tail()[/yellow]")
# print(daily.tail())
#
# print(f"EMA5: {ta.ema(daily["Close"], span=5).tail()}")
# print(f"EMA13: {ta.ema(daily["Close"], span=13).tail()}")
# print(f"EMA26: {ta.ema(daily["Close"], span=26).tail()}")
# print(f"EMA50: {ta.ema(daily["Close"], span=50).tail()}")
# print(f"EMA200: {ta.ema(daily["Close"], span=200).tail()}")

# EMAs
daily["EMA5"] = ta.ema(daily["Close"], span=5)
daily["EMA13"] = ta.ema(daily["Close"], span=13)
daily["EMA23"] = ta.ema(daily["Close"], span=23)
daily["EMA50"] = ta.ema(daily["Close"], span=50)
daily["EMA200"] = ta.ema(daily["Close"], span=200)
# bollinger band
sma_line, upper_bb, lower_bb = ta.bollinger_bands(daily["Close"])
daily["BB_SMA"] = sma_line
daily["BB_Upper"] = upper_bb
daily["BB_Lower"] = lower_bb
macd_line, signal_line, histogram = ta.macd(daily["Close"])
daily["MACD"] = macd_line
daily["MACD_Signal"] = signal_line
daily["MACD_Histo"] = histogram

console.print("[green]Daily price series & TAs[/green]")
print(daily.tail(20))

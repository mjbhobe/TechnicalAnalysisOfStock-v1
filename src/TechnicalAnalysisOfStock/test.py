from rich.console import Console
from rich import print
import pandas as pd
from utils.data import download_stock_data_and_indicators

console = Console()

_, _, daily = download_stock_data_and_indicators("RELIANCE.NS")
console.print("[green]Daily Prices[/green]")
print(daily.head())
console.print(f"[red]{'--'*80}[/red]")
print(daily.head())
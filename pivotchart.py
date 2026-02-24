import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def plot_stock_pivots(ticker, year):
    # 1. Download data
    start_date = f"{year-1}-01-01"
    end_date = f"{year}-12-31"
    print(f"Fetching data for {ticker}...")
    df = yf.download(ticker, start=start_date, end=end_date)
    
    if df.empty:
        print("No data found. Please check the ticker and year.")
        return

    # 2. Calculate Pivot Points from the PREVIOUS year's data
    # Adding .item() ensures we get a single number, not a "Series"
    prev_year = df.loc[str(year-1)]
    high_p = prev_year['High'].max().item()
    low_p = prev_year['Low'].min().item()
    close_p = prev_year['Close'].iloc[-1].item()
    
    # Formulas (as requested)
    pivot = (high_p + low_p + close_p) / 3
    r1 = (pivot * 2) - low_p
    s1 = (pivot * 2) - high_p

    # 3. Filter data for the CURRENT year only
    current_year_df = df.loc[str(year)]

    # 4. Plotting
    plt.figure(figsize=(12, 7))
    plt.plot(current_year_df.index, current_year_df['Close'], label=f'{ticker.upper()} Close', color='#1f77b4')
    
    # Draw horizontal lines
    plt.axhline(y=pivot, color='gray', linestyle='--', label=f'Pivot Point ({pivot:.2f})')
    plt.axhline(y=r1, color='red', linestyle='--', label=f'R1 Resistance ({r1:.2f})')
    plt.axhline(y=s1, color='green', linestyle='--', label=f'S1 Support ({s1:.2f})')

    # Formatting
    plt.title(f"{ticker.upper()} - {year} Price Action with Annual Pivots", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # In Codespaces, this will try to pop up a window. 
    # If it doesn't show, use plt.savefig('chart.png') instead.
    #plt.show()
plt.savefig('my_pivot_chart.png')
print("Chart saved as my_pivot_chart.png")
# Execution
user_ticker = input("Enter Stock Ticker (e.g., QQQ): ") or "QQQ"
user_year = int(input("Enter Year (e.g., 2024): ") or 2024)

plot_stock_pivots(user_ticker, user_year)
import yfinance as yf
import pandas as pd

def calculate_pivots_with_distance():
    # 1. User Inputs
    symbol = input("Enter Ticker (e.g., QQQ, SPY): ").strip().upper()
    print("Timeframes: annual, quarterly, monthly")
    timeframe = input("Enter timeframe: ").strip().lower()

    # 2. Fetch Data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2y")
    
    if df.empty:
        print("Error: Could not retrieve data.")
        return

    current_price = df['Close'].iloc[-1]

    # 3. Resample for the chosen period
    resample_map = {
        'annual': 'YE',      # Year End
        'quarterly': 'QE',   # Quarter End
        'monthly': 'ME'      # Month End
    }
    
    if timeframe not in resample_map:
        print("Invalid timeframe.")
        return

    resampled = df.resample(resample_map[timeframe]).agg({
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })

    if len(resampled) < 2:
        print("Error: Not enough historical data.")
        return
        
    prev_period = resampled.iloc[-2]
    H, L, C = prev_period['High'], prev_period['Low'], prev_period['Close']

    # 4. Standard Pivot Formulas
    P = (H + L + C) / 3
    R1 = (P * 2) - L
    S1 = (P * 2) - H
    R2 = P + (R1 - S1)
    S2 = P - (R1 - S1)
    R3 = H + 2 * (P - L)
    S3 = L - 2 * (H - P)

    levels = [
        ("Resistance 3 (R3)", R3),
        ("Resistance 2 (R2)", R2),
        ("Resistance 1 (R1)", R1),
        ("PIVOT POINT (P)", P),
        ("Support 1 (S1)", S1),
        ("Support 2 (S2)", S2),
        ("Support 3 (S3)", S3)
    ]

    # 5. Print Results Table
    header = f"\n{symbol} {timeframe.upper()} PIVOTS | Current Price: ${current_price:.2f}"
    print(header)
    print("=" * len(header))
    print(f"{'Level':<20} | {'Price':<10} | {'% Distance':<12} | {'Status'}")
    print("-" * 65)

    for name, val in levels:
        # Calculate raw percentage distance
        pct_dist = ((val / current_price) - 1) * 100
        
        # Round to nearest whole number and convert to string with %
        # Use :+d to include the + or - sign for the integer
        rounded_pct = f"{round(pct_dist):+d}%"
        
        status = "ABOVE (Resistance)" if val > current_price else "BELOW (Support)"
        
        # Printing with the updated rounded_pct string
        print(f"{name:<20} | ${val:>8.2f} | {rounded_pct:>10} | {status}")

    print("-" * 65)

if __name__ == "__main__":
    calculate_pivots_with_distance()

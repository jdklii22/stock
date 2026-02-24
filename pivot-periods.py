import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

def plot_candlestick_pivots(ticker, year, p_input):
    # Map letters to yfinance/pandas frequencies
    period_map = {
        'd': 'B',  # Business Day
        'w': 'W-MON', # Weekly (starting Monday)
        'm': 'ME', # Month End
        'q': 'QE', # Quarter End
        'a': 'YE'  # Year End
    }
    
    freq = period_map.get(p_input.lower(), 'YE')
    
    # 1. Fetch data (including previous year for calculation buffer)
    start_date = f"{year-1}-01-01"
    end_date = f"{year}-12-31"
    print(f"Fetching data for {ticker}...")
    
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    
    if df.empty:
        print("No data found.")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(ticker.upper(), axis=1, level=1)

    # 2. Resample to find H, L, C for the chosen period
    logic = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
    resampled = df.resample(freq).apply(logic)

    # 3. Calculate Pivot Points
    resampled['P'] = (resampled['High'] + resampled['Low'] + resampled['Close']) / 3
    resampled['R1'] = (resampled['P'] * 2) - resampled['Low']
    resampled['S1'] = (resampled['P'] * 2) - resampled['High']
    
    # Shift so the calculated levels apply to the FOLLOWING period
    pivot_levels = resampled[['P', 'R1', 'S1']].shift(1)

    # 4. Align levels to the daily chart (forward fill the gaps)
    # This creates the "Step" effect on a daily chart
    plot_data = pd.DataFrame(index=df.index).join(pivot_levels).ffill()
    
    # Filter for target year only
    current_year_df = df.loc[str(year)]
    plot_levels = plot_data.loc[str(year)]

    # 5. Build the Chart
    fig = go.Figure(data=[go.Candlestick(
        x=current_year_df.index,
        open=current_year_df['Open'],
        high=current_year_df['High'],
        low=current_year_df['Low'],
        close=current_year_df['Close'],
        name='Price'
    )])

    # Levels Configuration
    levels_config = [
        {'col': 'R1', 'name': 'R1 Resistance', 'color': '#FF4B4B'},
        {'col': 'P',  'name': 'Pivot Point',  'color': '#FFA500'},
        {'col': 'S1', 'name': 'S1 Support',    'color': '#00CC96'}
    ]

    for lvl in levels_config:
        fig.add_trace(go.Scatter(
            x=plot_levels.index,
            y=plot_levels[lvl['col']],
            name=lvl['name'],
            line=dict(color=lvl['color'], width=2, shape='hv'), # 'hv' = horizontal-then-vertical steps
            opacity=0.8
        ))

    fig.update_layout(
        title=f"{ticker.upper()} - {year} Price Action with {p_input.upper()} Pivots",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        xaxis_rangeslider_visible=False, # Removed for cleaner look with steps
        template="plotly_dark",
        height=800,
        hovermode="x unified"
    )

    fig.write_html("pivot_chart.html")
    print(f"\nSUCCESS! Created chart using {freq} frequency. Open 'pivot_chart.html' in Preview.")

if __name__ == "__main__":
    t = input("Ticker (e.g., TSLA): ").strip() or "TSLA"
    y = input("Year: ").strip() or "2024"
    p = input("Period - (d)aily, (w)eekly, (m)onthly, (q)uarterly, (a)nnually: ").strip().lower() or "a"
    
    plot_candlestick_pivots(t, int(y), p)

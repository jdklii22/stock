import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

def plot_interactive_pivots(ticker, year):
    # 1. Download data (Previous year + Current year)
    start_date = f"{year-1}-01-01"
    end_date = f"{year}-12-31"
    print(f"Fetching data for {ticker}...")
    
    # auto_adjust=True ensures we use split/dividend adjusted prices
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    
    if df.empty:
        print("No data found for that ticker and year.")
        return

    # 2. Extract Previous Year to calculate levels
    # Using .xs to handle potential MultiIndex columns from yfinance
    try:
        if isinstance(df.columns, pd.MultiIndex):
            prev_year_data = df.xs(ticker.upper(), axis=1, level=1).loc[str(year-1)]
            current_year_data = df.xs(ticker.upper(), axis=1, level=1).loc[str(year)]
        else:
            prev_year_data = df.loc[str(year-1)]
            current_year_data = df.loc[str(year)]
            
        high_p = float(prev_year_data['High'].max())
        low_p = float(prev_year_data['Low'].min())
        close_p = float(prev_year_data['Close'].iloc[-1])
    except KeyError:
        print(f"Error: Could not find data for the year {year-1} to calculate pivots.")
        return

    # 3. Pivot Formulas
    pivot = (high_p + low_p + close_p) / 3
    r1 = (pivot * 2) - low_p
    s1 = (pivot * 2) - high_p
    r2 = pivot + (high_p - low_p)

    # 4. Create the Interactive Plotly Figure
    fig = go.Figure()

    # Main Price Line
    fig.add_trace(go.Scatter(
        x=current_year_data.index, 
        y=current_year_data['Close'],
        mode='lines',
        name=f'{ticker.upper()} Price',
        line=dict(color='#1f77b4', width=2)
    ))

    # Define the levels to draw
    levels = [
        {'name': 'R2 Resistance', 'value': r2, 'color': 'rgba(255, 0, 0, 0.5)', 'dash': 'dot'},
        {'name': 'R1 Resistance', 'value': r1, 'color': 'red', 'dash': 'dash'},
        {'name': 'Pivot Point', 'value': pivot, 'color': 'orange', 'dash': 'dash'},
        {'name': 'S1 Support', 'value': s1, 'color': 'green', 'dash': 'dash'}
    ]

    for lvl in levels:
        # Add the horizontal line
        fig.add_hline(
            y=lvl['value'], 
            line_dash=lvl['dash'], 
            line_color=lvl['color'],
            annotation_text=f"{lvl['name']} ({lvl['value']:.2f})",
            annotation_position="bottom right"
        )

    # 5. Layout and Interactivity
    fig.update_layout(
        title=f"{ticker.upper()} - {year} Interactive Pivot Analysis",
        xaxis_title="Date",
        yaxis_title="Adjusted Price (USD)",
        hovermode="x unified",
        template="plotly_white",
        height=700
    )

    # Save as HTML (Best for Codespaces)
    fig.write_html("pivot_chart.html")
    print("\nSUCCESS!")
    print("1. Find 'pivot_chart.html' in the file list on the left.")
    print("2. Right-click it and select 'Open Preview'.")

# --- Run the Script ---
if __name__ == "__main__":
    ticker_input = input("Enter Stock Ticker (e.g., QQQ): ").strip() or "QQQ"
    year_input = input("Enter Year (e.g., 2024): ").strip() or "2024"
    plot_interactive_pivots(ticker_input, int(year_input))
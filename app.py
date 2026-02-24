import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Stock Pivot Analyzer", layout="wide")

st.title("📈 Stock Pivot Point Analyzer")
st.markdown("Enter a ticker and select your parameters to visualize price action against key pivot levels.")

# --- Sidebar Interface ---
st.sidebar.header("Chart Settings")
ticker = st.sidebar.text_input("Ticker (e.g., QQQ, TSLA, AAPL)", value="QQQ").upper()
year = st.sidebar.number_input("Year", min_value=2000, max_value=2026, value=2024)

period_options = {
    "Daily (d)": "B",
    "Weekly (w)": "W-MON",
    "Monthly (m)": "ME",
    "Quarterly (q)": "QE",
    "Annually (a)": "YE"
}
period_label = st.sidebar.selectbox("Pivot Period", options=list(period_options.keys()))
freq = period_options[period_label]

chart_type = st.sidebar.radio("Chart Type", ["Candlestick", "Line"])

# --- Data Processing ---
@st.cache_data # This prevents re-downloading data every time you toggle a setting
def get_data(ticker, year):
    start_date = f"{year-1}-01-01"
    end_date = f"{year}-12-31"
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    return df

if ticker:
    df = get_data(ticker, year)

    if not df.empty:
        # Clean MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(ticker, axis=1, level=1)

        # Resample for Pivot Calculations
        logic = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
        resampled = df.resample(freq).apply(logic)

        # Pivot Formulas
        resampled['P'] = (resampled['High'] + resampled['Low'] + resampled['Close']) / 3
        resampled['R1'] = (resampled['P'] * 2) - resampled['Low']
        resampled['S1'] = (resampled['P'] * 2) - resampled['High']
        
        # Shift and align to daily index
        pivot_levels = resampled[['P', 'R1', 'S1']].shift(1)
        plot_data = pd.DataFrame(index=df.index).join(pivot_levels).ffill()
        
        # Filter for the viewable year
        current_year_df = df.loc[str(year)]
        plot_levels = plot_data.loc[str(year)]

        # --- Plotly Chart ---
        fig = go.Figure()

        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=current_year_df.index,
                open=current_year_df['Open'], high=current_year_df['High'],
                low=current_year_df['Low'], close=current_year_df['Close'],
                name='Price'
            ))
        else:
            fig.add_trace(go.Scatter(x=current_year_df.index, y=current_year_df['Close'], 
                                     name='Close Price', line=dict(color='#1f77b4')))

        # Add Pivot Lines
        levels_config = [
            {'col': 'R1', 'name': 'R1 Resistance', 'color': '#FF4B4B'},
            {'col': 'P',  'name': 'Pivot Point',  'color': '#FFA500'},
            {'col': 'S1', 'name': 'S1 Support',    'color': '#00CC96'}
        ]

        for lvl in levels_config:
            fig.add_trace(go.Scatter(
                x=plot_levels.index, y=plot_levels[lvl['col']],
                name=lvl['name'],
                line=dict(color=lvl['color'], width=2, shape='hv'),
                opacity=0.8
            ))

        fig.update_layout(height=700, template="plotly_dark", hovermode="x unified",
                          xaxis_rangeslider_visible=(chart_type == "Candlestick"))

        st.plotly_chart(fig, use_container_width=True)
        
        # Display the math for reference
        st.subheader("Current Period Pivot Values")
        st.table(plot_levels.tail(1))

    else:
        st.error("No data found. Please check the ticker symbol.")

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Page Setup
st.set_page_config(page_title="Pivot Candlestick Chart", layout="wide")

st.title("🕯️ Annual Pivot Candlestick Analyzer")
st.markdown("Visualize stock price action against key annual support and resistance levels.")

# --- Sidebar Controls ---
st.sidebar.header("Chart Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="QQQ").strip().upper()
year = st.sidebar.number_input("Analysis Year", min_value=2000, max_value=2026, value=2024)

# --- Data Fetching & Logic ---
@st.cache_data(ttl=3600)
def get_candlestick_data(ticker, year):
    start_date = f"{year-1}-01-01"
    end_date = f"{year}-12-31"
    
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    return df

if ticker:
    df = get_candlestick_data(ticker, year)
    
    if not df.empty:
        try:
            # Handle MultiIndex and extract the requested year vs previous year
            if isinstance(df.columns, pd.MultiIndex):
                prev_year_data = df.xs(ticker, axis=1, level=1).loc[str(year-1)]
                current_year_data = df.xs(ticker, axis=1, level=1).loc[str(year)]
            else:
                prev_year_data = df.loc[str(year-1)]
                current_year_data = df.loc[str(year)]
                
            # Pivot Calculations
            high_p = float(prev_year_data['High'].max())
            low_p = float(prev_year_data['Low'].min())
            close_p = float(prev_year_data['Close'].iloc[-1])
            
            pivot = (high_p + low_p + close_p) / 3
            r1 = (pivot * 2) - low_p
            s1 = (pivot * 2) - high_p

            # --- Create Chart ---
            fig = go.Figure(data=[go.Candlestick(
                x=current_year_data.index,
                open=current_year_data['Open'],
                high=current_year_data['High'],
                low=current_year_data['Low'],
                close=current_year_data['Close'],
                name='Price Action'
            )])

            # Add Pivot Lines
            levels = [
                {'name': 'R1 (Resistance)', 'value': r1, 'color': '#FF4B4B'},
                {'name': 'Pivot Point', 'value': pivot, 'color': '#FFA500'},
                {'name': 'S1 (Support)', 'value': s1, 'color': '#00CC96'}
            ]

            for lvl in levels:
                fig.add_hline(
                    y=lvl['value'], 
                    line_dash="dash", 
                    line_color=lvl['color'],
                    annotation_text=f"{lvl['name']}: {lvl['value']:.2f}",
                    annotation_position="top left",
                    annotation_font_color=lvl['color']
                )

            # Layout Styling
            fig.update_layout(
                title=f"{ticker} - {year} Price Action & Annual Pivots",
                yaxis_title="Price (USD)",
                xaxis_title="Date",
                xaxis_rangeslider_visible=True,
                template="plotly_dark",
                height=800,
                hovermode="x unified"
            )

            # Display in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # --- Quick Stats ---
            col1, col2, col3 = st.columns(3)
            col1.metric("R1 Resistance", f"{r1:.2f}")
            col2.metric("Pivot Point", f"{pivot:.2f}")
            col3.metric("S1 Support", f"{s1:.2f}")

        except Exception as e:
            st.error(f"Error processing data: {e}")
            st.info("Check if the stock has history for the previous year.")
    else:
        st.error("No data found for this ticker.")

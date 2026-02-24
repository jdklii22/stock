import streamlit as st
import yfinance as yf
import pandas as pd

# Page setup
st.set_page_config(page_title="Pivot Distance Tracker", page_icon="🎯")

st.title("🎯 Pivot Point Distance Tracker")
st.markdown("Analyze how far the current price is from key psychological support and resistance levels.")

# --- Sidebar Inputs ---
st.sidebar.header("Parameters")
symbol = st.sidebar.text_input("Enter Ticker", value="QQQ").upper()
timeframe = st.sidebar.selectbox("Select Timeframe", ["Annual", "Quarterly", "Monthly"])

# --- Calculation Logic ---
@st.cache_data(ttl=3600)
def get_pivot_data(symbol, timeframe):
    resample_map = {'Annual': 'YE', 'Quarterly': 'QE', 'Monthly': 'ME'}
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2y")
    
    if df.empty:
        return None, None
        
    current_price = df['Close'].iloc[-1]
    
    # Resample
    resampled = df.resample(resample_map[timeframe]).agg({
        'High': 'max', 'Low': 'min', 'Close': 'last'
    })
    
    if len(resampled) < 2:
        return None, current_price
        
    prev_period = resampled.iloc[-2]
    H, L, C = prev_period['High'], prev_period['Low'], prev_period['Close']
    
    # Standard Pivot Formulas
    P = (H + L + C) / 3
    R1 = (P * 2) - L
    S1 = (P * 2) - H
    R2 = P + (R1 - S1)
    S2 = P - (R1 - S1)
    R3 = H + 2 * (P - L)
    S3 = L - 2 * (H - P)
    
    levels = [
        ("R3", R3), ("R2", R2), ("R1", R1),
        ("PIVOT (P)", P),
        ("S1", S1), ("S2", S2), ("S3", S3)
    ]
    
    return levels, current_price

# --- Main Interface ---
if symbol:
    levels, current_price = get_pivot_data(symbol, timeframe)
    
    if levels:
        st.metric(label=f"Current {symbol} Price", value=f"${current_price:.2f}")
        
        data_list = []
        for name, val in levels:
            pct_dist = ((val / current_price) - 1) * 100
            status = "Resistance (Above)" if val > current_price else "Support (Below)"
            
            # Formatting the distance: Round to nearest whole number and add %
            formatted_dist = f"{round(pct_dist)}%"
            
            data_list.append({
                "Level": name,
                "Price": round(val, 2),
                "% Distance": formatted_dist,
                "Status": status
            })
            
        pivot_df = pd.DataFrame(data_list)

        # Style the dataframe
        def color_status(val):
            color = '#ff4b4b' if 'Resistance' in val else '#00cc96'
            return f'color: {color}'

        st.subheader(f"{timeframe} Pivot Table")
        # Displaying with a clean table
        st.table(pivot_df.style.applymap(color_status, subset=['Status']))
        
        st.info("💡 **Positive %:** Price must rise to hit this level. **Negative %:** Price must fall to hit this level.")
        
    else:
        st.error("Could not retrieve enough data. Try a more common ticker (e.g., SPY).")

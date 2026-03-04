import streamlit as st
import yfinance as yf
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Stock Pivot Calculator", page_icon="📈")

# Title and Description
st.title("📈 Stock Pivot Point Calculator")
st.markdown("""
Calculate Standard Pivot Points based on the **previous completed period** (Annual, Quarterly, or Monthly).
""")

# --- Sidebar Inputs ---
st.sidebar.header("Configuration")
symbol = st.sidebar.text_input("Ticker Symbol", value="QQQ").strip().upper()
timeframe_option = st.sidebar.selectbox(
    "Timeframe",
    options=["Annual", "Quarterly", "Monthly"],
    index=1
)

# --- Helper Function ---
def calculate_pivots(symbol, timeframe_str):
    try:
        # 1. Fetch Data
        ticker = yf.Ticker(symbol)
        # Fetch 2 years to ensure we have enough history for resampling
        df = ticker.history(period="2y")

        if df.empty:
            return None, "Error: Could not retrieve data. Check ticker symbol."

        current_price = df["Close"].iloc[-1]

        # 2. Resample Mapping
        resample_map = {
            "Annual": "YE",
            "Quarterly": "QE",
            "Monthly": "ME",
        }
        resample_code = resample_map.get(timeframe_str)

        # 3. Resample Data
        resampled = df.resample(resample_code).agg(
            {"High": "max", "Low": "min", "Close": "last"}
        )
        
        # Drop rows with NaN values (incomplete periods)
        resampled = resampled.dropna()

        if len(resampled) < 2:
            return None, "Error: Not enough historical data to calculate previous period pivots."

        # 4. Get Previous Period Data
        # We use iloc[-2] because iloc[-1] is the current (incomplete) period
        prev_period = resampled.iloc[-2]
        H, L, C = prev_period["High"], prev_period["Low"], prev_period["Close"]

        # 5. Calculate Pivots
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
            ("Support 3 (S3)", S3),
        ]

        # 6. Build Results List
        results = []
        for name, val in levels:
            pct_dist = ((val / current_price) - 1) * 100
            status = "Resistance" if val > current_price else "Support"
            
            results.append({
                "Level": name,
                "Price": round(val, 2),
                "Distance (%)": f"{round(pct_dist):+d}%",
                "Status": status,
                "Raw Distance": pct_dist
            })

        # FIX: Return H, L, C in the result dictionary so they are accessible later
        return {
            "symbol": symbol,
            "timeframe": timeframe_str,
            "current_price": current_price,
            "data": results,
            "prev_high": H,
            "prev_low": L,
            "prev_close": C
        }, None

    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# --- Main Execution ---
if st.sidebar.button("Calculate Pivots", type="primary"):
    with st.spinner('Fetching data from Yahoo Finance...'):
        result, error = calculate_pivots(symbol, timeframe_option)

    if error:
        st.error(error)
    else:
        # Display Current Price Metric
        col1, col2, col3 = st.columns(3)
        col1.metric("Ticker", result['symbol'])
        col2.metric("Timeframe", result['timeframe'])
        col3.metric("Current Price", f"${result['current_price']:.2f}")

        st.divider()

        # Create DataFrame for display
        df_results = pd.DataFrame(result['data'])
        
        # Color map for Status column
        def color_status(val):
            color = '#ffcccc' if val == 'Resistance' else '#ccffcc'
            return f'background-color: {color}'

        # Display Table
        st.subheader("Pivot Levels")
        
        display_df = df_results[['Level', 'Price', 'Distance (%)', 'Status']].copy()
        
        st.dataframe(
            display_df.style.applymap(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )

        # Show Previous Period Data used for calculation (Accordion)
        with st.expander("View Calculation Data (Previous Period)"):
            st.write(f"Based on the previous completed {result['timeframe']} period:")
            # FIX: Access H, L, C from the result dictionary
            st.json({
                "High": round(result['prev_high'], 2),
                "Low": round(result['prev_low'], 2),
                "Close": round(result['prev_close'], 2)
            })
else:
    st.info("👈 Enter a ticker and click **Calculate Pivots** to begin.")

#!/usr/bin/env python3
"""
Stock Pivot Points CLI Calculator
Calculates Standard Floor Pivot Points across Monthly, Quarterly, and Annual
completed periods, with whole-number percentage distances and Markdown export.
"""

import os
import sys
import warnings

# Suppress 3rd-party library warnings (e.g. yfinance internal pandas deprecation notices)
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.simplefilter("ignore")

from datetime import datetime

import pandas as pd
import yfinance as yf

# Silence internal yfinance Pandas4Warning notices
try:
    if hasattr(yf, "utils") and hasattr(yf.utils, "Pandas4Warning"):
        warnings.filterwarnings("ignore", category=yf.utils.Pandas4Warning)
except Exception:
    pass

# ANSI Terminal Colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"

LEVEL_NAMES = [
    ("Resistance 3 (R3)", "R3"),
    ("Resistance 2 (R2)", "R2"),
    ("Resistance 1 (R1)", "R1"),
    ("PIVOT POINT (P)",   "P"),
    ("Support 1 (S1)",    "S1"),
    ("Support 2 (S2)",    "S2"),
    ("Support 3 (S3)",    "S3"),
]

def calculate_timeframe_pivots(df, resample_code):
    """
    Resample daily historical dataframe to the given frequency code,
    extract prior completed period (iloc[-2]), and calculate standard floor pivots.
    """
    resampled = df.resample(resample_code).agg(
        {"High": "max", "Low": "min", "Close": "last"}
    ).dropna()

    if len(resampled) < 2:
        return None, "Insufficient completed historical periods."

    prev_period = resampled.iloc[-2]
    H = float(prev_period["High"])
    L = float(prev_period["Low"])
    C = float(prev_period["Close"])
    period_label = str(prev_period.name.strftime('%Y-%m-%d') if hasattr(prev_period.name, 'strftime') else prev_period.name)

    P = (H + L + C) / 3.0
    R1 = (P * 2.0) - L
    S1 = (P * 2.0) - H
    R2 = P + (R1 - S1)
    S2 = P - (R1 - S1)
    R3 = H + 2.0 * (P - L)
    S3 = L - 2.0 * (H - P)

    return {
        "H": H, "L": L, "C": C, "period_label": period_label,
        "pivots": {
            "R3": R3, "R2": R2, "R1": R1, "P": P,
            "S1": S1, "S2": S2, "S3": S3
        }
    }, None

def process_ticker(symbol):
    """Fetch market data and compute Monthly, Quarterly, and Annual pivots."""
    symbol = symbol.strip().upper()
    print(f"\n{CYAN}Fetching 5-year market data for {BOLD}{symbol}{RESET}{CYAN}...{RESET}")

    ticker = yf.Ticker(symbol)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = ticker.history(period="5y")
    except Exception as e:
        print(f"{RED}Error fetching data from Yahoo Finance: {e}{RESET}")
        return

    if df is None or df.empty:
        print(f"{RED}Error: No price data found for ticker '{symbol}'. Please verify the symbol.{RESET}")
        return

    current_price = float(df["Close"].iloc[-1])
    latest_date = df.index[-1].strftime("%Y-%m-%d")

    # Resample and calculate for all 3 periods
    monthly_data, m_err = calculate_timeframe_pivots(df, "ME")
    quarterly_data, q_err = calculate_timeframe_pivots(df, "QE")
    annual_data, a_err = calculate_timeframe_pivots(df, "YE")

    if m_err or q_err or a_err:
        print(f"{YELLOW}Warning: Some periods could not be calculated:{RESET}")
        if m_err: print(f"  - Monthly: {m_err}")
        if q_err: print(f"  - Quarterly: {q_err}")
        if a_err: print(f"  - Annual: {a_err}")
        if not monthly_data and not quarterly_data and not annual_data:
            return

    # Build row data
    rows = []
    for full_name, code in LEVEL_NAMES:
        row = {"Level": full_name, "Code": code}
        for tf_name, tf_data in [("Monthly", monthly_data), ("Quarterly", quarterly_data), ("Annual", annual_data)]:
            if tf_data and code in tf_data["pivots"]:
                price = tf_data["pivots"][code]
                dist_pct = round(((price / current_price) - 1.0) * 100.0)
                row[tf_name] = {
                    "price": price,
                    "dist_pct": dist_pct,
                    "text": f"${price:.2f} ({dist_pct:+d}%)"
                }
            else:
                row[tf_name] = {"price": 0.0, "dist_pct": 0, "text": "N/A"}
        rows.append(row)

    # 1. Print Terminal Output
    print_terminal_table(symbol, current_price, latest_date, rows)

    # 2. Export Markdown File
    output_filename = f"{symbol}_pivots.md"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)
    export_markdown(output_path, symbol, current_price, latest_date, rows, monthly_data, quarterly_data, annual_data)
    print(f"\n{GREEN}✓ Markdown report saved to:{RESET} {BOLD}{output_path}{RESET}")

def print_terminal_table(symbol, current_price, latest_date, rows):
    """Format and print a combined side-by-side table in the terminal."""
    col_w_level = 22
    col_w_m = 25
    col_w_q = 25
    col_w_a = 25

    header_line = f"{'Level':<{col_w_level}} {'Monthly Price (% Dist)':<{col_w_m}} {'Quarterly Price (% Dist)':<{col_w_q}} {'Annual Price (% Dist)':<{col_w_a}}"
    separator = "─" * len(header_line)

    print(f"\n{BOLD}{'═' * len(header_line)}{RESET}")
    print(f"{BOLD}📈 {symbol} Pivot Points{RESET}  |  Current Price: {GREEN}${current_price:.2f}{RESET}  |  As of: {latest_date}")
    print(f"{BOLD}{'═' * len(header_line)}{RESET}")
    print(f"{BOLD}{header_line}{RESET}")
    print(f"{GRAY}{separator}{RESET}")

    for r in rows:
        code = r["Code"]
        if code.startswith("R"):
            color = RED
        elif code == "P":
            color = CYAN + BOLD
        else:
            color = GREEN

        level_str = f"{color}{r['Level']:<{col_w_level}}{RESET}"
        m_str = f"{r['Monthly']['text']:<{col_w_m}}"
        q_str = f"{r['Quarterly']['text']:<{col_w_q}}"
        a_str = f"{r['Annual']['text']:<{col_w_a}}"

        print(f"{level_str} {m_str} {q_str} {a_str}")

    print(f"{BOLD}{'═' * len(header_line)}{RESET}")

def export_markdown(path, symbol, current_price, latest_date, rows, m_data, q_data, a_data):
    """Generate a clean, professional Markdown report."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []
    md.append(f"# {symbol} — Stock Pivot Points Analysis")
    md.append("")
    md.append(f"> **Generated:** {now_str}  ")
    md.append(f"> **Current Market Price:** `${current_price:.2f}`  ")
    md.append(f"> **Market Data As Of:** `{latest_date}`  ")
    md.append("")
    md.append("## Pivot Points Summary (Floor Model)")
    md.append("")
    md.append("| Level | Monthly Price (% Dist) | Quarterly Price (% Dist) | Annual Price (% Dist) |")
    md.append("| :--- | :--- | :--- | :--- |")

    for r in rows:
        name = r["Level"]
        m_txt = r["Monthly"]["text"]
        q_txt = r["Quarterly"]["text"]
        a_txt = r["Annual"]["text"]

        # Bold pivot point for emphasis
        if r["Code"] == "P":
            md.append(f"| **{name}** | **{m_txt}** | **{q_txt}** | **{a_txt}** |")
        else:
            md.append(f"| {name} | {m_txt} | {q_txt} | {a_txt} |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## Underlying Calculation Data (Previous Completed Periods)")
    md.append("")
    md.append("| Period | Completed Period End | High | Low | Close |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")

    for label, d in [("Monthly", m_data), ("Quarterly", q_data), ("Annual", a_data)]:
        if d:
            md.append(f"| **{label}** | {d['period_label']} | `${d['H']:.2f}` | `${d['L']:.2f}` | `${d['C']:.2f}` |")
        else:
            md.append(f"| **{label}** | *N/A* | *N/A* | *N/A* | *N/A* |")

    md.append("")
    md.append("*Formulas: Floor Pivots: P = (H + L + C) / 3, R1 = 2P - L, S1 = 2P - H, R2 = P + (H - L), S2 = P - (H - L), R3 = H + 2(P - L), S3 = L - 2(H - P).*")
    md.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

def main():
    print(f"\n{BOLD}{CYAN}=== Stock Pivot Points Calculator (CLI) ==={RESET}")
    print(f"{GRAY}Computes Monthly, Quarterly & Annual Standard Floor Pivots with whole-number distances.{RESET}")

    # Check if a ticker was passed via command-line arguments
    if len(sys.argv) > 1:
        ticker_arg = sys.argv[1].strip()
        if ticker_arg:
            process_ticker(ticker_arg)

    # Interactive prompt loop
    while True:
        try:
            prompt_str = f"\n{BOLD}Enter ticker symbol{RESET} ({YELLOW}'q'{RESET} or {YELLOW}'quit'{RESET} to exit): "
            user_input = input(prompt_str).strip()

            if not user_input:
                continue

            if user_input.lower() in ("q", "quit", "exit"):
                print(f"{CYAN}Exiting. Have a profitable trading day! 👋{RESET}\n")
                break

            process_ticker(user_input)

        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Exiting. Goodbye! 👋{RESET}\n")
            break

if __name__ == "__main__":
    main()

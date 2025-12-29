import streamlit as st
import time
import datetime
import json
import os
import requests
import csv
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

SETTINGS_FILE = "settings.json"
TICKER_LISTS_FILE = "ticker_lists.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading settings: {e}")
    return {}

def load_ticker_lists():
    """Load saved ticker lists from file"""
    if os.path.exists(TICKER_LISTS_FILE):
        try:
            with open(TICKER_LISTS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.sidebar.error(f"Error loading ticker lists: {e}")
    return {}

def save_ticker_lists(ticker_lists):
    """Save ticker lists to file"""
    try:
        with open(TICKER_LISTS_FILE, "w") as f:
            json.dump(ticker_lists, f, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error saving ticker lists: {e}")

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error saving settings: {e}")

def auto_save_settings():
    # Only save if the data is actually in session state
    new_settings = {
        "tickers": st.session_state.get("tickers", ""),
        "timeframe": st.session_state.get("grid_tf", "3 Minutes"),
        "num_cols": st.session_state.get("num_cols", 2),
        "auto_refresh": st.session_state.get("auto_refresh", True),
        "refresh_interval": st.session_state.get("refresh_interval", 10),
        "mtf_tf1": st.session_state.get("mtf_tf1", "Daily"),
        "mtf_tf2": st.session_state.get("mtf_tf2", "15 Minutes"),
        "mtf_tf3": st.session_state.get("mtf_tf3", "3 Minutes"),
        "chart_height": st.session_state.get("chart_height", 350),
        "sort_by": st.session_state.get("sort_by", "Perf 30min"),
        "sort_order": st.session_state.get("sort_order", "DESC"),
        "finviz_cookie": st.session_state.get("finviz_cookie", ""),
        "show_metrics": st.session_state.get("show_metrics", True)
    }
    save_settings(new_settings)

def clean_tickers(tickers):
    """Clean a list of tickers or a comma-separated string."""
    if not tickers:
        return []
        
    if isinstance(tickers, str):
        # Support comma, space, or newline separation
        import re
        tickers = re.split(r'[,\s\n]+', tickers)
    
    cleaned = []
    for t in tickers:
        if not t: continue
        # Strip dots, spaces, and other non-alphanumeric trailing chars
        c = t.strip().upper().rstrip(".")
        if c and c not in cleaned:
            cleaned.append(c)
    return cleaned

def fetch_etf_holdings(etf_ticker):
    etf_ticker = etf_ticker.strip().upper()
    if not etf_ticker:
        return []
    
    # Yahoo Finance is more reliable for comprehensive top 10 holdings
    url = f"https://finance.yahoo.com/quote/{etf_ticker}/holdings/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    import time
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Increased timeout to 20s to handle Yahoo lag
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Yahoo Finance often renders table via JS, but data is in scripts
                extracted = []
            
                # Method 1: Try to find tickers in <a> tags within the holdings table
                links = soup.select('a[href*="/quote/"] span')
                for span in links:
                    text = span.text.strip()
                    if text.isupper() and 1 <= len(text) <= 5 and text != etf_ticker:
                        if text not in extracted:
                            extracted.append(text)
                
                # Method 2: Fallback search
                if len(extracted) < 5:
                    for a in soup.find_all('a', href=True):
                        if '/quote/' in a['href']:
                            parts = a['href'].split('/')
                            try:
                                ticker = parts[parts.index('quote') + 1].upper()
                                if ticker != etf_ticker and ticker.isalpha() and 1 <= len(ticker) <= 5:
                                    if ticker not in extracted:
                                        extracted.append(ticker)
                            except:
                                continue
                
                if extracted:
                    return extracted[:20]
            
            # If we reached here, status code wasn't 200 or no holdings found, so let it retry
        except (requests.timeout, requests.exceptions.ReadTimeout):
            if attempt < max_retries:
                time.sleep(2 * (attempt + 1))  # Exponential backoff
                continue
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1)
                continue
            st.sidebar.error(f"Error fetching Yahoo holdings: {e}")
            break
            
    return []

# Persistent session for better performance/reliability
if "requests_session" not in st.session_state:
    st.session_state["requests_session"] = requests.Session()

def fetch_sorted_tickers(tickers, sort_option):
    tickers = clean_tickers(tickers)
    ticker_str = ",".join(tickers)

    api_token = st.session_state.get("finviz_cookie", "").strip()

    # Updated column IDs based on current Finviz Custom view (v=152)
    # 0:No, 1:Ticker, 90:Perf 1m, 94:Perf 10m, 95:Perf 15m, 96:Perf 30m, 52:SMA20, 65:Price, 66:Change
    col_str = "0,1,90,94,95,96,52,65,66"

    # Use export API with auth token for Elite features
    if api_token:
        url = f"https://elite.finviz.com/export.ashx?v=152&c={col_str}&o={sort_option}&t={ticker_str}&auth={api_token}"
    else:
        url = f"https://finviz.com/screener.ashx?v=152&c={col_str}&o={sort_option}&t={ticker_str}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Increased timeout to 20s
            response = st.session_state["requests_session"].get(url, headers=headers, timeout=20)

            if response.status_code == 200:
                extracted = []

                # Check if response is CSV (from export API) or HTML (from screener)
                if api_token and 'export.ashx' in url:
                    # Parse CSV response
                    csv_reader = csv.reader(StringIO(response.text))
                    rows_data = list(csv_reader)
                    if len(rows_data) > 1:  # Skip header row
                        for row in rows_data[1:]:
                            if len(row) >= 2:
                                ticker_text = row[1].strip().upper()
                                if ticker_text and ticker_text in tickers:
                                    if ticker_text not in extracted:
                                        extracted.append(ticker_text)
                else:
                    # Parse HTML response
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the screener rows using modern and legacy selectors
                    rows = soup.select('tr.styled-row, tr.screener-body-row-nw, tr.screener-body-row-nb')
                    if not rows:
                        # Generic fallback for row extraction
                        rows = soup.find_all('tr', valign=['top', 'middle'])

                    for row in rows:
                        tds = row.find_all('td')
                        if len(tds) >= 2:
                            # The ticker is almost always in the second column (index 1)
                            ticker_a = tds[1].find('a')
                            if ticker_a:
                                ticker_text = ticker_a.text.strip().upper()
                                # Simple validation: tickers are 1-5 chars, mostly letters
                                if ticker_text.isalpha() and 1 <= len(ticker_text) <= 6:
                                    if ticker_text not in extracted:
                                        extracted.append(ticker_text)

                    # Special case: If row parsing failed entirely, try a global a.tab-link search
                    if not extracted:
                        for a in soup.select('a.tab-link, a.screener-link-primary'):
                            text = a.text.strip().upper()
                            if text.isalpha() and 1 <= len(text) <= 6:
                                if text not in extracted:
                                    extracted.append(text)

                # Preserve original tickers if they weren't found in the response
                sorted_tickers = [t for t in extracted if t in tickers]
                for t in tickers:
                    if t not in sorted_tickers:
                        sorted_tickers.append(t)
                return sorted_tickers

        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            if attempt < max_retries:
                time.sleep(2 * (attempt + 1))
                continue
            st.sidebar.error(f"Error sorting tickers: {e}")
            break
    return tickers

def fetch_ticker_metrics(tickers):
    tickers = clean_tickers(tickers)
    if not tickers:
        return {}

    ticker_str = ",".join(tickers)
    api_token = st.session_state.get("finviz_cookie", "").strip()

    col_str = "0,1,90,94,95,96,52,65,66"

    # Use export API with auth token for Elite features
    if api_token:
        url = f"https://elite.finviz.com/export.ashx?v=152&c={col_str}&t={ticker_str}&auth={api_token}"
    else:
        url = f"https://finviz.com/screener.ashx?v=152&c={col_str}&t={ticker_str}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }

    metrics_data = {}
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Increased timeout to 20s
            response = st.session_state["requests_session"].get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                # Check if response is CSV (from export API) or HTML (from screener)
                if api_token and 'export.ashx' in url:
                    # Parse CSV response
                    csv_reader = csv.reader(StringIO(response.text))
                    rows_data = list(csv_reader)
                    if len(rows_data) > 1:  # Skip header row
                        for row in rows_data[1:]:
                            if len(row) >= 9:
                                ticker = row[1].strip().upper()
                                if ticker in tickers:
                                    metrics_data[ticker] = {
                                        "perf_1m": row[2].strip(),
                                        "perf_10m": row[3].strip(),
                                        "perf_15m": row[4].strip(),
                                        "perf_30m": row[5].strip(),
                                        "sma20": row[6].strip(),
                                        "price": row[7].strip(),
                                        "change": row[8].strip()
                                    }
                else:
                    # Parse HTML response
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Find the screener rows using modern and legacy selectors
                    rows = soup.select('tr.styled-row, tr.screener-body-row-nw, tr.screener-body-row-nb')
                    if not rows:
                        rows = soup.find_all('tr', valign=['top', 'middle'])

                    for row in rows:
                        tds = row.find_all('td')
                        if len(tds) >= 9:
                            # Ticker is in second column (index 1)
                            ticker_a = tds[1].find('a')
                            if ticker_a:
                                ticker = ticker_a.text.strip().upper()
                                if ticker in tickers:
                                    metrics_data[ticker] = {
                                        "perf_1m": tds[2].text.strip(),
                                        "perf_10m": tds[3].text.strip(),
                                        "perf_15m": tds[4].text.strip(),
                                        "perf_30m": tds[5].text.strip(),
                                        "sma20": tds[6].text.strip(),
                                        "price": tds[7].text.strip(),
                                        "change": tds[8].text.strip()
                                    }

                if metrics_data:
                    return metrics_data

        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            if attempt < max_retries:
                time.sleep(2 * (attempt + 1))
                continue
            print(f"Error fetching metrics: {e}")
            break

    return metrics_data

# Load initial settings
saved_settings = load_settings()
chart_height = saved_settings.get("chart_height", 350)

# --- Page Configuration ---
st.set_page_config(
    page_title="Finviz Free - Realtime Chart Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Premium Look ---
st.markdown(f"""
    <style>
    /* Reduce top padding of the main container */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
    
    .main {{
        background-color: #ffffff;
    }}
    .stApp {{
        background: #ffffff;
    }}
    /* Global Image Scaling */
    [data-testid="stImage"] img {{
        height: {chart_height}px !important;
        object-fit: fill !important;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
    }}
    
    /* Increased spacing between charts (5x previous 4px) */
    [data-testid="stHorizontalBlock"] {{
        gap: 20px !important;
    }}
    [data-testid="stVerticalBlock"] {{
        gap: 8px !important;
    }}
    
    /* Hide Streamlit elements for a cleaner look */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Compact Info Bar Styling */
    .metric-info-bar {{
        background-color: #f8f9fa;
        padding: 2px 8px;
        border-radius: 2px;
        border: 1px solid #eeeeee;
        margin-top: 2px;
        margin-bottom: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        display: flex;
        justify-content: space-between;
        color: #666;
    }}
    .metric-item {{
        display: flex;
        gap: 3px;
    }}
    .pos-val {{ color: #00873c; font-weight: 600; }}
    .neg-val {{ color: #d60000; font-weight: 600; }}
    .neutral-val {{ font-weight: 600; }}
    
    /* Slimmer divider */
    hr {{
        margin: 0.5rem 0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---

# Initialize session state from saved settings
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["tickers"] = saved_settings.get("tickers", "MSFT,GOOGL,AAPL,SPY,AMZN,SMH")
    st.session_state["grid_tf"] = saved_settings.get("timeframe", "3 Minutes")
    st.session_state["num_cols"] = saved_settings.get("num_cols", 2)
    st.session_state["auto_refresh"] = saved_settings.get("auto_refresh", True)
    st.session_state["refresh_interval"] = saved_settings.get("refresh_interval", 10)
    st.session_state["mtf_tf1"] = saved_settings.get("mtf_tf1", "Daily")
    st.session_state["mtf_tf2"] = saved_settings.get("mtf_tf2", "15 Minutes")
    st.session_state["mtf_tf3"] = saved_settings.get("mtf_tf3", "3 Minutes")
    st.session_state["chart_height"] = saved_settings.get("chart_height", 350)
    st.session_state["sort_by"] = saved_settings.get("sort_by", "Perf 30min")
    st.session_state["sort_order"] = saved_settings.get("sort_order", "DESC")
    st.session_state["finviz_cookie"] = saved_settings.get("finviz_cookie", "")
    st.session_state["show_metrics"] = saved_settings.get("show_metrics", True)

# Callback function to handle automatic sorting
def handle_sort_change():
    # Only sort if something is selected
    if "sort_by" in st.session_state and "sort_order" in st.session_state:
        selected_label = st.session_state["sort_by"]
        order_raw = st.session_state["sort_order"]
        current_tickers = [t.strip().upper() for t in st.session_state["tickers"].split(",") if t.strip()]
        
        if not current_tickers:
            return

        if selected_label == "Ticker":
            # Local alphabetical sort
            sorted_list = sorted(current_tickers, reverse=(order_raw == "DESC"))
            st.session_state["tickers"] = ",".join(sorted_list)
            st.toast(f"Sorted by {selected_label} {order_raw}")
            auto_save_settings()
        else:
            # Finviz external sort
            finviz_order = sort_options[selected_label]
            if order_raw == "DESC":
                finviz_order = "-" + finviz_order
            
            try:
                sorted_list = fetch_sorted_tickers(current_tickers, finviz_order)
                if sorted_list == current_tickers and selected_label != "Ticker":
                    # If it returned the same, it might be a silent fail or elite restriction
                    if not st.session_state.get("finviz_cookie") and "perf" in finviz_order:
                        st.sidebar.warning("Intraday performance sorting requires a Finviz Elite cookie.")
                st.session_state["tickers"] = ",".join(sorted_list)
                st.toast(f"Sorted by {selected_label} {order_raw}")
                # Save settings after sorting to persist the new order
                auto_save_settings()
            except Exception as e:
                st.sidebar.error(f"Sorting failed: {e}")

# Callback function to handle ETF holdings loading
def handle_etf_load():
    input_text = st.session_state.get("etf_ticker", "").strip()
    if input_text:
        # Support multiple ETFs (comma separated)
        etf_tickers = [e.strip().upper() for e in input_text.split(",") if e.strip()]
        
        all_holdings = []
        for etf in etf_tickers:
            holdings = fetch_etf_holdings(etf)
            if holdings:
                # Add unique tickers to the list
                for h in holdings:
                    if h not in all_holdings:
                        all_holdings.append(h)
        
        if all_holdings:
            st.session_state["tickers"] = ",".join(all_holdings)
            # Automatically sort the new list before showing
            handle_sort_change()
            # Auto-save after update
            auto_save_settings()
        else:
            st.session_state["etf_error"] = f"No holdings found for {input_text}"
    else:
        st.session_state["etf_error"] = "Please enter one or more ETF tickers"


# Ticker Lists Management
with st.sidebar.expander("💾 Ticker Lists", expanded=False):
    # Load all saved ticker lists
    ticker_lists = load_ticker_lists()

    # Save current list
    st.markdown("**Save Current List**")
    col1, col2 = st.columns([3, 1])
    with col1:
        # Use value parameter to set default, don't modify session_state directly
        default_name = "" if st.session_state.get("clear_list_name") else st.session_state.get("new_list_name", "")
        new_list_name = st.text_input("List Name", value=default_name, key="new_list_name", label_visibility="collapsed", placeholder="Enter name...")
    with col2:
        if st.button("💾", help="Save current ticker list"):
            if new_list_name:
                current_tickers = st.session_state.get("tickers", "")
                if current_tickers.strip():
                    ticker_lists[new_list_name] = current_tickers
                    save_ticker_lists(ticker_lists)
                    st.toast(f"Saved '{new_list_name}'")
                    st.session_state["clear_list_name"] = True
                    st.rerun()
                else:
                    st.sidebar.error("No tickers to save")
            else:
                st.sidebar.error("Enter a name for the list")

    # Clear the flag after use
    if st.session_state.get("clear_list_name"):
        st.session_state["clear_list_name"] = False

    # Load saved list
    if ticker_lists:
        st.markdown("**Load Saved List**")
        selected_list = st.selectbox(
            "Select a list to load",
            options=[""] + list(ticker_lists.keys()),
            key="selected_ticker_list",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Load", disabled=not selected_list, width='stretch'):
                if selected_list:
                    st.session_state["tickers"] = ticker_lists[selected_list]
                    auto_save_settings()
                    st.toast(f"Loaded '{selected_list}'")
                    st.rerun()

        with col2:
            if st.button("Rename", disabled=not selected_list, width='stretch'):
                if selected_list:
                    st.session_state["rename_mode"] = selected_list
                    st.rerun()

        with col3:
            if st.button("Delete", disabled=not selected_list, width='stretch'):
                if selected_list:
                    del ticker_lists[selected_list]
                    save_ticker_lists(ticker_lists)
                    st.toast(f"Deleted '{selected_list}'")
                    st.rerun()

        # Rename mode
        if st.session_state.get("rename_mode"):
            old_name = st.session_state["rename_mode"]
            st.markdown(f"**Renaming: '{old_name}'**")
            col1, col2 = st.columns([3, 1])
            with col1:
                new_name = st.text_input("New Name", key="rename_input", label_visibility="collapsed", placeholder="Enter new name...")
            with col2:
                if st.button("✅", help="Confirm rename"):
                    if new_name and new_name != old_name:
                        if new_name in ticker_lists:
                            st.sidebar.error("Name already exists")
                        else:
                            ticker_lists[new_name] = ticker_lists[old_name]
                            del ticker_lists[old_name]
                            save_ticker_lists(ticker_lists)
                            st.session_state.pop("rename_mode")
                            st.toast(f"Renamed to '{new_name}'")
                            st.rerun()
                    else:
                        st.sidebar.error("Enter a different name")

            if st.button("❌ Cancel"):
                st.session_state.pop("rename_mode")
                st.rerun()
    else:
        st.info("No saved lists yet. Save your current ticker list above!")

st.sidebar.divider()

# Ticker Input (Top Level)
tickers_input = st.sidebar.text_area(
    "Enter Tickers",
    key="tickers",
    height=100,
    on_change=auto_save_settings,
    placeholder="AAPL, MSFT, NVDA\nor one per line:\nAAPL\nMSFT\nNVDA"
)

# ETF Holdings Loader
with st.sidebar.expander("📂 Load ETF Holdings", expanded=False):
    # Trigger on Enter automatically by using on_change
    st.text_input(
        "ETF Tickers (e.g. XLK, QQQ, SPY)", 
        key="etf_ticker",
        on_change=handle_etf_load,
        help="Press Enter to load holdings"
    )
    
    if "etf_error" in st.session_state and st.session_state["etf_error"]:
        st.error(st.session_state["etf_error"])
        st.session_state["etf_error"] = ""

# Sorting Options definition (moved up for the callback)
sort_options = {
    "Ticker": "ticker",
    "Perf 30min": "perfi30",
    "Perf 15min": "perfi15",
    "Perf 10min": "perfi10",
    "SMA20": "sma20",
    "Change": "change",
    "Change from Open": "changefromopen"
}

# 2. Sorting Controls (Automatic with callbacks)
selected_sort_label = st.sidebar.selectbox(
    "Sort By", 
    list(sort_options.keys()), 
    key="sort_by",
    on_change=lambda: [handle_sort_change(), auto_save_settings()],
    label_visibility="collapsed"
)

sort_order_raw = st.sidebar.radio(
    "Order",
    ["ASC", "DESC"],
    horizontal=True,
    key="sort_order",
    on_change=lambda: [handle_sort_change(), auto_save_settings()],
    label_visibility="collapsed"
)

st.sidebar.divider()

# Quick Metrics Table
st.sidebar.markdown("### 📊 Quick View")

# Get current tickers
current_tickers = clean_tickers(st.session_state.get("tickers", ""))

if current_tickers:
    # Fetch metrics for the table
    table_metrics = fetch_ticker_metrics(current_tickers)

    def get_color_for_value(val_str):
        """Return RGB color based on percentage value"""
        if not val_str or val_str == "-":
            return "rgba(255, 255, 255, 0)"
        try:
            val = float(val_str.replace('%', '').replace(',', ''))
            if val < 0:
                # Negative: Red shades (light red to dark red)
                # Map -5% to -0% -> dark red to light red
                intensity = min(abs(val) / 5.0, 1.0)  # Cap at 5% for max intensity
                # Light red (255, 200, 200) to dark red (180, 0, 0)
                r = int(180 + (255 - 180) * (1 - intensity))
                g = int(0 + 200 * (1 - intensity))
                b = int(0 + 200 * (1 - intensity))
                return f"rgba({r}, {g}, {b}, 0.6)"
            elif val > 0:
                # Positive: Green shades (light green to dark green)
                # Map 0% to 5% -> light green to dark green
                intensity = min(val / 5.0, 1.0)  # Cap at 5% for max intensity
                # Light green (200, 255, 200) to dark green (0, 120, 0)
                r = int(200 * (1 - intensity))
                g = int(200 + (120 - 200) * intensity)
                b = int(200 * (1 - intensity))
                return f"rgba({r}, {g}, {b}, 0.6)"
            else:
                return "rgba(255, 255, 255, 0)"
        except:
            return "rgba(255, 255, 255, 0)"

    # Helper function to convert percentage string to float for sorting
    def to_float(val_str):
        if not val_str or val_str == "-":
            return None
        try:
            return float(val_str.replace('%', '').replace(',', ''))
        except:
            return None

    # Prepare data for the table with color styling
    table_data = []
    for ticker in current_tickers:
        m = table_metrics.get(ticker, {})

        perf_30m_str = m.get("perf_30m", "-")
        perf_15m_str = m.get("perf_15m", "-")
        perf_1m_str = m.get("perf_1m", "-")
        change_str = m.get("change", "-")

        # Add color indicators
        def add_color_indicator(val_str):
            if val_str == "-":
                return val_str
            try:
                val = float(val_str.replace('%', '').replace(',', ''))
                if val > 0:
                    return f"🟢 {val_str}"
                elif val < 0:
                    return f"🔴 {val_str}"
                else:
                    return val_str
            except:
                return val_str

        table_data.append({
            "Ticker": ticker,
            "30m": add_color_indicator(perf_30m_str),
            "15m": add_color_indicator(perf_15m_str),
            "1m": add_color_indicator(perf_1m_str),
            "Chg": add_color_indicator(change_str),
            "30m_val": to_float(perf_30m_str),
        })

    # Create a dataframe and sort
    df = pd.DataFrame(table_data)
    df_sorted = df.sort_values(by="30m_val", ascending=False, na_position='last')
    df_display = df_sorted[["Ticker", "30m", "15m", "1m", "Chg"]]

    # Display using native Streamlit dataframe
    st.sidebar.dataframe(
        df_display,
        hide_index=True,
        width='stretch',
        height=min(len(table_data) * 35 + 38, 400)
    )
else:
    st.sidebar.info("Enter tickers to see quick metrics")

# Timeframe Options (shared across views)
tf_options = {
    "1 Minute": "i1",
    "3 Minutes": "i3",
    "5 Minutes": "i5",
    "15 Minutes": "i15",
    "30 Minutes": "i30",
    "Hourly": "h1",
    "Daily": "d",
    "Weekly": "w",
    "Monthly": "m"
}

st.sidebar.divider()

# Grouping Settings into Expanders
with st.sidebar.expander("🖼️ Grid View Settings", expanded=False):
    saved_tf = saved_settings.get("timeframe", "3 Minutes")
    tf_index = list(tf_options.keys()).index(saved_tf) if saved_tf in tf_options else 1
    selected_tf_label = st.selectbox("Select Grid Timeframe", list(tf_options.keys()), index=tf_index, key="grid_tf", on_change=auto_save_settings)
    selected_tf_code = tf_options[selected_tf_label]
    num_cols = st.slider("Grid Charts per row", 1, 4, saved_settings.get("num_cols", 2), key="num_cols", on_change=auto_save_settings)

with st.sidebar.expander("📊 Multi-Timeframe Settings", expanded=False):
    mtf_1_default = saved_settings.get("mtf_tf1", "Daily")
    mtf_2_default = saved_settings.get("mtf_tf2", "15 Minutes")
    mtf_3_default = saved_settings.get("mtf_tf3", "3 Minutes")

    mtf_tf1_label = st.selectbox("MTF 1 (Left)", list(tf_options.keys()), index=list(tf_options.keys()).index(mtf_1_default) if mtf_1_default in tf_options else 6, key="mtf_tf1", on_change=auto_save_settings)
    mtf_tf2_label = st.selectbox("MTF 2 (Middle)", list(tf_options.keys()), index=list(tf_options.keys()).index(mtf_2_default) if mtf_2_default in tf_options else 3, key="mtf_tf2", on_change=auto_save_settings)
    mtf_tf3_label = st.selectbox("MTF 3 (Right)", list(tf_options.keys()), index=list(tf_options.keys()).index(mtf_3_default) if mtf_3_default in tf_options else 1, key="mtf_tf3", on_change=auto_save_settings)

    mtf_tf1_code = tf_options[mtf_tf1_label]
    mtf_tf2_code = tf_options[mtf_tf2_label]
    mtf_tf3_code = tf_options[mtf_tf3_label]

with st.sidebar.expander("⚙️ General Settings", expanded=False):
    show_metrics = st.toggle("Show Metrics Info Bar", value=saved_settings.get("show_metrics", True), key="show_metrics", on_change=auto_save_settings)
    auto_refresh = st.toggle("Enable Auto-Refresh", value=saved_settings.get("auto_refresh", True), key="auto_refresh", on_change=auto_save_settings)
    refresh_interval = st.segmented_control(
        "Refresh Interval", 
        options=[10, 15, 20, 30], 
        selection_mode="single",
        default=saved_settings.get("refresh_interval", 10), 
        key="refresh_interval", 
        on_change=auto_save_settings,
        format_func=lambda x: f"{x}s"
    )
    selected_chart_height = st.slider("Chart Height", 100, 1000, chart_height, key="chart_height", on_change=auto_save_settings)
    
    st.text_input(
        "Finviz Elite API Token",
        value=saved_settings.get("finviz_cookie", ""),
        key="finviz_cookie",
        type="password",
        help="Enter your Finviz Elite API token to enable intraday performance metrics and Elite sorting features.",
        on_change=auto_save_settings
    )

# --- Main Dashboard ---
# Header removed as per user request

# Parse Tickers
ticker_list = clean_tickers(st.session_state["tickers"])

if not ticker_list:
    st.warning("Please enter at least one ticker.")
else:
    # Fetch metrics data
    with st.spinner("Fetching metrics..."):
        all_metrics = fetch_ticker_metrics(ticker_list)
    
    # Use a unique key for the refresh loop
    rev = int(time.time() * 1000)

    def get_color_class(val_str):
        if not val_str or val_str == "-": return "neutral-val"
        try:
            val = float(val_str.replace('%', '').replace(',', ''))
            if val > 0: return "pos-val"
            if val < 0: return "neg-val"
        except:
            pass
        return "neutral-val"

    def render_info_bar(ticker):
        # Even if metrics fail, we show the ticker name
        m = all_metrics.get(ticker, {})
        
        # Helper to format values
        p10 = m.get('perf_10m', '-')
        p15 = m.get('perf_15m', '-')
        p30 = m.get('perf_30m', '-')
        sma20 = m.get('sma20', '-')
        price = m.get('price', '-')
        change = m.get('change', '-')

        st.markdown(f"""
            <div class="metric-info-bar">
                <div class="metric-item">10m: <span class="{get_color_class(p10)}">{p10}</span></div>
                <div class="metric-item">15m: <span class="{get_color_class(p15)}">{p15}</span></div>
                <div class="metric-item">30m: <span class="{get_color_class(p30)}">{p30}</span></div>
                <div class="metric-item">SMA20: <span class="{get_color_class(sma20)}">{sma20}</span></div>
                <div class="metric-item">Price: <span class="neutral-val">{price}</span></div>
                <div class="metric-item">Change: <span class="{get_color_class(change)}">{change}</span></div>
            </div>
        """, unsafe_allow_html=True)

    # Tabs for different views
    tab1, tab2 = st.tabs(["🖼️ Grid View", "📊 Multi-Timeframe"])

    with tab1:
        # Create Grid
        cols = st.columns(num_cols)
        for i, ticker in enumerate(ticker_list):
            col_idx = i % num_cols
            with cols[col_idx]:
                chart_url = f"https://charts-node.finviz.com/chart.ashx?cs=&t={ticker}&tf={selected_tf_code}&s=linear&pm=0&am=0&ct=candle_stick&rev={rev}"
                st.image(chart_url, width="stretch")
                if show_metrics:
                    render_info_bar(ticker)

    with tab2:
        for ticker in ticker_list:
            cols = st.columns(3)
            # Column 1
            with cols[0]:
                chart_url1 = f"https://charts-node.finviz.com/chart.ashx?cs=&t={ticker}&tf={mtf_tf1_code}&s=linear&pm=0&am=0&ct=candle_stick&rev={rev}"
                st.image(chart_url1, width="stretch")
            
            # Column 2
            with cols[1]:
                chart_url2 = f"https://charts-node.finviz.com/chart.ashx?cs=&t={ticker}&tf={mtf_tf2_code}&s=linear&pm=0&am=0&ct=candle_stick&rev={rev}"
                st.image(chart_url2, width="stretch")
            
            # Column 3
            with cols[2]:
                chart_url3 = f"https://charts-node.finviz.com/chart.ashx?cs=&t={ticker}&tf={mtf_tf3_code}&s=linear&pm=0&am=0&ct=candle_stick&rev={rev}"
                st.image(chart_url3, width="stretch")
            
            # Info bar for MTF view - Moved below
            if show_metrics:
                render_info_bar(ticker)
            
            st.divider()

# --- Auto-Refresh Logic ---
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

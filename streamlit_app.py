import streamlit as st
import time
import datetime
import json
import os
import requests
from bs4 import BeautifulSoup

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading settings: {e}")
    return {}

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
        "refresh_interval": st.session_state.get("refresh_interval", 30),
        "mtf_tf1": st.session_state.get("mtf_tf1", "Daily"),
        "mtf_tf2": st.session_state.get("mtf_tf2", "15 Minutes"),
        "mtf_tf3": st.session_state.get("mtf_tf3", "3 Minutes"),
        "chart_height": st.session_state.get("chart_height", 350),
        "sort_by": st.session_state.get("sort_by", "Ticker"),
        "sort_order": st.session_state.get("sort_order", "ASC"),
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
    
    cookie = st.session_state.get("finviz_cookie", "").strip()
    base_url = "elite.finviz.com" if cookie else "finviz.com"
    
    # Updated column IDs based on current Finviz Custom view (v=152)
    # 0:No, 1:Ticker, 70:Perf 10m, 71:Perf 15m, 72:Perf 30m, 89:SMA20, 90:SMA50, 99:RSI, 121:Price, 118:Change
    col_str = "0,1,70,71,72,89,90,99,121,118"
    url = f"https://{base_url}/screener.ashx?v=152&c={col_str}&o={sort_option}&t={ticker_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    if cookie:
        headers['Cookie'] = cookie
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Increased timeout to 20s
            response = st.session_state["requests_session"].get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                # Fallback to standard view if custom view fails
                url_fallback = f"https://finviz.com/screener.ashx?v=111&o={sort_option}&t={ticker_str}"
                response = requests.get(url_fallback, headers=headers, timeout=20)
                
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                extracted = []
            
            # Find the screener rows using modern and legacy selectors
            rows = soup.select('tr.styled-row, tr.screener-body-row-nw, tr.screener-body-row-nb')
            if not rows:
                # Generic fallback for row extraction
                rows = soup.find_all('tr', valign=['top', 'middle'])
            
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    # The ticker is almost always in the second column (index 1)
                    # We look for the first link in that cell
                    ticker_a = tds[1].find('a')
                    if ticker_a:
                        ticker_text = ticker_a.text.strip().upper()
                        # Simple validation: tickers are 1-5 chars, mostly letters
                        if ticker_text.isalpha() and 1 <= len(ticker_text) <= 6:
                            if ticker_text not in extracted:
                                extracted.append(ticker_text)
            
            # Special case: If row parsing failed entirely, try a global a.tab-link search
            # but limit it to uppercase short strings to filter out navigation links
            if not extracted:
                for a in soup.select('a.tab-link, a.screener-link-primary'):
                    text = a.text.strip().upper()
                    if text.isalpha() and 1 <= len(text) <= 6:
                        if text not in extracted:
                            extracted.append(text)
            
            # Preserve original tickers if they weren't found in the response
            # (e.g. if some tickers were invalid for Finviz)
            sorted_tickers = [t for t in extracted if t in tickers]
            for t in tickers:
                if t not in sorted_tickers:
                    sorted_tickers.append(t)
            return sorted_tickers
            
            # If status not 200, retry or fail
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
    cookie = st.session_state.get("finviz_cookie", "").strip()
    base_url = "elite.finviz.com" if cookie else "finviz.com"
    
    col_str = "0,1,70,71,72,89,90,99,121,118"
    url = f"https://{base_url}/screener.ashx?v=152&c={col_str}&t={ticker_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    if cookie:
        headers['Cookie'] = cookie
    
    metrics_data = {}
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Increased timeout to 20s
            response = st.session_state["requests_session"].get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find the screener rows using modern and legacy selectors
                rows = soup.select('tr.styled-row, tr.screener-body-row-nw, tr.screener-body-row-nb')
                if not rows:
                    rows = soup.find_all('tr', valign=['top', 'middle'])
                    
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) >= 10:
                        # Ticker is in second column (index 1)
                        ticker_a = tds[1].find('a')
                        if ticker_a:
                            ticker = ticker_a.text.strip().upper()
                            if ticker in tickers:
                                metrics_data[ticker] = {
                                    "perf_10m": tds[2].text.strip(),
                                    "perf_15m": tds[3].text.strip(),
                                    "perf_30m": tds[4].text.strip(),
                                    "sma20": tds[5].text.strip(),
                                    "sma50": tds[6].text.strip(),
                                    "rsi": tds[7].text.strip(),
                                    "price": tds[8].text.strip(),
                                    "change": tds[9].text.strip()
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

# Initialize session state for tickers
if "tickers" not in st.session_state:
    st.session_state["tickers"] = saved_settings.get("tickers", "MSFT,GOOGL,AAPL,SPY,AMZN,SMH")

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


# Ticker Input (Top Level)
tickers_input = st.sidebar.text_area(
    "Enter Tickers (comma separated)",
    key="tickers",
    height=100,
    on_change=auto_save_settings
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
    "SMA 20": "sma20",
    "SMA 50": "sma50",
    "Change": "change"
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
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 300, saved_settings.get("refresh_interval", 30), key="refresh_interval", on_change=auto_save_settings)
    selected_chart_height = st.slider("Chart Height", 100, 1000, chart_height, key="chart_height", on_change=auto_save_settings)
    
    st.text_input(
        "Finviz Cookie (Optional - for Elite)", 
        value=saved_settings.get("finviz_cookie", ""), 
        key="finviz_cookie", 
        type="password",
        help="Paste your Finviz session cookie here to enable Elite sorting features.",
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
        rsi = m.get('rsi', '-')
        sma20 = m.get('sma20', '-')
        sma50 = m.get('sma50', '-')
        
        st.markdown(f"""
            <div class="metric-info-bar">
                <div class="metric-item">10m: <span class="{get_color_class(p10)}">{p10}</span></div>
                <div class="metric-item">15m: <span class="{get_color_class(p15)}">{p15}</span></div>
                <div class="metric-item">30m: <span class="{get_color_class(p30)}">{p30}</span></div>
                <div class="metric-item">RSI: <span class="neutral-val">{rsi}</span></div>
                <div class="metric-item">SMA20: <span class="{get_color_class(sma20)}">{sma20}</span></div>
                <div class="metric-item">SMA50: <span class="{get_color_class(sma50)}">{sma50}</span></div>
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

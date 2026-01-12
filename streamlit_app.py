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
import feedparser
import pytz

SETTINGS_FILE = "settings.json"
TICKER_LISTS_FILE = "ticker_lists.json"
TRADING_JOURNAL_FILE = "trading_journal.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading settings: {e}")
    return {}

def load_ticker_lists():
    """Load saved ticker lists from file with smart caching"""
    # Check if we need to bypass cache (after a save operation)
    bypass_cache = st.session_state.get("_ticker_lists_modified", False)

    if bypass_cache:
        # Reset flag and read directly from file
        st.session_state["_ticker_lists_modified"] = False
        if os.path.exists(TICKER_LISTS_FILE):
            try:
                with open(TICKER_LISTS_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                st.sidebar.error(f"Error loading ticker lists: {e}")
        return {}

    # Use cached version for normal reads
    cache_key = f"ticker_lists_cache_{os.path.getmtime(TICKER_LISTS_FILE) if os.path.exists(TICKER_LISTS_FILE) else 0}"
    if cache_key not in st.session_state:
        if os.path.exists(TICKER_LISTS_FILE):
            try:
                with open(TICKER_LISTS_FILE, "r") as f:
                    st.session_state[cache_key] = json.load(f)
            except Exception as e:
                st.sidebar.error(f"Error loading ticker lists: {e}")
                st.session_state[cache_key] = {}
        else:
            st.session_state[cache_key] = {}

    return st.session_state[cache_key]

def save_ticker_lists(ticker_lists):
    """Save ticker lists to file"""
    try:
        with open(TICKER_LISTS_FILE, "w") as f:
            json.dump(ticker_lists, f, indent=4)
        # Set flag to bypass cache on next load
        st.session_state["_ticker_lists_modified"] = True
    except Exception as e:
        st.sidebar.error(f"Error saving ticker lists: {e}")

def load_trading_journal():
    """Load trading journal from file with smart caching"""
    # Check if we need to bypass cache (after a save operation)
    bypass_cache = st.session_state.get("_journal_modified", False)

    if bypass_cache:
        # Reset flag and read directly from file
        st.session_state["_journal_modified"] = False
        if os.path.exists(TRADING_JOURNAL_FILE):
            try:
                with open(TRADING_JOURNAL_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    # Use cached version for normal reads
    cache_key = f"journal_cache_{os.path.getmtime(TRADING_JOURNAL_FILE) if os.path.exists(TRADING_JOURNAL_FILE) else 0}"
    if cache_key not in st.session_state:
        if os.path.exists(TRADING_JOURNAL_FILE):
            try:
                with open(TRADING_JOURNAL_FILE, "r") as f:
                    st.session_state[cache_key] = json.load(f)
            except:
                st.session_state[cache_key] = {}
        else:
            st.session_state[cache_key] = {}

    return st.session_state[cache_key]

def save_trading_journal(journal_data):
    """Save trading journal to file"""
    try:
        with open(TRADING_JOURNAL_FILE, "w") as f:
            json.dump(journal_data, f, indent=4)
        # Set flag to bypass cache on next load
        st.session_state["_journal_modified"] = True
    except Exception as e:
        st.error(f"Error saving journal: {e}")

def get_journal_entry(list_name, ticker):
    """Get journal entry for specific list+ticker combination"""
    journal = load_trading_journal()
    key = f"{list_name}_{ticker}"
    return journal.get(key, {}).get("journal", "")

def save_journal_entry(list_name, ticker, content):
    """Save journal entry for specific list+ticker combination"""
    journal = load_trading_journal()
    key = f"{list_name}_{ticker}"
    journal[key] = {
        "list_name": list_name,
        "ticker": ticker,
        "journal": content,
        "last_updated": datetime.datetime.now().isoformat()
    }
    save_trading_journal(journal)

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
        "cal_countries": st.session_state.get("cal_countries", ["USD"]),
        "cal_impacts": st.session_state.get("cal_impacts", ["🔴 High", "🟠 Medium"]),
        "index_cal_countries": st.session_state.get("index_cal_countries", ["USD"]),
        "index_cal_impacts": st.session_state.get("index_cal_impacts", ["🔴 High", "🟠 Medium"]),
        "news_watchlist_only": st.session_state.get("news_watchlist_only", False),
        "news_count": st.session_state.get("news_count", 50),
        "news_selected_tickers": st.session_state.get("news_selected_tickers", []),
        "news_source_filter": st.session_state.get("news_source_filter", []),
        "news_font_size": st.session_state.get("news_font_size", "Extra Large"),
        "rss_watchlist_only": st.session_state.get("rss_watchlist_only", False),
        "rss_count": st.session_state.get("rss_count", 50),
        "rss_selected_tickers": st.session_state.get("rss_selected_tickers", []),
        "rss_font_size": st.session_state.get("rss_font_size", "Extra Large"),
        "active_tab": st.session_state.get("active_tab", 0),
        "journal_selected_list": st.session_state.get("journal_selected_list", ""),
        "journal_selected_ticker": st.session_state.get("journal_selected_ticker", ""),
        "journal_news_font_size": st.session_state.get("journal_news_font_size", "Medium"),
        "ticker_view_search": st.session_state.get("ticker_view_search", ""),
        "ticker_view_timeframe": st.session_state.get("ticker_view_timeframe", "Daily"),
        "ticker_view_font_size": st.session_state.get("ticker_view_font_size", "Medium"),
        "ticker_view_filter_mode": st.session_state.get("ticker_view_filter_mode", "Enter Manually"),
        "ticker_view_sort_order": st.session_state.get("ticker_view_sort_order", "Desc (Top Gainers)"),
        "finviz_cookie": st.session_state.get("finviz_cookie", ""),
        "show_metrics": st.session_state.get("show_metrics", True)
    }
    
    # Handle date range serialization separately
    cal_range = st.session_state.get("cal_date_range")
    if isinstance(cal_range, (list, tuple)):
        new_settings["cal_date_range"] = [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in cal_range]
    elif hasattr(cal_range, 'isoformat'):
        new_settings["cal_date_range"] = [cal_range.isoformat()]
        
    save_settings(new_settings)

def clean_tickers(tickers):
    """Clean a list of tickers or a comma-separated string."""
    if not tickers:
        return []

    if isinstance(tickers, str):
        # Support comma, space, or newline separation
        import re
        tickers = re.split(r'[,\s\n]+', tickers)

    # Use set for O(1) deduplication lookups
    seen = set()
    cleaned = []
    for t in tickers:
        if not t: continue
        # Strip dots, spaces, and other non-alphanumeric trailing chars
        c = t.strip().upper().rstrip(".")
        if c and c not in seen:
            seen.add(c)
            cleaned.append(c)
    return cleaned

def fetch_major_news_movers(sort_desc=True, limit=50, signal_type="n_majornews"):
    """
    Fetch stocks from Finviz screener based on signal type, sorted by daily change.
    Uses caching to avoid re-fetching on every UI interaction.
    
    Args:
        sort_desc: If True, sort descending (top gainers first). If False, ascending (top losers first).
        limit: Maximum number of stocks to return.
        signal_type: Finviz signal type - "n_majornews", "n_upgrades", or "n_downgrades"
    
    Returns:
        List of dicts: [{"ticker": "AAPL", "change": "+5.53%", "company": "Apple Inc"}, ...]
    """
    # Cache key based on sort order and signal type
    cache_key = f"finviz_cache_{signal_type}_{'desc' if sort_desc else 'asc'}"
    cache_time_key = f"{cache_key}_time"
    
    # Check if we have cached data less than 60 seconds old
    cached_data = st.session_state.get(cache_key)
    cached_time = st.session_state.get(cache_time_key, 0)
    
    if cached_data and (time.time() - cached_time) < 60:
        return cached_data
    
    api_token = st.session_state.get("finviz_cookie", "").strip()
    
    # Build URL with sort order: -change for descending, change for ascending
    sort_param = "-change" if sort_desc else "change"
    
    if api_token:
        # Elite API export endpoint
        url = f"https://elite.finviz.com/export.ashx?v=111&s={signal_type}&f=sh_price_o10&o={sort_param}&auth={api_token}"
    else:
        # Public screener (HTML parsing required)
        url = f"https://finviz.com/screener.ashx?v=111&s={signal_type}&f=sh_price_o10&o={sort_param}"

    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    results = []
    
    try:
        session = st.session_state.get("requests_session", requests.Session())
        response = session.get(url, headers=headers, timeout=10)  # Reduced timeout
        
        if response.status_code == 200:
            if api_token and 'export.ashx' in url:
                # Parse CSV response from Elite API
                csv_reader = csv.reader(StringIO(response.text))
                rows_data = list(csv_reader)
                if len(rows_data) > 1:
                    # Get header to find column indices
                    header = [h.lower().strip() for h in rows_data[0]]
                    ticker_idx = header.index('ticker') if 'ticker' in header else 1
                    company_idx = header.index('company') if 'company' in header else 2
                    change_idx = header.index('change') if 'change' in header else -1
                    
                    for row in rows_data[1:limit+1]:
                        if len(row) > max(ticker_idx, company_idx):
                            ticker = row[ticker_idx].strip().upper()
                            company = row[company_idx].strip() if company_idx < len(row) else ""
                            change = row[change_idx].strip() if change_idx >= 0 and change_idx < len(row) else "-"
                            if ticker:
                                results.append({
                                    "ticker": ticker,
                                    "company": company,
                                    "change": change
                                })
            else:
                # Parse HTML response from public screener
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find table rows - try multiple selectors
                rows = soup.select('tr.styled-row')
                if not rows:
                    rows = soup.select('table.screener_table tr[valign="top"]')
                if not rows:
                    rows = soup.find_all('tr', {'valign': 'top'})
                
                for row in rows[:limit]:
                    tds = row.find_all('td')
                    if len(tds) >= 10:
                        # Ticker is in the second column (index 1)
                        ticker_link = tds[1].find('a')
                        if ticker_link:
                            ticker = ticker_link.text.strip().upper()
                            # Company name in third column
                            company = tds[2].text.strip() if len(tds) > 2 else ""
                            # Change is in column 10 (index 9) for v=111 view
                            change = tds[9].text.strip() if len(tds) > 9 else "-"
                            
                            if ticker and len(ticker) <= 6:
                                results.append({
                                    "ticker": ticker,
                                    "company": company[:30] + "..." if len(company) > 30 else company,
                                    "change": change
                                })
            
            # Cache the results
            if results:
                st.session_state[cache_key] = results
                st.session_state[cache_time_key] = time.time()
            
            return results
        else:
            st.error(f"Finviz returned status {response.status_code}")
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Finviz may be slow. Try again.")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)[:100]}")
    
    # Return cached data if available, even if stale
    if cached_data:
        return cached_data
    
    return results

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
                            elif len(row) >= 5:
                                # Guest view / fallback
                                ticker = row[1].strip().upper()
                                if ticker in tickers:
                                    metrics_data[ticker] = {
                                        "perf_1m": "-", "perf_10m": "-", "perf_15m": "-", "perf_30m": "-",
                                        "sma20": row[2].strip(),
                                        "price": row[3].strip(),
                                        "change": row[4].strip()
                                    }
                else:
                    # Parse HTML response
                    soup = BeautifulSoup(response.text, 'html.parser')
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
                        elif len(tds) >= 5:
                            # Guest view / fallback
                            ticker_a = tds[1].find('a')
                            if ticker_a:
                                ticker = ticker_a.text.strip().upper()
                                if ticker in tickers:
                                    metrics_data[ticker] = {
                                        "perf_1m": "-", "perf_10m": "-", "perf_15m": "-", "perf_30m": "-",
                                        "sma20": tds[2].text.strip(),
                                        "price": tds[3].text.strip(),
                                        "change": tds[4].text.strip()
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

@st.cache_data(ttl=300)
def fetch_forex_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_finviz_news(tickers=""):
    api_token = st.session_state.get("finviz_cookie", "").strip()
    if not api_token:
        return pd.DataFrame()
        
    url = f"https://elite.finviz.com/news_export.ashx?v=3&auth={api_token}"
    if tickers:
        url += f"&t={tickers}"
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = st.session_state["requests_session"].get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Clean column names (case-insensitive and strip)
            df.columns = [c.strip() for c in df.columns]
            
            # Map common variations to standard names
            col_map = {}
            for col in df.columns:
                lower_col = col.lower()
                if lower_col == "url": col_map[col] = "URL"
                elif lower_col == "date": col_map[col] = "Date"
                elif lower_col == "title": col_map[col] = "Title"
                elif lower_col == "source": col_map[col] = "Source"
                elif lower_col in ["ticker", "tickers"]: col_map[col] = "Ticker"
            
            if col_map:
                df = df.rename(columns=col_map)
            
            return df
    except Exception as e:
        print(f"Error fetching news: {e}")
    
    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_rss_news(tickers=""):
    """Fetch news from multiple RSS sources with timezone conversion (optimized with concurrent fetching)"""
    import concurrent.futures

    # Define RSS sources - using more reliable feeds
    rss_sources = {
        # General Market News
        'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
        'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
        'Reuters Business': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss',
        'CNBC Top News': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'Barrons': 'https://www.barrons.com/feed/rss/',
        'Investing.com': 'https://www.investing.com/rss/news.rss',
        'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
        'Google Finance': 'https://news.google.com/rss/search?q=stock+market+when:1d',
        'FT Markets': 'https://www.ft.com/markets?format=rss',
    }

    # Add Yahoo Finance if tickers provided
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(',') if t.strip()]
        if ticker_list:
            yahoo_tickers = ','.join(ticker_list[:10])  # Limit to 10 tickers
            rss_sources['Yahoo Finance'] = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={yahoo_tickers}'

    local_tz = pytz.timezone('Asia/Singapore')  # UTC+8
    failed_sources = []
    successful_sources = []
    all_news = []

    def fetch_single_source(source_name, url):
        """Fetch a single RSS source - for concurrent execution"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(url)

            # Check if feed has entries
            if not feed.entries:
                return (source_name, None, [])

            source_news = []
            for entry in feed.entries[:50]:  # Limit to 50 entries per source
                try:
                    # Extract data
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')

                    # Parse published time
                    published_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        # Convert struct_time to datetime
                        utc_time = datetime.datetime(*entry.published_parsed[:6])
                        utc_time = pytz.utc.localize(utc_time)
                        # Convert to local timezone
                        published_time = utc_time.astimezone(local_tz)
                    elif hasattr(entry, 'published'):
                        # Try to parse string date
                        try:
                            from dateutil import parser
                            utc_time = parser.parse(entry.published)
                            if utc_time.tzinfo is None:
                                utc_time = pytz.utc.localize(utc_time)
                            published_time = utc_time.astimezone(local_tz)
                        except:
                            published_time = datetime.datetime.now(local_tz)
                    else:
                        published_time = datetime.datetime.now(local_tz)

                    # Extract tickers if available
                    ticker_str = tickers if tickers else ''

                    source_news.append({
                        'Date': published_time,
                        'Title': title,
                        'URL': link,
                        'Source': source_name,
                        'Ticker': ticker_str
                    })

                except Exception as e:
                    continue

            return (source_name, True, source_news)

        except Exception as e:
            return (source_name, False, [])

    # Fetch all sources concurrently (up to 10 workers for 10 sources)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_source, name, url): name
                   for name, url in rss_sources.items()}

        for future in concurrent.futures.as_completed(futures):
            source_name, success, news_items = future.result()
            if success:
                successful_sources.append(source_name)
                all_news.extend(news_items)
            else:
                failed_sources.append(source_name)

    # Store source status in session state for UI display
    st.session_state['successful_sources'] = successful_sources
    st.session_state['failed_sources'] = failed_sources

    if all_news:
        df = pd.DataFrame(all_news)
        # Remove duplicates based on URL
        df = df.drop_duplicates(subset=['URL'], keep='first')
        # Sort by date descending
        df = df.sort_values('Date', ascending=False)
        return df

    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_ticker_rss_news(ticker):
    """Fetch Yahoo Finance RSS news for a specific ticker"""
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}"
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return []
        
        local_tz = pytz.timezone('Asia/Singapore')
        news_items = []
        
        for entry in feed.entries[:50]:  # Limit to 50 most recent (increased from 20)
            try:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                
                # Parse published time
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    utc_time = datetime.datetime(*entry.published_parsed[:6])
                    utc_time = pytz.utc.localize(utc_time)
                    published_time = utc_time.astimezone(local_tz)
                else:
                    published_time = datetime.datetime.now(local_tz)
                
                news_items.append({
                    'title': title,
                    'link': link,
                    'published': published_time
                })
            except:
                continue
        
        return news_items
    except:
        return []



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
    
    # Calendar Filter Defaults
    st.session_state["cal_countries"] = saved_settings.get("cal_countries", ["USD"])
    st.session_state["cal_impacts"] = saved_settings.get("cal_impacts", ["🔴 High", "🟠 Medium"])
    st.session_state["index_cal_countries"] = saved_settings.get("index_cal_countries", ["USD"])
    st.session_state["index_cal_impacts"] = saved_settings.get("index_cal_impacts", ["🔴 High", "🟠 Medium"])
    st.session_state["news_watchlist_only"] = saved_settings.get("news_watchlist_only", False)
    st.session_state["news_count"] = saved_settings.get("news_count", 50)
    st.session_state["news_selected_tickers"] = saved_settings.get("news_selected_tickers", [])
    st.session_state["news_source_filter"] = saved_settings.get("news_source_filter", [])
    st.session_state["news_font_size"] = saved_settings.get("news_font_size", "Extra Large")
    
    # RSS Feed News Defaults
    st.session_state["rss_watchlist_only"] = saved_settings.get("rss_watchlist_only", False)
    st.session_state["rss_count"] = saved_settings.get("rss_count", 50)
    st.session_state["rss_selected_tickers"] = saved_settings.get("rss_selected_tickers", [])
    st.session_state["rss_font_size"] = saved_settings.get("rss_font_size", "Extra Large")
    
    # Active tab and journal state
    st.session_state["active_tab"] = saved_settings.get("active_tab", 0)
    if "journal_selected_list" not in st.session_state:
        st.session_state["journal_selected_list"] = saved_settings.get("journal_selected_list", "")
    if "journal_selected_ticker" not in st.session_state:
        st.session_state["journal_selected_ticker"] = saved_settings.get("journal_selected_ticker", "")
    if "journal_news_font_size" not in st.session_state:
        st.session_state["journal_news_font_size"] = saved_settings.get("journal_news_font_size", "Medium")
    
    # Ticker View state
    # Only load manual search if filter mode is NOT Major News (prevents ghost charts)
    saved_filter_mode = saved_settings.get("ticker_view_filter_mode", "Enter Manually")
    if "ticker_view_search" not in st.session_state:
        if saved_filter_mode == "Changes With Major News":
            st.session_state["ticker_view_search"] = ""  # Clear to prevent ghost
        else:
            st.session_state["ticker_view_search"] = saved_settings.get("ticker_view_search", "")
    if "ticker_view_timeframe" not in st.session_state:
        st.session_state["ticker_view_timeframe"] = saved_settings.get("ticker_view_timeframe", "Daily")
    if "ticker_view_font_size" not in st.session_state:
        st.session_state["ticker_view_font_size"] = saved_settings.get("ticker_view_font_size", "Medium")
    
    cal_range_saved = saved_settings.get("cal_date_range")
    if cal_range_saved:
        try:
            st.session_state["cal_date_range"] = [datetime.date.fromisoformat(d) for d in cal_range_saved]
        except:
            st.session_state["cal_date_range"] = None
    else:
        st.session_state["cal_date_range"] = None

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
    # Show indicator if a list is currently loaded
    currently_loaded = st.session_state.get("currently_loaded_list", "")
    if currently_loaded:
        st.caption(f"📂 Active: **{currently_loaded}**")

    col1, col2 = st.columns([3, 1])
    with col1:
        # Auto-populate with currently loaded list name (if any)
        new_list_name = st.text_input("List Name", value=currently_loaded, key="new_list_name", label_visibility="collapsed", placeholder="Enter name...")
    with col2:
        if st.button("💾", help="Save/Update current ticker list"):
            if new_list_name:
                current_tickers = st.session_state.get("tickers", "")
                if current_tickers.strip():
                    # Check if overwriting existing list
                    is_update = new_list_name in ticker_lists
                    ticker_lists[new_list_name] = current_tickers
                    save_ticker_lists(ticker_lists)

                    # Show appropriate message
                    if is_update:
                        st.toast(f"✅ Updated '{new_list_name}'")
                    else:
                        st.toast(f"✅ Saved '{new_list_name}'")

                    # Keep the list name for future updates
                    st.session_state["currently_loaded_list"] = new_list_name
                    st.rerun()
                else:
                    st.sidebar.error("No tickers to save")
            else:
                st.sidebar.error("Enter a name for the list")

    # Load saved list
    if ticker_lists:
        st.markdown("**Load Saved List**")
        # Sort list names alphabetically
        sorted_list_names = sorted(ticker_lists.keys())
        selected_list = st.selectbox(
            "Select a list to load",
            options=[""] + sorted_list_names,
            key="selected_ticker_list",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Load", disabled=not selected_list, width='stretch'):
                if selected_list:
                    st.session_state["tickers"] = ticker_lists[selected_list]
                    # Remember which list was loaded for easy updates
                    st.session_state["currently_loaded_list"] = selected_list
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
                    # Clear currently loaded list if we deleted it
                    if st.session_state.get("currently_loaded_list") == selected_list:
                        st.session_state["currently_loaded_list"] = ""
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
                            # Update currently loaded list name if it was renamed
                            if st.session_state.get("currently_loaded_list") == old_name:
                                st.session_state["currently_loaded_list"] = new_name
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
    table_metrics = fetch_ticker_metrics(current_tickers) or {}

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
    # Fetch metrics data for both main list AND index tickers
    index_tickers = ["SPY", "QQQ", "SMH"]
    all_needed_tickers = list(dict.fromkeys(ticker_list + index_tickers)) # Preserve order and remove duplicates
    
    with st.spinner("Fetching metrics..."):
        all_metrics = fetch_ticker_metrics(all_needed_tickers) or {}
    
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
    # Use saved active tab index to restore user's position
    saved_tab_index = st.session_state.get("active_tab", 0)
    
    # Callback to save active tab
    def save_active_tab():
        # Streamlit doesn't directly expose which tab is active, so we track it via session state
        pass
    
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏛️ Index Multi-Timeframe",
        "🖼️ Grid View",
        "📊 Multi-Timeframe",
        "📅 Economic Calendar",
        "📰 Finviz News",
        "📡 RSS Feed News",
        "📝 Trading Journal by Theme",
        "🔍 Trading Journal by Ticker"
    ])
    
    # Note: Streamlit doesn't support default_index for tabs yet, 
    # but we save the state for future use when they add it

    with tab0:
        for ticker in index_tickers:
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
            
            # Info bar for MTF view
            if show_metrics:
                render_info_bar(ticker)
            
            st.divider()

        # Compact Today's Economic Calendar (Relocated to bottom)
        st.markdown("### 📅 Today's Economic Events")
        calendar_data = fetch_forex_calendar()
        if calendar_data:
            df_cal_all = pd.DataFrame(calendar_data)
            df_cal_all['date'] = pd.to_datetime(df_cal_all['date'])
            
            # Filter for today only
            today_date = datetime.date.today()
            df_today = df_cal_all[df_cal_all['date'].dt.date == today_date].copy()
            
            if not df_today.empty:
                # Map impact to emojis
                impact_map = {
                    "High": "🔴 High",
                    "Medium": "🟠 Medium",
                    "Low": "🟡 Low",
                    "Holiday": "⚪ Holiday"
                }
                df_today['Impact'] = df_today['impact'].map(impact_map).fillna(df_today['impact'])
                df_today['Time (ET)'] = df_today['date'].dt.strftime('%I:%M %p')
                
                # Selection for compact view (include date for styling)
                df_compact_base = df_today[['date', 'Time (ET)', 'country', 'Impact', 'title']]
                df_compact_base.columns = ['date', 'Time', 'Currency', 'Impact', 'Event']

                # Index Tab Calendar Filters
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    idx_countries = sorted(df_compact_base['Currency'].unique().tolist())
                    sel_countries = st.multiselect("Currency", options=idx_countries, key="index_cal_countries", on_change=auto_save_settings, placeholder="All")
                with f_col2:
                    idx_impacts = sorted(df_compact_base['Impact'].unique().tolist())
                    sel_impacts = st.multiselect("Impact", options=idx_impacts, key="index_cal_impacts", on_change=auto_save_settings, placeholder="All")

                # Apply index filters
                df_final = df_compact_base.copy()
                if sel_countries:
                    df_final = df_final[df_final['Currency'].isin(sel_countries)]
                if sel_impacts:
                    df_final = df_final[df_final['Impact'].isin(sel_impacts)]
                
                # Reverse Sort (Latest at top)
                df_final = df_final.sort_values('date', ascending=False)
                
                # Styling function
                def style_rows(row):
                    now = pd.Timestamp.now(tz=row['date'].tz)
                    if row['date'] > now:
                        return ['background-color: #FFD580; color: black'] * len(row) # Orange
                    else:
                        return ['background-color: #90EE90; color: black'] * len(row) # Light Green

                # Display as a compact table
                st.dataframe(
                    df_final.style.apply(style_rows, axis=1),
                    width="stretch",
                    height=200,
                    hide_index=True,
                    column_config={"date": None} # Hide date column
                )
            else:
                st.info("No economic events scheduled for today.")
        else:
            st.warning("⚠️ Could not load calendar data.")

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

    with tab3:
        st.subheader("📅 Forex Factory Economic Calendar")
        
        # Show last refresh time
        last_refresh_time = datetime.datetime.now().strftime("%I:%M %p")
        st.caption(f"🕐 Last Refreshed: {last_refresh_time}  (Refreshes every 1 hour)")
        
        calendar_data = fetch_forex_calendar()
        if calendar_data:
            df_cal = pd.DataFrame(calendar_data)
            
            # Convert date to datetime objects
            df_cal['date'] = pd.to_datetime(df_cal['date'])
            
            # Better date/time formatting
            df_cal['Day'] = df_cal['date'].dt.strftime('%a, %b %d')
            df_cal['Time (ET)'] = df_cal['date'].dt.strftime('%I:%M %p')
            
            # Map impact to emojis
            impact_map = {
                "High": "🔴 High",
                "Medium": "🟠 Medium",
                "Low": "🟡 Low",
                "Holiday": "⚪ Holiday"
            }
            df_cal['Impact'] = df_cal['impact'].map(impact_map).fillna(df_cal['impact'])

            # --- Interactive Filters ---
            with st.container():
                f_col1, f_col2, f_col3 = st.columns(3)
                
                with f_col1:
                    # Date Range Filter with "This Week" default
                    min_df_date = df_cal['date'].min().date()
                    max_df_date = df_cal['date'].max().date()
                    
                    # Calculate "This Week" (Sunday to Saturday)
                    today = datetime.date.today()
                    # If today is Sunday (weekday 6 in Sunday=0 system, but Python weekday() is Mon=0, Sun=6)
                    # Python weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
                    # We want Sunday (6) to be start of week.
                    days_since_sunday = (today.weekday() + 1) % 7
                    start_of_week = today - datetime.timedelta(days=days_since_sunday)
                    end_of_week = start_of_week + datetime.timedelta(days=6)
                    
                    # Use saved range if available, otherwise default to this week
                    current_range = st.session_state.get("cal_date_range")
                    if not current_range:
                        # Clamp to data range to avoid errors
                        default_val = (max(min_df_date, start_of_week), min(max_df_date, end_of_week))
                    else:
                        # Ensure saved values are clamped within the current data range
                        # This prevents errors when saved dates are outside current data
                        if isinstance(current_range, (list, tuple)) and len(current_range) == 2:
                            saved_start, saved_end = current_range
                            clamped_start = max(min_df_date, min(max_df_date, saved_start))
                            clamped_end = max(min_df_date, min(max_df_date, saved_end))
                            # Ensure start <= end after clamping
                            if clamped_start > clamped_end:
                                clamped_start = clamped_end
                            default_val = (clamped_start, clamped_end)
                        else:
                            # Single date or invalid format, default to this week
                            default_val = (max(min_df_date, start_of_week), min(max_df_date, end_of_week))

                    selected_range = st.date_input(
                        "Filter by Date Range",
                        value=default_val,
                        min_value=min_df_date,
                        max_value=max_df_date,
                        key="cal_date_range",
                        on_change=auto_save_settings
                    )
                    
                    # Convert to list for filtering logic below
                    filter_start = None
                    filter_end = None
                    if isinstance(selected_range, (list, tuple)) and len(selected_range) == 2:
                        filter_start, filter_end = selected_range
                    elif isinstance(selected_range, datetime.date):
                        filter_start = filter_end = selected_range
                    
                with f_col2:
                    countries = sorted(df_cal['country'].unique().tolist())
                    selected_countries = st.multiselect(
                        "Filter by Country", 
                        options=countries, 
                        key="cal_countries",
                        on_change=auto_save_settings,
                        placeholder="All Countries"
                    )
                    
                with f_col3:
                    impacts = sorted(df_cal['Impact'].unique().tolist())
                    selected_impacts = st.multiselect(
                        "Filter by Impact", 
                        options=impacts, 
                        key="cal_impacts",
                        on_change=auto_save_settings,
                        placeholder="All Impacts"
                    )

            # Apply filters
            df_filtered = df_cal.copy()
            
            # Application of date range filter
            if filter_start and filter_end:
                 df_filtered = df_filtered[
                     (df_filtered['date'].dt.date >= filter_start) & 
                     (df_filtered['date'].dt.date <= filter_end)
                 ]
            
            if selected_countries:
                df_filtered = df_filtered[df_filtered['country'].isin(selected_countries)]
            if selected_impacts:
                df_filtered = df_filtered[df_filtered['Impact'].isin(selected_impacts)]

            # Reorder and rename columns for display (include date for styling)
            cols_to_use = ['date', 'Day', 'Time (ET)', 'country', 'Impact', 'title']
            cols_names = ['date', 'Day', 'Time', 'Currency', 'Impact', 'Event']
            
            if 'actual' in df_cal.columns:
                cols_to_use.append('actual')
                cols_names.append('Actual')
            
            cols_to_use.extend(['forecast', 'previous'])
            cols_names.extend(['Forecast', 'Previous'])
            
            df_display_cal = df_filtered[cols_to_use]
            df_display_cal.columns = cols_names
            
            # Reverse Sort (Latest at top)
            df_display_cal = df_display_cal.sort_values('date', ascending=False)

            # Styling function
            def style_rows_full(row):
                now = pd.Timestamp.now(tz=row['date'].tz)
                if row['date'] > now:
                    return ['background-color: #FFD580; color: black'] * len(row) # Orange
                else:
                    return ['background-color: #90EE90; color: black'] * len(row) # Light Green

            # Styling: Filter for today and upcoming by default, or just show all
            st.dataframe(
                df_display_cal.style.apply(style_rows_full, axis=1),
                width="stretch",
                height=600,
                hide_index=True,
                column_config={"date": None} # Hide date column
            )
            st.info("💡 Data source: Forex Factory (via Fair Economy Feed). Time is in Eastern Time (ET).")
        else:
            st.warning("⚠️ Could not load calendar data at this moment.")

    with tab4:
        st.subheader("📰 Finviz Market News")
        
        # Show last refresh time
        last_refresh_time = datetime.datetime.now().strftime("%I:%M %p")
        st.caption(f"🕐 Last Refreshed: {last_refresh_time}  (Refreshes every 5 mins)")
        
        if not st.session_state.get("finviz_cookie"):
            st.warning("🔑 Finviz Elite API Token is required for the news feed.")
            st.info("Please enter your token in the sidebar settings.")
        else:
            # Controls for News
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                st.toggle("Watchlist Only", key="news_watchlist_only", value=False, on_change=auto_save_settings)
            with c2:
                st.selectbox("Results", [50, 100, 200], key="news_count", index=0, on_change=auto_save_settings)
            with c3:
                current_watchlist = clean_tickers(st.session_state.get("tickers", ""))
                st.multiselect("Drill-down Symbols", options=current_watchlist, key="news_selected_tickers", on_change=auto_save_settings)
            with c4:
                st.selectbox("Font Size", ["Small", "Medium", "Large", "Extra Large"], key="news_font_size", index=3, on_change=auto_save_settings)
            
            # Prep Ticker Filter String for API
            api_tickers = ""
            if st.session_state["news_watchlist_only"]:
                api_tickers = ",".join(current_watchlist)
            
            with st.spinner("Fetching latest news..."):
                df_news = fetch_finviz_news(api_tickers)
                
            if not df_news.empty:
                # Copy to avoid warnings
                df_news_display = df_news.copy()
                
                # Standardize columns to handle variations in CSV (Url vs URL)
                df_news_display.columns = [c.strip() for c in df_news_display.columns]
                
                # Check for standard columns
                required_cols = ['Date', 'Title', 'URL', 'Source', 'Ticker']
                has_cols = all(col in df_news_display.columns for col in required_cols)
                
                if has_cols:
                    # Filtering UI
                    n_col1, n_col2 = st.columns([2, 1])
                    with n_col1:
                        search_term = st.text_input("Search Headlines", placeholder="Type to filter...", key="news_search")
                    with n_col2:
                        sources_list = sorted(df_news_display['Source'].unique().tolist())
                        selected_sources = st.multiselect("Filter Sources", options=sources_list, key="news_source_filter", on_change=auto_save_settings, placeholder="All Sources")
                    
                    # Parse dates for comparison
                    df_news_display['parsed_date'] = pd.to_datetime(df_news_display['Date'], errors='coerce')
                    
                    # Categorize Source
                    mainstream_news = [
                        'Bloomberg', 'Reuters', 'BBC', 'The New York Times', 'WSJ', 'CNBC', 
                        'MarketWatch', 'Yahoo Finance', 'Fox Business', 'CNN', 'Barron\'s',
                        'Investor\'s Business Daily', 'The Wall Street Journal', 'Financial Times',
                        'Fortune', 'Forbes', 'Associated Press', 'AP News'
                    ]
                    
                    def categorize_source(s):
                        if any(mn in s for mn in mainstream_news):
                            return "News"
                        return "Blogs"
                    
                    df_news_display['Category'] = df_news_display['Source'].apply(categorize_source)
                    
                    # Apply filters
                    if search_term:
                        df_news_display = df_news_display[df_news_display['Title'].str.contains(search_term, case=False, na=False)]
                    if selected_sources:
                        df_news_display = df_news_display[df_news_display['Source'].isin(selected_sources)]
                    
                    # Secondary Ticker Filter (Local)
                    selected_symbols = st.session_state.get("news_selected_tickers", [])
                    if selected_symbols:
                        df_news_display = df_news_display[df_news_display['Ticker'].isin(selected_symbols)]

                    # Apply Result Limit
                    df_news_display = df_news_display.head(st.session_state.get("news_count", 50))
                    
                    def get_time_color(parsed_date):
                        if pd.isna(parsed_date): return "#ffffff", "#000000"
                        now = pd.Timestamp.now()
                        diff = now - parsed_date
                        is_today = parsed_date.date() == now.date()
                        is_yesterday = parsed_date.date() == (now.date() - pd.Timedelta(days=1))
                        
                        if diff < pd.Timedelta(hours=1):
                            return "#1B5E20", "white" # Dark Green
                        elif is_today:
                            return "#D4EDDA", "#155724" # Light Green
                        elif is_yesterday:
                            return "#FFF3CD", "#856404" # Yellow
                        else:
                            return "#7D2D26", "white" # Maple Red
                    
                    def render_news_grid(df_cat, category_name):
                        if df_cat.empty: return
                        st.subheader(f"📂 {category_name}")
                        
                        # Group by Source
                        sources_in_cat = sorted(df_cat['Source'].unique().tolist())
                        
                        # 3-column grid
                        cols = st.columns(3)
                        for idx, source in enumerate(sources_in_cat):
                            with cols[idx % 3]:
                                source_df = df_cat[df_cat['Source'] == source].head(10) # Max 10 per source
                                
                                # Render Source Box
                                html_lines = []
                                html_lines.append(f'<div style="background-color: #ffffff; border: 2px solid #1976D2; border-radius: 8px; padding: 12px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">')
                                html_lines.append(f'<h4 style="margin: 0 0 10px 0; color: #1565C0; font-weight: 700; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">📍 {source}</h4>')
                                
                                for _, row in source_df.iterrows():
                                    bg_color, txt_color = get_time_color(row['parsed_date'])
                                    # Intelligent time/date display
                                    if not pd.isna(row['parsed_date']):
                                        now = pd.Timestamp.now()
                                        if row['parsed_date'].date() >= (now.date() - pd.Timedelta(days=1)):
                                            time_str = row['parsed_date'].strftime('%H:%M')
                                        else:
                                            time_str = row['parsed_date'].strftime('%m-%d')
                                    else:
                                        time_str = "--:--"
                                    
                                    # Use single-line strings or ensure no leading spaces for HTML blocks
                                    # Dynamic font size based on user selection
                                    font_sizes = {"Small": "0.85rem", "Medium": "1.1rem", "Large": "1.4rem", "Extra Large": "1.7rem"}
                                    ticker_font_sizes = {"Small": "0.75rem", "Medium": "0.95rem", "Large": "1.2rem", "Extra Large": "1.5rem"}
                                    selected_font = st.session_state.get("news_font_size", "Extra Large")
                                    main_font = font_sizes.get(selected_font, "1.7rem")
                                    ticker_font = ticker_font_sizes.get(selected_font, "1.5rem")
                                    item_html = f'<div style="background-color: {bg_color}; color: {txt_color}; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px; font-size: {main_font}; line-height: 1.3;">'
                                    item_html += f'<span style="font-weight: 700; margin-right: 8px;">{time_str}</span>'
                                    item_html += f'<a href="{row["URL"]}" target="_blank" style="text-decoration: none; color: inherit; font-weight: 600;">{row["Title"]}</a>'
                                    item_html += f'<span style="display: block; font-size: {ticker_font}; color: #1565C0; font-weight: 500; margin-top: 2px;">{row["Ticker"]}</span>'
                                    item_html += '</div>'
                                    html_lines.append(item_html)
                                
                                html_lines.append('</div>')
                                st.markdown("".join(html_lines), unsafe_allow_html=True)

                    # Render Grid by Category
                    render_news_grid(df_news_display[df_news_display['Category'] == "News"], "Mainstream News")
                    st.divider()
                    render_news_grid(df_news_display[df_news_display['Category'] == "Blogs"], "Analysis & Blogs")
                    
                else:
                    st.warning("News data structure mismatch. Showing raw data.")
                    st.dataframe(df_news, width="stretch")
            else:
                st.info("No news found or unable to fetch feed.")

    with tab5:
        st.subheader("📡 RSS Feed News")
        
        # Show last refresh time
        last_refresh_time = datetime.datetime.now().strftime("%I:%M %p")
        st.caption(f"🕐 Last Refreshed: {last_refresh_time}  (Refreshes every 5 mins)")
        
        # Controls for News
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            st.toggle("Watchlist Only", key="rss_watchlist_only", value=False)
        with c2:
            st.selectbox("Results", [50, 100, 200], key="rss_count", index=0)
        with c3:
            current_watchlist = clean_tickers(st.session_state.get("tickers", ""))
            st.multiselect("Drill-down Symbols", options=current_watchlist, key="rss_selected_tickers")
        with c4:
            st.selectbox("Font Size", ["Small", "Medium", "Large", "Extra Large"], key="rss_font_size", index=3)
        
        # Prep Ticker Filter String for API
        api_tickers = ""
        if st.session_state.get("rss_watchlist_only"):
            api_tickers = ",".join(current_watchlist)
        elif st.session_state.get("rss_selected_tickers"):
            api_tickers = ",".join(st.session_state["rss_selected_tickers"])
        
        with st.spinner("Fetching latest RSS news..."):
            df_rss_news = fetch_rss_news(api_tickers)
        
        # Show feed status
        if 'successful_sources' in st.session_state and 'failed_sources' in st.session_state:
            with st.expander("📊 Feed Status", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Active Feeds ({len(st.session_state['successful_sources'])})")
                    for source in st.session_state['successful_sources']:
                        st.write(f"• {source}")
                with col2:
                    if st.session_state['failed_sources']:
                        st.error(f"❌ Failed Feeds ({len(st.session_state['failed_sources'])})")
                        for source in st.session_state['failed_sources']:
                            st.write(f"• {source}")
                    else:
                        st.success("All feeds working!")
            
        if not df_rss_news.empty:
            # Copy to avoid warnings
            df_news_display = df_rss_news.copy()
            
            # Filtering UI
            n_col1, n_col2 = st.columns([2, 1])
            with n_col1:
                search_term = st.text_input("Search Headlines", placeholder="Type to filter...", key="rss_news_search")
            with n_col2:
                sources_list = sorted(df_news_display['Source'].unique().tolist())
                selected_sources = st.multiselect("Filter Sources", options=sources_list, key="rss_source_filter", placeholder="All Sources")
            
            # Categorize Source
            mainstream_news = [
                'Bloomberg', 'Reuters', 'BBC', 'The New York Times', 'WSJ', 'CNBC', 
                'MarketWatch', 'Yahoo Finance', 'Fox Business', 'CNN', "Barron's",
                "Investor's Business Daily", 'The Wall Street Journal', 'Financial Times',
                'Fortune', 'Forbes', 'Associated Press', 'AP News', 'Investing.com',
                'WSJ Markets'
            ]
            
            def categorize_source(s):
                if any(mn in s for mn in mainstream_news):
                    return "News"
                return "Blogs"
            
            df_news_display['Category'] = df_news_display['Source'].apply(categorize_source)
            
            # Apply filters
            if search_term:
                df_news_display = df_news_display[df_news_display['Title'].str.contains(search_term, case=False, na=False)]
            if selected_sources:
                df_news_display = df_news_display[df_news_display['Source'].isin(selected_sources)]
            
            # Apply Result Limit
            df_news_display = df_news_display.head(st.session_state.get("rss_count", 50))
            
            def get_time_color(published_date):
                """Return background and text color based on article age"""
                if pd.isna(published_date): 
                    return "#ffffff", "#000000"
                
                now = pd.Timestamp.now(tz=pytz.timezone('Asia/Singapore'))
                
                # Ensure published_date is timezone-aware
                if published_date.tzinfo is None:
                    published_date = pytz.timezone('Asia/Singapore').localize(published_date)
                
                diff = now - published_date
                is_today = published_date.date() == now.date()
                is_yesterday = published_date.date() == (now.date() - pd.Timedelta(days=1))
                
                # Color coding based on age
                if diff < pd.Timedelta(minutes=10):
                    return "#1B5E20", "white"  # Dark Green - Very Recent
                elif diff < pd.Timedelta(hours=1):
                    return "#4CAF50", "white"  # Green - Recent
                elif is_today:
                    return "#D4EDDA", "#155724"  # Light Green - Today
                elif is_yesterday:
                    return "#FFF3CD", "#856404"  # Yellow - Yesterday
                else:
                    return "#F5F5F5", "#333333"  # Gray - Older
            
            def render_news_grid(df_cat, category_name):
                if df_cat.empty: 
                    return
                st.subheader(f"📂 {category_name}")
                
                # Group by Source
                sources_in_cat = sorted(df_cat['Source'].unique().tolist())
                
                # 3-column grid
                cols = st.columns(3)
                for idx, source in enumerate(sources_in_cat):
                    with cols[idx % 3]:
                        source_df = df_cat[df_cat['Source'] == source].head(10)  # Max 10 per source
                        
                        # Render Source Box
                        html_lines = []
                        html_lines.append(f'<div style="background-color: #ffffff; border: 2px solid #1976D2; border-radius: 8px; padding: 12px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">')
                        html_lines.append(f'<h4 style="margin: 0 0 10px 0; color: #1565C0; font-weight: 700; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">📍 {source}</h4>')
                        
                        for _, row in source_df.iterrows():
                            bg_color, txt_color = get_time_color(row['Date'])
                            
                            # Intelligent time/date display
                            if not pd.isna(row['Date']):
                                now = pd.Timestamp.now(tz=pytz.timezone('Asia/Singapore'))
                                if row['Date'].date() >= (now.date() - pd.Timedelta(days=1)):
                                    time_str = row['Date'].strftime('%H:%M')
                                else:
                                    time_str = row['Date'].strftime('%m-%d')
                            else:
                                time_str = "--:--"
                            
                            # Use single-line strings
                            # Dynamic font size based on user selection
                            font_sizes = {"Small": "0.85rem", "Medium": "1.1rem", "Large": "1.4rem", "Extra Large": "1.7rem"}
                            ticker_font_sizes = {"Small": "0.75rem", "Medium": "0.95rem", "Large": "1.2rem", "Extra Large": "1.5rem"}
                            selected_font = st.session_state.get("rss_font_size", "Extra Large")
                            main_font = font_sizes.get(selected_font, "1.7rem")
                            ticker_font = ticker_font_sizes.get(selected_font, "1.5rem")
                            item_html = f'<div style="background-color: {bg_color}; color: {txt_color}; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px; font-size: {main_font}; line-height: 1.3;">'
                            item_html += f'<span style="font-weight: 700; margin-right: 8px;">{time_str}</span>'
                            item_html += f'<a href="{row["URL"]}" target="_blank" style="text-decoration: none; color: inherit; font-weight: 600;">{row["Title"]}</a>'
                            if row["Ticker"]:
                                item_html += f'<span style="display: block; font-size: {ticker_font}; color: #1565C0; font-weight: 500; margin-top: 2px;">{row["Ticker"]}</span>'
                            item_html += '</div>'
                            html_lines.append(item_html)
                        
                        html_lines.append('</div>')
                        st.markdown("".join(html_lines), unsafe_allow_html=True)

            # Render Grid by Category
            render_news_grid(df_news_display[df_news_display['Category'] == "News"], "Mainstream News")
            st.divider()
            render_news_grid(df_news_display[df_news_display['Category'] == "Blogs"], "Analysis & Blogs")
            
        else:
            st.info("No RSS news found. Please check your internet connection or try again later.")

    with tab6:
        st.subheader("📝 Trading Journal")
        
        # Load ticker lists
        ticker_lists = load_ticker_lists()
        
        if not ticker_lists:
            st.warning("📋 No ticker lists found. Please create a ticker list first in the sidebar.")
            st.info("Go to the sidebar → 💾 Ticker Lists → Save your current ticker list")
        else:
            # Top controls
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                list_names = list(ticker_lists.keys())
                # Use saved list as default if it exists in current lists
                saved_list = st.session_state.get("journal_selected_list", "")
                default_list_index = list_names.index(saved_list) if saved_list in list_names else 0
                
                selected_list = st.selectbox(
                    "Select List",
                    options=list_names,
                    index=default_list_index,
                    key="journal_selected_list",
                    on_change=auto_save_settings
                )
            
            with col2:
                if selected_list:
                    # Get tickers from selected list
                    tickers_str = ticker_lists[selected_list]
                    tickers = clean_tickers(tickers_str)
                    
                    if tickers:
                        # Add 'All' option to show all tickers
                        ticker_options = ["All"] + tickers
                        
                        # Use saved ticker as default if it exists in current options
                        saved_ticker = st.session_state.get("journal_selected_ticker", "")
                        # If saved ticker is empty or not in options, default to "All" (index 0)
                        if saved_ticker and saved_ticker in ticker_options:
                            default_ticker_index = ticker_options.index(saved_ticker)
                        else:
                            default_ticker_index = 0
                        
                        selected_ticker = st.selectbox(
                            "Select Ticker",
                            options=ticker_options,
                            index=default_ticker_index,
                            key="journal_selected_ticker",
                            on_change=auto_save_settings
                        )
                    else:
                        st.warning("No tickers in this list")
                        selected_ticker = None
                else:
                    selected_ticker = None
            
            with col3:
                # Timeframe selector
                timeframe = st.radio(
                    "Chart Timeframe",
                    options=["Daily", "15m", "3m"],
                    horizontal=True,
                    key="journal_timeframe",
                    index=0
                )
                # Map timeframe to Finviz codes (matching codebase tf_options)
                tf_map = {"Daily": "d", "15m": "i15", "3m": "i3"}
                tf_code = tf_map[timeframe]
            
            with col4:
                # News font size selector
                journal_font_size = st.radio(
                    "News Font",
                    options=["Small", "Medium", "Large", "Extra Large"],
                    horizontal=True,
                    key="journal_news_font_size",
                    index=1,  # Default to Medium
                    on_change=auto_save_settings
                )
                # Map font sizes (Small=0.65rem, Medium=0.75rem, Large=0.85rem, Extra Large=0.95rem)
                font_size_map = {"Small": "0.65rem", "Medium": "0.75rem", "Large": "0.85rem", "Extra Large": "0.95rem"}
                news_font_size = font_size_map[journal_font_size]
            
            # List-level journal (appears after selecting list, before ticker selection)
            if selected_list:
                st.divider()
                st.markdown(f"### 📋 List Journal: {selected_list}")
                st.caption("Write notes about this list's overall theme, strategy, or criteria")
                
                # Load existing list journal
                list_journal_key = f"_LIST_{selected_list}"
                journal = load_trading_journal()
                existing_list_journal = journal.get(list_journal_key, {}).get("journal", "")
                
                # List journal text area with auto-save
                def save_list_journal_callback():
                    content = st.session_state.get("list_journal_text_area", "")
                    journal = load_trading_journal()
                    journal[list_journal_key] = {
                        "list_name": selected_list,
                        "ticker": "_LIST_",
                        "journal": content,
                        "last_updated": datetime.datetime.now().isoformat()
                    }
                    save_trading_journal(journal)
                
                list_journal_text = st.text_area(
                    "List Strategy & Theme",
                    value=existing_list_journal,
                    height=200,
                    key="list_journal_text_area",
                    on_change=save_list_journal_callback,
                    placeholder="Write about this list...\n\n• Overall theme or strategy\n• Selection criteria\n• Market conditions\n• Risk considerations\n• Expected timeframe",
                    label_visibility="collapsed"
                )
                
                # Info row for list journal
                info_col1, info_col2 = st.columns([1, 1])
                with info_col1:
                    char_count = len(list_journal_text)
                    st.caption(f"📝 {char_count} characters")
                
                with info_col2:
                    if list_journal_key in journal and journal[list_journal_key].get("last_updated"):
                        last_updated = journal[list_journal_key]["last_updated"]
                        try:
                            dt = datetime.datetime.fromisoformat(last_updated)
                            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                            st.caption(f"💾 Last saved: {formatted_time}")
                        except:
                            st.caption("💾 Auto-saved")
                    else:
                        st.caption("💾 Auto-save enabled")
            
            if selected_list and selected_ticker:
                st.divider()
                
                # Handle "All" option - show all tickers
                if selected_ticker == "All":
                    st.markdown(f"**📋 All Tickers in '{selected_list}'**")

                    # Get all tickers from the list
                    tickers_str = ticker_lists[selected_list]
                    all_tickers = clean_tickers(tickers_str)

                    # OPTIMIZATION: Load journal once before loop instead of per ticker
                    journal = load_trading_journal()
                    # OPTIMIZATION: Create timezone once instead of per news item
                    local_tz = pytz.timezone('Asia/Singapore')

                    # Display each ticker with chart and journal
                    for ticker in all_tickers:
                        st.markdown(f"### {ticker}")
                        
                        # Split layout for each ticker: Chart | News | Journal (1:1:1)
                        chart_col, news_col, journal_col = st.columns([1, 1, 1])
                        
                        with chart_col:
                            st.markdown(f"**📈 {timeframe} Chart**")
                            # Use charts-node URL format for all timeframes
                            chart_url = f"https://charts-node.finviz.com/chart.ashx?cs=&t={ticker}&tf={tf_code}&s=linear&pm=0&am=0&ct=candle_stick"
                            st.markdown(f'<div style="height: 300px; overflow: hidden;"><img src="{chart_url}" loading="lazy" style="width: 100%; height: 100%; object-fit: contain;"></div>', unsafe_allow_html=True)
                        
                        with news_col:
                            st.markdown(f"**📰 News**")
                            
                            # Fetch ticker-specific news
                            news_items = fetch_ticker_rss_news(ticker)
                            
                            if news_items:
                                # OPTIMIZATION: Build news HTML using list + join instead of string concatenation
                                news_parts = ['<div style="height: 300px; overflow-y: auto; padding: 8px; background-color: #fafafa; border-radius: 8px;">']
                                # OPTIMIZATION: Use pre-created timezone and calculate 'now' once
                                now = datetime.datetime.now(local_tz)
                                for item in news_items[:15]:  # Show 15 in All view
                                    # Calculate time ago and color
                                    diff = now - item['published']

                                    # Color coding based on age
                                    if diff.total_seconds() < 600:  # < 10 mins
                                        bg_color = "#1B5E20"
                                        txt_color = "white"
                                    elif diff.total_seconds() < 3600:  # < 1 hour
                                        bg_color = "#4CAF50"
                                        txt_color = "white"
                                    elif diff.days == 0:  # Today
                                        bg_color = "#D4EDDA"
                                        txt_color = "black"
                                    elif diff.days == 1:  # Yesterday
                                        bg_color = "#FFF3CD"
                                        txt_color = "black"
                                    else:  # Older
                                        bg_color = "#F5F5F5"
                                        txt_color = "black"

                                    time_str = item['published'].strftime("%H:%M")

                                    # Truncate title for compact display
                                    title = item['title'][:80] + "..." if len(item['title']) > 80 else item['title']
                                    title = title.replace('"', '&quot;')

                                    news_parts.append(f'<div style="background-color: {bg_color}; color: {txt_color}; padding: 6px 8px; margin-bottom: 6px; border-radius: 4px; font-size: {news_font_size}; line-height: 1.3;"><span style="font-weight: 700; opacity: 0.8; margin-right: 6px;">{time_str}</span><a href="{item["link"]}" target="_blank" style="text-decoration: none; color: inherit; font-weight: 600;">{title}</a></div>')
                                news_parts.append('</div>')
                                st.markdown(''.join(news_parts), unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="height: 300px; display: flex; align-items: center; justify-content: center; background-color: #fafafa; border-radius: 8px;"><span style="color: #888;">No news available</span></div>', unsafe_allow_html=True)
                        
                        with journal_col:
                            st.markdown(f"**📓 Journal Entry**")

                            # OPTIMIZATION: Use pre-loaded journal instead of calling get_journal_entry
                            key = f"{selected_list}_{ticker}"
                            existing_entry = journal.get(key, {}).get("journal", "")

                            # Unique key for each ticker's text area
                            journal_key = f"journal_{selected_list}_{ticker}"

                            # Journal text area with auto-save callback
                            def make_save_callback(list_name, tick):
                                def save_callback():
                                    content = st.session_state.get(f"journal_{list_name}_{tick}", "")
                                    save_journal_entry(list_name, tick, content)
                                return save_callback

                            journal_text = st.text_area(
                                f"Notes for {ticker}",
                                value=existing_entry,
                                height=300,
                                key=journal_key,
                                on_change=make_save_callback(selected_list, ticker),
                                placeholder=f"Write your notes for {ticker}...",
                                label_visibility="collapsed"
                            )

                            # Info row
                            info_col1, info_col2 = st.columns([1, 1])
                            with info_col1:
                                char_count = len(journal_text)
                                st.caption(f"📝 {char_count} characters")

                            with info_col2:
                                # OPTIMIZATION: Use already-loaded journal instead of re-loading
                                if key in journal and journal[key].get("last_updated"):
                                    last_updated = journal[key]["last_updated"]
                                    try:
                                        dt = datetime.datetime.fromisoformat(last_updated)
                                        formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                                        st.caption(f"💾 {formatted_time}")
                                    except:
                                        st.caption("💾 Auto-saved")
                                else:
                                    st.caption("💾 Auto-save")
                        
                        st.divider()
                
                else:
                    # Single ticker view
                    # OPTIMIZATION: Create timezone once for single ticker view
                    local_tz = pytz.timezone('Asia/Singapore')

                    # Split layout: Chart | News | Journal (1:1:1)
                    chart_col, news_col, journal_col = st.columns([1, 1, 1])

                    with chart_col:
                        st.markdown(f"**📈 {selected_ticker} - {timeframe} Chart**")
                        # Use charts-node URL format for all timeframes
                        chart_url = f"https://charts-node.finviz.com/chart.ashx?cs=&t={selected_ticker}&tf={tf_code}&s=linear&pm=0&am=0&ct=candle_stick"
                        st.markdown(f'<div style="height: 400px; overflow: hidden;"><img src="{chart_url}" loading="lazy" style="width: 100%; height: 100%; object-fit: contain;"></div>', unsafe_allow_html=True)

                    with news_col:
                        st.markdown(f"**📰 {selected_ticker} News**")

                        # Fetch ticker-specific news
                        news_items = fetch_ticker_rss_news(selected_ticker)

                        if news_items:
                            # OPTIMIZATION: Build news HTML using list + join instead of string concatenation
                            news_parts = ['<div style="height: 400px; overflow-y: auto; padding: 8px; background-color: #fafafa; border-radius: 8px;">']
                            # OPTIMIZATION: Calculate 'now' once instead of per item
                            now = datetime.datetime.now(local_tz)
                            for item in news_items:
                                # Calculate time ago and color
                                diff = now - item['published']

                                # Color coding based on age
                                if diff.total_seconds() < 600:  # < 10 mins
                                    bg_color = "#1B5E20"
                                    txt_color = "white"
                                elif diff.total_seconds() < 3600:  # < 1 hour
                                    bg_color = "#4CAF50"
                                    txt_color = "white"
                                elif diff.days == 0:  # Today
                                    bg_color = "#D4EDDA"
                                    txt_color = "black"
                                elif diff.days == 1:  # Yesterday
                                    bg_color = "#FFF3CD"
                                    txt_color = "black"
                                else:  # Older
                                    bg_color = "#F5F5F5"
                                    txt_color = "black"

                                time_str = item['published'].strftime("%H:%M")
                                title = item['title'].replace('"', '&quot;')

                                news_parts.append(f'<div style="background-color: {bg_color}; color: {txt_color}; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px; font-size: {news_font_size}; line-height: 1.3;"><span style="font-weight: 700; opacity: 0.8; margin-right: 8px;">{time_str}</span><a href="{item["link"]}" target="_blank" style="text-decoration: none; color: inherit; font-weight: 600;">{title}</a></div>')
                            news_parts.append('</div>')
                            st.markdown(''.join(news_parts), unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height: 400px; display: flex; align-items: center; justify-content: center; background-color: #fafafa; border-radius: 8px;"><span style="color: #888;">No news available</span></div>', unsafe_allow_html=True)
                    
                    with journal_col:
                        st.markdown(f"**📓 Journal Entry: {selected_list} → {selected_ticker}**")
                        
                        # Load existing journal entry
                        existing_entry = get_journal_entry(selected_list, selected_ticker)
                        
                        # Journal text area with auto-save callback
                        def save_journal_callback():
                            content = st.session_state.get("journal_text_area", "")
                            save_journal_entry(selected_list, selected_ticker, content)
                        
                        journal_text = st.text_area(
                            "Your notes and analysis",
                            value=existing_entry,
                            height=400,
                            key="journal_text_area",
                            on_change=save_journal_callback,
                            placeholder="Write your trading notes here...\n\n• Entry reasons\n• Technical analysis\n• Risk management\n• Exit strategy\n• Lessons learned",
                            label_visibility="collapsed"
                        )
                        
                        # Info row
                        info_col1, info_col2 = st.columns([1, 1])
                        with info_col1:
                            char_count = len(journal_text)
                            st.caption(f"📝 {char_count} characters")
                        
                        with info_col2:
                            # Get last updated timestamp
                            journal = load_trading_journal()
                            key = f"{selected_list}_{selected_ticker}"
                            if key in journal and journal[key].get("last_updated"):
                                last_updated = journal[key]["last_updated"]
                                try:
                                    dt = datetime.datetime.fromisoformat(last_updated)
                                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                                    st.caption(f"💾 Last saved: {formatted_time}")
                                except:
                                    st.caption("💾 Auto-saved")
                            else:
                                st.caption("💾 Auto-save enabled")
            else:
                st.info("👆 Select a list and ticker to start journaling")

    with tab7:
        st.subheader("🔍 Trading Journal by Ticker")
        st.caption("📅 Daily Planning Mode - Auto-refreshes every 30 minutes")

        # Quick Filter Row
        filter_col1, filter_col2 = st.columns([2, 1])
        
        with filter_col1:
            filter_mode = st.selectbox(
                "Quick Filter",
                options=["Enter Manually", "Changes With Major News", "Upgrades", "Downgrades"],
                key="ticker_view_filter_mode",
                on_change=auto_save_settings
            )
        
        with filter_col2:
            sort_order = st.selectbox(
                "Sort Order",
                options=["Desc (Top Gainers)", "Asc (Top Losers)"],
                key="ticker_view_sort_order",
                on_change=auto_save_settings
            )
        
        # Determine tickers based on filter mode
        # IMPORTANT: Only use ONE source of tickers based on filter mode (prevents ghost charts)
        search_tickers = []
        
        # Map filter modes to Finviz signal types
        signal_type_map = {
            "Changes With Major News": "n_majornews",
            "Upgrades": "n_upgrades",
            "Downgrades": "n_downgrades"
        }
        
        if filter_mode in signal_type_map:
            # Clear any manual entry to prevent ghost charts
            if "ticker_view_search" in st.session_state:
                st.session_state["ticker_view_search"] = ""
            
            # Fetch data based on selected filter
            sort_desc = sort_order == "Desc (Top Gainers)"
            signal_type = signal_type_map[filter_mode]
            
            with st.spinner(f"Fetching {filter_mode.lower()}..."):
                fetched_data = fetch_major_news_movers(sort_desc=sort_desc, limit=30, signal_type=signal_type)
            
            if fetched_data:
                # Create options with ticker and change percentage
                ticker_options = [f"{item['ticker']} ({item['change']})" for item in fetched_data]
                ticker_map = {f"{item['ticker']} ({item['change']})": item['ticker'] for item in fetched_data}
                
                # Multiselect for tickers - auto-populate with all tickers
                selected_options = st.multiselect(
                    "Select Ticker(s) to View",
                    options=ticker_options,
                    default=ticker_options,  # Auto-populate with all tickers
                    key=f"ticker_view_{signal_type}_selection",
                    placeholder=f"Select from {filter_mode.lower()}...",
                    on_change=auto_save_settings
                )
                
                # Convert selected options back to ticker symbols
                search_tickers = [ticker_map[opt] for opt in selected_options if opt in ticker_map]
            else:
                st.warning(f"⚠️ Could not fetch {filter_mode.lower()} data. Try again or use manual entry.")
        else:
            # Manual entry mode - original behavior
            search_input = st.text_input(
                "Enter Ticker Symbol(s)",
                key="ticker_view_search",
                placeholder="e.g., AAPL, SPY, QQQ",
                label_visibility="collapsed",
                on_change=auto_save_settings
            ).strip().upper()
            
            # Parse multiple tickers
            search_tickers = clean_tickers(search_input) if search_input else []


        # Only proceed if tickers are entered
        if search_tickers:
            # Load ticker lists and journal once for all tickers
            ticker_lists = load_ticker_lists()
            journal = load_trading_journal()
            local_tz = pytz.timezone('Asia/Singapore')

            # Settings row: Timeframe and Font Size
            col_tf, col_font = st.columns([1, 1])

            with col_tf:
                # Timeframe selection for chart (applies to all tickers)
                timeframe_options = {
                    "Daily": "d",
                    "15 Minutes": "i15",
                    "5 Minutes": "i5",
                    "3 Minutes": "i3",
                    "1 Minute": "i1"
                }
                timeframe_list = list(timeframe_options.keys())
                saved_tf = st.session_state.get("ticker_view_timeframe", "Daily")
                tf_index = timeframe_list.index(saved_tf) if saved_tf in timeframe_list else 0
                selected_tf = st.selectbox(
                    "Chart Timeframe",
                    options=timeframe_list,
                    index=tf_index,
                    key="ticker_view_timeframe",
                    on_change=auto_save_settings
                )
                tf_code = timeframe_options[selected_tf]

            with col_font:
                # Font size selection for news
                font_size_options = {
                    "Small": "10px",
                    "Medium": "12px",
                    "Large": "14px",
                    "Extra Large": "16px"
                }
                font_list = list(font_size_options.keys())
                saved_font = st.session_state.get("ticker_view_font_size", "Medium")
                font_index = font_list.index(saved_font) if saved_font in font_list else 1
                selected_font_size = st.selectbox(
                    "News Font Size",
                    options=font_list,
                    index=font_index,
                    key="ticker_view_font_size",
                    on_change=auto_save_settings
                )
                news_font_size = font_size_options[selected_font_size]

            # Loop through each ticker and display
            for ticker_index, search_ticker in enumerate(search_tickers):
                # Add separator between tickers (except for first one)
                if ticker_index > 0:
                    st.divider()

                # Find all lists containing this ticker
                lists_with_ticker = []
                if ticker_lists:
                    for list_name, tickers_str in ticker_lists.items():
                        tickers = clean_tickers(tickers_str)
                        if search_ticker in tickers:
                            # Get journal for this list+ticker combination
                            key = f"{list_name}_{search_ticker}"
                            journal_content = journal.get(key, {}).get("journal", "")
                            lists_with_ticker.append({
                                "list_name": list_name,
                                "journal": journal_content
                            })

                # Main layout: Chart | News+Journals | Ticker Journal (1:1:1)
                chart_col, middle_col, journal_col = st.columns([1, 1, 1])

                # LEFT COLUMN: Chart
                with chart_col:
                    st.markdown(f"**📈 {search_ticker} - {selected_tf}**")
                    chart_url = f"https://charts-node.finviz.com/chart.ashx?cs=&t={search_ticker}&tf={tf_code}&s=linear&pm=0&am=0&ct=candle_stick"
                    st.markdown(f'<div style="height: 600px; overflow: hidden;"><img src="{chart_url}" loading="lazy" style="width: 100%; height: 100%; object-fit: contain;"></div>', unsafe_allow_html=True)

                # MIDDLE COLUMN: News (top half) + List Journals (bottom half)
                with middle_col:
                    # NEWS SECTION (top half - 300px)
                    st.markdown(f"**📰 {search_ticker} News**")

                    # Fetch ticker-specific news
                    news_items = fetch_ticker_rss_news(search_ticker)

                    if news_items:
                        # Build news list (limit to 10 for compact view)
                        news_html_items = []
                        now = datetime.datetime.now(local_tz)

                        for item in news_items[:10]:
                            diff = now - item['published']

                            # Color coding based on age
                            if diff.total_seconds() < 600:  # < 10 mins
                                bg_color = "#1B5E20"
                                txt_color = "white"
                            elif diff.total_seconds() < 3600:  # < 1 hour
                                bg_color = "#4CAF50"
                                txt_color = "white"
                            elif diff.days == 0:  # Today
                                bg_color = "#D4EDDA"
                                txt_color = "black"
                            elif diff.days == 1:  # Yesterday
                                bg_color = "#FFF3CD"
                                txt_color = "black"
                            else:  # Older
                                bg_color = "#F5F5F5"
                                txt_color = "black"

                            time_str = item['published'].strftime("%H:%M")
                            title = item['title'][:60] + "..." if len(item['title']) > 60 else item['title']
                            title = title.replace('"', '&quot;').replace("'", '&#39;')

                            news_html_items.append(
                                f'<div style="background-color: {bg_color}; color: {txt_color}; padding: 4px 6px; margin-bottom: 4px; border-radius: 4px; font-size: {news_font_size}; line-height: 1.3;">'
                                f'<span style="font-weight: 700; margin-right: 4px;">{time_str}</span>'
                                f'<a href="{item["link"]}" target="_blank" style="text-decoration: none; color: inherit; font-weight: 600;">{title}</a>'
                                f'</div>'
                            )

                        # Render news container with all items
                        news_container = (
                            '<div style="height: 300px; overflow-y: auto; padding: 8px; background-color: #fafafa; border-radius: 8px; margin-bottom: 10px;">'
                            + ''.join(news_html_items) +
                            '</div>'
                        )
                        st.markdown(news_container, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="height: 300px; display: flex; align-items: center; justify-content: center; background-color: #fafafa; border-radius: 8px; margin-bottom: 10px;"><span style="color: #888;">No news available</span></div>', unsafe_allow_html=True)

                    # LIST JOURNALS SECTION (bottom half - 300px) - Using Expanders
                    st.markdown(f"**📋 Lists Containing {search_ticker}**")

                    if lists_with_ticker:
                        # Create a clean container without height to avoid rendering issues
                        st.markdown('<div style="max-height: 300px; overflow-y: auto;">', unsafe_allow_html=True)

                        for item in lists_with_ticker:
                            list_name = item['list_name']
                            journal_text = item['journal']

                            # Add emoji indicator: ✅ has journal, ⭕ empty
                            if journal_text and journal_text.strip():
                                emoji = "✅"
                            else:
                                emoji = "⭕"

                            # Create expander for each list with status emoji
                            with st.expander(f"{emoji} {list_name}", expanded=False):
                                if journal_text and journal_text.strip():
                                    st.markdown(f"**Journal Entry:**")
                                    st.text_area(
                                        "Journal content",
                                        value=journal_text,
                                        height=150,
                                        key=f"list_journal_view_{search_ticker}_{list_name}",
                                        disabled=True,  # Read-only
                                        label_visibility="collapsed"
                                    )
                                    st.caption(f"💡 *Edit this in the Trading Journal tab*")
                                else:
                                    st.info("No journal entry for this list yet")

                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"{search_ticker} is not found in any saved lists")

                # RIGHT COLUMN: Ticker-specific Journal
                with journal_col:
                    st.markdown(f"**📓 {search_ticker} Master Journal**")
                    st.caption("General notes for this ticker (not list-specific)")

                    # Use a special key for ticker-only journal
                    ticker_journal_key = f"_TICKER_{search_ticker}"
                    existing_ticker_journal = journal.get(ticker_journal_key, {}).get("journal", "")

                    # Journal text area with auto-save callback (unique key per ticker)
                    journal_area_key = f"ticker_view_journal_area_{search_ticker}"

                    def save_ticker_journal_callback():
                        content = st.session_state.get(journal_area_key, "")
                        journal_data = load_trading_journal()
                        journal_data[ticker_journal_key] = {
                            "list_name": "_TICKER_",
                            "ticker": search_ticker,
                            "journal": content,
                            "last_updated": datetime.datetime.now().isoformat()
                        }
                        save_trading_journal(journal_data)

                    ticker_journal_text = st.text_area(
                        f"Master notes for {search_ticker}",
                        value=existing_ticker_journal,
                        height=600,
                        key=journal_area_key,
                        on_change=save_ticker_journal_callback,
                        placeholder=f"General notes about {search_ticker}...\n\n• Company overview\n• Long-term thesis\n• Key catalysts\n• Overall strategy\n• Common patterns",
                        label_visibility="collapsed"
                    )

                    # Info row
                    info_col1, info_col2 = st.columns([1, 1])
                    with info_col1:
                        char_count = len(ticker_journal_text)
                        st.caption(f"📝 {char_count} characters")

                    with info_col2:
                        if ticker_journal_key in journal and journal[ticker_journal_key].get("last_updated"):
                            last_updated = journal[ticker_journal_key]["last_updated"]
                            try:
                                dt = datetime.datetime.fromisoformat(last_updated)
                                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                                st.caption(f"💾 {formatted_time}")
                            except:
                                st.caption("💾 Auto-saved")
                        else:
                            st.caption("💾 Auto-save enabled")
        else:
            st.info("👆 Enter a ticker symbol to view its chart, news, and journals")


# --- Smart Auto-Refresh Logic ---
# Only auto-refresh when NOT on news tabs to avoid interrupting reading
if auto_refresh:
    # Track which tab is active using session state
    # Streamlit doesn't directly expose active tab, so we use a workaround
    # We'll only refresh if the user hasn't interacted with news-specific filters recently
    
    # Check if user is likely on a news tab or Trading Journal by Ticker by looking at session keys
    on_finviz_news = 'news_search' in st.session_state or 'news_source_filter' in st.session_state
    on_rss_news = 'rss_news_search' in st.session_state or 'rss_source_filter' in st.session_state
    on_ticker_journal = 'ticker_view_filter_mode' in st.session_state or 'ticker_view_major_news_selection' in st.session_state
    
    # Different refresh intervals based on which tab is active
    if on_ticker_journal:
        # Trading Journal by Ticker - 30 minute refresh for daily planning
        time.sleep(1800)  # 30 minutes
        st.rerun()
    elif on_finviz_news or on_rss_news:
        # On news tabs, use a longer refresh interval (5 minutes) to be less disruptive
        time.sleep(300)  # 5 minutes
        st.rerun()
    elif 'cal_date_range' in st.session_state or 'cal_countries' in st.session_state:
        # Economic Calendar - 1 hour refresh since forex calendar doesn't change often
        time.sleep(3600)  # 1 hour
        st.rerun()
    else:
        # Default refresh interval for other tabs
        time.sleep(refresh_interval)
        st.rerun()

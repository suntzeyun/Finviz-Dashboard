# Finviz Expert Guide

A comprehensive guide to working with Finviz (Free and Elite) for building financial dashboards and trading tools. This document contains API insights, column mappings, best practices, and advanced techniques discovered through real-world implementation.

---

## 🎯 Overview

### What is Finviz?

**Finviz** (Financial Visualizations) is a powerful stock screening and charting platform offering:
- Real-time stock screener
- Interactive charts with technical indicators
- Market news and analysis
- ETF holdings data
- Economic calendar

### Free vs Elite Tiers

| Feature | Free | Elite ($39.50/month) |
|---------|------|---------------------|
| **Charts** | Daily only | Intraday (1m-4h) |
| **Performance Metrics** | Daily/Weekly/Monthly | 1m, 2m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h |
| **Sorting** | Limited | Full intraday sorting |
| **API Access** | Screen scraping only | Export API with auth token |
| **News** | Basic | Elite news feed |
| **Ads** | Yes | No |

---

## 🔑 1. API Access Methods

### 1.1 Elite Export API (Recommended)

**Authentication:**
```python
# Get API token from Finviz Elite account settings
api_token = "your_elite_api_token_here"

# Use in requests
url = f"https://elite.finviz.com/export.ashx?v=111&auth={api_token}"
```

**Export Endpoint:**
```
https://elite.finviz.com/export.ashx
```

**Parameters:**
- `v=111` - Version/view identifier
- `auth=YOUR_TOKEN` - Authentication token
- `c=COLUMNS` - Comma-separated column IDs (e.g., `0,1,65,66`)
- `f=FILTERS` - Screener filters
- `o=SORT` - Sort column (e.g., `-perfi30` for 30m desc)
- `r=RANGE` - Result range (e.g., `1,100`)

**Example Request:**
```python
import requests

api_token = "your_token"
columns = "0,1,94,95,96,52,65,66"  # Ticker, Company, 10m, 15m, 30m, SMA20, Price, Change

url = f"https://elite.finviz.com/export.ashx?v=111&auth={api_token}&c={columns}&o=-perfi30"

response = requests.get(url, timeout=20)
data = response.text  # CSV format
```

**Response Format:**
```csv
Ticker,Company,Perf 10min,Perf 15min,Perf 30min,SMA20,Price,Change
AAPL,Apple Inc.,+0.5%,+0.8%,+1.2%,-2.3%,150.25,+2.5%
MSFT,Microsoft Corporation,+0.3%,+0.6%,+0.9%,+1.5%,380.50,+1.8%
```

### 1.2 Free Tier (Screen Scraping)

**HTML Scraping:**
```python
from bs4 import BeautifulSoup
import requests

url = "https://finviz.com/screener.ashx?v=111"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find table rows
rows = soup.find_all('tr', class_='styled-row')
for row in rows:
    cells = row.find_all('td')
    ticker = cells[1].text.strip()
    # Extract other data...
```

**Limitations:**
- No intraday metrics
- Rate limiting
- HTML structure may change
- Slower than API

### 1.3 Chart URLs

**Chart Image Format:**
```
https://elite.finviz.com/chart.ashx?t=TICKER&ty=c&ta=1&p=TIMEFRAME&s=l
```

**Parameters:**
- `t=TICKER` - Stock symbol (e.g., AAPL)
- `ty=c` - Chart type (c=candle)
- `ta=1` - Technical analysis overlay
- `p=TIMEFRAME` - Timeframe code
- `s=l` - Size (l=large)

**Timeframe Codes:**
```python
TIMEFRAME_CODES = {
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
```

**Example:**
```python
ticker = "AAPL"
timeframe = "i15"  # 15-minute
chart_url = f"https://elite.finviz.com/chart.ashx?t={ticker}&ty=c&ta=1&p={timeframe}&s=l"
```

---

## 📊 2. Column ID Reference

### 2.1 Intraday Performance (Elite Only)

**Critical Discovery:** These are the correct column IDs for intraday metrics:

```python
INTRADAY_COLUMNS = {
    90: "Performance (1 Minute)",
    91: "Performance (2 Minutes)",
    92: "Performance (3 Minutes)",
    93: "Performance (5 Minutes)",
    94: "Performance (10 Minutes)",   # ⭐ Most used
    95: "Performance (15 Minutes)",   # ⭐ Most used
    96: "Performance (30 Minutes)",   # ⭐ Most used
    97: "Performance (1 Hour)",
    98: "Performance (2 Hours)",
    99: "Performance (4 Hours)"
}
```

**Common Mistake:**
```python
# ❌ WRONG - These return IPO dates, not performance!
columns = "70,71,72"

# ✅ CORRECT - Use these for intraday performance
columns = "94,95,96"
```

### 2.2 Essential Columns

**Price & Change:**
```python
PRICE_COLUMNS = {
    65: "Price",                    # Current price
    66: "Change",                   # % change from previous close
    60: "Change from Open",         # % change from today's open
    61: "Gap",                      # Gap % from previous close
    72: "After-Hours Change",       # After-hours % change
    81: "Prev Close",              # Previous close price
    86: "Open",                    # Today's open
    87: "High",                    # Today's high
    88: "Low"                      # Today's low
}
```

**Technical Indicators:**
```python
TECHNICAL_COLUMNS = {
    52: "20-Day SMA",              # ⭐ SMA20 (% distance)
    53: "50-Day SMA",              # SMA50 (% distance)
    54: "200-Day SMA",             # SMA200 (% distance)
    59: "RSI (14)",                # Relative Strength Index
    49: "ATR",                     # Average True Range
    48: "Beta"                     # Stock beta
}
```

**Volume:**
```python
VOLUME_COLUMNS = {
    67: "Volume",                  # Current volume
    63: "Average Volume",          # Average daily volume
    64: "Relative Volume"          # Volume vs average
}
```

**Fundamentals:**
```python
FUNDAMENTAL_COLUMNS = {
    4: "Market Cap",
    5: "P/E",
    6: "Forward P/E",
    7: "PEG",
    8: "P/S",
    9: "P/B",
    12: "Dividend Yield",
    32: "ROA",
    33: "ROE",
    39: "Gross Margin",
    40: "Operating Margin",
    41: "Profit Margin"
}
```

### 2.3 Building Column Strings

**Minimal Set (Fast):**
```python
# Ticker, Company, 30m perf, Price, Change
columns = "0,1,96,65,66"
```

**Standard Dashboard:**
```python
# Ticker, Company, 10m, 15m, 30m, SMA20, Price, Change
columns = "0,1,94,95,96,52,65,66"
```

**Full Metrics:**
```python
# Add volume, RSI, ATR
columns = "0,1,94,95,96,52,65,66,67,59,49"
```

---

## 🔧 3. Sorting & Filtering

### 3.1 Sort Codes

**Intraday Performance:**
```python
SORT_CODES = {
    "perfi1": "1-minute performance",
    "perfi3": "3-minute performance",
    "perfi5": "5-minute performance",
    "perfi10": "10-minute performance",
    "perfi15": "15-minute performance",
    "perfi30": "30-minute performance",   # ⭐ Most popular
    "perfi60": "1-hour performance"
}
```

**Prefix with `-` for descending:**
```python
sort_code = "-perfi30"  # 30m performance, highest first
```

**Other Sort Options:**
```python
OTHER_SORTS = {
    "ticker": "Ticker symbol (A-Z)",
    "change": "Daily % change",
    "changefromopen": "Change from open",
    "sma20": "Distance from 20-day SMA",
    "sma50": "Distance from 50-day SMA",
    "volume": "Volume",
    "relativevolume": "Relative volume"
}
```

### 3.2 Screener Filters

**Filter Format:**
```
f=FILTER1_FILTER2_FILTER3
```

**Common Filters:**
```python
FILTERS = {
    "cap_mega": "Market cap > $200B",
    "cap_large": "Market cap $10B-$200B",
    "cap_mid": "Market cap $2B-$10B",
    "cap_small": "Market cap $300M-$2B",
    "sh_avgvol_o1000": "Avg volume > 1M",
    "sh_price_o10": "Price > $10",
    "ta_perf_1wup": "Week performance up",
    "ta_sma20_pa": "Price above SMA20",
    "ta_sma50_pa": "Price above SMA50"
}
```

**Example:**
```python
# Large cap, high volume, price > $10
filters = "cap_large_sh_avgvol_o1000_sh_price_o10"
url = f"https://elite.finviz.com/export.ashx?v=111&auth={token}&f={filters}"
```

---

## 💡 4. Best Practices

### 4.1 API Rate Limiting

**Use Session for Connection Pooling:**
```python
import requests

# Create persistent session
session = requests.Session()

# Reuse for multiple requests
response1 = session.get(url1)
response2 = session.get(url2)
```

**Implement Exponential Backoff:**
```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        response = session.get(url, timeout=20)
        if response.status_code == 200:
            break
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
            continue
        raise
```

**Set Appropriate Timeouts:**
```python
# Connect timeout: 5s, Read timeout: 20s
response = requests.get(url, timeout=(5, 20))
```

### 4.2 Data Parsing

**CSV Parsing (Elite API):**
```python
import csv
from io import StringIO

response = requests.get(url)
csv_data = StringIO(response.text)
reader = csv.DictReader(csv_data)

for row in reader:
    ticker = row['Ticker']
    perf_30m = row['Perf 30min']
    price = row['Price']
    # Process data...
```

**Handle Missing Data:**
```python
def safe_parse_percent(value):
    """Parse percentage string, return 0.0 if invalid."""
    if not value or value == '-':
        return 0.0
    try:
        return float(value.strip('%'))
    except ValueError:
        return 0.0

perf = safe_parse_percent(row.get('Perf 30min', '-'))
```

### 4.3 Caching Strategy

**Cache API Responses:**
```python
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=60)  # 60 seconds
def fetch_ticker_metrics(tickers, api_token):
    """Fetch metrics with 1-minute cache."""
    # API call here
    return data
```

**File-based Cache:**
```python
import json
import os

def get_cached_data(cache_file, fetch_func, ttl_minutes=5):
    """Get data from cache or fetch fresh."""
    if os.path.exists(cache_file):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_age < timedelta(minutes=ttl_minutes):
            with open(cache_file, 'r') as f:
                return json.load(f)
    
    # Fetch fresh data
    data = fetch_func()
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump(data, f)
    
    return data
```

### 4.4 Error Handling

**Robust Fetching:**
```python
def fetch_with_fallback(url, api_token=None):
    """Fetch data with fallback to guest mode."""
    try:
        # Try Elite API first
        if api_token:
            elite_url = f"{url}&auth={api_token}"
            response = requests.get(elite_url, timeout=20)
            if response.status_code == 200:
                return response.text, "elite"
        
        # Fallback to free tier
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return response.text, "free"
        
        return None, "error"
    
    except requests.exceptions.Timeout:
        return None, "timeout"
    except Exception as e:
        return None, f"error: {str(e)}"
```

---

## 🚀 5. Advanced Techniques

### 5.1 Dual-Mode Support (Free + Elite)

**Detect Response Type:**
```python
def parse_finviz_response(response_text):
    """Parse CSV (Elite) or HTML (Free) response."""
    # Check if CSV
    if response_text.startswith('Ticker,') or 'Ticker' in response_text[:100]:
        return parse_csv(response_text)
    else:
        return parse_html(response_text)

def parse_csv(text):
    """Parse CSV response from Elite API."""
    reader = csv.DictReader(StringIO(text))
    return list(reader)

def parse_html(text):
    """Parse HTML response from Free tier."""
    soup = BeautifulSoup(text, 'html.parser')
    rows = soup.find_all('tr', class_='styled-row')
    # Extract data from HTML...
    return data
```

### 5.2 Batch Ticker Processing

**Fetch Multiple Tickers Efficiently:**
```python
def fetch_sorted_tickers(tickers, sort_option, api_token=""):
    """Fetch and sort multiple tickers in one request."""
    # Clean tickers
    ticker_list = [t.strip().upper() for t in tickers if t.strip()]
    ticker_str = ",".join(ticker_list)
    
    # Build URL with ticker filter
    columns = "0,1,94,95,96,52,65,66"
    sort_code = f"-{sort_option}"  # Descending
    
    url = f"https://elite.finviz.com/export.ashx?v=111&c={columns}&o={sort_code}"
    
    if api_token:
        url += f"&auth={api_token}"
    
    # Add ticker filter
    url += f"&f=ticker_{ticker_str.replace(',', '_')}"
    
    response = requests.get(url, timeout=20)
    return parse_csv(response.text)
```

### 5.3 Real-Time Updates

**Auto-Refresh Implementation:**
```python
import streamlit as st
import time

# Settings
auto_refresh = st.session_state.get("auto_refresh", False)
refresh_interval = st.session_state.get("refresh_interval", 10)

# Main app logic
display_dashboard()

# Auto-refresh at bottom
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
```

**Smart Refresh (Context-Aware):**
```python
# Longer interval when reading news
on_news_tab = st.session_state.get("active_tab") == "news"

if auto_refresh:
    if on_news_tab:
        time.sleep(300)  # 5 minutes for news
    else:
        time.sleep(refresh_interval)  # Normal interval
    st.rerun()
```

### 5.4 Performance Optimization

**Concurrent Chart Loading:**
```python
from concurrent.futures import ThreadPoolExecutor

def fetch_chart(ticker, timeframe):
    """Fetch single chart image."""
    url = f"https://elite.finviz.com/chart.ashx?t={ticker}&ty=c&ta=1&p={timeframe}&s=l"
    return requests.get(url).content

# Load multiple charts in parallel
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]
with ThreadPoolExecutor(max_workers=4) as executor:
    charts = list(executor.map(lambda t: fetch_chart(t, "i15"), tickers))
```

---

## 📰 6. News Integration

### 6.1 Finviz News API

**Elite News Endpoint:**
```
https://elite.finviz.com/news_export.ashx
```

**Parameters:**
- `auth=TOKEN` - API token
- `ticker=SYMBOL` - Filter by ticker
- `limit=N` - Number of results

**Example:**
```python
url = f"https://elite.finviz.com/news_export.ashx?auth={token}&limit=50"
response = requests.get(url)
news_data = response.json()
```

### 6.2 Yahoo Finance RSS (Alternative)

**RSS Feed URL:**
```python
def get_ticker_rss_url(ticker):
    """Get Yahoo Finance RSS feed URL for ticker."""
    return f"https://finance.yahoo.com/rss/headline?s={ticker}"
```

**Parse RSS:**
```python
import feedparser

def fetch_ticker_news(ticker):
    """Fetch news from Yahoo Finance RSS."""
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    feed = feedparser.parse(url)
    
    news_items = []
    for entry in feed.entries[:50]:  # Limit to 50
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        })
    
    return news_items
```

---

## 🎨 7. UI/UX Best Practices

### 7.1 Chart Display

**Streamlit Image Display:**
```python
import streamlit as st

# Display chart
chart_url = f"https://elite.finviz.com/chart.ashx?t={ticker}&ty=c&ta=1&p={timeframe}&s=l"
st.image(chart_url, width='stretch', caption=f"{ticker} - {timeframe}")
```

**Multi-Timeframe Layout:**
```python
# Three columns for different timeframes
col1, col2, col3 = st.columns(3)

with col1:
    st.image(get_chart_url(ticker, "d"), caption="Daily")
with col2:
    st.image(get_chart_url(ticker, "i15"), caption="15min")
with col3:
    st.image(get_chart_url(ticker, "i3"), caption="3min")
```

### 7.2 Metrics Display

**Info Bar Below Charts:**
```python
# Build metrics string
metrics = f"10m: {perf_10m} | 15m: {perf_15m} | 30m: {perf_30m} | SMA20: {sma20} | Price: ${price} | Chg: {change}"

# Display with color coding
if float(change.strip('%')) > 0:
    st.success(metrics)
else:
    st.error(metrics)
```

**Quick View Table:**
```python
import pandas as pd

# Build table data
table_data = []
for ticker in tickers:
    metrics = get_metrics(ticker)
    table_data.append({
        'Ticker': ticker,
        '30m': metrics['perf_30m'],
        '15m': metrics['perf_15m'],
        'Chg': metrics['change']
    })

df = pd.DataFrame(table_data)
st.dataframe(df, height=400)
```

### 7.3 Color Coding

**Time-Based News Colors:**
```python
from datetime import datetime, timedelta

def get_news_color(published_time):
    """Get color based on news age."""
    now = datetime.now()
    age = now - published_time
    
    if age < timedelta(minutes=10):
        return "#006400"  # Dark green
    elif age < timedelta(hours=1):
        return "#90EE90"  # Light green
    elif age.days == 0:
        return "#FFFFE0"  # Yellow (today)
    elif age.days == 1:
        return "#FFD700"  # Gold (yesterday)
    else:
        return "#808080"  # Gray (older)
```

**Performance Color Coding:**
```python
def get_performance_color(perf_str):
    """Get color based on performance."""
    perf = float(perf_str.strip('%'))
    
    if perf > 2:
        return "#006400"  # Dark green
    elif perf > 0:
        return "#90EE90"  # Light green
    elif perf > -2:
        return "#FFB6C1"  # Light red
    else:
        return "#8B0000"  # Dark red
```

---

## 🐛 8. Common Issues & Solutions

### 8.1 Column ID Confusion

**Problem:** Getting IPO dates instead of performance metrics

**Solution:**
```python
# ❌ WRONG
columns = "70,71,72"  # These are IPO-related columns

# ✅ CORRECT
columns = "94,95,96"  # Intraday performance (10m, 15m, 30m)
```

### 8.2 Authentication Failures

**Problem:** 401 Unauthorized with Elite API

**Solutions:**
```python
# Check token format
api_token = api_token.strip()  # Remove whitespace

# Verify token in URL
url = f"https://elite.finviz.com/export.ashx?v=111&auth={api_token}"

# Test with simple request
response = requests.get(url)
print(response.status_code, response.text[:200])
```

### 8.3 Timeout Issues

**Problem:** Requests timing out

**Solutions:**
```python
# Increase timeout
response = requests.get(url, timeout=30)

# Add retries
for attempt in range(3):
    try:
        response = requests.get(url, timeout=20)
        break
    except requests.exceptions.Timeout:
        if attempt < 2:
            time.sleep(2 ** attempt)
            continue
        raise
```

### 8.4 CSV Parsing Errors

**Problem:** CSV parsing fails with special characters

**Solution:**
```python
import csv

# Use proper CSV parsing
reader = csv.DictReader(StringIO(response.text))

# Handle special characters
for row in reader:
    ticker = row['Ticker'].strip()
    # Escape quotes in company names
    company = row['Company'].replace('"', '""')
```

---

## 📋 9. Quick Reference

### Essential Column IDs
```python
QUICK_COLUMNS = {
    0: "Ticker",
    1: "Company",
    65: "Price",
    66: "Change",
    94: "Perf 10min",
    95: "Perf 15min",
    96: "Perf 30min",
    52: "SMA20"
}
```

### Common API Calls
```python
# Get top performers (30m)
url = f"https://elite.finviz.com/export.ashx?v=111&auth={token}&c=0,1,96,65,66&o=-perfi30&r=1,20"

# Get specific tickers
tickers = "AAPL,MSFT,GOOGL"
url = f"https://elite.finviz.com/export.ashx?v=111&auth={token}&c=0,1,96,65,66&f=ticker_{tickers.replace(',', '_')}"

# Get chart
chart_url = f"https://elite.finviz.com/chart.ashx?t=AAPL&ty=c&ta=1&p=i15&s=l"
```

### Timeframe Codes
```python
"i1"  # 1 minute
"i3"  # 3 minutes
"i5"  # 5 minutes
"i15" # 15 minutes
"i30" # 30 minutes
"h1"  # 1 hour
"d"   # Daily
"w"   # Weekly
"m"   # Monthly
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Finviz Integration Guide  
**Based On:** Real-world implementation of Finviz Dashboard with 2700+ lines of production code

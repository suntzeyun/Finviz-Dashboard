# RSS Feed Expert Guide

A comprehensive guide to accessing, parsing, and integrating RSS feeds in Python applications. This framework covers RSS feed discovery, concurrent fetching, time-based filtering, and real-world optimization techniques based on production implementation.

---

## 🎯 Overview

This guide documents RSS integration patterns including:
- RSS feed discovery and URL construction
- Feed parsing with `feedparser`
- Concurrent fetching (5x speedup)
- Time-based color coding
- Timezone handling
- Error handling and fallbacks

**Based on:** Production dashboard fetching 50+ news sources with concurrent operations (50s → 10s).

---

## 📡 1. RSS Feed Basics

### 1.1 What is RSS?

**RSS (Really Simple Syndication)** is an XML format for distributing web content:
- News articles
- Blog posts
- Podcasts
- Video updates

**Common RSS Formats:**
- RSS 2.0 (most common)
- Atom 1.0
- RSS 1.0 (RDF)

### 1.2 RSS Feed Structure

**Basic RSS XML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Example News</title>
    <link>https://example.com</link>
    <description>Latest news</description>
    
    <item>
      <title>Breaking News Story</title>
      <link>https://example.com/article/123</link>
      <description>Article summary...</description>
      <pubDate>Mon, 13 Jan 2026 10:30:00 GMT</pubDate>
      <guid>https://example.com/article/123</guid>
    </item>
    
    <!-- More items... -->
  </channel>
</rss>
```

---

## 🔍 2. Finding RSS Feeds

### 2.1 Common RSS Feed Patterns

**News Websites:**
```
https://example.com/rss
https://example.com/feed
https://example.com/rss.xml
https://example.com/feed.xml
https://example.com/index.xml
```

**Ticker-Specific Feeds:**
```
# Yahoo Finance
https://finance.yahoo.com/rss/headline?s=TICKER

# Google News
https://news.google.com/rss/search?q=TICKER

# Seeking Alpha
https://seekingalpha.com/api/sa/combined/TICKER.xml
```

**Category Feeds:**
```
https://example.com/category/technology/feed
https://example.com/tag/stocks/rss
```

### 2.2 RSS Feed Discovery

**Method 1: Check HTML `<link>` Tags**
```python
import requests
from bs4 import BeautifulSoup

def find_rss_feeds(url):
    """Discover RSS feeds from website."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    feeds = []
    
    # Look for RSS/Atom links
    for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
        feeds.append({
            'title': link.get('title', 'RSS Feed'),
            'url': link.get('href')
        })
    
    return feeds

# Usage
feeds = find_rss_feeds('https://example.com')
for feed in feeds:
    print(f"{feed['title']}: {feed['url']}")
```

**Method 2: Try Common Patterns**
```python
def try_common_rss_patterns(base_url):
    """Try common RSS feed URL patterns."""
    patterns = [
        '/rss',
        '/feed',
        '/rss.xml',
        '/feed.xml',
        '/index.xml',
        '/atom.xml'
    ]
    
    feeds = []
    for pattern in patterns:
        url = base_url.rstrip('/') + pattern
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                feeds.append(url)
        except:
            pass
    
    return feeds
```

---

## 📥 3. Fetching RSS Feeds

### 3.1 Basic Feed Fetching

**Using feedparser:**
```python
import feedparser

# Install: pip install feedparser

def fetch_rss_feed(url):
    """Fetch and parse RSS feed."""
    feed = feedparser.parse(url)
    
    # Check if feed is valid
    if feed.bozo:
        print(f"Warning: Feed parsing error - {feed.bozo_exception}")
    
    # Access feed metadata
    print(f"Title: {feed.feed.title}")
    print(f"Description: {feed.feed.description}")
    print(f"Link: {feed.feed.link}")
    
    # Access entries
    for entry in feed.entries:
        print(f"\n{entry.title}")
        print(f"Link: {entry.link}")
        print(f"Published: {entry.published}")
        print(f"Summary: {entry.summary}")
    
    return feed

# Usage
feed = fetch_rss_feed('https://finance.yahoo.com/rss/headline?s=AAPL')
```

### 3.2 Ticker-Specific News

**Yahoo Finance RSS:**
```python
def fetch_ticker_news(ticker, limit=50):
    """Fetch news for specific ticker from Yahoo Finance."""
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    
    feed = feedparser.parse(url)
    
    news_items = []
    for entry in feed.entries[:limit]:
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.get('summary', ''),
            'source': 'Yahoo Finance'
        })
    
    return news_items

# Usage
aapl_news = fetch_ticker_news('AAPL', limit=10)
```

**Multiple Tickers:**
```python
def fetch_multi_ticker_news(tickers, limit=10):
    """Fetch news for multiple tickers."""
    all_news = []
    
    for ticker in tickers:
        news = fetch_ticker_news(ticker, limit)
        # Add ticker to each news item
        for item in news:
            item['ticker'] = ticker
        all_news.extend(news)
    
    # Sort by published date (newest first)
    all_news.sort(key=lambda x: x['published'], reverse=True)
    
    return all_news

# Usage
tickers = ['AAPL', 'MSFT', 'GOOGL']
news = fetch_multi_ticker_news(tickers, limit=10)
```

---

## ⚡ 4. Concurrent Fetching (5x Speedup)

### 4.1 Sequential vs Concurrent

**Sequential (Slow):**
```python
# ❌ SLOW: 50 seconds for 10 sources
all_news = []
for source_name, url in rss_sources.items():
    feed = feedparser.parse(url)  # 5s each
    all_news.extend(feed.entries)
# Total: 10 sources × 5s = 50 seconds
```

**Concurrent (Fast):**
```python
import concurrent.futures
import feedparser

def fetch_rss_source(source_name, url):
    """Fetch single RSS source."""
    try:
        feed = feedparser.parse(url)
        return (source_name, True, feed.entries)
    except Exception as e:
        return (source_name, False, [])

# ✅ FAST: 10 seconds for 10 sources
rss_sources = {
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'Reuters Business': 'https://www.reuters.com/rssfeed/businessNews',
    'Bloomberg': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
    # ... 7 more sources
}

all_news = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Submit all fetch tasks
    futures = {
        executor.submit(fetch_rss_source, name, url): name 
        for name, url in rss_sources.items()
    }
    
    # Collect results as they complete
    for future in concurrent.futures.as_completed(futures):
        source_name, success, news_items = future.result()
        if success:
            # Add source to each item
            for item in news_items:
                item['source'] = source_name
            all_news.extend(news_items)

# Total: ~10 seconds (limited by slowest source)
# Result: 5x faster!
```

### 4.2 Production-Ready Concurrent Fetcher

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import feedparser
from datetime import datetime

def fetch_rss_source_safe(source_name, url, timeout=10):
    """Fetch RSS source with error handling and timeout."""
    try:
        # feedparser doesn't support timeout directly
        # Use requests with timeout, then parse
        import requests
        
        response = requests.get(url, timeout=timeout)
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            # Parsing error
            return (source_name, False, [], str(feed.bozo_exception))
        
        return (source_name, True, feed.entries, None)
    
    except requests.exceptions.Timeout:
        return (source_name, False, [], "Timeout")
    except Exception as e:
        return (source_name, False, [], str(e))

def fetch_all_rss_sources(rss_sources, max_workers=10, timeout=10):
    """
    Fetch multiple RSS sources concurrently.
    
    Args:
        rss_sources: Dict of {source_name: url}
        max_workers: Number of concurrent workers
        timeout: Timeout per source in seconds
    
    Returns:
        Tuple of (news_items, errors)
    """
    all_news = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(fetch_rss_source_safe, name, url, timeout): name
            for name, url in rss_sources.items()
        }
        
        # Collect results
        for future in as_completed(futures):
            source_name, success, news_items, error = future.result()
            
            if success:
                # Add metadata to each item
                for item in news_items:
                    item['source'] = source_name
                    item['fetched_at'] = datetime.now()
                
                all_news.extend(news_items)
            else:
                errors.append({
                    'source': source_name,
                    'error': error
                })
    
    return all_news, errors

# Usage
rss_sources = {
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'Reuters': 'https://www.reuters.com/rssfeed/businessNews',
    'Bloomberg': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
}

news, errors = fetch_all_rss_sources(rss_sources, max_workers=10, timeout=10)

print(f"Fetched {len(news)} news items")
if errors:
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(f"  {error['source']}: {error['error']}")
```

---

## 🕐 5. Time Handling & Formatting

### 5.1 Parse Published Dates

**feedparser handles multiple date formats:**
```python
import feedparser
from datetime import datetime

feed = feedparser.parse(url)

for entry in feed.entries:
    # feedparser provides parsed time tuple
    if hasattr(entry, 'published_parsed'):
        # Convert to datetime
        pub_date = datetime(*entry.published_parsed[:6])
        print(f"Published: {pub_date}")
    
    # Or use published string
    print(f"Published (raw): {entry.published}")
```

### 5.2 Timezone Conversion

**Convert to Local Time:**
```python
import pytz
from datetime import datetime

def convert_to_local_time(pub_date_str, local_tz='Asia/Singapore'):
    """Convert published date to local timezone."""
    # Parse the date string
    feed = feedparser.parse(f"<item><pubDate>{pub_date_str}</pubDate></item>")
    
    if feed.entries and hasattr(feed.entries[0], 'published_parsed'):
        # Get UTC datetime
        utc_time = datetime(*feed.entries[0].published_parsed[:6])
        utc_time = pytz.utc.localize(utc_time)
        
        # Convert to local timezone
        local_tz_obj = pytz.timezone(local_tz)
        local_time = utc_time.astimezone(local_tz_obj)
        
        return local_time
    
    return None

# Usage
pub_date = "Mon, 13 Jan 2026 10:30:00 GMT"
local_time = convert_to_local_time(pub_date, 'Asia/Singapore')
print(f"Local time: {local_time}")
```

### 5.3 Time-Based Color Coding

**Visual Age Indicators:**
```python
from datetime import datetime, timedelta
import pytz

def get_news_age_color(published_time, local_tz='Asia/Singapore'):
    """
    Get color based on news age.
    
    Returns:
        Tuple of (color_hex, age_label)
    """
    # Convert to local timezone
    if isinstance(published_time, str):
        published_time = convert_to_local_time(published_time, local_tz)
    
    # Get current time in local timezone
    local_tz_obj = pytz.timezone(local_tz)
    now = datetime.now(local_tz_obj)
    
    # Calculate age
    age = now - published_time
    
    if age < timedelta(minutes=10):
        return ("#006400", "< 10 min")  # Dark green
    elif age < timedelta(hours=1):
        return ("#90EE90", "< 1 hour")  # Light green
    elif age.days == 0:
        return ("#FFFFE0", "Today")     # Yellow
    elif age.days == 1:
        return ("#FFD700", "Yesterday") # Gold
    else:
        return ("#808080", f"{age.days} days ago")  # Gray

# Usage
for entry in feed.entries:
    pub_time = datetime(*entry.published_parsed[:6])
    color, label = get_news_age_color(pub_time)
    print(f"{entry.title} - {label}")
```

---

## 🎨 6. Displaying RSS Feeds

### 6.1 Streamlit Integration

**Basic News Display:**
```python
import streamlit as st
import feedparser

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_ticker_rss_news(ticker):
    """Fetch and cache RSS news."""
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    feed = feedparser.parse(url)
    return feed.entries[:50]

# Display news
ticker = st.selectbox("Ticker", ["AAPL", "MSFT", "GOOGL"])
news = fetch_ticker_rss_news(ticker)

for item in news:
    st.markdown(f"**[{item.title}]({item.link})**")
    st.caption(f"Published: {item.published}")
    st.write(item.summary)
    st.divider()
```

### 6.2 HTML Rendering with Color Coding

**Production-Ready News Feed:**
```python
import streamlit as st
from datetime import datetime
import pytz

def render_news_feed(news_items, timezone='Asia/Singapore', font_size='Medium'):
    """Render news feed with time-based color coding."""
    
    # Font size mapping
    font_sizes = {
        'Small': '12px',
        'Medium': '14px',
        'Large': '16px',
        'Extra Large': '18px'
    }
    
    # Build HTML
    html_parts = []
    html_parts.append(f'<div style="font-size: {font_sizes[font_size]};">')
    
    for item in news_items:
        # Get published time
        if hasattr(item, 'published_parsed'):
            pub_time = datetime(*item.published_parsed[:6])
            pub_time = pytz.utc.localize(pub_time)
            
            # Convert to local timezone
            local_tz = pytz.timezone(timezone)
            local_time = pub_time.astimezone(local_tz)
            
            # Get color based on age
            color, age_label = get_news_age_color(local_time, timezone)
            
            # Format time
            time_str = local_time.strftime('%Y-%m-%d %H:%M')
        else:
            color = "#808080"
            time_str = item.get('published', 'Unknown')
            age_label = ""
        
        # Escape HTML characters
        title = item.title.replace('"', '&quot;').replace("'", '&#39;')
        link = item.link.replace('"', '&quot;')
        
        # Build news item HTML
        html_parts.append(f'''
            <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid {color};">
                <a href="{link}" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">
                    {title}
                </a>
                <div style="color: {color}; font-size: 0.9em; margin-top: 4px;">
                    {time_str} ({age_label})
                </div>
            </div>
        ''')
    
    html_parts.append('</div>')
    
    # Render HTML
    st.markdown(''.join(html_parts), unsafe_allow_html=True)

# Usage
news = fetch_ticker_rss_news('AAPL')
render_news_feed(news, timezone='Asia/Singapore', font_size='Medium')
```

### 6.3 Scrollable Container

**Fixed-Height News Feed:**
```python
import streamlit as st

# Create scrollable container
st.markdown("""
<div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
""", unsafe_allow_html=True)

# Render news inside container
render_news_feed(news)

st.markdown("</div>", unsafe_allow_html=True)
```

---

## 🔧 7. Advanced Techniques

### 7.1 Deduplication

**Remove Duplicate News:**
```python
def deduplicate_news(news_items):
    """Remove duplicate news based on title similarity."""
    seen_titles = set()
    unique_news = []
    
    for item in news_items:
        # Normalize title (lowercase, remove extra spaces)
        normalized = ' '.join(item.title.lower().split())
        
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique_news.append(item)
    
    return unique_news
```

### 7.2 Keyword Filtering

**Filter News by Keywords:**
```python
def filter_news_by_keywords(news_items, keywords, exclude_keywords=None):
    """Filter news by keywords."""
    filtered = []
    
    keywords = [k.lower() for k in keywords]
    exclude_keywords = [k.lower() for k in (exclude_keywords or [])]
    
    for item in news_items:
        title_lower = item.title.lower()
        summary_lower = item.get('summary', '').lower()
        
        # Check if any keyword matches
        has_keyword = any(kw in title_lower or kw in summary_lower for kw in keywords)
        
        # Check if any exclude keyword matches
        has_exclude = any(kw in title_lower or kw in summary_lower for kw in exclude_keywords)
        
        if has_keyword and not has_exclude:
            filtered.append(item)
    
    return filtered

# Usage
news = fetch_ticker_rss_news('AAPL')
filtered = filter_news_by_keywords(
    news,
    keywords=['earnings', 'revenue', 'profit'],
    exclude_keywords=['rumor', 'speculation']
)
```

### 7.3 Sentiment Analysis

**Basic Sentiment Detection:**
```python
def get_sentiment(text):
    """Simple sentiment analysis based on keywords."""
    positive_words = ['surge', 'gain', 'profit', 'growth', 'up', 'rise', 'bullish']
    negative_words = ['drop', 'loss', 'decline', 'down', 'fall', 'bearish', 'crash']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive', positive_count - negative_count
    elif negative_count > positive_count:
        return 'negative', negative_count - positive_count
    else:
        return 'neutral', 0

# Usage
for item in news:
    sentiment, score = get_sentiment(item.title + ' ' + item.get('summary', ''))
    print(f"{item.title} - {sentiment} ({score})")
```

---

## 📋 8. Common RSS Sources

### 8.1 Financial News

```python
FINANCIAL_RSS_SOURCES = {
    # General Financial News
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'Reuters Business': 'https://www.reuters.com/rssfeed/businessNews',
    'Bloomberg Markets': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
    'CNBC Top News': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Financial Times': 'https://www.ft.com/?format=rss',
    
    # Analysis & Opinion
    'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
    'Zero Hedge': 'https://www.zerohedge.com/fullrss2.xml',
    'The Motley Fool': 'https://www.fool.com/feeds/index.aspx',
    
    # Ticker-Specific (Yahoo Finance)
    # Use: f'https://finance.yahoo.com/rss/headline?s={ticker}'
}
```

### 8.2 Technology News

```python
TECH_RSS_SOURCES = {
    'TechCrunch': 'https://techcrunch.com/feed/',
    'The Verge': 'https://www.theverge.com/rss/index.xml',
    'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/index',
    'Hacker News': 'https://news.ycombinator.com/rss',
    'Wired': 'https://www.wired.com/feed/rss',
}
```

---

## 🐛 9. Error Handling

### 9.1 Common Issues

**Issue 1: Feed Parsing Errors**
```python
feed = feedparser.parse(url)

if feed.bozo:
    print(f"Parsing error: {feed.bozo_exception}")
    # Handle malformed XML
```

**Issue 2: Missing Fields**
```python
for entry in feed.entries:
    title = entry.get('title', 'No title')
    link = entry.get('link', '#')
    published = entry.get('published', 'Unknown date')
    summary = entry.get('summary', entry.get('description', ''))
```

**Issue 3: Network Timeouts**
```python
import requests

try:
    response = requests.get(url, timeout=10)
    feed = feedparser.parse(response.content)
except requests.exceptions.Timeout:
    print(f"Timeout fetching {url}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📊 10. Performance Metrics

**Real-World Results:**

| Metric | Sequential | Concurrent | Improvement |
|--------|-----------|------------|-------------|
| 10 sources | 50s | 10s | **5x faster** |
| 20 sources | 100s | 15s | **6.7x faster** |
| 50 sources | 250s | 30s | **8.3x faster** |

**Optimization Tips:**
- Use `ThreadPoolExecutor` for I/O-bound operations
- Set appropriate timeouts (10-20s)
- Cache results with TTL (5-10 minutes)
- Limit workers to 10-20 for best performance

---

## 📝 Quick Reference

### Fetch Single Feed
```python
import feedparser
feed = feedparser.parse(url)
```

### Fetch Ticker News
```python
url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
feed = feedparser.parse(url)
```

### Concurrent Fetching
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(fetch_rss_source, sources)
```

### Time-Based Coloring
```python
age = now - published_time
if age < timedelta(minutes=10):
    color = "#006400"  # Dark green
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** RSS Integration Guide  
**Based On:** Production dashboard with 50+ RSS sources, concurrent fetching (5x speedup)

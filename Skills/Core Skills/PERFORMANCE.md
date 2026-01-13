# Performance Optimization Guide

A comprehensive guide for optimizing web applications and Streamlit dashboards. This framework covers profiling, caching strategies, database optimization, memory management, and load testing to ensure fast, responsive applications.

---

## 🎯 Performance Goals

### Target Metrics

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| **Initial Load** | < 2s | 2-5s | > 5s |
| **Page Interaction** | < 100ms | 100-300ms | > 300ms |
| **API Response** | < 500ms | 500ms-2s | > 2s |
| **Memory Usage** | < 200MB | 200-500MB | > 500MB |
| **CPU Usage** | < 30% | 30-60% | > 60% |

### Performance Principles

1. **Measure First** - Profile before optimizing
2. **Cache Aggressively** - Avoid redundant computation
3. **Lazy Load** - Load data only when needed
4. **Batch Operations** - Reduce API calls
5. **Optimize Queries** - Database performance matters
6. **Monitor Continuously** - Track metrics over time

---

## 📊 1. Profiling & Measurement

### 1.1 Python Profiling

**cProfile (Built-in):**
```bash
# Profile entire application
python -m cProfile -o profile.stats streamlit_app.py

# View results
python -m pstats profile.stats
>>> sort cumtime
>>> stats 20  # Top 20 functions by cumulative time
```

**Line Profiler (Detailed):**
```bash
# Install
pip install line_profiler

# Add @profile decorator to functions
@profile
def expensive_function():
    # code here
    pass

# Run profiler
kernprof -l -v streamlit_app.py
```

**Memory Profiler:**
```bash
# Install
pip install memory_profiler

# Add @profile decorator
from memory_profiler import profile

@profile
def memory_intensive_function():
    # code here
    pass

# Run profiler
python -m memory_profiler streamlit_app.py
```

### 1.2 Streamlit Performance Monitoring

**Built-in Metrics:**
```python
import streamlit as st
import time

# Track execution time
start_time = time.time()

# Your code here
expensive_operation()

execution_time = time.time() - start_time
st.sidebar.metric("Execution Time", f"{execution_time:.2f}s")
```

**Custom Performance Tracker:**
```python
import time
from functools import wraps

def track_performance(func):
    """Decorator to track function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        # Log to file or display
        print(f"{func.__name__}: {duration:.3f}s")
        
        # Store in session state for dashboard
        if "perf_metrics" not in st.session_state:
            st.session_state.perf_metrics = {}
        st.session_state.perf_metrics[func.__name__] = duration
        
        return result
    return wrapper

@track_performance
def fetch_data():
    # Implementation
    pass
```

### 1.3 Browser Performance Tools

**Chrome DevTools:**
1. Open DevTools (F12)
2. Go to Performance tab
3. Record page load
4. Analyze:
   - Loading time
   - Scripting time
   - Rendering time
   - Network requests

**Lighthouse Audit:**
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse http://localhost:8501 --view
```

---

## 💾 2. Caching Strategies

### 2.1 Streamlit Caching

**@st.cache_data (Data Caching):**
```python
import streamlit as st
import pandas as pd

# Cache data that changes infrequently
@st.cache_data(ttl=300)  # 5 minutes
def load_data():
    """Load data from API or database."""
    # Expensive operation
    return pd.read_csv("large_file.csv")

# Cache with parameters
@st.cache_data(ttl=60)
def fetch_ticker_data(ticker: str, timeframe: str):
    """Fetch data for specific ticker and timeframe."""
    return api.get_data(ticker, timeframe)

# Clear specific cache
load_data.clear()

# Clear all caches
st.cache_data.clear()
```

**@st.cache_resource (Resource Caching):**
```python
# Cache database connections, ML models
@st.cache_resource
def get_database_connection():
    """Create and cache database connection."""
    return create_connection()

@st.cache_resource
def load_ml_model():
    """Load and cache ML model."""
    return joblib.load("model.pkl")

# Use cached resources
conn = get_database_connection()
model = load_ml_model()
```

**Cache Configuration:**
```python
# Ignore specific parameters
@st.cache_data(hash_funcs={dict: lambda x: None})
def process_data(data, config):
    # config dict won't affect cache
    pass

# Show spinner while caching
@st.cache_data(show_spinner="Loading data...")
def load_data():
    pass

# Suppress warnings
@st.cache_data(suppress_st_warning=True)
def cached_function():
    st.write("This won't cause a warning")
```

### 2.2 Manual Caching

**Session State Caching:**
```python
# Cache in session state
def get_cached_data(key, fetch_func, ttl=300):
    """Generic caching function using session state."""
    cache_key = f"cache_{key}"
    time_key = f"cache_time_{key}"
    
    # Check if cached and not expired
    if cache_key in st.session_state:
        cache_time = st.session_state.get(time_key, 0)
        if time.time() - cache_time < ttl:
            return st.session_state[cache_key]
    
    # Fetch new data
    data = fetch_func()
    st.session_state[cache_key] = data
    st.session_state[time_key] = time.time()
    
    return data

# Usage
data = get_cached_data("ticker_AAPL", lambda: fetch_ticker("AAPL"), ttl=60)
```

**File-based Caching:**
```python
import json
import os
from datetime import datetime, timedelta

def file_cache(filename, fetch_func, ttl_hours=1):
    """Cache data to file with TTL."""
    cache_file = f"cache/{filename}.json"
    
    # Check if cache exists and is fresh
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time < timedelta(hours=ttl_hours):
            with open(cache_file, 'r') as f:
                return json.load(f)
    
    # Fetch new data
    data = fetch_func()
    
    # Save to cache
    os.makedirs("cache", exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(data, f)
    
    return data
```

**Session-State File Caching (40x Improvement):**
```python
import os
import json
import streamlit as st

def load_with_session_cache(filename, bypass_key="_file_modified"):
    """
    Load JSON file with session-state caching and modification time tracking.
    
    Real-world performance:
    - Before: 40+ file reads per render (20 tickers)
    - After: 1 file read per render
    - Result: 40x faster file I/O
    """
    cache_key = f"{filename}_cache"
    mtime_key = f"{filename}_mtime"
    
    # Check bypass flag (set after save operations)
    if st.session_state.get(bypass_key, False):
        st.session_state[bypass_key] = False
        # Force fresh read, skip cache
    else:
        # Check if file was modified
        if os.path.exists(filename):
            current_mtime = os.path.getmtime(filename)
            
            # Return cached if file unchanged
            if cache_key in st.session_state:
                if st.session_state.get(mtime_key) == current_mtime:
                    return st.session_state[cache_key]
    
    # Load fresh data
    if not os.path.exists(filename):
        data = {}
    else:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    # Cache in session state
    st.session_state[cache_key] = data
    if os.path.exists(filename):
        st.session_state[mtime_key] = os.path.getmtime(filename)
    
    return data

def save_with_cache_invalidation(filename, data, bypass_key="_file_modified"):
    """Save JSON file and set bypass flag for cache invalidation."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    # Set bypass flag to force fresh read on next load
    st.session_state[bypass_key] = True

# Usage example
ticker_lists = load_with_session_cache("ticker_lists.json", "_ticker_lists_modified")

# After saving
save_with_cache_invalidation("ticker_lists.json", new_data, "_ticker_lists_modified")

# Performance impact:
# - 20 tickers × 2 files (lists + journal) = 40 file reads per render
# - With caching: 2 file reads per render (one for each file type)
# - 40x reduction in file I/O operations
```

### 2.3 HTTP Caching

**requests-cache:**
```python
import requests_cache

# Install: pip install requests-cache

# Setup cache
requests_cache.install_cache(
    'api_cache',
    backend='sqlite',
    expire_after=300  # 5 minutes
)

# Use requests normally
response = requests.get("https://api.example.com/data")
# Second call uses cache

# Clear cache
requests_cache.clear()
```

---

## 🚀 3. Code Optimization

### 3.1 Efficient Data Structures

**Use Appropriate Data Types:**
```python
# ❌ Slow: List lookup O(n)
tickers = ["AAPL", "MSFT", "GOOGL"]
if "AAPL" in tickers:  # O(n)
    pass

# ✅ Fast: Set lookup O(1)
tickers = {"AAPL", "MSFT", "GOOGL"}
if "AAPL" in tickers:  # O(1)
    pass

# ❌ Slow: Multiple list iterations
for ticker in tickers:
    for metric in metrics:
        process(ticker, metric)  # O(n*m)

# ✅ Fast: Dictionary lookup
ticker_metrics = {t: m for t, m in zip(tickers, metrics)}
for ticker, metric in ticker_metrics.items():  # O(n)
    process(ticker, metric)
```

**Pandas Optimization:**
```python
import pandas as pd

# ❌ Slow: Iterating rows
for index, row in df.iterrows():
    df.at[index, 'new_col'] = row['col1'] + row['col2']

# ✅ Fast: Vectorized operations
df['new_col'] = df['col1'] + df['col2']

# ❌ Slow: Appending in loop
df = pd.DataFrame()
for data in data_list:
    df = df.append(data)  # Creates new DataFrame each time

# ✅ Fast: Create from list
data_list = []
for data in source:
    data_list.append(data)
df = pd.DataFrame(data_list)
```

### 3.2 Lazy Loading

**Load Data on Demand:**
```python
# ❌ Load everything upfront
all_data = load_all_tickers()  # Slow initial load

# ✅ Load on demand
if st.button("Show AAPL"):
    aapl_data = load_ticker("AAPL")  # Fast initial load
    st.write(aapl_data)

# ✅ Pagination
page = st.number_input("Page", min_value=1, max_value=10)
data = load_page(page, page_size=20)
```

**Lazy Imports:**
```python
# ❌ Import everything at startup
import heavy_library  # Slow startup

# ✅ Import when needed
def use_heavy_feature():
    import heavy_library  # Only imported when function called
    return heavy_library.process()
```

### 3.3 Async Operations

**Concurrent API Calls:**
```python
import concurrent.futures
import requests

def fetch_ticker(ticker):
    """Fetch data for single ticker."""
    return requests.get(f"https://api.example.com/{ticker}").json()

# ❌ Sequential (slow)
results = []
for ticker in tickers:
    results.append(fetch_ticker(ticker))  # 1s each = 10s total

# ✅ Concurrent (fast)
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_ticker, tickers))  # ~1s total
```

**Example: Concurrent RSS Fetching:**
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

# Fetch all sources concurrently
rss_sources = {
    'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
    'Reuters': 'https://www.reuters.com/rssfeed/...',
    # ... more sources
}

all_news = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_rss_source, name, url): name 
               for name, url in rss_sources.items()}
    
    for future in concurrent.futures.as_completed(futures):
        source_name, success, news_items = future.result()
        if success:
            all_news.extend(news_items)

# Before: 50 seconds (sequential)
# After: 10 seconds (concurrent) - 5x faster!
```

---

## 🗄️ 4. Database Optimization

### 4.1 Query Optimization

**Efficient Queries:**
```python
# ❌ N+1 Query Problem
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id={user.id}")
    # 1 + N queries

# ✅ Join Query
result = db.query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
""")
# 1 query

# ❌ Select all columns
data = db.query("SELECT * FROM large_table")

# ✅ Select only needed columns
data = db.query("SELECT id, name, price FROM large_table")
```

**Indexing:**
```sql
-- Create index on frequently queried columns
CREATE INDEX idx_ticker ON stocks(ticker);
CREATE INDEX idx_date ON stocks(date);

-- Composite index for multi-column queries
CREATE INDEX idx_ticker_date ON stocks(ticker, date);
```

**Connection Pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Create engine with connection pool
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)

# Cache engine
@st.cache_resource
def get_engine():
    return create_engine(...)
```

### 4.2 Batch Operations

**Batch Inserts:**
```python
# ❌ Individual inserts
for record in records:
    db.execute("INSERT INTO table VALUES (?)", record)
    # 1000 records = 1000 queries

# ✅ Batch insert
db.executemany("INSERT INTO table VALUES (?)", records)
# 1000 records = 1 query
```

**Bulk Updates:**
```python
# ❌ Update one by one
for ticker in tickers:
    update_ticker_data(ticker)

# ✅ Batch update
update_all_tickers(tickers)  # Single transaction
```

---

## 💻 5. Memory Optimization

### 5.1 Memory Profiling

**Track Memory Usage:**
```python
import psutil
import os

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# Display in sidebar
st.sidebar.metric("Memory Usage", f"{get_memory_usage():.1f} MB")
```

**Memory Profiler:**
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Large list
    data = [i for i in range(10000000)]
    # Process data
    return sum(data)

# Run and check output for memory usage per line
```

### 5.2 Memory Optimization Techniques

**Generators Instead of Lists:**
```python
# ❌ Creates entire list in memory
def get_numbers():
    return [i for i in range(1000000)]  # ~40MB

numbers = get_numbers()

# ✅ Generator - one item at a time
def get_numbers():
    for i in range(1000000):
        yield i  # ~80 bytes

numbers = get_numbers()
```

**Delete Unused Objects:**
```python
# Process large data
large_data = load_large_dataset()
processed = process(large_data)

# Free memory
del large_data
import gc
gc.collect()
```

**Use Appropriate Data Types:**
```python
import numpy as np

# ❌ Python list of integers (28 bytes per int)
data = [1, 2, 3, 4, 5] * 1000000  # ~140MB

# ✅ NumPy array (4 bytes per int32)
data = np.array([1, 2, 3, 4, 5] * 1000000, dtype=np.int32)  # ~20MB
```

**Chunking Large Files:**
```python
# ❌ Load entire file
with open("large_file.csv") as f:
    data = f.read()  # Loads all into memory

# ✅ Process in chunks
import pandas as pd

chunk_size = 10000
for chunk in pd.read_csv("large_file.csv", chunksize=chunk_size):
    process(chunk)
    # Each chunk processed and released
```

---

## 🌐 6. Network Optimization

### 6.1 Reduce API Calls

**Batch Requests:**
```python
# ❌ Multiple API calls
for ticker in tickers:
    data = api.get(f"/ticker/{ticker}")  # 10 calls

# ✅ Single batch call
tickers_str = ",".join(tickers)
data = api.get(f"/tickers?symbols={tickers_str}")  # 1 call
```

**Request Deduplication:**
```python
# Avoid duplicate requests
requested = set()

def fetch_with_dedup(ticker):
    if ticker in requested:
        return get_from_cache(ticker)
    
    requested.add(ticker)
    return api.get(ticker)
```

### 6.2 Compression

**Enable Compression:**
```python
import requests

# Request compressed response
headers = {
    'Accept-Encoding': 'gzip, deflate'
}
response = requests.get(url, headers=headers)
```

**Compress Data:**
```python
import gzip
import json

# Save compressed
data = {"large": "data"}
with gzip.open("data.json.gz", "wt") as f:
    json.dump(data, f)

# Load compressed
with gzip.open("data.json.gz", "rt") as f:
    data = json.load(f)
```

### 6.3 Timeouts and Retries

**Set Appropriate Timeouts:**
```python
# ❌ No timeout (can hang forever)
response = requests.get(url)

# ✅ With timeout
response = requests.get(url, timeout=10)  # 10 seconds

# ✅ Separate connect and read timeouts
response = requests.get(url, timeout=(3, 10))  # 3s connect, 10s read
```

**Retry Logic:**
```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.5,  # 0.5s, 1s, 2s
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(url)
```

---

## 🎨 7. UI/UX Performance

### 7.1 Minimize Reruns

**Use Callbacks:**
```python
# ❌ Triggers rerun on every keystroke
search = st.text_input("Search")
if search:
    results = search_database(search)  # Runs on every character

# ✅ Use form to batch input
with st.form("search_form"):
    search = st.text_input("Search")
    submitted = st.form_submit_button("Search")
    
if submitted and search:
    results = search_database(search)  # Runs once on submit
```

**Debouncing:**
```python
import time

def debounced_search(query, delay=0.5):
    """Only search after user stops typing."""
    if "last_search_time" not in st.session_state:
        st.session_state.last_search_time = 0
    
    current_time = time.time()
    if current_time - st.session_state.last_search_time < delay:
        return None
    
    st.session_state.last_search_time = current_time
    return search_database(query)
```

### 7.2 Progressive Loading

**Show Skeleton/Placeholder:**
```python
# Show placeholder while loading
with st.spinner("Loading data..."):
    data = load_data()

# Or custom placeholder
placeholder = st.empty()
placeholder.text("Loading...")
data = load_data()
placeholder.empty()
```

**Pagination:**
```python
# Don't load all data at once
total_items = 1000
page_size = 20
page = st.number_input("Page", 1, total_items // page_size)

start = (page - 1) * page_size
end = start + page_size
data = load_data_range(start, end)
```

### 7.3 Optimize Rendering

**Limit Displayed Items:**
```python
# ❌ Display 10,000 rows
st.dataframe(large_df)  # Slow rendering

# ✅ Display top 100 with option to download full
st.dataframe(large_df.head(100))
st.download_button("Download Full Data", large_df.to_csv())
```

**Use Appropriate Widgets:**
```python
# ❌ Slow for many options
selected = st.multiselect("Select", range(10000))

# ✅ Fast for many options
selected = st.text_input("Enter IDs (comma-separated)")
selected = [int(x.strip()) for x in selected.split(",")]
```

---

## 🧪 8. Load Testing

### 8.1 Locust (Load Testing)

**Install:**
```bash
pip install locust
```

**locustfile.py:**
```python
from locust import HttpUser, task, between

class StreamlitUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3s between requests
    
    @task(3)  # Weight: 3x more likely than other tasks
    def index(self):
        self.client.get("/")
    
    @task(1)
    def health_check(self):
        self.client.get("/_stcore/health")
    
    def on_start(self):
        """Called when user starts."""
        pass
```

**Run Load Test:**
```bash
# Start Locust
locust -f locustfile.py --host=http://localhost:8501

# Open browser: http://localhost:8089
# Set number of users and spawn rate
```

### 8.2 Apache Bench

```bash
# Install Apache Bench (comes with Apache)

# Simple load test
ab -n 1000 -c 10 http://localhost:8501/
# -n: Total requests
# -c: Concurrent requests

# With results
ab -n 1000 -c 10 -g results.tsv http://localhost:8501/
```

### 8.3 Stress Testing

**gradual_load.py:**
```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def make_request():
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        return response.status_code == 200
    except:
        return False

# Gradually increase load
for concurrent_users in [1, 5, 10, 20, 50, 100]:
    print(f"\nTesting with {concurrent_users} concurrent users...")
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        results = list(executor.map(lambda x: make_request(), range(100)))
    
    duration = time.time() - start
    success_rate = sum(results) / len(results) * 100
    
    print(f"Duration: {duration:.2f}s")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Requests/sec: {100/duration:.2f}")
```

---

## 📋 9. Performance Checklist

### Code Level
- [ ] Profile code to identify bottlenecks
- [ ] Use appropriate data structures (sets, dicts)
- [ ] Implement caching for expensive operations
- [ ] Use vectorized operations (pandas, numpy)
- [ ] Avoid nested loops where possible
- [ ] Use generators for large datasets
- [ ] Delete unused objects to free memory

### Database Level
- [ ] Add indexes on frequently queried columns
- [ ] Use connection pooling
- [ ] Batch inserts/updates
- [ ] Select only needed columns
- [ ] Optimize query structure

### Network Level
- [ ] Batch API requests
- [ ] Implement caching (HTTP, file, memory)
- [ ] Use concurrent requests
- [ ] Set appropriate timeouts
- [ ] Enable compression

### UI/UX Level
- [ ] Minimize reruns (use forms, callbacks)
- [ ] Implement pagination
- [ ] Show loading indicators
- [ ] Lazy load data
- [ ] Limit displayed items

### Deployment Level
- [ ] Use production server (not development)
- [ ] Enable caching headers
- [ ] Use CDN for static assets
- [ ] Monitor resource usage
- [ ] Set up auto-scaling

---

## 🎯 Quick Wins

### Immediate Improvements

1. **Add Caching:**
```python
@st.cache_data(ttl=300)
def expensive_function():
    pass
```

2. **Use Concurrent Requests:**
```python
with ThreadPoolExecutor() as executor:
    results = executor.map(fetch_data, items)
```

3. **Optimize Pandas:**
```python
# Use vectorized operations
df['new'] = df['a'] + df['b']  # Not iterrows()
```

4. **Batch API Calls:**
```python
# One call with multiple tickers
data = api.get(f"/tickers?symbols={','.join(tickers)}")
```

5. **Add Indexes:**
```sql
CREATE INDEX idx_ticker ON stocks(ticker);
```

---

## 📊 Monitoring Dashboard

**Create Performance Dashboard:**
```python
import streamlit as st
import psutil
import time

# Sidebar metrics
with st.sidebar:
    st.header("📊 Performance")
    
    # Memory
    memory = psutil.virtual_memory()
    st.metric("Memory", f"{memory.percent}%")
    
    # CPU
    cpu = psutil.cpu_percent(interval=1)
    st.metric("CPU", f"{cpu}%")
    
    # Cache stats
    if hasattr(st, 'cache_data'):
        st.metric("Cache Hits", st.session_state.get('cache_hits', 0))
    
    # Response times
    if 'perf_metrics' in st.session_state:
        st.write("**Function Times:**")
        for func, duration in st.session_state.perf_metrics.items():
            st.text(f"{func}: {duration:.3f}s")
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Performance Optimization Guide

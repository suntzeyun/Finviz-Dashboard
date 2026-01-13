# Session State Patterns

Advanced session state usage patterns for Streamlit applications. This guide documents sophisticated state management techniques including authentication, cache invalidation, performance tracking, and common anti-patterns discovered through building production dashboards.

---

## 🎯 Overview

Session state is Streamlit's mechanism for persisting data across reruns. This guide covers:
- Authentication state management
- Active resource tracking
- Cache invalidation flags
- Performance metrics tracking
- Widget state persistence
- Common pitfalls and anti-patterns

**Based on:** Production dashboard with 7 tabs, password protection, and 40x performance optimization through session-state caching.

---

## 🔐 1. Authentication State

### 1.1 Password Protection Pattern

**Complete Implementation:**
```python
import streamlit as st

def check_password():
    """Returns True if user is authenticated."""
    
    def password_entered():
        """Callback when password is submitted."""
        # Check password
        if st.session_state["password"] == "your_secure_password":
            st.session_state["password_correct"] = True
            # Delete password from memory
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    
    # First run - no authentication attempt yet
    if "password_correct" not in st.session_state:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    
    # Password was incorrect
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    
    # Password correct
    else:
        return True

# Usage at top of app
if not check_password():
    st.stop()

# Protected content below
st.write("Welcome to the dashboard!")
```

**Key Points:**
- State key: `password_correct` (boolean)
- Temporary key: `password` (deleted after validation)
- Use `on_change` callback for immediate validation
- Use `st.stop()` to prevent unauthorized access

### 1.2 Session Timeout

**Auto-Logout After Inactivity:**
```python
from datetime import datetime, timedelta

def check_session_timeout(timeout_minutes=30):
    """Check if session has timed out."""
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()
        return False
    
    # Check time since last activity
    elapsed = datetime.now() - st.session_state.last_activity
    
    if elapsed > timedelta(minutes=timeout_minutes):
        # Timeout - clear authentication
        st.session_state.password_correct = False
        st.warning("Session timed out. Please log in again.")
        return True
    
    # Update last activity
    st.session_state.last_activity = datetime.now()
    return False

# Usage
if check_session_timeout(timeout_minutes=30):
    st.stop()
```

---

## 📂 2. Active Resource Tracking

### 2.1 Currently Loaded List Pattern

**Track Active Selection:**
```python
# Initialize
if "currently_loaded_list" not in st.session_state:
    st.session_state.currently_loaded_list = None

# When loading a list
def load_ticker_list(list_name, ticker_lists):
    """Load ticker list and track as active."""
    # Update tickers
    st.session_state.tickers = ticker_lists[list_name]
    
    # Track as active
    st.session_state.currently_loaded_list = list_name
    
    st.toast(f"✅ Loaded: {list_name}")
    st.rerun()

# When saving
def save_ticker_list(list_name, tickers, ticker_lists):
    """Save ticker list and track as active."""
    # Check if updating existing
    is_update = list_name in ticker_lists
    
    # Save
    ticker_lists[list_name] = tickers
    save_to_file(ticker_lists)
    
    # Track as active
    st.session_state.currently_loaded_list = list_name
    
    # Show appropriate message
    if is_update:
        st.toast(f"✅ Updated: {list_name}")
    else:
        st.toast(f"✅ Saved: {list_name}")

# When renaming
def rename_ticker_list(old_name, new_name, ticker_lists):
    """Rename list and update active tracking."""
    ticker_lists[new_name] = ticker_lists.pop(old_name)
    save_to_file(ticker_lists)
    
    # Update active if renamed
    if st.session_state.currently_loaded_list == old_name:
        st.session_state.currently_loaded_list = new_name
    
    st.toast(f"✅ Renamed to: {new_name}")

# When deleting
def delete_ticker_list(list_name, ticker_lists):
    """Delete list and clear active if deleted."""
    del ticker_lists[list_name]
    save_to_file(ticker_lists)
    
    # Clear active if deleted
    if st.session_state.currently_loaded_list == list_name:
        st.session_state.currently_loaded_list = None
    
    st.toast(f"🗑️ Deleted: {list_name}")

# Display active indicator
if st.session_state.currently_loaded_list:
    st.caption(f"📂 Active: {st.session_state.currently_loaded_list}")
```

### 2.2 Active Tab Tracking

**Remember Last Viewed Tab:**
```python
# Initialize
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# Create tabs
tab_names = ["Index", "Grid", "MTF", "News", "Calendar", "Journal", "Ticker"]
tabs = st.tabs([f"📊 {name}" for name in tab_names])

# Track which tab is active
for idx, (tab, name) in enumerate(zip(tabs, tab_names)):
    with tab:
        # Update active tab when content is rendered
        st.session_state.active_tab = idx
        
        # Render tab content
        render_tab_content(name)

# Use active tab for conditional logic
if st.session_state.active_tab == 3:  # News tab
    # Longer refresh interval when reading news
    refresh_interval = 300  # 5 minutes
else:
    # Normal interval
    refresh_interval = st.session_state.get("refresh_interval", 10)
```

---

## 🚫 3. Cache Invalidation Flags

### 3.1 File Modification Flags

**Force Fresh Read After Save:**
```python
# Save function sets flag
def save_ticker_lists(ticker_lists):
    """Save ticker lists with cache invalidation."""
    with open("ticker_lists.json", "w") as f:
        json.dump(ticker_lists, f, indent=2)
    
    # Set bypass flag
    st.session_state["_ticker_lists_modified"] = True

# Load function checks flag
def load_ticker_lists():
    """Load ticker lists with bypass check."""
    cache_key = "ticker_lists_cache"
    bypass_key = "_ticker_lists_modified"
    
    # Check bypass flag first
    if st.session_state.get(bypass_key, False):
        # Clear flag
        st.session_state[bypass_key] = False
        
        # Force fresh read (skip cache)
        with open("ticker_lists.json", "r") as f:
            data = json.load(f)
        
        # Update cache
        st.session_state[cache_key] = data
        return data
    
    # Normal cache check
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Load and cache
    with open("ticker_lists.json", "r") as f:
        data = json.load(f)
    st.session_state[cache_key] = data
    return data
```

### 3.2 Multiple Bypass Flags

**For Different Data Sources:**
```python
# Bypass flags for different files
BYPASS_FLAGS = {
    "settings": "_settings_modified",
    "ticker_lists": "_ticker_lists_modified",
    "journal": "_journal_modified"
}

def set_bypass_flag(data_type):
    """Set bypass flag for specific data type."""
    flag = BYPASS_FLAGS.get(data_type)
    if flag:
        st.session_state[flag] = True

def check_bypass_flag(data_type):
    """Check and clear bypass flag."""
    flag = BYPASS_FLAGS.get(data_type)
    if flag and st.session_state.get(flag, False):
        st.session_state[flag] = False
        return True
    return False

# Usage
def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    set_bypass_flag("settings")

def load_settings():
    if check_bypass_flag("settings"):
        # Force fresh read
        pass
    # Normal cache logic
```

---

## 📈 4. Performance Metrics Tracking

### 4.1 Execution Time Tracking

**Track Function Performance:**
```python
import time
from functools import wraps

def track_performance(func):
    """Decorator to track function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        # Store in session state
        if "perf_metrics" not in st.session_state:
            st.session_state.perf_metrics = {}
        
        st.session_state.perf_metrics[func.__name__] = duration
        
        return result
    return wrapper

# Usage
@track_performance
def fetch_ticker_metrics(tickers):
    # Expensive operation
    return data

# Display metrics in sidebar
if "perf_metrics" in st.session_state:
    with st.sidebar.expander("⏱️ Performance", expanded=False):
        for func_name, duration in st.session_state.perf_metrics.items():
            st.text(f"{func_name}: {duration:.3f}s")
```

### 4.2 Page Load Time

**Track Overall Page Performance:**
```python
import time

# At top of app
if "page_load_start" not in st.session_state:
    st.session_state.page_load_start = time.time()

# At bottom of app
page_load_time = time.time() - st.session_state.page_load_start
st.sidebar.metric("Page Load Time", f"{page_load_time:.2f}s")

# Reset for next rerun
st.session_state.page_load_start = time.time()
```

### 4.3 Cache Hit Rate

**Monitor Cache Effectiveness:**
```python
# Initialize counters
if "cache_hits" not in st.session_state:
    st.session_state.cache_hits = 0
    st.session_state.cache_misses = 0

def load_with_cache_tracking(cache_key, load_func):
    """Load data with cache hit tracking."""
    if cache_key in st.session_state:
        # Cache hit
        st.session_state.cache_hits += 1
        return st.session_state[cache_key]
    else:
        # Cache miss
        st.session_state.cache_misses += 1
        data = load_func()
        st.session_state[cache_key] = data
        return data

# Display cache stats
total = st.session_state.cache_hits + st.session_state.cache_misses
if total > 0:
    hit_rate = st.session_state.cache_hits / total * 100
    st.sidebar.metric("Cache Hit Rate", f"{hit_rate:.1f}%")
```

---

## 🎛️ 5. Widget State Persistence

### 5.1 Form State Preservation

**Preserve Form Input Across Reruns:**
```python
# Initialize form state
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "email": "",
        "message": ""
    }

# Form with preserved state
with st.form("contact_form"):
    name = st.text_input(
        "Name",
        value=st.session_state.form_data["name"]
    )
    email = st.text_input(
        "Email",
        value=st.session_state.form_data["email"]
    )
    message = st.text_area(
        "Message",
        value=st.session_state.form_data["message"]
    )
    
    submitted = st.form_submit_button("Submit")

if submitted:
    # Save form data
    st.session_state.form_data = {
        "name": name,
        "email": email,
        "message": message
    }
    
    # Process form
    send_message(name, email, message)
    
    # Clear form
    st.session_state.form_data = {"name": "", "email": "", "message": ""}
    st.rerun()
```

### 5.2 Multi-Step Wizard State

**Track Progress Through Multi-Step Process:**
```python
# Initialize wizard state
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
    st.session_state.wizard_data = {}

# Step 1: Basic Info
if st.session_state.wizard_step == 1:
    st.header("Step 1: Basic Information")
    name = st.text_input("Name")
    email = st.text_input("Email")
    
    if st.button("Next"):
        st.session_state.wizard_data["name"] = name
        st.session_state.wizard_data["email"] = email
        st.session_state.wizard_step = 2
        st.rerun()

# Step 2: Preferences
elif st.session_state.wizard_step == 2:
    st.header("Step 2: Preferences")
    theme = st.selectbox("Theme", ["Light", "Dark"])
    notifications = st.checkbox("Enable notifications")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.wizard_step = 1
            st.rerun()
    with col2:
        if st.button("Next"):
            st.session_state.wizard_data["theme"] = theme
            st.session_state.wizard_data["notifications"] = notifications
            st.session_state.wizard_step = 3
            st.rerun()

# Step 3: Confirmation
elif st.session_state.wizard_step == 3:
    st.header("Step 3: Confirmation")
    st.write("Review your information:")
    st.json(st.session_state.wizard_data)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.wizard_step = 2
            st.rerun()
    with col2:
        if st.button("Submit"):
            # Process data
            save_user_data(st.session_state.wizard_data)
            
            # Reset wizard
            st.session_state.wizard_step = 1
            st.session_state.wizard_data = {}
            st.success("Submitted successfully!")
            st.rerun()
```

---

## ⚠️ 6. Common Anti-Patterns

### 6.1 Infinite Rerun Loop

**Problem:**
```python
# ❌ BAD: Infinite loop
if "counter" not in st.session_state:
    st.session_state.counter = 0

# This increments every rerun!
st.session_state.counter += 1
st.write(f"Counter: {st.session_state.counter}")
# Counter keeps incrementing forever
```

**Solution:**
```python
# ✅ GOOD: Only increment on user action
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment"):
    st.session_state.counter += 1

st.write(f"Counter: {st.session_state.counter}")
```

### 6.2 Stale Local Variables

**Problem:**
```python
# ❌ BAD: Local variable doesn't update
with st.sidebar.expander("Settings"):
    auto_refresh = st.toggle("Auto-Refresh", key="auto_refresh")

# Later (expander collapsed)
if auto_refresh:  # ❌ Stale! Uses old value
    st.rerun()
```

**Solution:**
```python
# ✅ GOOD: Always use session state
with st.sidebar.expander("Settings"):
    st.toggle("Auto-Refresh", key="auto_refresh")

# Later
if st.session_state.get("auto_refresh", False):  # ✅ Always current
    st.rerun()
```

### 6.3 Uninitialized State

**Problem:**
```python
# ❌ BAD: KeyError if not initialized
value = st.session_state["my_key"]  # Crashes if key doesn't exist
```

**Solution:**
```python
# ✅ GOOD: Use .get() with default
value = st.session_state.get("my_key", default_value)

# Or initialize first
if "my_key" not in st.session_state:
    st.session_state.my_key = default_value

value = st.session_state.my_key
```

### 6.4 State Pollution

**Problem:**
```python
# ❌ BAD: Too many session state keys
st.session_state.temp_var_1 = x
st.session_state.temp_var_2 = y
st.session_state.temp_var_3 = z
# Session state gets cluttered
```

**Solution:**
```python
# ✅ GOOD: Group related state
if "temp_data" not in st.session_state:
    st.session_state.temp_data = {}

st.session_state.temp_data["var_1"] = x
st.session_state.temp_data["var_2"] = y
st.session_state.temp_data["var_3"] = z

# Or use local variables if not needed across reruns
temp_var_1 = x
temp_var_2 = y
```

---

## 🧹 7. State Cleanup

### 7.1 Clear Temporary State

**Clean Up After Operations:**
```python
def process_upload():
    """Process file upload and clean up temp state."""
    # Use temp state during processing
    st.session_state.temp_file = uploaded_file
    st.session_state.temp_progress = 0
    
    # Process...
    for i in range(100):
        st.session_state.temp_progress = i
        process_chunk(i)
    
    # Clean up temp state
    del st.session_state.temp_file
    del st.session_state.temp_progress
    
    st.success("Processing complete!")
```

### 7.2 Reset to Defaults

**Reset Button:**
```python
def reset_to_defaults():
    """Reset all settings to defaults."""
    defaults = {
        "tickers": "",
        "timeframe": "Daily",
        "num_cols": 2,
        "auto_refresh": True,
        "refresh_interval": 10
    }
    
    # Update session state
    for key, value in defaults.items():
        st.session_state[key] = value
    
    # Save to file
    save_settings(defaults)
    
    st.toast("✅ Reset to defaults")
    st.rerun()

# Reset button
if st.button("🔄 Reset to Defaults"):
    reset_to_defaults()
```

---

## 📋 8. Quick Reference

### Initialization Pattern
```python
if "key" not in st.session_state:
    st.session_state.key = default_value
```

### Safe Access
```python
value = st.session_state.get("key", default)
```

### Bypass Flag Pattern
```python
# Set flag after save
st.session_state["_data_modified"] = True

# Check flag on load
if st.session_state.get("_data_modified", False):
    st.session_state["_data_modified"] = False
    # Force fresh read
```

### Performance Tracking
```python
if "perf_metrics" not in st.session_state:
    st.session_state.perf_metrics = {}

st.session_state.perf_metrics[func_name] = duration
```

### State Cleanup
```python
del st.session_state.temp_key
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Session State Patterns  
**Based On:** Production Finviz Dashboard (password protection, 40x caching optimization, multi-tab state management)

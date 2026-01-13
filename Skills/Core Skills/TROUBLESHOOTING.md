# Troubleshooting Guide

A comprehensive troubleshooting guide for diagnosing and resolving common issues in web applications, Streamlit dashboards, and API integrations. Use this framework to quickly identify and fix problems.

---

## 🎯 Quick Diagnostic Checklist

**Before diving into specific issues, check these common culprits:**
- [ ] Is Python installed and correct version? (`python --version`)
- [ ] Are all dependencies installed? (`pip list`)
- [ ] Is virtual environment activated?
- [ ] Are environment variables set correctly?
- [ ] Is internet connection working?
- [ ] Are API keys/tokens valid and not expired?
- [ ] Is the correct port available?
- [ ] Are firewall/antivirus blocking the app?

---

## 📦 1. Installation Issues

### 1.1 Python Version Problems

**Issue:** Wrong Python version or Python not found
```
'python' is not recognized as an internal or external command
```

**Solutions:**
```bash
# Check Python version
python --version
python3 --version

# Install Python 3.8+ from python.org
# Add Python to PATH during installation

# Windows: Add to PATH manually
# System Properties → Environment Variables → Path → Add Python folder
```

**Verify Installation:**
```bash
python --version  # Should show 3.8 or higher
pip --version     # Should show pip version
```

### 1.2 Pip Installation Failures

**Issue:** Cannot install packages
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solutions:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with --user flag
pip install --user -r requirements.txt

# Use virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Clear pip cache
pip cache purge
```

### 1.3 Dependency Conflicts

**Issue:** Package version conflicts
```
ERROR: pip's dependency resolver does not currently take into account all the packages
```

**Solutions:**
```bash
# Create fresh virtual environment
rm -rf .venv  # or rd /s /q .venv on Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Install specific versions
pip install streamlit==1.30.0

# Check for conflicts
pip check
```

### 1.4 SSL Certificate Errors

**Issue:** SSL verification failed
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**
```bash
# Upgrade certifi
pip install --upgrade certifi

# Install with trusted host (temporary)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org streamlit

# Update system certificates (Windows)
# Download and run: https://curl.se/ca/cacert.pem
```

---

## 🚀 2. Streamlit Runtime Issues

### 2.1 Port Already in Use

**Issue:** Port 8501 is already occupied
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
```bash
# Find process using port (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Find process using port (Linux/Mac)
lsof -i :8501
kill -9 <PID>

# Use different port
streamlit run app.py --server.port 8502
```

### 2.2 Module Not Found Errors

**Issue:** Import errors after installation
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**
```bash
# Verify virtual environment is activated
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Reinstall package
pip install streamlit

# Check if installed
pip show streamlit

# Verify Python path
python -c "import sys; print(sys.executable)"
```

### 2.3 Streamlit Won't Start

**Issue:** App crashes on startup
```
streamlit run app.py
# No output or immediate crash
```

**Solutions:**
```bash
# Check for syntax errors
python -m py_compile app.py

# Run with verbose logging
streamlit run app.py --logger.level=debug

# Check config file
cat .streamlit/config.toml

# Reset Streamlit cache
streamlit cache clear

# Remove corrupted cache
rm -rf ~/.streamlit  # Linux/Mac
rd /s /q %USERPROFILE%\.streamlit  # Windows
```

### 2.4 Page Config Error

**Issue:** `set_page_config` must be first command
```
StreamlitAPIException: set_page_config() can only be called once per app
```

**Solution:**
```python
# CORRECT: set_page_config MUST be first Streamlit command
import streamlit as st

st.set_page_config(
    page_title="My App",
    layout="wide"
)

# Then other imports and code
import pandas as pd
# ... rest of code

# WRONG: Anything before set_page_config
import streamlit as st
import pandas as pd

@st.cache_data  # ❌ This is a Streamlit command!
def load_data():
    pass

st.set_page_config(...)  # ❌ Too late!
```

### 2.5 Rerun Loop / Infinite Refresh

**Issue:** App keeps refreshing infinitely

**Causes & Solutions:**
```python
# CAUSE 1: st.rerun() without condition
if st.button("Click"):
    st.rerun()  # ❌ Infinite loop

# FIX: Add condition
if st.button("Click"):
    if some_condition:
        st.rerun()

# CAUSE 2: Session state modification triggering rerun
if "counter" not in st.session_state:
    st.session_state.counter = 0
st.session_state.counter += 1  # ❌ Increments every rerun

# FIX: Only modify on user action
if st.button("Increment"):
    st.session_state.counter += 1

# CAUSE 3: Auto-refresh with session state bug
if st.session_state.get("auto_refresh", False):  # ✅ Correct
    time.sleep(interval)
    st.rerun()

# NOT: if auto_refresh:  # ❌ Local variable may be stale
```

---

## 🌐 3. API Integration Issues

### 3.1 API Connection Timeout

**Issue:** Requests timing out
```
requests.exceptions.Timeout: HTTPSConnectionPool
```

**Solutions:**
```python
# Increase timeout
response = requests.get(url, timeout=30)  # 30 seconds

# Add retry logic with exponential backoff
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            break
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
            continue
        raise

# Use session for connection pooling
session = requests.Session()
response = session.get(url, timeout=20)
```

### 3.2 API Rate Limiting

**Issue:** Too many requests
```
429 Too Many Requests
```

**Solutions:**
```python
# Add caching
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_data(ticker):
    return requests.get(f"https://api.example.com/{ticker}").json()

# Add rate limiting
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def fetch_ticker(ticker):
    return requests.get(f"https://api.example.com/{ticker}")
```

### 3.3 API Authentication Failures

**Issue:** 401 Unauthorized or 403 Forbidden
```
HTTPError: 401 Client Error: Unauthorized
```

**Solutions:**
```python
# Check API key is set
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API key not found. Set API_KEY environment variable.")
    st.stop()

# Verify key format
headers = {
    "Authorization": f"Bearer {api_key}",  # or "Token {api_key}"
    "User-Agent": "MyApp/1.0"
}

# Check key expiration
# Most APIs return expiration info in response headers or body

# Test with curl
# curl -H "Authorization: Bearer YOUR_KEY" https://api.example.com/test
```

### 3.4 JSON Parsing Errors

**Issue:** Cannot parse API response
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solutions:**
```python
# Check response status first
response = requests.get(url)
if response.status_code != 200:
    st.error(f"API returned status {response.status_code}")
    st.write(response.text)  # Show actual response
    st.stop()

# Try parsing with error handling
try:
    data = response.json()
except json.JSONDecodeError:
    st.error("Invalid JSON response")
    st.write("Raw response:", response.text[:500])  # First 500 chars
    st.stop()

# Check content type
if "application/json" not in response.headers.get("Content-Type", ""):
    st.warning("Response is not JSON")
```

### 3.5 CORS Errors (Browser-based)

**Issue:** Cross-Origin Resource Sharing blocked
```
Access to fetch at 'https://api.example.com' has been blocked by CORS policy
```

**Solutions:**
```python
# Use server-side requests (Python), not client-side (JavaScript)
# Streamlit runs server-side, so CORS shouldn't be an issue

# If using external API in browser:
# 1. Use proxy server
# 2. Enable CORS on API server
# 3. Use CORS proxy service (development only)

# Streamlit config for CORS
# .streamlit/config.toml
[server]
enableCORS = false
enableXsrfProtection = false
```

---

## 🔗 4. ngrok Issues

### 4.1 ngrok Not Found

**Issue:** ngrok command not recognized
```
'ngrok' is not recognized as an internal or external command
```

**Solutions:**
```bash
# Download ngrok
# https://ngrok.com/download

# Windows: Extract to C:\ngrok\
# Add to PATH or use full path

# Verify installation
ngrok version

# Use full path in batch file
C:\ngrok\ngrok.exe http 8501
```

### 4.2 ngrok Authentication Required

**Issue:** Tunnel creation failed
```
ERROR: authentication failed: usage of ngrok requires a verified account
```

**Solutions:**
```bash
# Sign up at ngrok.com (free)
# Get authtoken from dashboard

# Configure authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Verify config
ngrok config check

# Config file location:
# Windows: %USERPROFILE%\.ngrok2\ngrok.yml
# Linux/Mac: ~/.ngrok2/ngrok.yml
```

### 4.3 ngrok Tunnel Disconnects

**Issue:** Tunnel closes unexpectedly

**Solutions:**
```bash
# Check ngrok status
# Visit http://localhost:4040 (ngrok inspector)

# Increase timeout (paid feature)
# Free tier has 2-hour session limit

# Use ngrok config file for persistence
# ngrok.yml:
version: "2"
authtoken: YOUR_TOKEN
tunnels:
  streamlit:
    proto: http
    addr: 8501

# Start with config
ngrok start streamlit
```

### 4.4 Streamlit + ngrok Connection Issues

**Issue:** ngrok tunnel works but Streamlit shows errors

**Solutions:**
```python
# .streamlit/config.toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
serverAddress = "0.0.0.0"
serverPort = 8501
```

```bash
# Start Streamlit with correct settings
streamlit run app.py --server.port 8501 --server.headless true

# Wait for Streamlit to fully start before starting ngrok
timeout /t 5  # Windows
sleep 5  # Linux/Mac

# Then start ngrok
ngrok http 8501
```

---

## ☁️ 5. Streamlit Cloud Deployment Issues

### 5.1 Deployment Fails

**Issue:** App won't deploy on Streamlit Cloud
```
Error: Application failed to start
```

**Solutions:**
```bash
# Check requirements.txt exists and is correct
cat requirements.txt

# Ensure all dependencies listed
pip freeze > requirements.txt

# Check Python version
# Create runtime.txt (optional)
echo "python-3.11" > runtime.txt

# Verify main file name
# Must be: streamlit_app.py, app.py, or specified in config

# Check logs in Streamlit Cloud dashboard
# Settings → Logs
```

### 5.2 Module Import Errors on Cloud

**Issue:** Works locally but fails on cloud
```
ModuleNotFoundError: No module named 'xyz'
```

**Solutions:**
```bash
# Add missing package to requirements.txt
echo "xyz==1.2.3" >> requirements.txt

# Check for system dependencies
# Create packages.txt for apt packages
echo "libsomething-dev" > packages.txt

# Common system packages:
# packages.txt:
libgl1-mesa-glx
libglib2.0-0
```

### 5.3 Secrets Not Working

**Issue:** Environment variables not accessible
```
KeyError: 'API_KEY'
```

**Solutions:**
```python
# Use Streamlit secrets (recommended)
# Settings → Secrets in Streamlit Cloud dashboard

# secrets.toml format:
API_KEY = "your_key_here"
DB_PASSWORD = "password"

# Access in code:
api_key = st.secrets["API_KEY"]

# Fallback for local development
# .streamlit/secrets.toml (gitignored)
api_key = st.secrets.get("API_KEY", os.getenv("API_KEY", ""))
```

### 5.4 File Persistence Issues

**Issue:** Files don't persist between sessions
```
settings.json not found after restart
```

**Solutions:**
```python
# Streamlit Cloud is ephemeral - files don't persist!

# Solutions:
# 1. Use Streamlit session state (temporary)
if "settings" not in st.session_state:
    st.session_state.settings = {}

# 2. Use external database (permanent)
# - Supabase, Firebase, MongoDB Atlas
# - AWS S3, Google Cloud Storage

# 3. Use Streamlit Cloud secrets for config
# Settings → Secrets
```

### 5.5 Performance Issues on Cloud

**Issue:** App is slow on Streamlit Cloud

**Solutions:**
```python
# Add caching aggressively
@st.cache_data(ttl=300)  # 5 minutes
def expensive_operation():
    pass

# Reduce API calls
# Batch requests when possible

# Optimize imports
# Import only what you need

# Check resource limits
# Free tier: 1 GB RAM, shared CPU
# Consider upgrading if needed
```

---

## 💾 6. Data & File Issues

### 6.1 File Not Found Errors

**Issue:** Cannot find data files
```
FileNotFoundError: [Errno 2] No such file or directory: 'data.json'
```

**Solutions:**
```python
# Use absolute paths
import os
from pathlib import Path

# Get script directory
script_dir = Path(__file__).parent
data_file = script_dir / "data" / "settings.json"

# Check if file exists
if not data_file.exists():
    st.error(f"File not found: {data_file}")
    # Create default file
    data_file.parent.mkdir(exist_ok=True)
    with open(data_file, 'w') as f:
        json.dump({}, f)

# Use relative to current directory
data_file = os.path.join(os.getcwd(), "data", "settings.json")
```

### 6.2 JSON Decode Errors

**Issue:** Cannot parse JSON file
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solutions:**
```python
# Check file exists and is not empty
if os.path.getsize("data.json") == 0:
    st.warning("File is empty, using defaults")
    data = {}
else:
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        # Show file contents
        with open("data.json", "r") as f:
            st.code(f.read())
        # Use defaults
        data = {}

# Validate JSON file
import json
try:
    json.loads(open("data.json").read())
    print("Valid JSON")
except json.JSONDecodeError as e:
    print(f"Invalid JSON at line {e.lineno}, column {e.colno}")
```

### 6.3 Permission Denied Errors

**Issue:** Cannot write to file
```
PermissionError: [Errno 13] Permission denied: 'settings.json'
```

**Solutions:**
```bash
# Check file permissions
ls -l settings.json  # Linux/Mac
icacls settings.json  # Windows

# Fix permissions
chmod 644 settings.json  # Linux/Mac

# Check if file is open in another program
# Close Excel, text editors, etc.

# Check if running as administrator (Windows)
# Right-click → Run as administrator

# Use temp directory if needed
import tempfile
temp_file = tempfile.NamedTemporaryFile(delete=False)
```

---

## 🐛 7. Common Python Errors

### 7.1 IndentationError

**Issue:** Incorrect indentation
```
IndentationError: expected an indented block
```

**Solutions:**
```python
# Use consistent indentation (4 spaces recommended)
# Configure editor:
# VS Code: "editor.tabSize": 4, "editor.insertSpaces": true

# Check for mixed tabs and spaces
# Python 3 doesn't allow mixing

# Use autopep8 to fix
pip install autopep8
autopep8 --in-place --aggressive script.py
```

### 7.2 NameError

**Issue:** Variable not defined
```
NameError: name 'variable' is not defined
```

**Solutions:**
```python
# Initialize variables before use
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Check spelling
# variable vs varaible

# Check scope
def my_function():
    local_var = 10

print(local_var)  # ❌ NameError

# Fix: Return or use global
def my_function():
    return 10

result = my_function()
print(result)  # ✅
```

### 7.3 TypeError

**Issue:** Wrong type for operation
```
TypeError: can only concatenate str (not "int") to str
```

**Solutions:**
```python
# Convert types explicitly
age = 25
message = "Age: " + str(age)  # ✅

# Use f-strings (recommended)
message = f"Age: {age}"  # ✅

# Check types
if isinstance(value, str):
    # Handle string
elif isinstance(value, int):
    # Handle integer
```

---

## 🔍 8. Debugging Techniques

### 8.1 Enable Debug Logging

```python
# Streamlit debug mode
streamlit run app.py --logger.level=debug

# Python logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 8.2 Print Debugging

```python
# Use st.write for debugging
st.write("Debug:", variable)
st.write("Type:", type(variable))
st.write("Session state:", st.session_state)

# Use st.json for structured data
st.json({"key": "value", "nested": {"data": 123}})

# Use st.code for formatted output
st.code(f"Variable value: {variable}")

# Temporary debug expander
with st.expander("🐛 Debug Info", expanded=False):
    st.write("Session state:", dict(st.session_state))
    st.write("Current time:", datetime.now())
```

### 8.3 Exception Handling

```python
# Catch and display errors
try:
    result = risky_operation()
except Exception as e:
    st.error(f"Error: {type(e).__name__}")
    st.error(f"Message: {str(e)}")
    
    # Show traceback
    import traceback
    st.code(traceback.format_exc())
    
    # Log to file
    with open("error.log", "a") as f:
        f.write(f"{datetime.now()}: {traceback.format_exc()}\n")
```

---

## 📋 9. Troubleshooting Workflow

### Step-by-Step Diagnostic Process

1. **Identify the Error**
   - Read error message carefully
   - Note the line number and file
   - Copy full error traceback

2. **Reproduce the Issue**
   - Can you reproduce it consistently?
   - What are the exact steps?
   - Does it happen in different environments?

3. **Isolate the Problem**
   - Comment out code sections
   - Test individual functions
   - Use minimal reproduction

4. **Check Recent Changes**
   - What changed since it last worked?
   - Review git commits
   - Rollback if needed

5. **Search for Solutions**
   - Google the exact error message
   - Check Stack Overflow
   - Review documentation
   - Check GitHub issues

6. **Test the Fix**
   - Apply solution
   - Verify it works
   - Test edge cases
   - Document the fix

7. **Prevent Recurrence**
   - Add error handling
   - Add tests
   - Update documentation
   - Share knowledge with team

---

## 🆘 Getting Help

### Information to Provide

When asking for help, include:
- **Error message** (full traceback)
- **Python version** (`python --version`)
- **Package versions** (`pip list`)
- **Operating system** (Windows/Mac/Linux)
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Code snippet** (minimal reproduction)
- **What you've tried**

### Where to Get Help

- **Streamlit Forum**: https://discuss.streamlit.io/
- **Stack Overflow**: Tag with `streamlit`, `python`
- **GitHub Issues**: For package-specific bugs
- **Discord/Slack**: Community channels
- **Documentation**: Official docs first!

---

## 📝 Quick Reference

### Common Commands

```bash
# Check versions
python --version
pip --version
streamlit --version

# Clear caches
streamlit cache clear
pip cache purge
rm -rf __pycache__

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run with debug
streamlit run app.py --logger.level=debug

# Check for issues
python -m py_compile app.py
pip check
```

### Emergency Fixes

```bash
# Nuclear option: Fresh start
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Reset Streamlit
rm -rf ~/.streamlit
streamlit cache clear

# Reset git (careful!)
git stash
git checkout main
git pull
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Troubleshooting Guide

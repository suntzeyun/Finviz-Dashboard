# Project Organization & Cleanup Framework

A comprehensive guide for organizing, cleaning up, and maintaining professional project folder structures. This framework ensures easy navigation, proper archiving, and efficient batch file management for any Python/Streamlit project.

---

## 📁 1. Recommended Folder Structure

### 1.1 Standard Project Layout

```
project-name/
├── 📄 Batch Files (Root Level Only)
│   ├── 01_run_local.bat              # Run app locally (port 8501)
│   ├── 02_run_public_ngrok.bat       # Run with ngrok for external access
│   ├── 03_install_dependencies.bat   # Install/update requirements
│   ├── 04_run_tests.bat              # Run all tests
│   └── 05_cleanup_cache.bat          # Clean __pycache__, .pyc files
│
├── 📂 src/                            # Source code
│   ├── __init__.py
│   ├── app.py                         # Main application
│   ├── config.py                      # Configuration
│   ├── utils.py                       # Utility functions
│   └── modules/                       # Feature modules
│       ├── __init__.py
│       ├── data_fetcher.py
│       ├── chart_renderer.py
│       └── news_aggregator.py
│
├── 📂 tests/                          # Test files
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_utils.py
│   └── test_integration.py
│
├── 📂 scripts/                        # Utility scripts
│   ├── archive_old_data.py
│   ├── migrate_settings.py
│   └── generate_report.py
│
├── 📂 archive/                        # Archived/deprecated code
│   ├── 2025-12-old-implementation/
│   ├── deprecated-features/
│   └── test-scripts/
│       ├── test_api_v1.py
│       └── experimental_feature.py
│
├── 📂 data/                           # Data files
│   ├── settings.json
│   ├── ticker_lists.json
│   └── trading_journal.json
│
├── 📂 docs/                           # Documentation
│   ├── README.md
│   ├── Project_History.md
│   ├── API.md
│   └── images/
│       └── screenshots/
│
├── 📂 .streamlit/                     # Streamlit config
│   └── config.toml
│
├── 📂 logs/                           # Log files (gitignored)
│   └── app.log
│
├── 📄 Configuration Files
│   ├── requirements.txt               # Python dependencies
│   ├── .gitignore
│   ├── .env.example                   # Environment variables template
│   └── README.md                      # Project overview
│
└── 📂 .venv/                          # Virtual environment (gitignored)
```

### 1.2 Streamlit-Specific Structure

```
streamlit-dashboard/
├── 01_run_local.bat
├── 02_run_public_ngrok.bat
├── 03_install_dependencies.bat
│
├── streamlit_app.py                   # Main app (root for Streamlit Cloud)
│
├── src/
│   ├── data_fetcher.py
│   ├── chart_utils.py
│   └── news_parser.py
│
├── data/
│   ├── settings.json
│   └── ticker_lists.json
│
├── archive/
│   └── old-test-scripts/
│
└── .streamlit/
    └── config.toml
```

---

## 🔢 2. Batch File Naming Convention

### 2.1 Numbering Format

**Format:** `NN_descriptive_name.bat`

- `NN` = Two-digit number (01-99)
- Use leading zeros for proper sorting
- Group related scripts by number range

**Number Ranges:**
```
01-09: Core Operations (run, install, setup)
10-19: Development Tools (test, debug, profile)
20-29: Deployment (build, deploy, publish)
30-39: Maintenance (cleanup, backup, archive)
40-49: Utilities (convert, migrate, generate)
50-99: Project-specific scripts
```

### 2.2 Batch File Template

```batch
@echo off
REM ============================================================================
REM Script: 01_run_local.bat
REM Purpose: Run Streamlit app locally on port 8501
REM Author: [Your Name]
REM Created: 2026-01-13
REM Last Modified: 2026-01-13
REM
REM Description:
REM   Starts the Streamlit dashboard on localhost:8501
REM   Automatically opens browser window
REM   Press Ctrl+C to stop the server
REM
REM Requirements:
REM   - Python 3.8+
REM   - Streamlit installed (see requirements.txt)
REM
REM Usage:
REM   Double-click this file or run from command line
REM ============================================================================

echo.
echo ========================================
echo  Starting Streamlit Dashboard (Local)
echo ========================================
echo.
echo Server will start on: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run Streamlit
streamlit run streamlit_app.py --server.port 8501

pause
```

### 2.3 Essential Batch Files

**01_run_local.bat:**
```batch
@echo off
REM Run Streamlit app locally
streamlit run streamlit_app.py --server.port 8501
pause
```

**02_run_public_ngrok.bat:**
```batch
@echo off
REM ============================================================================
REM Script: 02_run_public_ngrok.bat
REM Purpose: Run Streamlit with ngrok for external access
REM
REM Requirements:
REM   - ngrok installed and in PATH
REM   - ngrok authtoken configured
REM
REM Setup ngrok:
REM   1. Download from https://ngrok.com/download
REM   2. Extract to C:\ngrok\ (or add to PATH)
REM   3. Run: ngrok config add-authtoken YOUR_TOKEN
REM ============================================================================

echo.
echo ========================================
echo  Starting Streamlit with ngrok
echo ========================================
echo.

REM Start Streamlit in background
start "Streamlit Server" streamlit run streamlit_app.py --server.port 8501

REM Wait for Streamlit to start
timeout /t 5 /nobreak

REM Start ngrok tunnel
echo Starting ngrok tunnel...
echo.
echo Your public URL will appear below:
echo.
ngrok http 8501

pause
```

**03_install_dependencies.bat:**
```batch
@echo off
REM Install/update Python dependencies

echo.
echo ========================================
echo  Installing Dependencies
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.

pause
```

**04_run_tests.bat:**
```batch
@echo off
REM Run all tests

echo.
echo ========================================
echo  Running Tests
echo ========================================
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run pytest
pytest tests/ -v --tb=short

echo.
pause
```

**05_cleanup_cache.bat:**
```batch
@echo off
REM Clean up Python cache files and temporary data

echo.
echo ========================================
echo  Cleaning Cache Files
echo ========================================
echo.

REM Remove __pycache__ directories
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remove .pyc files
echo Removing .pyc files...
del /s /q *.pyc 2>nul

REM Remove .pytest_cache
echo Removing pytest cache...
if exist .pytest_cache rd /s /q .pytest_cache

REM Remove .ruff_cache
echo Removing ruff cache...
if exist .ruff_cache rd /s /q .ruff_cache

REM Remove Streamlit cache
echo Removing Streamlit cache...
if exist .streamlit\cache rd /s /q .streamlit\cache

echo.
echo ========================================
echo  Cleanup Complete!
echo ========================================
echo.

pause
```

---

## 🗂️ 3. Archiving Strategy

### 3.1 What to Archive

**Archive When:**
- Code is no longer used but might be referenced
- Feature is deprecated but not deleted
- Test scripts are one-off experiments
- Old implementations replaced by new ones
- Temporary debugging code

**Don't Archive:**
- Active production code
- Current tests
- Recent bug fixes
- Documentation (update instead)

### 3.2 Archive Folder Structure

```
archive/
├── 2025-12-old-api-implementation/
│   ├── README.md                      # Why it was archived
│   ├── old_data_fetcher.py
│   └── old_config.py
│
├── deprecated-features/
│   ├── feature-x/
│   │   ├── DEPRECATED.md              # Deprecation notice
│   │   └── feature_x.py
│   └── feature-y/
│
├── test-scripts/
│   ├── 2026-01-api-test.py
│   ├── experimental_chart.py
│   └── performance_benchmark.py
│
└── migrations/
    ├── migrate_v1_to_v2.py
    └── data_migration_2025.py
```

### 3.3 Archive Documentation Template

**archive/YYYY-MM-feature-name/README.md:**
```markdown
# Archived: [Feature Name]

**Archived Date:** 2026-01-13
**Archived By:** [Your Name]
**Reason:** Replaced by new implementation

## Original Purpose
[What this code did]

## Why Archived
[Why it was replaced/deprecated]

## Replacement
[What replaced it, if applicable]
- New implementation: `src/new_feature.py`
- Migration guide: `docs/migration_v2.md`

## Dependencies
[Any dependencies this code had]

## Notes
[Any important notes for future reference]
```

### 3.4 Archiving Checklist

**Before Archiving:**
- [ ] Code is no longer referenced in production
- [ ] Tests for this code removed/updated
- [ ] Documentation updated to reflect removal
- [ ] Dependencies cleaned up (if unique to archived code)
- [ ] README.md created in archive folder
- [ ] Git commit message explains archival

**Archive Process:**
```bash
# 1. Create archive folder with date
mkdir archive/2026-01-old-feature

# 2. Move files
move src/old_feature.py archive/2026-01-old-feature/

# 3. Create README
echo "# Archived: Old Feature" > archive/2026-01-old-feature/README.md

# 4. Commit
git add .
git commit -m "Archive: Moved old feature implementation to archive/"
```

---

## 🧹 4. Cleanup Procedures

### 4.1 Regular Cleanup Schedule

**Daily:**
- Clear temporary files
- Remove debug print statements

**Weekly:**
- Clean Python cache (`__pycache__`, `.pyc`)
- Review and archive test scripts
- Update .gitignore if needed

**Monthly:**
- Archive deprecated code
- Review and clean logs
- Update dependencies
- Remove unused imports

**Quarterly:**
- Full codebase review
- Reorganize folder structure if needed
- Archive old documentation versions
- Clean up git history (if needed)

### 4.2 Cleanup Checklist

**Code Cleanup:**
- [ ] Remove commented-out code
- [ ] Remove unused imports
- [ ] Remove debug print statements
- [ ] Remove TODO comments (or create issues)
- [ ] Consolidate duplicate code
- [ ] Update outdated comments

**File Cleanup:**
- [ ] Delete temporary files (`.tmp`, `.bak`)
- [ ] Archive old test scripts
- [ ] Remove empty directories
- [ ] Clean up log files
- [ ] Remove duplicate files

**Dependency Cleanup:**
- [ ] Remove unused packages from requirements.txt
- [ ] Update outdated packages
- [ ] Check for security vulnerabilities
- [ ] Verify all imports are in requirements.txt

### 4.3 Automated Cleanup Script

**scripts/cleanup.py:**
```python
"""
Automated cleanup script for project maintenance.
Run weekly to keep project organized.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def remove_pycache():
    """Remove all __pycache__ directories."""
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"Removing: {pycache_path}")
            shutil.rmtree(pycache_path)

def remove_old_logs(days=30):
    """Remove log files older than specified days."""
    log_dir = Path('logs')
    if not log_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for log_file in log_dir.glob('*.log'):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
            print(f"Removing old log: {log_file}")
            log_file.unlink()

def list_large_files(size_mb=10):
    """List files larger than specified size."""
    print(f"\nFiles larger than {size_mb}MB:")
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and git
        if '.venv' in root or '.git' in root:
            continue
        
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            if size > size_mb:
                print(f"  {filepath}: {size:.2f}MB")

if __name__ == '__main__':
    print("=" * 50)
    print("Project Cleanup")
    print("=" * 50)
    
    remove_pycache()
    remove_old_logs(days=30)
    list_large_files(size_mb=10)
    
    print("\nCleanup complete!")
```

---

## 📦 5. Python Library Organization

### 5.1 Module Structure

**Keep Libraries in Organized Folders:**
```
src/
├── __init__.py
├── data/                              # Data handling modules
│   ├── __init__.py
│   ├── fetcher.py                     # API data fetching
│   ├── parser.py                      # Data parsing
│   └── cache.py                       # Caching logic
│
├── ui/                                # UI components
│   ├── __init__.py
│   ├── charts.py                      # Chart rendering
│   ├── tables.py                      # Table components
│   └── forms.py                       # Form elements
│
├── utils/                             # Utility functions
│   ├── __init__.py
│   ├── validators.py                  # Input validation
│   ├── formatters.py                  # Data formatting
│   └── helpers.py                     # Helper functions
│
└── config/                            # Configuration
    ├── __init__.py
    ├── settings.py                    # App settings
    └── constants.py                   # Constants
```

### 5.2 Import Organization

**In main app (streamlit_app.py):**
```python
"""
Main Streamlit application.
Imports are organized by category.
"""

# Standard library
import os
import json
import time
from datetime import datetime

# Third-party
import streamlit as st
import pandas as pd
import requests

# Local modules - data
from src.data.fetcher import fetch_ticker_metrics
from src.data.parser import parse_finviz_response
from src.data.cache import cache_data

# Local modules - UI
from src.ui.charts import render_chart
from src.ui.tables import render_metrics_table

# Local modules - utils
from src.utils.validators import clean_tickers
from src.utils.formatters import format_percentage

# Local modules - config
from src.config.settings import load_settings, save_settings
from src.config.constants import TIMEFRAME_OPTIONS
```

### 5.3 Module Best Practices

**Each module should:**
- [ ] Have a clear, single purpose
- [ ] Include docstring at top
- [ ] Have `__init__.py` in package folders
- [ ] Use relative imports within package
- [ ] Export public API via `__all__`

**Example module (src/data/fetcher.py):**
```python
"""
Data fetching module.

This module handles all external API calls including:
- Finviz screener data
- Yahoo Finance RSS feeds
- Economic calendar data
"""

import requests
from typing import List, Dict, Optional

__all__ = ['fetch_ticker_metrics', 'fetch_news', 'fetch_calendar']

def fetch_ticker_metrics(tickers: List[str]) -> Dict:
    """Fetch performance metrics for tickers."""
    # Implementation
    pass

def fetch_news(ticker: str) -> List[Dict]:
    """Fetch news for specific ticker."""
    # Implementation
    pass
```

---

## ✂️ 6. Code Refactoring & Helper Files

### 6.1 When to Refactor

**File Size Thresholds:**
```
� Green Zone:    < 500 lines   - Acceptable, no action needed
🟡 Yellow Zone:   500-1000 lines - Consider refactoring
🟠 Orange Zone:   1000-2000 lines - Should refactor soon
🔴 Red Zone:      > 2000 lines   - Refactor immediately
```

**Signs You Need Helper Files:**
- [ ] File exceeds 500 lines
- [ ] Scrolling to find functions takes too long
- [ ] Multiple unrelated features in one file
- [ ] Duplicate code patterns
- [ ] Functions doing multiple things
- [ ] Difficult to test individual components
- [ ] Hard to understand file purpose at a glance

### 6.2 Refactoring Strategy

**Step 1: Identify Logical Groups**

Analyze your large file and group related functionality:
```python
# Example: streamlit_app.py (2740 lines) can be split into:

# 1. Settings & Configuration (lines 1-250)
#    → src/config/settings.py
#    → src/config/constants.py

# 2. Data Fetching (lines 250-650)
#    → src/data/finviz_fetcher.py
#    → src/data/news_fetcher.py
#    → src/data/calendar_fetcher.py

# 3. Data Processing (lines 650-900)
#    → src/utils/data_cleaners.py
#    → src/utils/formatters.py

# 4. UI Components (lines 900-2500)
#    → src/ui/charts.py
#    → src/ui/tables.py
#    → src/ui/news_feed.py
#    → src/ui/trading_journal.py

# 5. Main App Logic (lines 2500-2740)
#    → streamlit_app.py (keep minimal, just orchestration)
```

**Step 2: Create Helper Files**

**Before (monolithic file):**
```python
# streamlit_app.py - 2740 lines

import streamlit as st
import requests
# ... 50 more imports

def fetch_ticker_metrics(tickers):
    # 100 lines of code
    pass

def fetch_finviz_news(tickers):
    # 80 lines of code
    pass

def fetch_rss_news(tickers):
    # 120 lines of code
    pass

def clean_tickers(tickers):
    # 30 lines of code
    pass

def render_chart(ticker, timeframe):
    # 150 lines of code
    pass

# ... 2000 more lines
```

**After (refactored):**

**src/data/finviz_fetcher.py:**
```python
"""
Finviz data fetching module.
Handles all Finviz API interactions.
"""

import requests
from typing import List, Dict

def fetch_ticker_metrics(tickers: List[str]) -> Dict:
    """Fetch performance metrics from Finviz."""
    # 100 lines of implementation
    pass

def fetch_finviz_news(tickers: str) -> List[Dict]:
    """Fetch news from Finviz Elite API."""
    # 80 lines of implementation
    pass
```

**src/data/news_fetcher.py:**
```python
"""
News aggregation module.
Fetches news from multiple RSS sources.
"""

import feedparser
from typing import List, Dict

def fetch_rss_news(tickers: str = "") -> List[Dict]:
    """Fetch news from RSS feeds."""
    # 120 lines of implementation
    pass
```

**src/utils/validators.py:**
```python
"""
Input validation utilities.
"""

from typing import List, Union

def clean_tickers(tickers: Union[str, List[str]]) -> List[str]:
    """Clean and deduplicate ticker list."""
    # 30 lines of implementation
    pass
```

**src/ui/charts.py:**
```python
"""
Chart rendering components.
"""

import streamlit as st

def render_chart(ticker: str, timeframe: str, height: int = 350):
    """Render Finviz chart for ticker."""
    # 150 lines of implementation
    pass
```

**streamlit_app.py (now ~300 lines):**
```python
"""
Main Streamlit application.
Orchestrates UI and data flow.
"""

import streamlit as st

# Import helper modules
from src.data.finviz_fetcher import fetch_ticker_metrics, fetch_finviz_news
from src.data.news_fetcher import fetch_rss_news
from src.utils.validators import clean_tickers
from src.ui.charts import render_chart
from src.config.settings import load_settings, save_settings

# Page config
st.set_page_config(...)

# Main app logic (orchestration only)
def main():
    settings = load_settings()
    tickers = clean_tickers(settings['tickers'])
    metrics = fetch_ticker_metrics(tickers)
    
    # Render UI
    for ticker in tickers:
        render_chart(ticker, settings['timeframe'])

if __name__ == '__main__':
    main()
```

### 6.3 Refactoring Checklist

**Before Refactoring:**
- [ ] Commit current working code
- [ ] Create backup branch
- [ ] Document current functionality
- [ ] Run existing tests (if any)
- [ ] Note any known issues

**During Refactoring:**
- [ ] Create helper file with clear name
- [ ] Move related functions together
- [ ] Add module docstring
- [ ] Update imports in main file
- [ ] Test each moved function
- [ ] Remove unused imports

**After Refactoring:**
- [ ] Run full test suite
- [ ] Verify app still works
- [ ] Update documentation
- [ ] Clean up old code
- [ ] Commit with clear message

### 6.4 Practical Refactoring Examples

**Example 1: Extract Data Fetching**

**Before:**
```python
# streamlit_app.py (lines 437-522)
def fetch_sorted_tickers(tickers, sort_option):
    tickers = clean_tickers(tickers)
    ticker_str = ",".join(tickers)
    api_token = st.session_state.get("finviz_cookie", "").strip()
    
    # 80 lines of implementation...
    
    return sorted_tickers
```

**After:**
```python
# src/data/finviz_fetcher.py
def fetch_sorted_tickers(tickers: List[str], sort_option: str, 
                        api_token: str = "") -> List[str]:
    """
    Fetch and sort tickers by specified metric.
    
    Args:
        tickers: List of ticker symbols
        sort_option: Finviz sort code (e.g., '-perfi30')
        api_token: Optional Finviz Elite API token
    
    Returns:
        List of sorted ticker symbols
    """
    # 80 lines of implementation...
    return sorted_tickers

# streamlit_app.py
from src.data.finviz_fetcher import fetch_sorted_tickers

# Usage
api_token = st.session_state.get("finviz_cookie", "")
sorted_list = fetch_sorted_tickers(tickers, sort_option, api_token)
```

**Example 2: Extract UI Components**

**Before:**
```python
# streamlit_app.py (lines 1290-1310)
# Quick metrics table rendering inline
table_data = []
for ticker in current_tickers:
    m = table_metrics.get(ticker, {})
    # 20 lines of table building...
st.sidebar.dataframe(df_display, ...)
```

**After:**
```python
# src/ui/tables.py
def render_quick_metrics_table(tickers: List[str], 
                               metrics: Dict) -> None:
    """
    Render quick metrics table in sidebar.
    
    Args:
        tickers: List of ticker symbols
        metrics: Dictionary of ticker metrics
    """
    table_data = []
    for ticker in tickers:
        m = metrics.get(ticker, {})
        # 20 lines of table building...
    
    st.sidebar.dataframe(df_display, ...)

# streamlit_app.py
from src.ui.tables import render_quick_metrics_table

# Usage
render_quick_metrics_table(current_tickers, table_metrics)
```

**Example 3: Extract Configuration**

**Before:**
```python
# streamlit_app.py (scattered throughout)
tf_options = {
    "1 Minute": "i1",
    "3 Minutes": "i3",
    # ... 7 more entries
}

sort_options = {
    "Ticker": "ticker",
    "Perf 30min": "perfi30",
    # ... 5 more entries
}
```

**After:**
```python
# src/config/constants.py
"""Application constants and configuration."""

TIMEFRAME_OPTIONS = {
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

SORT_OPTIONS = {
    "Ticker": "ticker",
    "Perf 30min": "perfi30",
    "Perf 15min": "perfi15",
    "Perf 10min": "perfi10",
    "SMA20": "sma20",
    "Change": "change",
    "Change from Open": "changefromopen"
}

REFRESH_INTERVALS = [10, 15, 20, 30, 300, 600]  # seconds

# streamlit_app.py
from src.config.constants import TIMEFRAME_OPTIONS, SORT_OPTIONS

# Usage
selected_tf = st.selectbox("Timeframe", list(TIMEFRAME_OPTIONS.keys()))
```

### 6.5 Helper File Organization

**Recommended Helper Structure:**
```
src/
├── data/                              # Data operations
│   ├── finviz_fetcher.py             # Finviz API calls
│   ├── news_fetcher.py               # News aggregation
│   ├── calendar_fetcher.py           # Economic calendar
│   └── etf_fetcher.py                # ETF holdings
│
├── ui/                                # UI components
│   ├── charts.py                     # Chart rendering
│   ├── tables.py                     # Table components
│   ├── news_feed.py                  # News display
│   ├── trading_journal.py            # Journal UI
│   └── ticker_view.py                # Ticker view tab
│
├── utils/                             # Utilities
│   ├── validators.py                 # Input validation
│   ├── formatters.py                 # Data formatting
│   ├── cache_helpers.py              # Caching utilities
│   └── session_helpers.py            # Session state helpers
│
└── config/                            # Configuration
    ├── settings.py                   # Settings management
    └── constants.py                  # Constants
```

### 6.6 Migration Script Template

**scripts/refactor_to_helpers.py:**
```python
"""
Script to help migrate code to helper files.
Analyzes main file and suggests refactoring.
"""

import re
from pathlib import Path

def analyze_file(filepath: str):
    """Analyze file and suggest refactoring."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    
    # Count functions
    functions = re.findall(r'^def\s+(\w+)', ''.join(lines), re.MULTILINE)
    
    # Count imports
    imports = [l for l in lines if l.startswith('import ') or l.startswith('from ')]
    
    print(f"File Analysis: {filepath}")
    print(f"=" * 50)
    print(f"Total Lines: {total_lines}")
    print(f"Total Functions: {len(functions)}")
    print(f"Total Imports: {len(imports)}")
    print()
    
    # Recommendations
    if total_lines > 2000:
        print("🔴 CRITICAL: File exceeds 2000 lines!")
        print("   Immediate refactoring recommended")
    elif total_lines > 1000:
        print("🟠 WARNING: File exceeds 1000 lines")
        print("   Refactoring recommended soon")
    elif total_lines > 500:
        print("🟡 NOTICE: File exceeds 500 lines")
        print("   Consider refactoring")
    else:
        print("🟢 OK: File size acceptable")
    
    print()
    print("Suggested Helper Files:")
    
    # Suggest based on function names
    data_funcs = [f for f in functions if 'fetch' in f or 'load' in f or 'save' in f]
    ui_funcs = [f for f in functions if 'render' in f or 'display' in f or 'show' in f]
    util_funcs = [f for f in functions if 'clean' in f or 'format' in f or 'validate' in f]
    
    if data_funcs:
        print(f"  → src/data/fetcher.py ({len(data_funcs)} functions)")
    if ui_funcs:
        print(f"  → src/ui/components.py ({len(ui_funcs)} functions)")
    if util_funcs:
        print(f"  → src/utils/helpers.py ({len(util_funcs)} functions)")

if __name__ == '__main__':
    analyze_file('streamlit_app.py')
```

### 6.7 Refactoring Best Practices

**Do:**
- ✅ Refactor one module at a time
- ✅ Test after each refactoring step
- ✅ Keep related functions together
- ✅ Use clear, descriptive file names
- ✅ Add docstrings to all modules
- ✅ Update imports incrementally
- ✅ Commit frequently with clear messages

**Don't:**
- ❌ Refactor everything at once
- ❌ Split functions arbitrarily
- ❌ Create too many small files
- ❌ Forget to update imports
- ❌ Skip testing after changes
- ❌ Leave orphaned code
- ❌ Lose git history

---

## �🚀 7. ngrok Integration

### 6.1 ngrok Setup

**Installation:**
```batch
REM Download ngrok
REM https://ngrok.com/download

REM Extract to C:\ngrok\

REM Add to PATH or use full path in batch files

REM Configure authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 6.2 ngrok Batch File (Advanced)

**02_run_public_ngrok.bat:**
```batch
@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM Script: 02_run_public_ngrok.bat
REM Purpose: Run Streamlit with ngrok tunnel for external access
REM ============================================================================

echo.
echo ========================================
echo  Streamlit + ngrok Public Access
echo ========================================
echo.

REM Configuration
set PORT=8501
set NGROK_REGION=us
set APP_FILE=streamlit_app.py

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ngrok not found in PATH
    echo.
    echo Please install ngrok:
    echo 1. Download from https://ngrok.com/download
    echo 2. Extract to C:\ngrok\
    echo 3. Add to PATH or place in project folder
    echo 4. Run: ngrok config add-authtoken YOUR_TOKEN
    echo.
    pause
    exit /b 1
)

REM Check if Streamlit app exists
if not exist %APP_FILE% (
    echo ERROR: %APP_FILE% not found
    pause
    exit /b 1
)

REM Start Streamlit in background
echo [1/3] Starting Streamlit server on port %PORT%...
start "Streamlit Server" /MIN streamlit run %APP_FILE% --server.port %PORT% --server.headless true

REM Wait for Streamlit to initialize
echo [2/3] Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Start ngrok tunnel
echo [3/3] Starting ngrok tunnel (region: %NGROK_REGION%)...
echo.
echo ========================================
echo  Public URL (share this link):
echo ========================================
echo.

ngrok http %PORT% --region=%NGROK_REGION%

REM Cleanup on exit
echo.
echo Shutting down...
taskkill /FI "WINDOWTITLE eq Streamlit Server" /F >nul 2>nul

pause
```

### 6.3 ngrok Configuration File

**ngrok.yml (optional):**
```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
region: us
tunnels:
  streamlit:
    proto: http
    addr: 8501
    inspect: true
    bind_tls: true
```

**Run with config:**
```batch
ngrok start streamlit
```

---

## 📋 7. Project Organization Checklist

### 7.1 Initial Setup

- [ ] Create folder structure
- [ ] Set up virtual environment
- [ ] Create numbered batch files
- [ ] Write README.md
- [ ] Configure .gitignore
- [ ] Initialize git repository

### 7.2 Ongoing Maintenance

**Weekly:**
- [ ] Run cleanup batch file
- [ ] Archive completed test scripts
- [ ] Update documentation

**Monthly:**
- [ ] Review folder structure
- [ ] Archive deprecated code
- [ ] Update dependencies
- [ ] Clean up logs

**Quarterly:**
- [ ] Full project reorganization review
- [ ] Update batch file descriptions
- [ ] Consolidate similar scripts

### 7.3 Before Sharing/Deploying

- [ ] All batch files have clear descriptions
- [ ] README.md is up to date
- [ ] No sensitive data in repository
- [ ] .gitignore configured correctly
- [ ] Dependencies listed in requirements.txt
- [ ] Archive folder cleaned up
- [ ] Test scripts moved to archive/
- [ ] All batch files tested

---

## 🎯 Quick Reference

### Folder Organization Rules
1. **Batch files** → Root level only, numbered
2. **Source code** → `src/` folder, organized by feature
3. **Tests** → `tests/` folder, mirror src structure
4. **Old code** → `archive/` folder with date/description
5. **Data files** → `data/` folder
6. **Documentation** → `docs/` folder or root

### Batch File Naming
```
01-09: Core (run, install, setup)
10-19: Development (test, debug)
20-29: Deployment (build, deploy)
30-39: Maintenance (cleanup, backup)
40-49: Utilities (convert, migrate)
50-99: Project-specific
```

### Archive Naming
```
archive/
├── YYYY-MM-description/           # Date-based
├── deprecated-feature-name/       # Feature-based
└── test-scripts/                  # Category-based
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Project Organization Guidelines

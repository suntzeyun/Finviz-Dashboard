# Code Documentation Framework

A comprehensive guide for documenting code, projects, and technical implementations. This framework ensures maintainability, knowledge transfer, and professional standards across all development projects.

---

## 📚 Documentation Philosophy

### Core Principles
1. **Write for Future You** - Document as if you'll forget everything in 6 months
2. **Clarity Over Brevity** - Be thorough but concise
3. **Living Documents** - Keep documentation updated with code changes
4. **Progressive Disclosure** - Start simple, add detail as needed
5. **Searchable** - Use clear headings and keywords
6. **Actionable** - Include examples and code snippets

---

## 📋 1. Project Documentation Structure

### 1.1 Essential Documents

**README.md** - Project overview and quick start
```markdown
# Project Name

Brief description (1-2 sentences)

## Features
- Feature 1
- Feature 2

## Quick Start
```bash
# Installation
pip install -r requirements.txt

# Run
streamlit run app.py
```

## Documentation
- [Project History](Project_History.md)
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
```

**Project_History.md** - Development timeline and decisions
- Session logs with dates
- Major accomplishments
- Technical changes
- Bug fixes
- Architecture notes

**CHANGELOG.md** - Version history
```markdown
# Changelog

## [1.2.0] - 2026-01-13
### Added
- Auto-refresh 5m and 10m intervals
- Session state bug fix

### Fixed
- Auto-refresh toggle not working
- Refresh interval not persisting

### Changed
- Updated refresh interval display format
```

**API.md** - API endpoints and usage (if applicable)

**DEPLOYMENT.md** - Deployment instructions and configuration

### 1.2 Optional Documents

- **CONTRIBUTING.md** - Contribution guidelines
- **ARCHITECTURE.md** - System design and architecture
- **TROUBLESHOOTING.md** - Common issues and solutions
- **FAQ.md** - Frequently asked questions
- **SECURITY.md** - Security policies and reporting

---

## 💻 2. Code Documentation

### 2.1 File Headers

**Python Files:**
```python
"""
Module: data_fetcher.py
Purpose: Fetch and parse data from external APIs
Author: [Name]
Created: 2026-01-13
Last Modified: 2026-01-13

This module handles all external API interactions including:
- Finviz screener data
- Yahoo Finance RSS feeds
- Economic calendar data

Dependencies:
- requests
- beautifulsoup4
- feedparser
"""

import requests
from bs4 import BeautifulSoup
```

**Configuration Files:**
```toml
# .streamlit/config.toml
# Streamlit configuration for production deployment
# Last updated: 2026-01-13

[server]
# Use headless mode for cloud deployment
headless = true
```

### 2.2 Function Documentation

**Docstring Format (Google Style):**
```python
def fetch_ticker_metrics(tickers):
    """Fetch performance metrics for given tickers from Finviz.
    
    This function queries the Finviz API (Elite or Free) to retrieve
    intraday performance metrics including 10m, 15m, and 30m changes.
    Results are cached for 60 seconds to reduce API calls.
    
    Args:
        tickers (list or str): List of ticker symbols or comma-separated string.
            Examples: ['AAPL', 'MSFT'] or 'AAPL,MSFT'
    
    Returns:
        dict: Dictionary mapping tickers to their metrics.
            Format: {
                'AAPL': {
                    'perf_10m': '+0.5%',
                    'perf_15m': '+0.8%',
                    'perf_30m': '+1.2%',
                    'price': '150.25',
                    'change': '+2.5%'
                }
            }
            Returns empty dict {} if fetch fails.
    
    Raises:
        requests.exceptions.Timeout: If API request exceeds 20s timeout.
        ValueError: If tickers parameter is invalid type.
    
    Example:
        >>> metrics = fetch_ticker_metrics(['AAPL', 'MSFT'])
        >>> print(metrics['AAPL']['perf_30m'])
        '+1.2%'
    
    Note:
        - Requires Finviz Elite API token for intraday metrics
        - Falls back to free tier if token not provided
        - Uses session-based caching for performance
    """
    # Implementation
```

**Minimal Docstring (for simple functions):**
```python
def clean_tickers(tickers):
    """Clean and deduplicate ticker list, supporting comma/newline separation."""
    # Implementation
```

### 2.3 Inline Comments

**When to Comment:**
- Complex logic or algorithms
- Non-obvious workarounds
- Business logic decisions
- Performance optimizations
- Bug fixes (reference issue number)

**Good Comments:**
```python
# Use session state instead of local variables to ensure settings
# persist correctly when sidebar expander is collapsed (Bug #42)
if st.session_state.get("auto_refresh", False):
    
# Exponential backoff: 2s, 4s, 6s for retries
time.sleep(2 * (attempt + 1))

# Column 96 is Finviz's ID for 30-minute performance (Elite only)
col_str = "0,1,90,94,95,96,52,65,66"
```

**Bad Comments:**
```python
# Increment i
i += 1

# Get the ticker
ticker = row[1]
```

### 2.4 TODO Comments

**Format:**
```python
# TODO(username): Add error handling for network timeouts
# FIXME: Memory leak when processing 1000+ tickers
# HACK: Temporary workaround until API v2 is available
# NOTE: This assumes data is always in ascending order
# OPTIMIZE: Consider caching this expensive operation
```

---

## 📊 3. API Documentation

### 3.1 Endpoint Documentation

**REST API Format:**
```markdown
## GET /api/tickers

Retrieve ticker data with performance metrics.

**Endpoint:** `https://api.example.com/tickers`

**Authentication:** Bearer token required

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbols | string | Yes | Comma-separated ticker symbols |
| timeframe | string | No | Chart timeframe (default: 'd') |
| metrics | boolean | No | Include performance metrics (default: true) |

**Request Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/tickers?symbols=AAPL,MSFT&timeframe=i15"
```

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "AAPL": {
      "price": 150.25,
      "change": 2.5,
      "perf_30m": 1.2
    }
  }
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| 400 | Invalid parameters |
| 401 | Unauthorized |
| 429 | Rate limit exceeded |
| 500 | Server error |
```

### 3.2 Function API Documentation

**Public Functions:**
```python
# In API.md or separate documentation

## fetch_sorted_tickers(tickers, sort_option)

Fetch and sort tickers by specified metric.

**Parameters:**
- `tickers` (list): Ticker symbols to sort
- `sort_option` (str): Finviz sort code (e.g., '-perfi30' for 30m desc)

**Returns:**
- `list`: Sorted ticker symbols

**Example:**
```python
sorted_list = fetch_sorted_tickers(['AAPL', 'MSFT', 'GOOGL'], '-perfi30')
# Returns: ['MSFT', 'AAPL', 'GOOGL'] (sorted by 30m performance)
```

**Notes:**
- Requires Elite API token for intraday sorting
- Preserves original order if sorting fails
```

---

## 🏗️ 4. Architecture Documentation

### 4.1 System Architecture

**High-Level Overview:**
```markdown
## Architecture Overview

### Components
1. **Frontend**: Streamlit (Python)
2. **Data Sources**: 
   - Finviz API (Elite/Free)
   - Yahoo Finance RSS
   - Forex Factory Calendar
3. **Storage**: Local JSON files
4. **Hosting**: Streamlit Community Cloud

### Data Flow
```
User Input → Streamlit UI → Data Fetcher → External APIs
                ↓                              ↓
          Session State ←──────────────── Cached Data
                ↓
          JSON Storage (settings, lists, journal)
```

### Performance Optimizations
- Session-state caching for file I/O (40x reduction)
- Concurrent RSS fetching (5x faster)
- API response caching (60s TTL)
- Lazy image loading
```

### 4.2 Design Decisions

**Document Key Decisions:**
```markdown
## Design Decision: Session State vs Local Variables

**Date:** 2026-01-13
**Decision:** Use `st.session_state` for all user settings instead of local variables

**Context:**
Auto-refresh settings were not persisting when sidebar expander was collapsed.

**Alternatives Considered:**
1. Global variables (rejected: not Streamlit-compatible)
2. Local variables from widgets (rejected: don't persist)
3. Session state (chosen)

**Rationale:**
- Session state persists across reruns
- Works regardless of widget visibility
- Streamlit's recommended approach

**Consequences:**
- Slightly more verbose code
- Better reliability
- Easier to debug

**References:**
- Streamlit docs: https://docs.streamlit.io/library/api-reference/session-state
- Bug fix: Project_History.md (2026-01-13)
```

### 4.3 Data Models

**Document Data Structures:**
```python
# In ARCHITECTURE.md or code comments

"""
Settings Data Model (settings.json):
{
    "tickers": "AAPL,MSFT,GOOGL",           # Comma-separated string
    "timeframe": "3 Minutes",                # Display name
    "num_cols": 2,                           # Integer 1-4
    "auto_refresh": true,                    # Boolean
    "refresh_interval": 10,                  # Seconds (int)
    "chart_height": 350,                     # Pixels (int)
    "sort_by": "Perf 30min",                # Display name
    "sort_order": "DESC",                    # "ASC" or "DESC"
    "finviz_cookie": "encrypted_token",      # String (sensitive)
    "show_metrics": true                     # Boolean
}

Ticker Lists Data Model (ticker_lists.json):
{
    "Tech Stocks": "AAPL,MSFT,GOOGL,NVDA",
    "Energy": "XLE,XOM,CVX",
    "My Watchlist": "SPY,QQQ,IWM"
}

Trading Journal Data Model (trading_journal.json):
{
    "Tech Stocks_AAPL": {
        "list_name": "Tech Stocks",
        "ticker": "AAPL",
        "journal": "Watching for breakout above 150...",
        "last_updated": "2026-01-13T10:30:00"
    },
    "_TICKER_AAPL": {                        # Ticker-only journal
        "list_name": "_TICKER_",
        "ticker": "AAPL",
        "journal": "Long-term hold, strong fundamentals",
        "last_updated": "2026-01-13T10:30:00"
    }
}
"""
```

---

## 🐛 5. Bug Documentation

### 5.1 Bug Report Format

**In Project_History.md or Issue Tracker:**
```markdown
### 🐛 Bug: Auto-Refresh Not Working

**Date Reported:** 2026-01-13
**Severity:** High
**Status:** ✅ Fixed

**Problem:**
- Auto-refresh toggle had no effect
- Changing refresh interval didn't change timing
- Dashboard refreshed regardless of settings

**Root Cause:**
Auto-refresh logic used local variables (`auto_refresh`, `refresh_interval`) 
instead of session state values. When sidebar expander was collapsed, 
variables didn't reflect user settings.

**Solution:**
Changed lines 2726 and 2738 to use `st.session_state.get()` instead of 
local variables.

**Code Changes:**
```python
# Before
if auto_refresh:
    time.sleep(refresh_interval)

# After
if st.session_state.get("auto_refresh", False):
    interval = st.session_state.get("refresh_interval", 10)
    time.sleep(interval)
```

**Testing:**
- ✅ Toggle auto-refresh on/off
- ✅ Change interval to 10s, 15s, 20s, 30s, 5m, 10m
- ✅ Settings persist across page refresh
- ✅ Works with sidebar collapsed

**Lessons Learned:**
Always use session state for persistent settings in Streamlit, especially 
when widgets are inside collapsible containers.
```

### 5.2 Known Issues

**Document Limitations:**
```markdown
## Known Issues

### Issue #1: ETF Holdings Fetch Timeout on Cloud
**Status:** Workaround Available
**Severity:** Medium

**Description:**
Yahoo Finance ETF holdings scraping times out on Streamlit Cloud 
(20s limit) but works locally.

**Workaround:**
Use local deployment with ngrok for ETF holdings feature.

**Permanent Fix:**
Migrate to alternative API or increase timeout (requires paid hosting).

### Issue #2: Intraday Metrics Require Elite Subscription
**Status:** By Design
**Severity:** Low

**Description:**
10m, 15m, 30m performance metrics only available with Finviz Elite.

**Workaround:**
Use daily performance metrics on free tier.
```

---

## 📝 6. Session Log Format

### 6.1 Development Session Template

**From Project_History.md:**
```markdown
## 📅 Session Log: [Date]

### 🚀 Major Accomplishments
- **Feature Name**: Brief description of what was added
- **Integration**: What was integrated and why
- **Optimization**: Performance improvements made

### 🛠️ Technical Changes
- Updated `function_name()` to include X feature
- Added `new_module.py` for Y functionality
- Migrated from approach A to approach B
- Column ID discovery: Column 96 = 30-minute performance

### 🐛 Bug Fixes
- **Issue Description**: What was broken
  - Root Cause: Why it was broken
  - Solution: How it was fixed
  - Testing: How it was verified

### 📊 User Experience Improvements
- Added visual feedback for action X
- Improved layout for better readability
- Reduced clicks from 5 to 2 for common workflow

### 🎯 Current Status
- ✅ Feature A complete and tested
- ✅ Bug B fixed and verified
- ⏳ Feature C in progress
- 📋 Feature D planned for next session

### 📝 Next Steps
- [ ] Implement feature X
- [ ] Optimize performance for Y
- [ ] Add tests for Z
```

### 6.2 What to Document in Sessions

**Always Include:**
- Date and session number
- What was accomplished (features, fixes, optimizations)
- Technical implementation details
- Code changes (file names, function names)
- Testing performed
- Current status

**Include When Relevant:**
- API discoveries (column IDs, endpoints)
- Performance metrics (before/after)
- Design decisions and rationale
- User feedback incorporated
- Breaking changes
- Migration notes

---

## 🔧 7. Configuration Documentation

### 7.1 Configuration Files

**Document All Settings:**
```python
# config.py or in README.md

"""
Configuration Guide

## Environment Variables
- `FINVIZ_API_TOKEN`: Finviz Elite API token (optional)
- `PORT`: Server port (default: 8501)
- `DEBUG`: Enable debug mode (default: false)

## Settings File (settings.json)
Auto-generated on first run. Manual editing supported.

### Key Settings:
- `auto_refresh`: Enable automatic page refresh (boolean)
- `refresh_interval`: Seconds between refreshes (10, 15, 20, 30, 300, 600)
- `chart_height`: Chart height in pixels (100-1000)

## Deployment Configuration (.streamlit/config.toml)

### Local Development:
```toml
[server]
port = 8999
headless = false
```

### Production (Streamlit Cloud):
```toml
[server]
headless = true
enableCORS = false
```

## File Locations
- Settings: `./settings.json`
- Ticker Lists: `./ticker_lists.json`
- Trading Journal: `./trading_journal.json`
- Logs: `./logs/` (if enabled)
"""
```

### 7.2 Dependencies Documentation

**requirements.txt with comments:**
```txt
# Core Framework
streamlit>=1.30.0        # Web application framework

# Data Fetching
requests>=2.31.0         # HTTP library for API calls
beautifulsoup4>=4.12.0   # HTML parsing for web scraping

# Data Processing
pandas>=2.1.0            # Data manipulation and analysis

# News & Calendar
feedparser>=6.0.10       # RSS feed parsing
pytz>=2023.3             # Timezone handling

# Optional: Performance Monitoring
# sentry-sdk>=1.40.0     # Error tracking (uncomment if needed)
```

---

## 📚 8. User Documentation

### 8.1 User Guide Structure

```markdown
# User Guide

## Getting Started
1. Installation
2. First-time setup
3. Basic usage

## Features
### Feature 1: Ticker Lists
- How to create a list
- How to load a list
- How to rename/delete lists

### Feature 2: Auto-Refresh
- Enabling auto-refresh
- Changing refresh interval
- When to disable auto-refresh

## Tips & Tricks
- Keyboard shortcuts
- Power user features
- Performance optimization

## Troubleshooting
- Common issues
- Error messages
- How to get help
```

### 8.2 Screenshots & Examples

**Include Visual Aids:**
```markdown
## Creating a Ticker List

1. Enter tickers in the input field:
   ```
   AAPL, MSFT, GOOGL
   ```

2. Click the "💾 Ticker Lists" expander

3. Enter a name and click Save

![Ticker List Save](docs/images/ticker-list-save.png)

**Result:** Your list is now saved and can be loaded anytime.
```

---

## 🎯 9. Documentation Checklist

### Before Committing Code
- [ ] Function docstrings added/updated
- [ ] Complex logic commented
- [ ] README.md reflects new features
- [ ] Project_History.md session log added
- [ ] CHANGELOG.md updated (if versioned)
- [ ] Configuration changes documented
- [ ] Breaking changes highlighted

### Before Release
- [ ] User guide updated
- [ ] API documentation current
- [ ] Deployment guide verified
- [ ] Known issues documented
- [ ] Migration guide (if needed)
- [ ] Version number updated

### Monthly Review
- [ ] Remove outdated documentation
- [ ] Update screenshots
- [ ] Verify all links work
- [ ] Check for accuracy
- [ ] Improve clarity where needed

---

## 📖 10. Documentation Best Practices

### Writing Style
- **Be Concise**: Remove unnecessary words
- **Be Specific**: Use exact names, numbers, examples
- **Be Consistent**: Same terminology throughout
- **Be Current**: Update with code changes
- **Be Helpful**: Anticipate questions

### Formatting
- Use headings for structure (H1-H4)
- Use code blocks for code
- Use tables for comparisons
- Use lists for steps/items
- Use bold for emphasis
- Use links for references

### Code Examples
- Include complete, runnable examples
- Show both input and output
- Explain non-obvious parts
- Keep examples simple
- Test examples before publishing

### Maintenance
- Review quarterly
- Update on major changes
- Archive obsolete docs
- Version documentation with code
- Track documentation debt

---

## 🛠️ 11. Tools & Templates

### Documentation Tools
- **Markdown Editors**: Typora, Mark Text, VS Code
- **Diagrams**: Mermaid, Draw.io, Excalidraw
- **Screenshots**: ShareX, Lightshot, Snagit
- **API Docs**: Swagger, Postman, Redoc
- **Static Sites**: MkDocs, Docusaurus, GitBook

### Quick Templates

**Feature Documentation:**
```markdown
## Feature: [Name]

**Purpose:** [What it does]

**Usage:**
```python
# Example code
```

**Parameters:**
- `param1`: Description
- `param2`: Description

**Returns:** Description

**Example:**
```python
# Complete example
```

**Notes:**
- Important consideration 1
- Important consideration 2
```

**Bug Fix Documentation:**
```markdown
### Bug: [Title]
**Status:** Fixed
**Date:** YYYY-MM-DD

**Problem:** [Description]
**Root Cause:** [Why it happened]
**Solution:** [How it was fixed]
**Testing:** [How it was verified]
```

---

## 📋 Quick Reference

### Documentation Priority
1. **Critical**: README, API docs, deployment guide
2. **Important**: Project history, architecture, troubleshooting
3. **Nice to Have**: FAQ, contributing guide, examples

### When to Document
- ✅ New feature added
- ✅ Bug fixed
- ✅ API changed
- ✅ Configuration changed
- ✅ Architecture decision made
- ✅ Workaround implemented
- ✅ Performance optimized

### Documentation Smells
- ❌ Outdated examples
- ❌ Broken links
- ❌ Missing version info
- ❌ No code examples
- ❌ Unclear instructions
- ❌ No troubleshooting section
- ❌ Inconsistent terminology

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Code Documentation Guidelines

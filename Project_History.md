# Project History - Finviz Free Dashboard

This file documents the development, features, and refinements of the Finviz Free Realtime Chart Dashboard. 

## Project Objective
Create a high-performance, minimalist Streamlit dashboard for monitoring multiple stocks via Finviz intraday charts with advanced technical indicators and automatic sorting.

---

## 📅 Session Log: December 27, 2024

### 🚀 Major Accomplishments
- **Elite Subdomain & Cookie Support**: Added support for Finviz Elite features. Users can now provide a session cookie to unlock intraday performance metrics and sorting via `elite.finviz.com`.
- **Advanced Sorting Logic**: Implemented accurate sorting by SMA20, SMA50, and 10m/15m/30m performance. The app now handles the new Finviz table structure (`styled-row`).
- **Dynamic ETF Loader**: Improved the Yahoo Finance ETF scraper with a 20s timeout and exponential backoff to handle network lag.
- **UX Refinements**: 
  - Added Ticker labels to the info bars.
  - Implemented automatic ticker cleaning (stripping dots/spaces).
  - Switched to `width='stretch'` for `st.image` to address Streamlit deprecations.
  - Added "Sort Success" toast notifications.

### 🛠️ Core Features Implemented
- [x] **Grid View**: Compact 1-4 column layout for intraday charts.
- [x] **Multi-Timeframe View**: Ticker rows showing Daily, 15m, and 3m charts side-by-side.
- [x] **Metric Overlay**: Info bar below charts showing Change, RSI, SMA, and Intraday Perf.
- [x] **Metrics Toggle**: Added a sidebar setting to show or hide the metric info bar.
- [x] **Auto-Save**: All sidebar settings persist automatically to `settings.json`.
- [x] **Auto-Refresh**: Configurable refresh interval (5s to 300s).

### 🐛 Bug Fixes
- **SMA Sorting Fix**: Corrected column index mapping and row selectors for the modern Finviz layout.
- **Yahoo Timeout Fix**: Added retries and increased timeout to handle "Read Timed Out" errors.
- **Ticker Clean Fix**: Ticker lists now correctly handle commas, spaces, and newlines.
- **Header Clean Fix**: Removed redundant ticker names from the info bar and moved it below charts in MTF view for a cleaner layout.
- **Connection Hardening (Finviz)**: Implemented `requests.Session()` persistence and exponential backoff to ensure metric data loads reliably without ConnectTimeout errors.

### 📝 Current Task / Next Steps
- [ ] Finalize robust metric extraction (Ensuring no dashes are shown).
- [ ] Implement retry logic for all Finviz API calls.

---

## 🏗️ Architecture Note
- **Frontend**: Streamlit (Python)
- **Data Source**: Finviz (Charts + Metrics), Yahoo Finance (ETF Holdings)
- **Persistence**: Local `settings.json`
- **Launch Strategy**: `run.bat` for automatic port assignment (8999) and browser launch.

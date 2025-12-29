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
- [x] Finalize robust metric extraction (Ensuring no dashes are shown).
- [x] Implement retry logic for all Finviz API calls.

---

## 📅 Session Log: December 30, 2025

### 🚀 Major Accomplishments
- **Correct Column ID Discovery**: Discovered the correct Finviz column IDs for intraday performance metrics:
  - Column 94: Performance (10 Minutes)
  - Column 95: Performance (15 Minutes)
  - Column 96: Performance (30 Minutes)
  - Column 65: Price
  - Column 66: Change
- **Export API Integration**: Migrated from HTML screen scraping to Finviz Elite Export API (`export.ashx`) with auth token support
- **Simplified Metrics**: Removed RSI, SMA20, and SMA50 from display to focus on intraday performance metrics
- **Dual Mode Support**: App now handles both CSV responses (Elite API) and HTML responses (Free tier) seamlessly

### 🛠️ Technical Changes
- Updated `fetch_sorted_tickers()` to use export API with `auth=` parameter
- Updated `fetch_ticker_metrics()` to parse CSV responses from Elite API
- Added CSV parsing support with `csv` and `StringIO` imports
- Corrected column index mapping for all metric extractions
- Removed SMA20, SMA50, RSI from sort options and metric display
- Updated metric info bar to show: 10m, 15m, 30m performance, Price, and Change

### 🐛 Bug Fixes
- **Column ID Correction**: Fixed incorrect column IDs (70, 71, 72) that were returning IPO dates instead of intraday performance
- **API Token Support**: Implemented proper auth token usage for Elite features instead of cookie headers

### 📝 Testing & Validation
- Verified Elite API token functionality with test scripts
- Confirmed intraday performance data retrieval (tested with AAPL, MSFT, GOOGL, NVDA, TSLA)
- Validated CSV parsing and data extraction accuracy

### 📊 Finviz Elite Column ID Reference

**Intraday Performance Columns (Elite Only):**
- Column 90: Performance (1 Minute)
- Column 91: Performance (2 Minutes)
- Column 92: Performance (3 Minutes)
- Column 93: Performance (5 Minutes)
- **Column 94: Performance (10 Minutes)** ⭐ Used
- **Column 95: Performance (15 Minutes)** ⭐ Used
- **Column 96: Performance (30 Minutes)** ⭐ Used
- Column 97: Performance (1 Hour)
- Column 98: Performance (2 Hours)
- Column 99: Performance (4 Hours)

**Longer-Term Performance Columns:**
- Column 42: Performance (Week)
- Column 43: Performance (Month)
- Column 44: Performance (Quarter)
- Column 45: Performance (Half Year)
- Column 46: Performance (Year)
- Column 47: Performance (YTD)
- Column 138: Performance (3 Years)
- Column 139: Performance (5 Years)
- Column 140: Performance (10 Years)

**Price & Change Columns:**
- **Column 65: Price** ⭐ Used
- **Column 66: Change** ⭐ Used
- Column 60: Change from Open
- Column 61: Gap
- Column 72: After-Hours Change
- Column 71: After-Hours Close
- Column 81: Prev Close
- Column 86: Open
- Column 87: High
- Column 88: Low

**Volume & Trading Columns:**
- Column 63: Average Volume
- Column 64: Relative Volume
- Column 67: Volume
- Column 89: Trades
- Column 141: After-Hours Volume

**Fundamental Metrics:**
- Column 4: Market Cap
- Column 5: P/E
- Column 6: Forward P/E
- Column 7: PEG
- Column 8: P/S
- Column 9: P/B
- Column 10: P/Cash
- Column 11: P/Free Cash Flow

**Growth Metrics:**
- Column 15: EPS Growth This Year
- Column 16: EPS Growth Next Year
- Column 17: EPS Growth Past 5 Years
- Column 20: EPS Growth Next 5 Years
- Column 21: Sales Growth Past 5 Years
- Column 22: EPS Growth Quarter Over Quarter
- Column 23: Sales Growth Quarter Over Quarter
- Column 142: EPS Growth Past 3 Years
- Column 143: Sales Growth Past 3 Years

**Profitability Metrics:**
- Column 32: Return on Assets
- Column 33: Return on Equity
- Column 34: Return on Invested Capital
- Column 39: Gross Margin
- Column 40: Operating Margin
- Column 41: Profit Margin

**Dividend Metrics:**
- Column 12: Dividend Yield
- Column 13: Payout Ratio
- Column 75: Dividend
- Column 130: Dividend TTM
- Column 131: Dividend Ex Date
- Column 147: Dividend Growth 1 Year
- Column 148: Dividend Growth 3 Years
- Column 149: Dividend Growth 5 Years

**Ownership & Short Interest:**
- Column 26: Insider Ownership
- Column 27: Insider Transactions
- Column 28: Institutional Ownership
- Column 29: Institutional Transactions
- Column 30: Short Float
- Column 31: Short Ratio
- Column 84: Short Interest
- Column 85: Float %

**ETF-Specific Columns:**
- Column 100: Asset Type
- Column 101: ETF Type
- Column 102: Region
- Column 103: Single Category
- Column 104: Sector/Theme
- Column 105: Tags
- Column 106: Active/Passive
- Column 107: Net Expense Ratio
- Column 108: Total Holdings
- Column 109: Assets Under Management
- Column 110: Net Asset Value
- Column 111: Net Asset Value %
- Column 112-119: Net Flows (various periods)

**Other Useful Columns:**
- Column 48: Beta
- Column 49: Average True Range
- Column 62: Analyst Recom
- Column 68: Earnings Date
- Column 69: Target Price
- Column 70: IPO Date
- Column 125: All-Time High
- Column 126: All-Time Low
- Column 134: 52-Week Range
- Column 135: News Time
- Column 136: News URL
- Column 137: News Title

**Technical Analysis Indicators:**
- **Column 52: 20-Day Simple Moving Average** ⭐ Used
- Column 53: 50-Day Simple Moving Average
- Column 54: 200-Day Simple Moving Average
- Column 55: 50-Day High
- Column 56: 50-Day Low
- Column 57: 52-Week High
- Column 58: 52-Week Low
- Column 59: Relative Strength Index (14)

**Note:** Columns marked with ⭐ are currently used in the dashboard. All intraday performance columns (90-99) require Finviz Elite subscription.

---

## 📅 Session Log: December 30, 2025 (Update 2)

### 🚀 SMA20 Sorting Addition
- **Added SMA20 Sorting**: Added 20-Day Simple Moving Average (Relative) to sorting options
- **Column Discovery**: Identified Column 52 as 20-Day SMA (shows percentage distance from 20-day average)
- **Updated Metrics Display**: Added SMA20 to the metric info bar alongside performance metrics
- **Updated Column Configuration**: Now fetching columns: 0, 1, 94, 95, 96, 52, 65, 66

### 🛠️ Technical Changes
- Added "SMA20" to sort_options with Finviz sort code "sma20"
- Updated column string from "0,1,94,95,96,65,66" to "0,1,94,95,96,52,65,66"
- Updated metrics extraction to include sma20 field
- Updated display bar to show: 10m, 15m, 30m, SMA20, Price, Change

---

## 📅 Session Log: December 30, 2025 (Update 3)

### 🚀 Quick View Table Addition
- **Added Sidebar Quick View Table**: Interactive table showing Ticker, 30m, 15m, and Change
- **Clickable Column Headers**: Users can click column headers to sort the table
- **Compact Display**: Small, efficient table that updates with metrics data
- **Dynamic Sizing**: Table height adjusts based on number of tickers (max 400px)

### 🛠️ Technical Changes
- Added pandas import for DataFrame support
- Created quick metrics table below sorting controls in sidebar
- Implemented custom column configuration for compact display
- Added dynamic height calculation: `min(len(table_data) * 35 + 38, 400)`
- Table displays: Ticker (left-aligned, bold) | 30m | 15m | Chg (right-aligned)

### 📊 User Experience Improvements
- Quick at-a-glance view of all tickers without scrolling main content
- Interactive sorting by any column in the table
- Positioned strategically in sidebar for easy access
- Falls back to info message when no tickers are entered

---

## 📅 Session Log: December 30, 2025 (Update 4)

### 🔧 UI/UX Refinement
- **Renamed Input Field**: Changed "Finviz Cookie (Optional - for Elite)" to "Finviz Elite API Token"
- **Updated Help Text**: Clarified that this is an API token (not a cookie) for Elite features
- **Improved Clarity**: Help text now mentions "intraday performance metrics and Elite sorting features"

### 🛠️ Technical Changes
- Updated label from "Finviz Cookie (Optional - for Elite)" to "Finviz Elite API Token"
- Updated help text to reflect API token usage instead of cookie
- Internal key name remains `finviz_cookie` for backward compatibility with settings.json
- **Changed Default Sorting**: Updated default sort from "Ticker" (ASC) to "Perf 30min" (DESC)
- New users will see tickers sorted by 30-minute performance in descending order by default
- **Added "Change from Open" Sorting**: New sort option to order tickers by their change from opening price

---

## 📅 Session Log: December 30, 2025 (Update 5)

### 🚀 Ticker List Save/Load System
- **Save Multiple Named Lists**: Users can now save multiple ticker lists with custom names
- **Load Saved Lists**: Quick loading of any saved ticker list with a single click
- **Rename Lists**: Ability to rename saved lists directly in the UI
- **Delete Lists**: Remove unwanted ticker lists from storage
- **Persistent Storage**: All lists saved to `ticker_lists.json` for persistence across sessions

### 🛠️ Technical Changes
- Added `ticker_lists.json` file for storing named ticker lists
- Created `load_ticker_lists()` function to load saved lists from JSON
- Created `save_ticker_lists()` function to save lists to JSON
- Added "Ticker Lists" expander in sidebar with complete management UI:
  - Save current list: Text input + save button
  - Load saved list: Selectbox + Load/Rename/Delete buttons
  - Rename mode: Inline renaming with confirm/cancel buttons
- Integrated with existing auto-save system to persist loaded lists

### 📊 User Experience Improvements
- Compact UI design fitting neatly in sidebar
- Toast notifications for all actions (save, load, rename, delete)
- Input validation to prevent empty names or duplicate list names
- Clear visual feedback for rename mode
- Automatic refresh after load/save/rename/delete operations

### 🎯 Use Cases
- Save different watchlists for various sectors (e.g., "Tech Stocks", "Energy", "Crypto")
- Quickly switch between intraday trading lists and long-term portfolios
- Save ETF holdings as named lists for easy recall
- Maintain multiple timeframe-specific watchlists

---

## 📅 Session Log: December 30, 2025 (Update 6)

### 🚀 Quick View Table Enhancements

**Problem Encountered:**
- Quick View table was not rendering due to Streamlit limitations with HTML styling in sidebars
- Initial attempt to use custom HTML table with background color gradients failed
- Table showed raw HTML code instead of rendered table

**Solution Implemented:**
- Switched from HTML table to native Streamlit dataframe with emoji indicators
- Replaced complex color gradient backgrounds with simple 🟢 (green circle) and 🔴 (red circle) emojis
- Used pandas DataFrame with proper numeric sorting

### 🛠️ Technical Changes
- **Fixed Quick View Rendering**: Replaced `st.sidebar.markdown()` with custom HTML to `st.sidebar.dataframe()` with emoji indicators
- **Added Color Indicators**: Implemented `add_color_indicator()` function that adds 🟢 for positive values and 🔴 for negative values
- **Improved Ticker Parsing**: Updated Quick View to use `clean_tickers()` function instead of manual comma-splitting to support newline-separated ticker lists
- **Enhanced Placeholder Text**: Updated ticker input placeholder to show both comma-separated and newline-separated format examples
- **Streamlit Deprecation Fix**: Replaced all `use_container_width=True` with `width='stretch'` to comply with Streamlit's API changes (effective 2025-12-31)

### 🐛 Bug Fixes
- **Quick View Data Loading**: Fixed issue where Quick View table wasn't displaying metrics when tickers were entered with newlines
- **Vertical Ticker Support**: Ensured newline-separated ticker lists work correctly throughout the app
- **Button Width Standardization**: Updated Load/Rename/Delete buttons to use `width='stretch'` instead of deprecated `use_container_width`
- **Dataframe Width Fix**: Updated sidebar dataframe to use `width='stretch'` for consistent sizing

### 📊 Quick View Table Features
- Displays: Ticker | 30m | 15m | 1m | Chg
- Sorted by 30m performance (descending) - best performers at top
- Color-coded with emoji indicators for quick visual scanning
- Dynamic height based on number of tickers (max 400px)
- Compact, efficient design that fits in sidebar

### 🎯 User Experience Improvements
- **Multi-Format Ticker Input**: Users can now enter tickers as:
  - Comma-separated: `AAPL, MSFT, NVDA`
  - Newline-separated (one per line):
    ```
    AAPL
    MSFT
    NVDA
    ```
  - Mixed format with blank lines (automatically cleaned)
- **Visual Performance Indicators**: Quick glance at green/red circles shows market sentiment
- **No Deprecation Warnings**: Updated all deprecated Streamlit API calls for future compatibility

### 📝 Current Status
- ✅ Quick View table fully functional with emoji indicators
- ✅ Vertical ticker list support working
- ✅ All Streamlit deprecation warnings resolved
- ✅ Clean, maintainable codebase ready for future updates

---

## 🏗️ Architecture Note
- **Frontend**: Streamlit (Python)
- **Data Source**: Finviz Export API (Elite) / Scraping (Free), Yahoo Finance (ETF Holdings)
- **Persistence**: `settings.json`, `ticker_lists.json`
- **Launch Strategy**: `run.bat` for automatic port assignment (8999) and browser launch.

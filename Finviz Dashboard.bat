@echo off
chcp 65001 > nul
title Finviz Realtime Chart Dashboard
cls
echo ======================================================================
echo           FINVIZ REALTIME CHART DASHBOARD - LAUNCHER
echo ======================================================================
echo.
echo DESCRIPTION:
echo This dashboard provides a high-performance, minimalist interface for 
echo monitoring multiple stocks via Finviz intraday charts. 
echo.
echo KEY FEATURES:
echo  - 🏛️ Index Multi-Timeframe (SPY, QQQ, SMH)
echo  - 🖼️ Dynamic Grid View (1-4 charts per row)
echo  - 📊 Multi-Timeframe Analysis (Daily, 15m, 3m)
echo  - 🚀 Real-time Performance Metrics and Auto-Refresh
echo.
echo Launching Streamlit on port 8999...
echo ======================================================================
echo.
streamlit run streamlit_app.py --server.port 8999 --server.headless false
pause

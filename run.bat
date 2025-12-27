@echo off
rem Give the server a tiny head start or just let streamlit handle the launch
streamlit run streamlit_app.py --server.port 8999 --server.headless false
pause

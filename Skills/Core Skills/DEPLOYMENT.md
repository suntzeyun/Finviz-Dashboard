# Deployment Guide

A comprehensive deployment guide for web applications and Streamlit dashboards across multiple platforms. This framework covers local development, cloud deployment, containerization, and production best practices.

---

## 🎯 Deployment Overview

### Deployment Options Comparison

| Platform | Best For | Cost | Complexity | Persistence |
|----------|----------|------|------------|-------------|
| **Local** | Development, testing | Free | Low | Yes |
| **ngrok** | Quick sharing, demos | Free/Paid | Low | No |
| **Streamlit Cloud** | Quick deployment, prototypes | Free/Paid | Low | No* |
| **Docker** | Consistent environments | Free | Medium | Yes |
| **Heroku** | Simple cloud hosting | Free/Paid | Medium | Yes |
| **AWS/GCP/Azure** | Production, scalability | Paid | High | Yes |

*Streamlit Cloud: Files don't persist, use external storage

---

## 💻 1. Local Deployment

### 1.1 Development Setup

**Prerequisites:**
- Python 3.8 or higher
- pip package manager
- Git (optional but recommended)

**Step-by-Step Setup:**

```bash
# 1. Clone or download project
git clone https://github.com/username/project.git
cd project

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create configuration files (if needed)
cp .env.example .env
# Edit .env with your settings

# 7. Run the application
streamlit run streamlit_app.py
```

**Verify Installation:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check installed packages
pip list

# Check Streamlit
streamlit --version

# Test import
python -c "import streamlit; print('Streamlit OK')"
```

### 1.2 Local Configuration

**.streamlit/config.toml (Local Development):**
```toml
[server]
port = 8501
headless = false
runOnSave = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

**Environment Variables (.env):**
```bash
# API Keys
FINVIZ_API_TOKEN=your_token_here
TIINGO_API_KEY=your_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO

# Database (if applicable)
DATABASE_URL=sqlite:///data.db
```

**Load Environment Variables:**
```python
# In your app
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

api_key = os.getenv("FINVIZ_API_TOKEN")
```

### 1.3 Batch Files for Easy Running

**01_run_local.bat:**
```batch
@echo off
echo Starting Streamlit Dashboard...
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run Streamlit
streamlit run streamlit_app.py --server.port 8501

pause
```

**03_install_dependencies.bat:**
```batch
@echo off
echo Installing dependencies...

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Installation complete!
pause
```

---

## 🌐 2. ngrok Deployment (External Access)

### 2.1 ngrok Setup

**Installation:**
```bash
# Download ngrok
# Windows: https://ngrok.com/download
# Extract to C:\ngrok\ or add to PATH

# Linux/Mac:
brew install ngrok  # Mac
snap install ngrok  # Linux

# Verify installation
ngrok version
```

**Authentication:**
```bash
# Sign up at ngrok.com (free)
# Get authtoken from dashboard

# Configure authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Verify configuration
ngrok config check
```

### 2.2 Running with ngrok

**Method 1: Simple (Two Terminals)**

Terminal 1:
```bash
# Start Streamlit
streamlit run streamlit_app.py --server.port 8501
```

Terminal 2:
```bash
# Start ngrok tunnel
ngrok http 8501
```

**Method 2: Batch File (Automated)**

**02_run_public_ngrok.bat:**
```batch
@echo off
setlocal enabledelayedexpansion

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

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
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

### 2.3 ngrok Configuration File

**ngrok.yml (Advanced):**
```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
region: us  # us, eu, ap, au, sa, jp, in

tunnels:
  streamlit:
    proto: http
    addr: 8501
    inspect: true
    bind_tls: true
    
  # Multiple tunnels (paid feature)
  api:
    proto: http
    addr: 8000
```

**Run with config:**
```bash
ngrok start streamlit
```

### 2.4 ngrok Best Practices

**Security:**
```python
# Add password protection
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", key="password")
        if st.session_state.get("password") == "your_password":
            st.session_state.password_correct = True
            st.rerun()
        return False
    return True

if not check_password():
    st.stop()
```

**Limitations:**
- Free tier: 2-hour session limit
- Free tier: Random URL each time
- Free tier: 40 connections/minute
- Paid tier: Custom domains, longer sessions

---

## ☁️ 3. Streamlit Cloud Deployment

### 3.1 Prerequisites

- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Repository with your code

### 3.2 Preparing Your Repository

**Required Files:**

1. **Main app file** (one of these):
   - `streamlit_app.py` (recommended)
   - `app.py`
   - Custom name (specify in deployment)

2. **requirements.txt:**
```txt
streamlit>=1.30.0
pandas>=2.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
feedparser>=6.0.10
pytz>=2023.3
```

3. **Optional: packages.txt** (system dependencies):
```txt
libgl1-mesa-glx
libglib2.0-0
```

4. **Optional: runtime.txt** (Python version):
```txt
python-3.11
```

5. **Optional: .streamlit/config.toml:**
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### 3.3 Deployment Steps

**Step 1: Push to GitHub**
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create repository on GitHub
# Then push
git remote add origin https://github.com/username/repo.git
git branch -M main
git push -u origin main
```

**Step 2: Deploy on Streamlit Cloud**

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your repository
4. Choose branch (usually `main`)
5. Specify main file path (e.g., `streamlit_app.py`)
6. Click "Deploy"

**Step 3: Configure Secrets**

In Streamlit Cloud dashboard:
1. Go to app settings
2. Click "Secrets"
3. Add secrets in TOML format:

```toml
# .streamlit/secrets.toml format
FINVIZ_API_TOKEN = "your_token_here"
TIINGO_API_KEY = "your_key_here"

[database]
host = "db.example.com"
port = 5432
username = "user"
password = "pass"
```

**Access secrets in code:**
```python
import streamlit as st

# Access secrets
api_token = st.secrets["FINVIZ_API_TOKEN"]

# Access nested secrets
db_host = st.secrets["database"]["host"]

# With fallback for local development
api_token = st.secrets.get("FINVIZ_API_TOKEN", os.getenv("FINVIZ_API_TOKEN"))
```

### 3.4 Streamlit Cloud Configuration

**.gitignore (Important!):**
```gitignore
# Environment
.env
.venv/
venv/

# Secrets
.streamlit/secrets.toml

# Data files (if sensitive)
data/*.json
*.db

# Cache
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
```

**Auto-deployment:**
- Streamlit Cloud auto-deploys on every push to main branch
- View deployment logs in dashboard
- Rollback to previous versions if needed

### 3.5 Troubleshooting Streamlit Cloud

**Common Issues:**

1. **Module not found:**
   - Add to requirements.txt
   - Check spelling and version

2. **File not found:**
   - Use relative paths
   - Files must be in repository
   - Data doesn't persist (use external storage)

3. **Slow performance:**
   - Add caching: `@st.cache_data`
   - Reduce API calls
   - Optimize data processing

4. **Memory limit exceeded:**
   - Free tier: 1 GB RAM
   - Optimize memory usage
   - Consider upgrading

---

## 🐳 4. Docker Deployment

### 4.1 Dockerfile

**Dockerfile:**
```dockerfile
# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - FINVIZ_API_TOKEN=${FINVIZ_API_TOKEN}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### 4.2 Building and Running

**Build Docker Image:**
```bash
# Build image
docker build -t streamlit-app .

# Run container
docker run -p 8501:8501 streamlit-app

# Run with environment variables
docker run -p 8501:8501 \
  -e FINVIZ_API_TOKEN=your_token \
  streamlit-app

# Run in background
docker run -d -p 8501:8501 --name my-app streamlit-app
```

**Using Docker Compose:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 4.3 Docker Best Practices

**.dockerignore:**
```
.git
.gitignore
.venv
venv
__pycache__
*.pyc
.pytest_cache
.ruff_cache
.env
.streamlit/secrets.toml
*.log
README.md
```

**Multi-stage Build (Optimization):**
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🚀 5. Cloud Platform Deployment

### 5.1 Heroku Deployment

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Required Files:**

**Procfile:**
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.11.0
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Deployment Steps:**
```bash
# Login to Heroku
heroku login

# Create app
heroku create my-streamlit-app

# Set environment variables
heroku config:set FINVIZ_API_TOKEN=your_token

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

### 5.2 AWS Deployment (EC2)

**Launch EC2 Instance:**
1. Choose Ubuntu Server 22.04 LTS
2. Instance type: t2.micro (free tier) or larger
3. Configure security group:
   - SSH (22) - Your IP
   - Custom TCP (8501) - Anywhere

**Connect and Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Clone repository
git clone https://github.com/username/repo.git
cd repo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with nohup (background)
nohup streamlit run streamlit_app.py --server.port 8501 &

# Or use systemd service (recommended)
```

**Systemd Service (Production):**

**/etc/systemd/system/streamlit.service:**
```ini
[Unit]
Description=Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/repo
Environment="PATH=/home/ubuntu/repo/.venv/bin"
ExecStart=/home/ubuntu/repo/.venv/bin/streamlit run streamlit_app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Check status
sudo systemctl status streamlit

# View logs
sudo journalctl -u streamlit -f
```

### 5.3 Google Cloud Platform (Cloud Run)

**Dockerfile (Cloud Run optimized):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD streamlit run streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
```

**Deploy to Cloud Run:**
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy streamlit-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

---

## 🔒 6. Production Best Practices

### 6.1 Security

**Environment Variables:**
```python
# Never hardcode secrets
# ❌ BAD
API_KEY = "sk_live_abc123"

# ✅ GOOD
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("API_KEY not set")
    st.stop()
```

**Password Protection:**
```python
def check_password():
    """Returns True if password is correct."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", 
                     on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", 
                     on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

**HTTPS/SSL:**
- Use HTTPS in production
- Streamlit Cloud: Automatic HTTPS
- Self-hosted: Use nginx reverse proxy with Let's Encrypt

### 6.2 Performance

**Caching:**
```python
# Cache expensive operations
@st.cache_data(ttl=300)  # 5 minutes
def fetch_data():
    return expensive_api_call()

# Cache resources
@st.cache_resource
def get_database_connection():
    return create_connection()
```

**Lazy Loading:**
```python
# Load data only when needed
if st.button("Load Data"):
    data = fetch_data()
    st.write(data)
```

**Optimize Imports:**
```python
# Import only what you need
from datetime import datetime  # ✅
import datetime  # ❌ (if only using datetime)
```

### 6.3 Monitoring

**Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

logger.info("App started")
logger.error("Error occurred", exc_info=True)
```

**Error Tracking:**
```python
# Use Sentry for error tracking
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

### 6.4 Backup and Recovery

**Data Backup:**
```python
import shutil
from datetime import datetime

def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.json"
    shutil.copy("data.json", f"backups/{backup_file}")
```

**Database Backups:**
```bash
# PostgreSQL
pg_dump dbname > backup.sql

# SQLite
sqlite3 database.db ".backup backup.db"
```

---

## 📋 7. Deployment Checklist

### Pre-Deployment

- [ ] All features tested locally
- [ ] No hardcoded secrets
- [ ] requirements.txt up to date
- [ ] .gitignore configured
- [ ] README.md complete
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Performance optimized

### Deployment

- [ ] Environment variables set
- [ ] Database configured (if applicable)
- [ ] SSL/HTTPS enabled
- [ ] Monitoring enabled
- [ ] Backup strategy in place
- [ ] Domain configured (if applicable)

### Post-Deployment

- [ ] Test all features in production
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Verify backups working
- [ ] Document deployment process
- [ ] Share access with team

---

## 🆘 Troubleshooting Deployment

### Common Issues

**Port conflicts:**
```bash
# Find process using port
netstat -ano | findstr :8501  # Windows
lsof -i :8501  # Linux/Mac

# Kill process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Linux/Mac
```

**Permission errors:**
```bash
# Fix file permissions
chmod +x script.sh
chmod 644 config.toml
```

**Memory issues:**
```python
# Monitor memory usage
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```

---

**Last Updated:** January 13, 2026  
**Version:** 1.0  
**Framework Type:** Deployment Guide

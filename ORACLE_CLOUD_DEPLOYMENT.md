# Oracle Cloud Free Tier Deployment Guide

Deploy your Finviz Dashboard to Oracle Cloud for **FREE 24/7 hosting**.

## 📋 Prerequisites

- Credit/Debit card (for verification only - won't be charged)
- Email address
- Your Finviz Dashboard code

---

## 🚀 Step 1: Create Oracle Cloud Account

1. Go to [cloud.oracle.com/free](https://www.oracle.com/cloud/free/)
2. Click **"Start for Free"**
3. Fill in your details and verify your email
4. Enter payment info (required for verification, **no charge**)
5. Select your **Home Region** (choose closest to you)

> ⚠️ **Important**: Choose your region carefully - it cannot be changed later!

---

## 🖥️ Step 2: Create a Free VM Instance

1. Go to **Oracle Cloud Console** → **Compute** → **Instances**
2. Click **"Create Instance"**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `finviz-dashboard` |
| **Image** | Ubuntu 22.04 (or 24.04) |
| **Shape** | `VM.Standard.E2.1.Micro` (Always Free) |
| **OCPU** | 1 |
| **Memory** | 1 GB |

4. **Networking**: Keep defaults (creates VCN automatically)
5. **SSH Keys**: 
   - Select **"Generate a key pair for me"**
   - **Download BOTH** private and public keys
   - Save them somewhere safe!

6. Click **"Create"** and wait ~2 minutes

---

## 🔓 Step 3: Open Firewall Port 8501

### A. Oracle Cloud Security List:

1. Go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. Click **"Add Ingress Rules"**
4. Add this rule:

| Field | Value |
|-------|-------|
| Source Type | CIDR |
| Source CIDR | `0.0.0.0/0` |
| IP Protocol | TCP |
| Destination Port Range | `8501` |
| Description | Streamlit Dashboard |

5. Click **"Add Ingress Rules"**

### B. Ubuntu Firewall (after SSH):

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save
```

---

## 🔑 Step 4: Connect via SSH

### On Windows (PowerShell):

```powershell
# Navigate to your key location
cd C:\Users\YourName\Downloads

# Set permissions (important!)
icacls ssh-key-*.key /inheritance:r /grant:r "$($env:USERNAME):R"

# Connect (replace with your instance's public IP)
ssh -i ssh-key-XXXX.key ubuntu@YOUR_PUBLIC_IP
```

### On Mac/Linux:

```bash
chmod 400 ~/Downloads/ssh-key-*.key
ssh -i ~/Downloads/ssh-key-*.key ubuntu@YOUR_PUBLIC_IP
```

> 💡 Find your **Public IP** in Oracle Console → Instances → Your Instance

---

## 📦 Step 5: Install Dependencies

Once connected via SSH, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv git -y

# Create project directory
mkdir ~/finviz-dashboard
cd ~/finviz-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

---

## 📤 Step 6: Upload Your Code

### Option A: Using Git (Recommended)

If your code is on GitHub:

```bash
cd ~/finviz-dashboard
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
```

### Option B: Using SCP (Direct Upload)

From your **local Windows PowerShell**:

```powershell
# Upload entire folder
scp -i ssh-key-*.key -r C:\Automation\Python\Finviz-Dashboard\* ubuntu@YOUR_PUBLIC_IP:~/finviz-dashboard/
```

### Option C: Using SFTP (GUI)

Use [WinSCP](https://winscp.net/) or [FileZilla](https://filezilla-project.org/):
- Host: Your Public IP
- Username: `ubuntu`
- Key file: Your downloaded SSH key

---

## 🔧 Step 7: Install Python Packages

```bash
cd ~/finviz-dashboard
source venv/bin/activate

# Install requirements
pip install streamlit pandas requests beautifulsoup4 feedparser pytz
```

Or if you have a requirements.txt:

```bash
pip install -r requirements.txt
```

---

## ▶️ Step 8: Run Streamlit

### Test Run (foreground):

```bash
cd ~/finviz-dashboard
source venv/bin/activate
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

Access at: `http://YOUR_PUBLIC_IP:8501`

### Production Run (background with auto-restart):

Create a systemd service:

```bash
sudo nano /etc/systemd/system/streamlit.service
```

Paste this content:

```ini
[Unit]
Description=Streamlit Finviz Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/finviz-dashboard
Environment="PATH=/home/ubuntu/finviz-dashboard/venv/bin"
ExecStart=/home/ubuntu/finviz-dashboard/venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
```

Check status:

```bash
sudo systemctl status streamlit
```

---

## 🌐 Step 9: Access Your Dashboard

Open in browser:

```
http://YOUR_PUBLIC_IP:8501
```

🎉 **Your dashboard is now live 24/7!**

---

## 🔒 Optional: Add HTTPS with Free Domain

### Using Cloudflare (Free SSL + Domain):

1. Get a free domain from [Freenom](https://freenom.com) or buy one
2. Add domain to [Cloudflare](https://cloudflare.com) (free plan)
3. Point A record to your Oracle IP
4. Enable **Flexible SSL** in Cloudflare
5. Access via: `https://yourdomain.com:8501`

### Using Nginx Reverse Proxy (Port 80/443):

```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/streamlit
```

Add:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable and get SSL:

```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🛠️ Maintenance Commands

```bash
# View logs
sudo journalctl -u streamlit -f

# Restart service
sudo systemctl restart streamlit

# Update code (if using git)
cd ~/finviz-dashboard
git pull
sudo systemctl restart streamlit

# Check disk space
df -h
```

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to port 8501 | Check both Oracle Security List AND iptables |
| SSH connection refused | Verify you're using correct IP and key file |
| Service won't start | Check logs: `sudo journalctl -u streamlit -n 50` |
| Out of memory | Enable swap: `sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |

---

## 📊 Free Tier Limits

Oracle Cloud Always Free includes:

| Resource | Amount |
|----------|--------|
| AMD VMs | 2 x VM.Standard.E2.1.Micro |
| ARM VMs | Up to 4 OCPUs + 24 GB RAM |
| Storage | 200 GB total |
| Bandwidth | 10 TB/month |

Your Finviz Dashboard fits easily within these limits! 🎉

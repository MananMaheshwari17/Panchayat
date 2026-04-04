# 🚀 Panchayat — Vultr Deployment Guide

## Option A: Docker Deploy (Recommended)

### 1. Provision a Vultr Server
- **Type**: Cloud Compute (Shared CPU)
- **Plan**: 1 vCPU / 1 GB RAM ($6/mo) is enough
- **OS**: Ubuntu 22.04 or Docker marketplace image
- **Region**: Mumbai (closest to Indian users)

### 2. SSH into your server
```bash
ssh root@YOUR_VULTR_IP
```

### 3. Install Docker (if not pre-installed)
```bash
curl -fsSL https://get.docker.com | sh
```

### 4. Clone the repo
```bash
git clone https://github.com/YOUR_REPO/Panchayat.git
cd Panchayat
```

### 5. Create the `.env` file
```bash
cp .env.example .env
nano .env
# Fill in your actual API keys:
#   MONGO_URI=mongodb+srv://...
#   GROQ_API_KEY=gsk_...
#   ELEVENLABS_API_KEY=sk_...
#   ARMORIQ_API_KEY=ak_...
#   GOOGLE_API_KEY=AI...
```

### 6. Build and run
```bash
docker build -t panchayat .
docker run -d \
  --name panchayat \
  --restart unless-stopped \
  -p 80:8000 \
  --env-file .env \
  panchayat
```

### 7. Verify
```bash
curl http://localhost/api/candidates-info
# Open in browser: http://YOUR_VULTR_IP
```

---

## Option B: Bare-Metal Deploy (No Docker)

### 1. Provision & SSH
Same as above, Ubuntu 22.04.

### 2. Install Python 3.11+
```bash
apt update && apt install -y python3.11 python3.11-venv python3-pip git
```

### 3. Clone & setup
```bash
git clone https://github.com/YOUR_REPO/Panchayat.git
cd Panchayat
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Create `.env`
```bash
cp .env.example .env
nano .env
# Fill in your API keys
```

### 5. Initialize the database
```bash
python -c "from server.init_db import restart_game_state; restart_game_state()"
```

### 6. Run with systemd (auto-restart on crash/reboot)
```bash
cat > /etc/systemd/system/panchayat.service << 'EOF'
[Unit]
Description=Panchayat Game Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Panchayat
Environment="PATH=/root/Panchayat/.venv/bin"
EnvironmentFile=/root/Panchayat/.env
ExecStart=/root/Panchayat/.venv/bin/uvicorn server.fastapi_server:app --host 0.0.0.0 --port 80 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable panchayat
systemctl start panchayat
```

### 7. Check status
```bash
systemctl status panchayat
journalctl -u panchayat -f  # live logs
```

---

## Setting Up a Domain (Optional)

### With Cloudflare (free SSL)
1. Point your domain's DNS to `YOUR_VULTR_IP` (A record)
2. Enable Cloudflare proxy (orange cloud) for free SSL
3. Set SSL mode to "Flexible" in Cloudflare dashboard

### With Let's Encrypt (direct SSL)
```bash
apt install certbot
certbot certonly --standalone -d yourdomain.com
# Then update uvicorn command:
# --ssl-keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem
# --ssl-certfile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
```

---

## Quick Commands

```bash
# View logs
docker logs -f panchayat        # Docker
journalctl -u panchayat -f      # Bare-metal

# Restart
docker restart panchayat         # Docker
systemctl restart panchayat      # Bare-metal

# Update code
git pull
docker build -t panchayat . && docker restart panchayat  # Docker
systemctl restart panchayat                                # Bare-metal
```

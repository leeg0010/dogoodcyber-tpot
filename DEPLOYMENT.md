# T-Pot Custom Honeypot Deployment Guide

## Quick Start

### GitHub Setup
```bash
# 1. Create private repo on GitHub.com:
#    Repository: tpot-custom-honeypots  
#    Privacy: Private
#    Do NOT initialize with README

# 2. Add remote and push
cd ~/tpotce
git remote add origin git@github.com:YOUR_USERNAME/tpot-custom-honeypots.git
git branch -M main
git push -u origin main
```

### Deploy to New Honeypot (10 min reimage)
```bash
# On fresh Ubuntu 22.04 system:
git clone git@github.com:YOUR_USERNAME/tpot-custom-honeypots.git ~/tpotce
cd ~/tpotce
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## What's Deployed

### Custom Images
1. **heralding-stealth:custom**
   - VNC: RFB 003.008 (vs ancient 003.003)
   - PostgreSQL: version 14.10
   - Authentication delays: 1.5-3 seconds
   - Honeypot test filtering

2. **dionaea:branded** 
   - DoGoodCyberSecurity branding
   - Better MySQL protocol emulation

### Port Allocation
- **dionaea**: 3306 (MySQL), SMB, FTP, MSSQL
- **heralding**: VNC (5900), PostgreSQL (5432), Mail, RDP, SOCKS5
- **cowrie**: SSH/Telnet (22, 23, 21)
- **h0neytr4p**: HTTP/HTTPS (80, 443)

## Validation

### Check Deployment
```bash
# Container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test VNC banner (should show RFB 003.008)
timeout 3 nc localhost 5900 | head -1

# Check heralding logs
docker logs heralding | tail -50
```

### Monitor Effectiveness (24-48 hours)
Target metrics:
- VNC authentication rate: >1% (vs 0% baseline)
- PostgreSQL authentication rate: >15% (vs 2.4%)
- Overall: 2-5% (vs 0.005%)

Query in Kibana Dev Tools:
```elasticsearch
GET heralding-*/_search
{
  "size": 0,
  "query": { "range": { "@timestamp": { "gte": "now-24h" } } },
  "aggs": {
    "auth_attempts": { "filter": { "term": { "action": "auth" } } },
    "total_sessions": { "cardinality": { "field": "src_ip" } }
  }
}
```

## Post-Compromise Recovery

```bash
# 1. Stop containers
docker compose down

# 2. Pull latest from GitHub  
cd ~/tpotce
git fetch origin
git reset --hard origin/main

# 3. Redeploy
./scripts/deploy.sh

# 4. Verify
docker ps
docker logs heralding | head -50
```

## Manual Deployment

```bash
# Build images
cd ~/tpotce/docker/heralding
docker build -f Dockerfile.stealth -t heralding-stealth:custom .

cd ~/tpotce/docker/dionaea
docker build -t dtagdevsec/dionaea:branded .

# Deploy
cd ~/tpotce
docker compose -f docker/heralding/docker-compose-stealth.yml up -d
```

## Rollback to Stock T-Pot

```bash
# Stop custom containers
docker compose -f docker/heralding/docker-compose-stealth.yml down

# Checkout stock Dockerfiles
git checkout HEAD -- docker/heralding/Dockerfile docker/dionaea/Dockerfile

# Rebuild and deploy stock
cd docker/heralding && docker build -t heralding:latest .
cd ../dionaea && docker build -t dionaea:latest .
docker compose up -d
```

## Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
sudo lsof -i :3306
sudo ss -tulpn | grep :3306

# Kill process
sudo kill $(sudo lsof -t -i:3306)
```

### Container Won't Start
```bash
# Check logs
docker logs heralding --tail 100
docker logs dionaea --tail 100

# Check disk space
df -h
docker system df

# Clean up
docker system prune -f
```

### Verify Stealth Implementation
```bash
# Check image
docker ps --format "{{.Names}}: {{.Image}}"
# Should show: heralding: heralding-stealth:custom

# Verify VNC protocol
docker exec heralding cat /usr/lib/python3.12/site-packages/heralding/capabilities/vnc.py | grep "RFB_VERSION"
# Should show: RFB_VERSION = b'RFB 003.008\n'
```

## Secrets Management

**Never commit:**
- `.env` files
- `*.pem`, `*.key`, `*.crt`
- Database credentials
- API tokens

Create separate `.env` file (excluded by .gitignore):
```bash
cat > ~/.tpot_secrets.env << 'EOF'
ELASTIC_PASSWORD=<generate_strong_password>
GITHUB_TOKEN=ghp_<your_token>
EOF
chmod 600 ~/.tpot_secrets.env
```

## Documentation
- Main README: [README.md](README.md) 
- Port allocation table: See README.md
- Change log: Git commit history

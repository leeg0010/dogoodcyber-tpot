# DoGoodCyberSecurity T-Pot Honeypot Configuration

Custom T-Pot deployment with enhanced stealth configurations and DoGoodCyberSecurity branding.

## Custom Components

### Heralding (Stealth Enhanced)
- **VNC**: RFB 003.008 with 1.5-3s authentication delays
- **PostgreSQL**: Version 14.10 Ubuntu with realistic timing
- **Authentication**: Filtered honeypot test credentials, selective acceptance
- **Location**: `docker/heralding/`

### Dionaea (Branded)
- **Branding**: DoGoodCyberSecurity attribution
- **Services**: MySQL, SMB, FTP, MSSQL, SIP
- **Location**: `docker/dionaea/`

## Deployment

```bash
# Quick deployment (after fresh install)
cd ~/tpotce
git pull
bash scripts/deploy.sh
```

## Port Allocation

| Service | Port | Honeypot | Purpose |
|---------|------|----------|---------|
| SSH/Telnet | 22-23 | Cowrie | Shell emulation |
| SMTP/Mail | 25, 110, 143, 465, 993, 995 | Heralding | Mail credential harvesting |
| HTTP/HTTPS | 80, 443 | h0neytr4p | Web attacks |
| SOCKS5 | 1080 | Heralding | Proxy abuse |
| MySQL | 3306 | Dionaea | Database attacks |
| RDP | 3389 | Heralding | Remote desktop attacks |
| PostgreSQL | 5432 | Heralding (stealth) | Database credential harvesting |
| VNC | 5900 | Heralding (stealth) | Remote access attacks |

## Changes from Stock T-Pot

1. **Heralding Stealth Mode**: Modern protocol versions, authentication delays
2. **Dionaea Branding**: DoGoodCyberSecurity attribution
3. **Port Optimization**: MySQL moved to dionaea for better emulation
4. **HTTP/HTTPS**: Disabled in heralding, served by h0neytr4p

## Maintenance

```bash
# Update custom images
cd ~/tpotce/docker/heralding && docker compose -f docker-compose-stealth.yml build
cd ~/tpotce/docker/dionaea && docker build -t dtagdevsec/dionaea:branded .

# Restart services
cd ~/tpotce && docker compose restart heralding dionaea
```

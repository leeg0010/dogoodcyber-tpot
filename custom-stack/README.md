# DoGoodCyber Custom Honeypot Stack

**Custom lightweight honeypot deployment - replacing T-Pot full stack**

## Architecture

**6 ports exposed:**
- 22, 23 (cowrie) - SSH/Telnet honeypot
- 80, 443 (h0neytr4p) - Web honeypot
- 993, 5900 (heralding) - IMAPS/VNC honeypot

**4 containers:**
- cowrie - SSH/Telnet attacks
- h0neytr4p - Web attacks
- heralding - Email/VNC attacks
- logstash - Log aggregation

## Deployment

```bash
# Stop T-Pot
cd ~/tpotce && docker compose down

# Start custom stack
cd ~/dogoodcyber-tpot/custom-stack
docker compose up -d

# Verify
docker compose ps
docker compose logs -f
```

## Rollback to T-Pot

```bash
cd ~/dogoodcyber-tpot/custom-stack && docker compose down
cd ~/tpotce && docker compose up -d
```

## Log Preservation

All logs stored in `/data/` - same paths as T-Pot:
- `/data/cowrie/` - SSH/Telnet logs
- `/data/h0neytr4p/` - Web attack logs
- `/data/heralding/` - Email/VNC logs

## Changes from T-Pot

**Removed:**
- dionaea (explicit honeypot signature)
- elasticpot (explicit honeypot signature)
- redishoneypot (unnecessary for cover story)
- adbhoney, p0f, fatt, suricata
- tpotinit orchestration

**Simplified:**
- Single network (honeypot_net) vs per-service networks
- Direct volume mounts for configs
- No tpotinit dependencies

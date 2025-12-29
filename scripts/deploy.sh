#!/bin/bash
###############################################################################
# T-Pot Custom Honeypot Deployment Script  
# Purpose: Automated deployment of custom heralding stealth + dionaea branding
# Target: 10 minute reimage after compromise
###############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

log "Starting T-Pot deployment..."

# Build images
log "Building heralding-stealth:custom..."
cd ~/tpotce/docker/heralding
docker build -f Dockerfile.stealth -t heralding-stealth:custom .

log "Building dionaea:branded..."
cd ~/tpotce/docker/dionaea  
docker build -t dtagdevsec/dionaea:branded .

# Deploy
log "Deploying containers..."
cd ~/tpotce
docker compose -f docker/heralding/docker-compose-stealth.yml down || true
docker compose -f docker/heralding/docker-compose-stealth.yml up -d

# Validate
log "Validating..."
sleep 3
docker ps --format "table {{.Names}}\t{{.Status}}"

log "Testing VNC banner..."
timeout 3 nc localhost 5900 | head -1

log "✓ Deployment complete!"
log "Check logs: docker logs -f heralding"

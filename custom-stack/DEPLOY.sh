#!/bin/bash
set -e

echo "[1/6] Creating data directories..."
mkdir -p /data/cowrie /data/h0neytr4p /data/heralding

echo "[2/6] Stopping current T-Pot stack..."
cd /home/l/tpotce
docker compose down

echo "[3/6] Backing up current T-Pot compose..."
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)

echo "[4/6] Starting custom honeypot stack..."
cd /home/l/dogoodcyber-tpot/custom-stack
docker compose up -d

echo "[5/6] Waiting for services to start..."
sleep 15

echo "[6/6] Verifying deployment..."
docker compose ps
echo ""
echo "Port verification:"
for port in 22 23 80 443 993 5900; do
  timeout 2 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null && echo "  ✓ Port $port OPEN" || echo "  ✗ Port $port CLOSED"
done

echo ""
echo "Deployment complete!"
echo ""
echo "Monitor logs: docker compose logs -f"
echo "Check logstash: docker exec logstash curl -s http://localhost:9600/_node/stats"
echo "Rollback: cd /home/l/tpotce && docker compose up -d"

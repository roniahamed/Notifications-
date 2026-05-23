#!/bin/bash
set -e

echo "Building and starting all services..."
docker compose up --build -d

echo ""
echo "Services are running:"
docker compose ps
echo ""
echo "Web API: http://localhost:8000"
echo "WebSocket: ws://localhost:8000/ws/notifications/?token=<jwt>"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"

#!/bin/bash

# WebSocket Simulation Runner Script
# Starts backend/Redis, runs simulation, collects metrics

set -e

echo "🚀 Starting WebSocket Simulation..."

# Set defaults
USERS=${SIMULATION_USERS:-1000}
DURATION=${SIMULATION_DURATION:-60}
REDIS_PASSWORD=${REDIS_PASSWORD:-workforce_redis_pw}

export SIMULATION_USERS=$USERS
export SIMULATION_DURATION=$DURATION
export REDIS_PASSWORD=$REDIS_PASSWORD

# Start services
echo "📦 Starting Docker services..."
docker-compose up -d redis postgres backend-migrate

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check Redis health
echo "🔍 Checking Redis health..."
docker exec $(docker ps -q --filter name=redis) redis-cli --pass $REDIS_PASSWORD ping | grep PONG || (echo "Redis not healthy" && exit 1)

# Check backend health
echo "🔍 Checking backend health..."
curl -f http://localhost:8000/health || (echo "Backend not healthy" && exit 1)

# Run simulation
echo "🎯 Running simulation with $USERS users for $DURATION seconds..."
python3 websocket_simulation.py

# Collect additional metrics
echo "📊 Collecting additional metrics..."
REDIS_INFO=$(docker exec $(docker ps -q --filter name=redis) redis-cli --pass $REDIS_PASSWORD info stats)
REDIS_PUBSUB=$(echo "$REDIS_INFO" | grep pubsub_channels || echo "pubsub_channels:0")

echo "Redis PubSub Channels: $REDIS_PUBSUB"

# Cleanup
echo "🧹 Cleaning up..."
docker-compose down

echo "✅ Simulation complete! Check simulation_results.json for metrics."

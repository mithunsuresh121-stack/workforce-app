#!/bin/bash

# Test script to verify React web app Docker setup

echo "Testing React web app Docker setup..."

# Check if Dockerfile exists
if [ -f "frontend/web-app/Dockerfile" ]; then
    echo "✓ Dockerfile found at frontend/web-app/Dockerfile"
else
    echo "✗ Dockerfile not found"
    exit 1
fi

# Check if docker-compose.yml has React service
if grep -q "react-web-app" docker-compose.yml; then
    echo "✓ React web app service found in docker-compose.yml"
else
    echo "✗ React web app service not found in docker-compose.yml"
    exit 1
fi

# Check if environment variable is configured
if grep -q "REACT_APP_API_URL" docker-compose.yml; then
    echo "✓ REACT_APP_API_URL environment variable configured"
else
    echo "✗ REACT_APP_API_URL environment variable not configured"
    exit 1
fi

# Check if port mapping is correct
if grep -A5 -B5 "react-web-app" docker-compose.yml | grep -q "8080:8080"; then
    echo "✓ Port 8080 mapping configured correctly"
else
    echo "✗ Port 8080 mapping not configured correctly"
    exit 1
fi

echo ""
echo "Docker setup verification completed successfully!"
echo ""
echo "To run the application:"
echo "1. Start Docker Desktop"
echo "2. Run: docker compose up --build"
echo "3. React web app will be available at: http://localhost:8080"
echo "4. Backend API will be available at: http://localhost:8000"
echo ""

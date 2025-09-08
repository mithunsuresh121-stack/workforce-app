#!/bin/bash

# Performance and concurrency test script for Employee endpoints
# Tests multiple simultaneous requests and response times

API_URL="http://localhost:8000"

# Login as SuperAdmin to get valid token
echo "Logging in as SuperAdmin..."
SUPERADMIN_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@example.com","password":"password123"}' | jq -r '.access_token')

if [ "$SUPERADMIN_TOKEN" == "null" ] || [ -z "$SUPERADMIN_TOKEN" ]; then
  echo "Login failed. Exiting."
  exit 1
fi
echo "Login successful."

echo
echo "=== Testing Performance and Concurrency ==="

# Function to measure response time
measure_response_time() {
  local method=$1
  local endpoint=$2
  local data=$3

  start_time=$(date +%s%N)
  if [ "$method" == "GET" ]; then
    response=$(curl -s -w "@curl-format.txt" -X GET "$API_URL$endpoint" \
      -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
      -o /dev/null)
  else
    response=$(curl -s -w "@curl-format.txt" -X $method "$API_URL$endpoint" \
      -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data" \
      -o /dev/null)
  fi
  end_time=$(date +%s%N)

  # Extract timing info (this would require curl-format.txt file)
  # For now, just calculate total time
  total_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
  echo "${total_time}ms"
}

# Create curl-format.txt for detailed timing
cat > curl-format.txt << EOF
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF

# Test 1: Single request performance
echo "1. Testing single request performance..."
echo "GET /employees/ response time: $(measure_response_time GET /employees/)"

# Test 2: Multiple sequential requests
echo "2. Testing multiple sequential requests..."
for i in {1..10}; do
  time=$(measure_response_time GET /employees/)
  echo "Request $i: ${time}ms"
done

# Test 3: Concurrent requests using background processes
echo "3. Testing concurrent requests..."
concurrent_requests() {
  local id=$1
  start_time=$(date +%s%N)
  curl -s -X GET "$API_URL/employees/" \
    -H "Authorization: Bearer $SUPERADMIN_TOKEN" > /dev/null
  end_time=$(date +%s%N)
  total_time=$(( (end_time - start_time) / 1000000 ))
  echo "Concurrent request $id: ${total_time}ms"
}

# Launch 10 concurrent requests
echo "Launching 10 concurrent GET requests..."
for i in {1..10}; do
  concurrent_requests $i &
done

# Wait for all background processes to complete
wait
echo "All concurrent requests completed."

# Test 4: Mixed operations performance
echo "4. Testing mixed operations performance..."

# Create test data
CREATE_DATA='{"user_id": 31, "company_id": 1, "department": "Engineering", "position": "Developer", "hire_date": "2023-01-01T00:00:00"}'
UPDATE_DATA='{"department": "Product", "position": "Senior Developer"}'

echo "POST /employees/ response time: $(measure_response_time POST /employees/ "$CREATE_DATA")"
echo "PUT /employees/31 response time: $(measure_response_time PUT /employees/31 "$UPDATE_DATA")"
echo "GET /employees/31 response time: $(measure_response_time GET /employees/31)"
echo "DELETE /employees/31 response time: $(measure_response_time DELETE /employees/31)"

# Test 5: Load test with many requests
echo "5. Testing load with 50 sequential requests..."
total_time=0
for i in {1..50}; do
  time=$(measure_response_time GET /employees/)
  total_time=$((total_time + time))
  if (( i % 10 == 0 )); then
    echo "Completed $i requests..."
  fi
done
average_time=$((total_time / 50))
echo "Average response time for 50 requests: ${average_time}ms"
echo "Total time for 50 requests: ${total_time}ms"

# Test 6: Database connection stress test
echo "6. Testing database connection stress..."
for i in {1..20}; do
  # Create multiple profiles to stress the database
  curl -s -X POST "$API_URL/employees/" \
    -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": $((40 + i)), \"company_id\": 1, \"department\": \"Dept$i\", \"position\": \"Pos$i\", \"hire_date\": \"2023-01-01T00:00:00\"}" > /dev/null &
done
wait
echo "Database stress test completed."

# Cleanup
rm -f curl-format.txt

echo
echo "Performance and concurrency tests completed."
echo "Note: For production systems, consider using tools like Apache Bench (ab) or Siege for more comprehensive load testing."

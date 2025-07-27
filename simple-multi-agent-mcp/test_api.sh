#!/bin/bash
# Test script for the Multi-Agent System API

BASE_URL="http://localhost:8000"

echo "🧪 Testing Multi-Agent System API..."
echo "=================================="

# Test 1: Health Check
echo "📊 Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .
echo

# Test 2: Root endpoint
echo "🏠 Testing root endpoint..."
curl -s "$BASE_URL/" | jq .
echo

# Test 3: Status endpoint
echo "📈 Testing status endpoint..."
curl -s "$BASE_URL/status" | jq .
echo

# Test 4: Math query
echo "🔢 Testing math calculation..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 15 + 27"}' | jq .
echo

# Test 5: Text analysis
echo "📝 Testing text analysis..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze the sentiment of: I love sunny days!"}' | jq .
echo

# Test 6: Complex task
echo "🎯 Testing task coordination..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me solve 2x + 5 = 15 and then count the words in the solution"}' | jq .
echo

echo "✅ API testing complete!"

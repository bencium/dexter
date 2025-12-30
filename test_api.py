#!/usr/bin/env python3
"""
Test script for Dexter API
Run this after starting the API server to verify it's working correctly
"""
import requests
import json
import time
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_root_endpoint():
    """Test the root endpoint"""
    print_section("Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Root endpoint working")
        print(f"Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print_section("Testing Health Check Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check working")
        print(f"Status: {data['status']}")
        print(f"API Keys: {json.dumps(data['api_keys_configured'], indent=2)}")

        if data['status'] != 'healthy':
            print(f"\n⚠️  Warning: API is in '{data['status']}' state")
            print(f"Message: {data['message']}")

        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print_section("Testing Status Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status endpoint working")
        print(f"Available tools: {', '.join(data['available_tools'])}")
        return True
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint with a simple financial query"""
    print_section("Testing Query Endpoint")

    query = "What is Apple's stock ticker symbol?"

    print(f"Query: {query}")
    print(f"⏳ Sending request (this may take 10-30 seconds)...\n")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query},
            timeout=120  # 2 minute timeout for complex queries
        )
        elapsed_time = time.time() - start_time

        response.raise_for_status()
        data = response.json()

        print(f"✅ Query completed in {elapsed_time:.2f} seconds")
        print(f"\nStatus: {data['status']}")

        if data['status'] == 'success':
            print(f"Answer: {data.get('answer', 'No answer provided')}")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")

        return data['status'] == 'success'

    except requests.exceptions.Timeout:
        print(f"❌ Query timed out (>120 seconds)")
        return False
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_docs_endpoint():
    """Test that API documentation is accessible"""
    print_section("Testing API Documentation")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        response.raise_for_status()
        print(f"✅ API documentation accessible at: {BASE_URL}/docs")
        return True
    except Exception as e:
        print(f"❌ Documentation endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  🤖 Dexter API Test Suite")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Make sure the API server is running with: uv run dexter-api\n")

    # Check if server is reachable
    try:
        requests.get(BASE_URL, timeout=5)
    except Exception as e:
        print(f"\n❌ Cannot reach API server at {BASE_URL}")
        print(f"Error: {e}")
        print(f"\nPlease start the server first:")
        print(f"  uv run dexter-api")
        sys.exit(1)

    # Run tests
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Check", test_health_endpoint),
        ("Status Endpoint", test_status_endpoint),
        ("API Documentation", test_docs_endpoint),
        ("Query Endpoint", test_query_endpoint),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 All tests passed! Your API is ready to deploy.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

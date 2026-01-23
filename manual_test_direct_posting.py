#!/usr/bin/env python3
"""
Manual test script for direct LinkedIn posting endpoint

This script demonstrates how the new direct posting endpoint works.
It can be used to test the endpoint without needing the full admin panel.

Usage:
    # Start the API server first in another terminal:
    python api_server.py
    
    # Then run this test:
    python manual_test_direct_posting.py
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:5000"

def test_health():
    """Test that the API server is running"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("\nMake sure the API server is running:")
        print("  python api_server.py")
        return False


def test_direct_posting():
    """Test the direct posting endpoint"""
    print("\nTesting direct LinkedIn posting endpoint...")
    
    # Sample content to post
    test_content = """🚀 Exciting AI Research Alert!

Just discovered an amazing paper on neural networks that achieves state-of-the-art results.

Key highlights:
• Novel architecture design
• 20% improvement over previous methods
• Open-source implementation available

#AI #MachineLearning #Research"""
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/publish/linkedin/direct",
            json={"content": test_content},
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print("\n✅ Direct posting succeeded!")
            print(f"Post URL: {result.get('post_url', 'N/A')}")
            return True
        elif response.status_code == 400:
            print(f"\n⚠️  Request validation failed: {result.get('error')}")
            if 'credentials' in result.get('error', '').lower():
                print("\nNote: This is expected if LinkedIn credentials are not configured.")
                print("To configure credentials, set these environment variables:")
                print("  LINKEDIN_ACCESS_TOKEN=your_token")
                print("  LINKEDIN_USER_ID=your_user_id")
            return True  # Expected error for missing credentials
        else:
            print(f"\n❌ Unexpected response: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False


def test_missing_content():
    """Test validation for missing content"""
    print("\nTesting validation for missing content...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/publish/linkedin/direct",
            json={},  # Missing content field
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if response.status_code == 400 and 'content' in result.get('error', '').lower():
            print("✅ Missing content validation works correctly")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False


def test_empty_content():
    """Test validation for empty content"""
    print("\nTesting validation for empty content...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/publish/linkedin/direct",
            json={"content": ""},  # Empty content
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if response.status_code == 400 and 'empty' in result.get('error', '').lower():
            print("✅ Empty content validation works correctly")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Direct LinkedIn Posting Endpoint - Manual Test")
    print("="*60)
    
    # Test API health
    if not test_health():
        print("\n❌ Cannot proceed without API server running")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_missing_content,
        test_empty_content,
        test_direct_posting,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

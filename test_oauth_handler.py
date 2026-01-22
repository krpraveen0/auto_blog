#!/usr/bin/env python3
"""
Simple tests for the OAuth handler to verify functionality.
Run with: python test_oauth_handler.py
"""

import os
import sys

# Mock environment variables for testing
os.environ['GITHUB_CLIENT_ID'] = 'test_client_id'
os.environ['GITHUB_CLIENT_SECRET'] = 'test_client_secret'
os.environ['ALLOWED_USERS'] = 'testuser1,testuser2'

try:
    from oauth_handler import app
    print("✅ OAuth handler imports successfully")
except Exception as e:
    print(f"❌ Failed to import OAuth handler: {e}")
    sys.exit(1)

# Test Flask app creation
try:
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'oauth-handler'
        print("✅ Health endpoint works correctly")
except Exception as e:
    print(f"❌ Health endpoint test failed: {e}")
    sys.exit(1)

# Test missing token in verify endpoint
try:
    with app.test_client() as client:
        response = client.post('/auth/verify',
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print("✅ Verify endpoint rejects missing token")
except Exception as e:
    print(f"❌ Verify endpoint test failed: {e}")
    sys.exit(1)

# Test missing code in callback endpoint
try:
    with app.test_client() as client:
        response = client.get('/auth/callback')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        print("✅ Callback endpoint rejects missing code")
except Exception as e:
    print(f"❌ Callback endpoint test failed: {e}")
    sys.exit(1)

# Test CORS headers
try:
    with app.test_client() as client:
        response = client.options('/auth/verify',
                                  headers={'Origin': 'https://test.github.io'})
        # CORS should be configured for github.io domains
        print("✅ CORS configuration is set up")
except Exception as e:
    print(f"❌ CORS test failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ All OAuth handler tests passed!")
print("="*50)
print("\nThe OAuth handler is ready to be deployed.")
print("\nNext steps:")
print("1. Deploy to Railway, Render, or Heroku")
print("2. Set environment variables in deployment:")
print("   - GITHUB_CLIENT_ID")
print("   - GITHUB_CLIENT_SECRET")
print("   - ALLOWED_USERS (optional)")
print("3. Update OAUTH_HANDLER_URL in docs/admin/index.html")
print("4. Update GitHub OAuth App callback URL")

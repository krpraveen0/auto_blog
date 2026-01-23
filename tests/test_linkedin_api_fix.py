"""
Test for LinkedIn API response handling fix
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from publishers.linkedin_api import LinkedInPublisher


def test_only_201_is_success():
    """Test that only 201 status code is treated as successful"""
    
    config = {
        'enabled': True,
        'auto_publish': False
    }
    
    # Mock environment variables
    with patch.dict('os.environ', {
        'LINKEDIN_ACCESS_TOKEN': 'test_token',
        'LINKEDIN_USER_ID': 'test_user_id'
    }):
        publisher = LinkedInPublisher(config)
        
        # Test 201 response - should be success
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.content = b'{"id": "urn:li:activity:123456"}'
            mock_response.json.return_value = {"id": "urn:li:activity:123456"}
            mock_response.headers = {}
            mock_post.return_value = mock_response
            
            result = publisher._post_to_linkedin("Test content")
            assert result['success'] is True, "201 response should be success"
            assert 'post_id' in result, "Should return post_id"
            
            # Verify correct endpoint is used (v2/ugcPosts)
            call_args = mock_post.call_args
            assert call_args[0][0].endswith('/v2/ugcPosts'), "Should use exact /v2/ugcPosts endpoint"
            
            # Verify correct payload structure
            payload = call_args[1]['json']
            assert 'specificContent' in payload, "Payload should have specificContent"
            assert 'com.linkedin.ugc.ShareContent' in payload['specificContent'], "Should use ShareContent"
            assert 'shareCommentary' in payload['specificContent']['com.linkedin.ugc.ShareContent'], "Should have shareCommentary"
            
            print("✅ Test passed: 201 status code is treated as success")
            print("✅ Test passed: Correct v2 API endpoint and structure used")
        
        # Test 200 response - should be failure (not success)
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_response.ok = True
            mock_post.return_value = mock_response
            
            result = publisher._post_to_linkedin("Test content")
            assert result['success'] is False, "200 response should NOT be success"
            assert 'error' in result, "Should return error message"
            assert '200' in result['error'], "Error should mention status code"
            print("✅ Test passed: 200 status code is treated as failure")
        
        # Test 202 response - should be failure (not success)
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 202
            mock_response.text = "Accepted"
            mock_response.ok = True
            mock_post.return_value = mock_response
            
            result = publisher._post_to_linkedin("Test content")
            assert result['success'] is False, "202 response should NOT be success"
            assert 'error' in result, "Should return error message"
            print("✅ Test passed: 202 status code is treated as failure")
        
        # Test 400 response - should be failure
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_response.ok = False
            mock_post.return_value = mock_response
            
            result = publisher._post_to_linkedin("Test content")
            assert result['success'] is False, "400 response should be failure"
            assert 'error' in result, "Should return error message"
            print("✅ Test passed: 400 status code is treated as failure")
        
        # Test 401 response - should be failure
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.ok = False
            mock_post.return_value = mock_response
            
            result = publisher._post_to_linkedin("Test content")
            assert result['success'] is False, "401 response should be failure"
            assert 'error' in result, "Should return error message"
            print("✅ Test passed: 401 status code is treated as failure")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_only_201_is_success,
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("Running LinkedIn API Fix Tests")
    print("="*60 + "\n")
    
    for test in tests:
        try:
            print(f"Running: {test.__name__}...")
            test()
            passed += 1
            print()
        except AssertionError as e:
            print(f"❌ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

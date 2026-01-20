"""
Test suite for enhanced LinkedIn posting features
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.prompts import get_prompt, LINKEDIN_VIRAL_PATTERNS, LINKEDIN_ENGAGING_POST_PROMPT
from formatters.linkedin import LinkedInFormatter


def test_via_source_removed():
    """Test that 'via {source}' is removed from LinkedIn posts"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    # Test source link generation
    item = {
        'url': 'https://arxiv.org/abs/2401.12345',
        'source': 'arxiv',
        'source_name': 'arXiv'
    }
    
    source_link = formatter._generate_source_link(item)
    
    # Verify 'via' is NOT in the source link
    assert 'via' not in source_link.lower(), f"Found 'via' in source link: {source_link}"
    assert '📎 Read more:' in source_link, f"Missing read more link: {source_link}"
    assert item['url'] in source_link, f"URL missing from source link: {source_link}"
    
    print("✅ Test passed: 'via {source}' successfully removed from LinkedIn posts")


def test_prompt_availability():
    """Test that new engagement prompts are available"""
    
    # Test viral patterns doc exists
    assert len(LINKEDIN_VIRAL_PATTERNS) > 0, "LINKEDIN_VIRAL_PATTERNS is empty"
    assert 'Pattern:' in LINKEDIN_VIRAL_PATTERNS, "Viral patterns not documented"
    
    # Test engaging prompt exists
    assert len(LINKEDIN_ENGAGING_POST_PROMPT) > 0, "LINKEDIN_ENGAGING_POST_PROMPT is empty"
    assert 'ENGAGEMENT FRAMEWORK' in LINKEDIN_ENGAGING_POST_PROMPT, "Engagement framework not found"
    
    # Test prompts are accessible
    try:
        prompt = get_prompt('linkedin_engaging', title='Test', url='http://test.com', analyzed_content='Test content')
        assert len(prompt) > 0, "Empty prompt returned"
        assert 'Test' in prompt, "Title not in prompt"
    except Exception as e:
        raise AssertionError(f"Failed to get linkedin_engaging prompt: {e}")
    
    try:
        prompt = get_prompt('linkedin_validation', content='Test post content')
        assert len(prompt) > 0, "Empty validation prompt returned"
        assert 'VALIDATION CHECKLIST' in prompt, "Validation checklist not found"
    except Exception as e:
        raise AssertionError(f"Failed to get linkedin_validation prompt: {e}")
    
    try:
        prompt = get_prompt('trend_discovery', current_date='2024-01-01', recent_content='[]')
        assert len(prompt) > 0, "Empty trend discovery prompt returned"
        assert 'FOCUS AREAS' in prompt, "Focus areas not found"
    except Exception as e:
        raise AssertionError(f"Failed to get trend_discovery prompt: {e}")
    
    print("✅ Test passed: All new prompts are available and accessible")


def test_content_cleaning():
    """Test content cleaning removes problematic elements"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    # Test citation marker removal
    content = "This is great research [1] with citations [2]."
    cleaned = formatter._clean_content(content)
    assert '[1]' not in cleaned, f"Citation markers not removed: {cleaned}"
    assert '[2]' not in cleaned, f"Citation markers not removed: {cleaned}"
    
    # Test hashtag# removal
    content = "Check out hashtag#AI and hashtag#ML"
    cleaned = formatter._clean_content(content)
    assert 'hashtag#' not in cleaned, f"hashtag# not removed: {cleaned}"
    assert '#AI' in cleaned or 'AI' in cleaned, f"Hashtag content lost: {cleaned}"
    
    # Test markdown removal
    content = "This is **bold** and *italic* text"
    cleaned = formatter._clean_content(content)
    assert '**' not in cleaned, f"Bold markdown not removed: {cleaned}"
    assert '*' not in cleaned or cleaned.count('*') == 0, f"Italic markdown not removed: {cleaned}"
    
    print("✅ Test passed: Content cleaning works correctly")


def test_trend_discovery_import():
    """Test that trend discovery module can be imported"""
    try:
        from sources.trends import TrendDiscovery, TrendScheduler
        
        # Verify classes exist
        assert TrendDiscovery is not None, "TrendDiscovery class not found"
        assert TrendScheduler is not None, "TrendScheduler class not found"
        
        print("✅ Test passed: Trend discovery module imports successfully")
    except Exception as e:
        raise AssertionError(f"Failed to import trend discovery: {e}")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_via_source_removed,
        test_prompt_availability,
        test_content_cleaning,
        test_trend_discovery_import,
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("Running LinkedIn Enhancement Tests")
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

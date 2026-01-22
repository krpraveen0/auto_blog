"""
Test suite for agent conversation filtering in LinkedIn posts
"""

import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from formatters.linkedin import LinkedInFormatter


def test_agent_phrase_removal():
    """Test that agent-related phrases are removed from content"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    test_cases = [
        # Agent identity phrases
        ("As an AI, I think this is important.", "", True),
        ("I'm an AI assistant helping you.", "", True),
        
        # Meta-commentary (now more specific)
        ("Here's what you need to know about AI.", "about AI.", True),
        ("Here is how you should implement this.", "this.", True),
        ("In this post, we discuss AI research.", "AI research.", True),
        
        # Conversational hedges (at start of sentence)
        ("It seems that this approach works well.", "that this approach works well.", True),
        ("It appears as if we have progress.", "as if we have progress.", True),
        
        # LLM artifacts
        ("According to my analysis, this is good.", "this is good.", True),
        ("Based on my understanding, it works.", "it works.", True),
        
        # Content that should be preserved (legitimate uses)
        ("This research achieves 95% accuracy.", "This research achieves 95% accuracy.", False),
        ("The model uses transformer architecture.", "The model uses transformer architecture.", False),
        ("New findings show significant improvements.", "New findings show significant improvements.", False),
        ("Here's a new framework for ML.", "Here's a new framework for ML.", False),  # Not filtered - doesn't match pattern
        ("I will implement this feature.", "I will implement this feature.", False),  # Not filtered - not agent context
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected_pattern, should_filter in test_cases:
        cleaned = formatter._clean_content(input_text)
        
        # For filtered content, check that agent phrases are gone
        if should_filter:
            agent_phrases = ['as an ai', 'i am an ai', "here's", 'here is', 
                           'in this post', 'it seems', 'it appears', 
                           'according to my', 'based on my']
            has_agent_phrase = any(phrase in cleaned.lower() for phrase in agent_phrases)
            
            if has_agent_phrase:
                print(f"❌ FAILED: Agent phrase still in: '{input_text}' -> '{cleaned}'")
                failed += 1
            else:
                passed += 1
        else:
            # For non-filtered content, verify it's preserved
            if cleaned.strip() and input_text.strip() in cleaned:
                passed += 1
            else:
                print(f"❌ FAILED: Content lost: '{input_text}' -> '{cleaned}'")
                failed += 1
    
    print(f"\n✅ Passed: {passed}/{passed + failed} tests")
    
    if failed > 0:
        raise AssertionError(f"{failed} test(s) failed")


def test_comprehensive_cleaning():
    """Test that all cleaning operations work together"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    # Complex content with multiple issues but also real content
    content = """
    New research achieves breakthrough results [1].
    As an AI, here's what you need to know about this.
    
    The model uses **transformer** architecture with *attention* mechanisms.
    It seems that this approach works well in production.
    
    Key findings:
    - 95% accuracy on benchmarks
    - Faster inference time
    
    According to my analysis, this is interesting.
    """
    
    cleaned = formatter._clean_content(content)
    
    # Verify all problematic elements are removed
    assert '[1]' not in cleaned, "Citation markers not removed"
    assert '**' not in cleaned, "Markdown bold not removed"
    assert '*' not in cleaned, "Markdown italic not removed"
    assert 'as an ai' not in cleaned.lower(), "Agent phrases not removed"
    assert 'it seems' not in cleaned.lower(), "Hedging phrases not removed"
    assert 'according to my' not in cleaned.lower(), "Attribution phrases not removed"
    
    # Verify content is preserved (some meaningful text should remain)
    assert len(cleaned.strip()) > 0, "All content was removed"
    assert 'transformer' in cleaned.lower() or 'architecture' in cleaned.lower(), "Core technical content was lost"
    assert '95%' in cleaned or 'accuracy' in cleaned, "Key findings were lost"
    
    print("✅ Comprehensive cleaning test passed")


def test_citation_removal():
    """Test that citation markers are properly removed"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    test_cases = [
        ("Research shows promising results [1].", "Research shows promising results."),
        ("Multiple citations [1][2][3] here.", "Multiple citations here."),
        ("Start [1] and end [2] citations.", "Start and end citations."),
    ]
    
    for input_text, expected in test_cases:
        cleaned = formatter._clean_content(input_text)
        # Check that no citation markers remain
        has_citations = bool(re.search(r'\[\d+\]', cleaned))
        
        if has_citations:
            raise AssertionError(f"Citations not removed from: '{input_text}' -> '{cleaned}'")
    
    print("✅ Citation removal test passed")


def test_markdown_removal():
    """Test that markdown formatting is removed"""
    config = {
        'max_words': 150,
        'bullet_points': 3,
        'hashtag_count': 4,
        'emojis': False
    }
    
    formatter = LinkedInFormatter(config)
    
    test_cases = [
        ("This is **bold** text.", "This is bold text."),
        ("This is *italic* text.", "This is italic text."),
        ("This is __underlined__ text.", "This is underlined text."),
        ("Mix of **bold** and *italic*.", "Mix of bold and italic."),
    ]
    
    for input_text, expected_pattern in test_cases:
        cleaned = formatter._clean_content(input_text)
        
        # Check that no markdown remains
        if '**' in cleaned or '__' in cleaned:
            raise AssertionError(f"Markdown not removed from: '{input_text}' -> '{cleaned}'")
        
        # Verify core content is preserved
        if 'bold' in input_text and 'bold' not in cleaned:
            raise AssertionError(f"Content lost: '{input_text}' -> '{cleaned}'")
    
    print("✅ Markdown removal test passed")


def run_all_tests():
    """Run all agent filtering tests"""
    tests = [
        test_agent_phrase_removal,
        test_comprehensive_cleaning,
        test_citation_removal,
        test_markdown_removal,
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("Running Agent Filtering Tests")
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
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

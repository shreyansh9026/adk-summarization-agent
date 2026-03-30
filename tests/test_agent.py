"""
Local testing script for the ADK Text Classification Agent
Run this to verify the agent works before deployment
"""

import json
import sys
from agent import create_agent


def test_agent():
    """Test the agent with sample inputs"""
    
    print("=" * 60)
    print("ADK Text Classification Agent - Local Test")
    print("=" * 60)
    
    # Initialize agent
    print("\n[1/4] Initializing agent...")
    try:
        agent = create_agent()
        print("✓ Agent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        print("Make sure GOOGLE_API_KEY environment variable is set")
        return False
    
    # Test 1: News classification
    print("\n[2/4] Test 1: News Classification")
    news_text = "Breaking news: Scientists discover new renewable energy source that could revolutionize power generation globally"
    print(f"Input: {news_text}")
    result = agent.classify(news_text)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result.get("success"), "Test 1 failed"
    print("✓ Test 1 passed")
    
    # Test 2: Technical classification
    print("\n[3/4] Test 2: Technical Classification")
    tech_text = "The REST API endpoint uses HTTP GET method with query parameters: ?limit=10&offset=0. Authentication requires Bearer token in Authorization header"
    print(f"Input: {tech_text}")
    result = agent.classify(tech_text)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result.get("success"), "Test 2 failed"
    print("✓ Test 2 passed")
    
    # Test 3: Opinion classification
    print("\n[4/4] Test 3: Opinion Classification")
    opinion_text = "In my view, this policy change is a mistake. The government should have consulted stakeholders before implementation. I believe this will have negative consequences for the community"
    print(f"Input: {opinion_text}")
    result = agent.classify(opinion_text)
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result.get("success"), "Test 3 failed"
    print("✓ Test 3 passed")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


def test_edge_cases():
    """Test edge cases"""
    
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    agent = create_agent()
    
    # Empty input
    print("\n[Edge Case 1] Empty input")
    result = agent.classify("")
    assert not result.get("success"), "Should fail on empty input"
    print(f"✓ Correctly rejected: {result.get('error')}")
    
    # Very short input
    print("\n[Edge Case 2] Very short input")
    result = agent.classify("Hi")
    print(f"Result: {json.dumps(result, indent=2)}")
    print("✓ Handled short input")
    
    # Very long input
    print("\n[Edge Case 3] Very long input")
    long_text = "Lorem ipsum " * 500  # ~6000 characters
    result = agent.classify(long_text)
    print(f"Result: {json.dumps(result, indent=2)}")
    print("✓ Handled long input")
    
    print("\n" + "=" * 60)
    print("Edge case tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_agent()
        test_edge_cases()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

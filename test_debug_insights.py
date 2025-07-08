#!/usr/bin/env python3
"""
Debug insight retrieval and filtering step by step
"""

import sys
sys.path.append('.')

from enhanced_collective_memory import EnhancedCollectiveMemoryAgent

def debug_insight_flow():
    """Debug the complete insight flow"""
    print("🔍 DEBUGGING INSIGHT FLOW")
    print("=" * 50)
    
    # Create enhanced system
    system = EnhancedCollectiveMemoryAgent(role="debug_agent")
    print("✅ Enhanced system created")
    
    # Test problem
    test_problem_name = "sort_array"
    test_description = "Given a list of integers, sort the array using an efficient sorting algorithm and return the sorted result."
    test_problem = f"""
def {test_problem_name}(numbers: List[int]) -> List[int]:
    \"\"\" {test_description}
    >>> {test_problem_name}([3, 2, 1])
    [1, 2, 3]
    >>> {test_problem_name}([5, 4, 3, 2, 1])
    [1, 2, 3, 4, 5]
    \"\"\"
"""
    
    print(f"\n📝 Test problem: {test_problem_name}")
    
    # Step 1: Domain classification
    domain = system.domain_memory.classify_domain(test_problem)
    print(f"🏷️  Classified domain: {domain}")
    
    # Step 2: Raw insight retrieval
    print(f"\n🔍 Retrieving raw insights...")
    raw_insights = system.domain_memory.retrieve_domain_insights(
        test_problem, system.agent_id, limit=20
    )
    print(f"📊 Raw insights found: {len(raw_insights)}")
    
    for i, insight in enumerate(raw_insights, 1):
        domain = getattr(insight, 'domain', 'unknown')
        print(f"   {i}. [{domain}] {insight.content[:80]}...")
    
    # Step 3: Intelligent filtering
    print(f"\n🧠 Applying intelligent filtering...")
    filtered_insights = system.insight_filter.filter_insights(raw_insights, test_problem)
    print(f"📊 Filtered insights: {len(filtered_insights)}")
    
    for i, insight in enumerate(filtered_insights, 1):
        domain = getattr(insight, 'domain', 'unknown')
        quality = getattr(insight, 'quality_score', 0.0)
        print(f"   {i}. [{domain}] Quality: {quality:.2f}")
        print(f"      Content: {insight.content[:80]}...")
    
    # Step 4: Check filtering criteria
    print(f"\n🔧 Checking filtering criteria...")
    if raw_insights:
        sample_insight = raw_insights[0]
        quality = getattr(sample_insight, 'quality_score', 0.0)
        success_rate = getattr(sample_insight, 'success_rate', 1.0)
        usage_count = getattr(sample_insight, 'usage_count', 0)
        print(f"Sample insight quality: {quality}")
        print(f"Sample insight success rate: {success_rate}")
        print(f"Sample insight usage count: {usage_count}")
        
        # Check if it passes the filter
        relevance_score = system.insight_filter.calculate_relevance_score(sample_insight, test_problem)
        print(f"Calculated relevance score: {relevance_score}")

if __name__ == "__main__":
    debug_insight_flow()

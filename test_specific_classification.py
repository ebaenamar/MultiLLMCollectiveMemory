#!/usr/bin/env python3
"""
Test specific problem classification
"""

import sys
sys.path.append('.')

from enhanced_collective_memory import DomainSpecificMemory

def test_specific_problem():
    """Test the exact problem we're using"""
    domain_memory = DomainSpecificMemory()
    
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
    
    print("🔍 SPECIFIC PROBLEM CLASSIFICATION")
    print("=" * 50)
    print(f"Problem: {test_problem}")
    
    domain = domain_memory.classify_domain(test_problem)
    print(f"Classified domain: {domain}")
    
    # Test retrieval from that domain
    try:
        memory = domain_memory.get_domain_memory(domain)
        insights = memory.retrieve(test_problem, "test_agent", limit=5)
        
        print(f"\nInsights found in '{domain}' domain: {len(insights)}")
        for i, insight in enumerate(insights, 1):
            print(f"  {i}. {insight.content[:100]}...")
            
    except Exception as e:
        print(f"Error retrieving insights: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_problem()

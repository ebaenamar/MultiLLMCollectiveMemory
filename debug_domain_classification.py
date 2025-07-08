#!/usr/bin/env python3
"""
Debug domain classification and insight retrieval
"""

import sys
sys.path.append('.')

from enhanced_collective_memory import DomainSpecificMemory

def test_domain_classification():
    """Test domain classification for different queries"""
    domain_memory = DomainSpecificMemory()
    
    test_queries = [
        "has_close_elements",
        "Check whether two numbers in a given list are closer to each other than a given threshold",
        "sort algorithm implementation",
        "binary search tree operations", 
        "input validation techniques",
        "unit testing best practices",
        "performance optimization strategies",
        "list comparison and distance calculation",
        "array processing and element comparison"
    ]
    
    print("🔍 DOMAIN CLASSIFICATION TEST")
    print("=" * 50)
    
    for query in test_queries:
        domain = domain_memory.classify_domain(query)
        print(f"Query: '{query}'")
        print(f"  -> Domain: {domain}")
        print()

def test_domain_memories():
    """Test what domain memories exist"""
    domain_memory = DomainSpecificMemory()
    
    print("🗄️  DOMAIN MEMORIES STATUS")
    print("=" * 50)
    
    print(f"Available domain memories: {list(domain_memory.domain_memories.keys())}")
    
    # Try to create some domain memories
    test_domains = ['algorithms', 'data_structures', 'validation', 'testing', 'optimization', 'general']
    
    for domain in test_domains:
        try:
            memory = domain_memory.get_domain_memory(domain)
            print(f"✅ {domain}: Memory system created/retrieved")
        except Exception as e:
            print(f"❌ {domain}: Error - {e}")

def test_insight_retrieval():
    """Test insight retrieval from domain memories"""
    domain_memory = DomainSpecificMemory()
    
    print("🔍 INSIGHT RETRIEVAL TEST")
    print("=" * 50)
    
    test_queries = [
        ("algorithms", "sort algorithm implementation"),
        ("data_structures", "binary search tree operations"),
        ("validation", "input validation techniques"),
        ("testing", "unit testing best practices"),
        ("optimization", "performance optimization strategies")
    ]
    
    for domain, query in test_queries:
        try:
            # Get domain memory
            memory = domain_memory.get_domain_memory(domain)
            
            # Try to retrieve insights
            insights = memory.retrieve(query, "test_agent", limit=3)
            
            print(f"Domain: {domain}")
            print(f"Query: '{query}'")
            print(f"  -> Found {len(insights)} insights")
            
            for i, insight in enumerate(insights, 1):
                print(f"     {i}. {insight.content[:80]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error retrieving from {domain}: {e}")
            import traceback
            traceback.print_exc()
            print()

if __name__ == "__main__":
    test_domain_classification()
    test_domain_memories()
    test_insight_retrieval()

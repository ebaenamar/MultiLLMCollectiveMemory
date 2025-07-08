#!/usr/bin/env python3
"""
Test memory persistence across different agent instances
"""

import sys
sys.path.append('.')

from enhanced_collective_memory import EnhancedCollectiveMemoryAgent, DomainSpecificMemory

def test_memory_persistence():
    """Test if memories persist across different agent instances"""
    print("🔍 TESTING MEMORY PERSISTENCE")
    print("=" * 50)
    
    # Test 1: Direct domain memory access
    print("📂 Testing direct domain memory access...")
    domain_memory = DomainSpecificMemory()
    
    # Get data_structures domain memory
    ds_memory = domain_memory.get_domain_memory("data_structures")
    
    # Try to retrieve insights directly
    insights = ds_memory.retrieve("sort algorithm", "test_agent", limit=5)
    print(f"Direct retrieval from data_structures domain: {len(insights)} insights")
    
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight.content[:80]}...")
    
    # Test 2: Agent-based access
    print(f"\n👤 Testing agent-based access...")
    agent1 = EnhancedCollectiveMemoryAgent(role="test_agent_1")
    
    # Try to retrieve through agent
    agent_insights = agent1.domain_memory.retrieve_domain_insights(
        "sort algorithm", "test_agent_1", limit=5
    )
    print(f"Agent-based retrieval: {len(agent_insights)} insights")
    
    for i, insight in enumerate(agent_insights, 1):
        print(f"   {i}. {insight.content[:80]}...")
    
    # Test 3: Check if it's a storage path issue
    print(f"\n📁 Checking storage paths...")
    print(f"Domain memory base path: {domain_memory.base_path}")
    print(f"Agent domain memory base path: {agent1.domain_memory.base_path}")
    
    # Test 4: Check ChromaDB collections
    print(f"\n🗄️  Checking ChromaDB collections...")
    try:
        # Get the ChromaDB client from the domain memory
        ds_memory_agent = agent1.domain_memory.get_domain_memory("data_structures")
        if hasattr(ds_memory_agent, 'chroma_client'):
            collections = ds_memory_agent.chroma_client.list_collections()
            print(f"Available ChromaDB collections: {[c.name for c in collections]}")
        else:
            print("No ChromaDB client found")
    except Exception as e:
        print(f"Error checking collections: {e}")

if __name__ == "__main__":
    test_memory_persistence()

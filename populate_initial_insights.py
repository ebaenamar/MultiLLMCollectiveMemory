#!/usr/bin/env python3
"""
Populate the enhanced memory system with initial insights from domain JSON files
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append('.')

def load_domain_insights():
    """Load insights from domain JSON files"""
    domain_files = {
        'algorithms': 'memory_data/domains/algorithms.json',
        'data_structures': 'memory_data/domains/data_structures.json', 
        'validation': 'memory_data/domains/validation.json',
        'testing': 'memory_data/domains/testing.json',
        'optimization': 'memory_data/domains/optimization.json'
    }
    
    all_insights = []
    
    for domain, file_path in domain_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Extract insights from the JSON structure
                insights = data.get('insights', [])
                for insight in insights:
                    all_insights.append({
                        'domain': domain,
                        'content': insight,
                        'keywords': data.get('keywords', []),
                        'patterns': data.get('patterns', [])
                    })
                    
                print(f"✅ Loaded {len(insights)} insights from {domain}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return all_insights

def populate_memory_system(insights):
    """Populate the enhanced memory system with insights"""
    try:
        from enhanced_collective_memory import EnhancedCollectiveMemoryAgent, EnhancedMemoryEntry
        from memory_systems.base_memory import MemoryEntry
        import uuid
        
        # Create enhanced agent
        agent = EnhancedCollectiveMemoryAgent(role="system_initializer")
        print("✅ Enhanced memory agent created")
        
        stored_count = 0
        
        for insight_data in insights:
            try:
                # Create enhanced memory entry
                # Convert lists to strings for ChromaDB compatibility
                entry = EnhancedMemoryEntry(
                    id=f"init_{uuid.uuid4().hex[:8]}",
                    content=insight_data['content'],
                    metadata={
                        'source': 'initial_population',
                        'domain': insight_data['domain'],
                        'keywords': ', '.join(insight_data['keywords']),
                        'patterns': ', '.join(insight_data['patterns'])
                    },
                    timestamp=datetime.now(),
                    agent_id="system_initializer",
                    tags=[insight_data['domain'], 'initial', 'system'],
                    importance_score=0.8,
                    domain=insight_data['domain'],
                    quality_score=0.9,
                    usage_count=0,
                    success_rate=1.0,
                    federation_source=None
                )
                
                # Store in domain-specific memory
                success = agent.domain_memory.store_domain_insight(entry)
                if success:
                    stored_count += 1
                    
            except Exception as e:
                print(f"❌ Error storing insight: {e}")
                continue
        
        print(f"✅ Successfully stored {stored_count} insights in memory system")
        return stored_count
        
    except Exception as e:
        print(f"❌ Error initializing memory system: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_populated_system():
    """Test that the populated system can retrieve insights"""
    try:
        from enhanced_collective_memory import EnhancedCollectiveMemoryAgent
        
        # Create test agent
        agent = EnhancedCollectiveMemoryAgent(role="test_retrieval")
        
        # Test queries for different domains
        test_queries = [
            "sort algorithm implementation",
            "binary search tree operations", 
            "input validation techniques",
            "unit testing best practices",
            "performance optimization strategies"
        ]
        
        total_retrieved = 0
        
        for query in test_queries:
            insights = agent.domain_memory.retrieve_domain_insights(query, "test_agent", limit=3)
            total_retrieved += len(insights)
            print(f"🔍 Query: '{query}' -> {len(insights)} insights found")
            
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. [{insight.domain}] {insight.content[:80]}...")
        
        print(f"\n📊 Total insights retrieved across all queries: {total_retrieved}")
        return total_retrieved > 0
        
    except Exception as e:
        print(f"❌ Error testing populated system: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main population function"""
    print("🚀 POPULATING ENHANCED MEMORY SYSTEM WITH INITIAL INSIGHTS")
    print("=" * 70)
    
    # Load insights from JSON files
    insights = load_domain_insights()
    print(f"\n📊 Total insights loaded: {len(insights)}")
    
    if not insights:
        print("❌ No insights loaded. Check that domain JSON files exist.")
        return
    
    # Populate memory system
    stored_count = populate_memory_system(insights)
    
    if stored_count > 0:
        print(f"\n✅ Successfully populated memory system with {stored_count} insights")
        
        # Test the populated system
        print(f"\n🧪 TESTING POPULATED SYSTEM")
        print("=" * 50)
        
        success = test_populated_system()
        
        if success:
            print(f"\n🎉 Memory system is now populated and ready!")
            print("   You can now run the enhanced system and it should use insights.")
        else:
            print(f"\n⚠️  Population successful but retrieval test failed.")
    else:
        print(f"\n❌ Failed to populate memory system.")

if __name__ == "__main__":
    main()

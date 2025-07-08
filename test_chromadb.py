#!/usr/bin/env python3
"""
Test ChromaDB functionality and setup
"""

import os
import sys
import chromadb
from datetime import datetime

def test_chromadb_embedded():
    """Test ChromaDB in embedded mode"""
    print("🧪 TESTING CHROMADB EMBEDDED MODE")
    print("=" * 50)
    
    try:
        # Create embedded ChromaDB client
        client = chromadb.PersistentClient(path="./test_chromadb")
        print("✅ ChromaDB client created successfully")
        
        # Create or get collection
        collection = client.get_or_create_collection(name="test_collection")
        print("✅ Collection created/retrieved successfully")
        
        # Test data
        test_documents = [
            "This is a function that calculates fibonacci numbers",
            "Algorithm for sorting arrays using quicksort method",
            "Data structure implementation of binary search tree",
            "Unit test for validating user input parameters"
        ]
        
        test_ids = [f"doc_{i}" for i in range(len(test_documents))]
        test_metadatas = [{"type": "code", "domain": "algorithms"} for _ in test_documents]
        
        # Add documents
        collection.add(
            documents=test_documents,
            ids=test_ids,
            metadatas=test_metadatas
        )
        print(f"✅ Added {len(test_documents)} test documents")
        
        # Test query
        results = collection.query(
            query_texts=["fibonacci sequence calculation"],
            n_results=2
        )
        
        print("\n🔍 QUERY RESULTS:")
        print(f"Query: 'fibonacci sequence calculation'")
        print(f"Results found: {len(results['documents'][0])}")
        
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"  {i+1}. Distance: {distance:.4f}")
            print(f"     Document: {doc[:80]}...")
        
        # Test count
        count = collection.count()
        print(f"\n📊 Total documents in collection: {count}")
        
        # Cleanup
        client.delete_collection("test_collection")
        print("✅ Test collection cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

def test_memory_system_integration():
    """Test integration with our memory system"""
    print("\n🔗 TESTING MEMORY SYSTEM INTEGRATION")
    print("=" * 50)
    
    try:
        # Import our memory system
        sys.path.append('./memory_systems')
        from memory_systems.shared_memory import SharedMemorySystem
        from memory_systems.base_memory import MemoryEntry
        
        # Create memory system
        memory_system = SharedMemorySystem(
            system_id="test_system",
            storage_path="./test_memory"
        )
        print("✅ SharedMemorySystem created")
        
        # Create test memory entry
        test_entry = MemoryEntry(
            id="test_001",
            content="Test function for calculating prime numbers using sieve method",
            metadata={"domain": "algorithms", "complexity": "O(n log log n)"},
            timestamp=datetime.now(),
            agent_id="test_agent",
            tags=["algorithms", "prime", "sieve"],
            importance_score=0.8
        )
        
        # Store entry
        success = memory_system.store(test_entry)
        print(f"✅ Memory entry stored: {success}")
        
        # Retrieve with semantic search
        results = memory_system.retrieve("prime number calculation", "test_agent", limit=5)
        print(f"✅ Retrieved {len(results)} results for semantic search")
        
        if results:
            print(f"   Best match: {results[0].content[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory system integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_domain_files():
    """Check if domain JSON files exist"""
    print("\n📁 CHECKING DOMAIN FILES")
    print("=" * 50)
    
    domain_files = [
        "data_structures.json",
        "algorithms.json", 
        "validation.json",
        "testing.json",
        "optimization.json"
    ]
    
    existing_files = []
    missing_files = []
    
    for file in domain_files:
        if os.path.exists(file):
            existing_files.append(file)
            print(f"✅ {file} exists")
        else:
            missing_files.append(file)
            print(f"❌ {file} missing")
    
    print(f"\n📊 Summary: {len(existing_files)} existing, {len(missing_files)} missing")
    
    if missing_files:
        print("\n💡 Missing domain files may explain why insights_used = 0 in experiments")
        print("   These files are needed for domain-specific insight filtering")
    
    return len(missing_files) == 0

def create_sample_domain_files():
    """Create sample domain files for testing"""
    print("\n🛠️  CREATING SAMPLE DOMAIN FILES")
    print("=" * 50)
    
    domain_data = {
        "data_structures.json": {
            "keywords": ["array", "list", "tree", "graph", "hash", "stack", "queue", "heap"],
            "patterns": ["binary search", "traversal", "insertion", "deletion", "lookup"],
            "insights": [
                "Use hash tables for O(1) lookup operations",
                "Binary search trees provide O(log n) search in balanced cases",
                "Arrays offer constant-time access but expensive insertions"
            ]
        },
        "algorithms.json": {
            "keywords": ["sort", "search", "dynamic", "greedy", "divide", "conquer"],
            "patterns": ["recursion", "iteration", "memoization", "optimization"],
            "insights": [
                "Dynamic programming reduces time complexity by avoiding recomputation",
                "Divide and conquer often leads to O(n log n) solutions",
                "Greedy algorithms work when local optima lead to global optima"
            ]
        },
        "validation.json": {
            "keywords": ["test", "assert", "validate", "check", "verify", "edge case"],
            "patterns": ["boundary testing", "null checks", "type validation"],
            "insights": [
                "Always test edge cases like empty inputs and boundary values",
                "Type validation prevents runtime errors in dynamic languages",
                "Unit tests should cover both happy path and error conditions"
            ]
        }
    }
    
    created_files = []
    for filename, data in domain_data.items():
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            created_files.append(filename)
            print(f"✅ Created {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    print(f"\n📊 Created {len(created_files)} domain files")
    return created_files

def main():
    """Run all tests"""
    print("🚀 CHROMADB DIAGNOSTIC AND SETUP")
    print("=" * 60)
    
    # Test ChromaDB embedded mode
    chromadb_ok = test_chromadb_embedded()
    
    # Test memory system integration
    memory_ok = test_memory_system_integration()
    
    # Check domain files
    domain_files_ok = test_domain_files()
    
    # Create sample domain files if missing
    if not domain_files_ok:
        created_files = create_sample_domain_files()
        print(f"\n💡 Created {len(created_files)} sample domain files")
    
    # Summary
    print("\n🏆 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"ChromaDB embedded mode: {'✅ WORKING' if chromadb_ok else '❌ FAILED'}")
    print(f"Memory system integration: {'✅ WORKING' if memory_ok else '❌ FAILED'}")
    print(f"Domain files: {'✅ COMPLETE' if domain_files_ok else '⚠️  CREATED SAMPLES'}")
    
    if chromadb_ok and memory_ok:
        print("\n🎉 ChromaDB is ready for enhanced memory system!")
        print("   You can now rerun the enhanced experiment with semantic search enabled.")
    else:
        print("\n⚠️  Some issues need to be resolved before full functionality.")
    
    # Cleanup test files
    import shutil
    if os.path.exists("./test_chromadb"):
        shutil.rmtree("./test_chromadb")
    if os.path.exists("./test_memory"):
        shutil.rmtree("./test_memory")
    print("\n🧹 Test files cleaned up")

if __name__ == "__main__":
    main()

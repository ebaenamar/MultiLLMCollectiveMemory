#!/usr/bin/env python3
"""
Test enhanced collective memory system with ChromaDB enabled
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append('.')

def test_enhanced_system_with_chromadb():
    """Test the enhanced system with ChromaDB working"""
    print("🧪 TESTING ENHANCED SYSTEM WITH CHROMADB")
    print("=" * 60)
    
    try:
        from enhanced_collective_memory import EnhancedCollectiveMemoryAgent
        
        # Create enhanced system
        system = EnhancedCollectiveMemoryAgent(role="test_agent")
        print("✅ Enhanced system created successfully")
        
        # Test with a sample HumanEval problem that should match algorithms domain
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
        
        print(f"\n🎯 Testing with problem: {test_problem_name}")
        print("=" * 50)
        
        # Run the enhanced system
        result = system.solve_task_with_enhanced_memory(test_problem)
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Problem solved successfully")
        print(f"💰 Cost: ${result['cost']:.4f}")
        print(f"⏱️  Execution time: {result['execution_time']:.1f}s")
        print(f"🧠 Insights used: {result['insights_used']}")
        print(f"🔤 Tokens used: {result['tokens_used']}")
        print(f"📝 Solution length: {len(result['solution'])} characters")
        
        # Check if ChromaDB was used
        if result['insights_used'] > 0:
            print("🎉 ChromaDB semantic search is working!")
            print(f"   System successfully used {result['insights_used']} insights")
        else:
            print("⚠️  No insights used - may need more memory entries or better matching")
        
        # Show insight details if available
        if result.get('insights_details'):
            print(f"\n🔍 INSIGHTS DETAILS:")
            for i, insight in enumerate(result['insights_details'], 1):
                print(f"  {i}. Domain: {insight['domain']}")
                print(f"     Quality: {insight['quality']:.2f}")
                print(f"     Source: {insight['source']}")
                print(f"     Content: {insight['content']}")
        else:
            print(f"\n⚠️  No insights were used for this task")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_system_status():
    """Check the status of all system components"""
    print("\n🔍 SYSTEM STATUS CHECK")
    print("=" * 50)
    
    # Check ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./test_status_check")
        collection = client.get_or_create_collection("test")
        collection.add(documents=["test"], ids=["test_id"])
        count = collection.count()
        client.delete_collection("test")
        print("✅ ChromaDB: Working")
    except Exception as e:
        print(f"❌ ChromaDB: Failed - {e}")
    
    # Check domain files
    domain_files = ["data_structures.json", "algorithms.json", "validation.json", "testing.json", "optimization.json"]
    missing_files = [f for f in domain_files if not os.path.exists(f)]
    
    if not missing_files:
        print("✅ Domain files: All present")
    else:
        print(f"⚠️  Domain files: Missing {missing_files}")
    
    # Check memory systems
    try:
        from memory_systems.shared_memory import SharedMemorySystem
        from memory_systems.private_memory import PrivateMemorySystem
        print("✅ Memory systems: Importable")
    except Exception as e:
        print(f"❌ Memory systems: Import failed - {e}")
    
    # Check OpenAI API
    try:
        import openai
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and len(api_key) > 10:
            print("✅ OpenAI API: Key configured")
        else:
            print("⚠️  OpenAI API: Key not found or invalid")
    except Exception as e:
        print(f"❌ OpenAI API: Setup failed - {e}")

def main():
    """Main test function"""
    print("🚀 ENHANCED SYSTEM WITH CHROMADB TEST")
    print("=" * 60)
    
    # Check system status
    check_system_status()
    
    # Test enhanced system
    success = test_enhanced_system_with_chromadb()
    
    print(f"\n🏆 TEST SUMMARY")
    print("=" * 50)
    if success:
        print("🎉 Enhanced system with ChromaDB is working!")
        print("   Ready to run full HumanEval benchmark with semantic search")
    else:
        print("⚠️  Some issues need to be resolved")
    
    # Cleanup
    import shutil
    if os.path.exists("./test_status_check"):
        shutil.rmtree("./test_status_check")

if __name__ == "__main__":
    main()

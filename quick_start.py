#!/usr/bin/env python3
"""
Quick start script for Multi-LLM Collective Memory Benchmark.
"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Set up the environment for running experiments."""
    print("🚀 Multi-LLM Collective Memory Benchmark - Quick Start")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        
        # Copy .env.example to .env
        with open(".env.example", "r") as f:
            env_content = f.read()
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ .env file created. Please edit it with your API keys.")
        print("   Especially set your OPENAI_API_KEY")
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "results",
        "memory_data", 
        "logs",
        "analysis_output"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")

def run_demo():
    """Run a quick demo of the system."""
    print("\n🧪 Running Quick Demo...")
    
    try:
        # Import after environment setup
        from experiments.run_benchmark import BenchmarkRunner, BenchmarkConfiguration
        
        # Create a minimal demo configuration
        demo_config = {
            "experiment_id": "quick_demo",
            "task_description": "Design a simple traffic light optimization system with basic sensors and timing algorithms.",
            "configurations": ["single_agent_baseline", "multi_agent_shared_memory"],
            "iterations": 1,
            "timeout_minutes": 5,
            "output_dir": "./results"
        }
        
        config = BenchmarkConfiguration(demo_config)
        runner = BenchmarkRunner(config)
        
        print("Running demo benchmark (this may take a few minutes)...")
        results = runner.run_benchmark()
        
        print(f"✅ Demo completed! Results saved to: {results.get('results_file', 'results/')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples."""
    print("\n📚 Usage Examples:")
    print("-" * 40)
    
    examples = [
        {
            "title": "1. Create default configuration",
            "command": "python experiments/run_benchmark.py --create-config"
        },
        {
            "title": "2. Run full benchmark",
            "command": "python experiments/run_benchmark.py --config benchmark_config.json"
        },
        {
            "title": "3. Analyze results",
            "command": "python evaluation/analyze_results.py --results results/benchmark_results_*.json --plots --report"
        },
        {
            "title": "4. Start with Docker",
            "command": "docker-compose up -d"
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(f"   {example['command']}")

def main():
    """Main quick start function."""
    print("Starting Multi-LLM Collective Memory Benchmark setup...\n")
    
    # Setup environment
    if not setup_environment():
        print("\n⚠️  Please configure your .env file before proceeding.")
        print("   Set your OPENAI_API_KEY and other configuration values.")
        return
    
    # Create directories
    create_directories()
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Run quick demo")
    print("2. Show usage examples") 
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            success = run_demo()
            if success:
                print("\n🎉 Demo completed successfully!")
                print("Check the results/ directory for output files.")
        elif choice == "2":
            show_usage_examples()
        elif choice == "3":
            print("👋 Goodbye!")
            return
        else:
            print("Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("For more information, check the README.md file.")
    print("For issues, please check the documentation or create an issue.")

if __name__ == "__main__":
    main()

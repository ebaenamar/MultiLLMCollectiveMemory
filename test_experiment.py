#!/usr/bin/env python3
"""
Simple test script to run actual experiments with OpenAI API.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def create_directories():
    """Create necessary directories for results."""
    directories = ['results', 'memory_data', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def get_traffic_control_prompt():
    """Get the main traffic control system design prompt."""
    return """
Design an intelligent traffic control system using sensors, edge computing, and AI-based prediction for a medium-sized city (population ~500,000). Your solution must address:

**System Requirements:**
1. Handle 200+ intersections across the city
2. Support real-time decision making with <100ms response time  
3. Achieve 20-30% reduction in average travel times
4. Integrate with existing city infrastructure
5. Ensure 99.5%+ system uptime

**Deliverables Required:**
1. **System Architecture**: Overall design, component integration, data flow
2. **Hardware Specifications**: Sensor types, deployment strategy, networking
3. **AI/ML Architecture**: Prediction models, training strategy, inference pipeline
4. **Implementation Plan**: Phased rollout, timeline, resource requirements
5. **Evaluation Framework**: Success metrics, monitoring, validation methodology

**Constraints:**
- Budget: $15-20M total investment
- Timeline: 36 months for full deployment
- Existing infrastructure: Legacy traffic signals, city network, operations center
- Regulatory: Must comply with traffic safety standards and data privacy laws

Provide a comprehensive solution that demonstrates deep technical understanding and practical implementation considerations.
"""

def call_openai_api(prompt, model="gpt-4", max_tokens=2000):
    """Make a call to OpenAI API."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert system architect and engineer with deep knowledge in traffic systems, IoT, machine learning, and urban infrastructure."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "content": None,
            "usage": None
        }

def run_single_agent_baseline():
    """Run single agent baseline experiment."""
    print("🤖 Running Single Agent Baseline...")
    
    prompt = get_traffic_control_prompt()
    start_time = time.time()
    
    result = call_openai_api(prompt)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    experiment_result = {
        "configuration": "single_agent_baseline",
        "timestamp": datetime.now().isoformat(),
        "execution_time": execution_time,
        "success": result["success"],
        "solution": result["content"] if result["success"] else None,
        "error": result.get("error"),
        "token_usage": result["usage"],
        "quality_metrics": {
            "solution_length": len(result["content"]) if result["content"] else 0,
            "estimated_completeness": estimate_completeness(result["content"]) if result["content"] else 0
        }
    }
    
    return experiment_result

def run_specialized_agent_test():
    """Run a test with specialized agents."""
    print("👥 Running Specialized Agents Test...")
    
    agents = {
        "system_architect": "As a System Architect, focus on the overall system design, architecture patterns, component integration, and technology stack for the traffic control system.",
        "sensor_expert": "As a Sensor Hardware Expert, focus on sensor technology selection, deployment topology, hardware specifications, and network architecture for the traffic control system.",
        "ml_engineer": "As an ML Engineer, focus on traffic prediction algorithms, model architecture, real-time inference requirements, and training strategies for the traffic control system."
    }
    
    results = {}
    total_tokens = 0
    start_time = time.time()
    
    base_prompt = get_traffic_control_prompt()
    
    for agent_name, agent_role in agents.items():
        print(f"  🔧 Running {agent_name}...")
        
        specialized_prompt = f"{agent_role}\n\n{base_prompt}"
        result = call_openai_api(specialized_prompt, max_tokens=1500)
        
        if result["success"]:
            total_tokens += result["usage"]["total_tokens"]
            results[agent_name] = {
                "content": result["content"],
                "token_usage": result["usage"]
            }
        else:
            results[agent_name] = {
                "error": result["error"],
                "content": None
            }
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Combine results
    combined_solution = "\n\n".join([
        f"## {agent.replace('_', ' ').title()} Response:\n{data['content']}" 
        for agent, data in results.items() 
        if data.get('content')
    ])
    
    experiment_result = {
        "configuration": "multi_agent_specialized",
        "timestamp": datetime.now().isoformat(),
        "execution_time": execution_time,
        "success": len([r for r in results.values() if r.get('content')]) > 0,
        "solution": combined_solution,
        "individual_results": results,
        "total_token_usage": total_tokens,
        "quality_metrics": {
            "solution_length": len(combined_solution),
            "estimated_completeness": estimate_completeness(combined_solution),
            "agent_contributions": len([r for r in results.values() if r.get('content')])
        }
    }
    
    return experiment_result

def estimate_completeness(solution_text):
    """Estimate solution completeness based on key terms."""
    if not solution_text:
        return 0
    
    key_terms = [
        "architecture", "sensor", "machine learning", "implementation", "evaluation",
        "traffic", "intersection", "real-time", "prediction", "deployment",
        "budget", "timeline", "infrastructure", "monitoring", "performance"
    ]
    
    text_lower = solution_text.lower()
    found_terms = sum(1 for term in key_terms if term in text_lower)
    
    return (found_terms / len(key_terms)) * 100

def analyze_results(results):
    """Analyze and compare experimental results."""
    print("\n📊 Analysis Results:")
    print("=" * 50)
    
    for result in results:
        config = result["configuration"]
        print(f"\n{config.upper()}:")
        print(f"  ✅ Success: {result['success']}")
        print(f"  ⏱️  Execution Time: {result['execution_time']:.2f}s")
        
        if result.get('token_usage'):
            tokens = result['token_usage']['total_tokens']
            print(f"  🎯 Token Usage: {tokens}")
        elif result.get('total_token_usage'):
            print(f"  🎯 Total Token Usage: {result['total_token_usage']}")
        
        if result.get('quality_metrics'):
            metrics = result['quality_metrics']
            print(f"  📝 Solution Length: {metrics['solution_length']} chars")
            print(f"  📋 Estimated Completeness: {metrics['estimated_completeness']:.1f}%")
            
            if 'agent_contributions' in metrics:
                print(f"  👥 Agent Contributions: {metrics['agent_contributions']}")

def save_results(results):
    """Save results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/experiment_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    return filename

def main():
    """Run the experimental tests."""
    print("🚀 Multi-LLM Collective Memory Benchmark - Test Run")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Create directories
    create_directories()
    
    # Run experiments
    results = []
    
    try:
        # Test 1: Single Agent Baseline
        result1 = run_single_agent_baseline()
        results.append(result1)
        
        print(f"✅ Single agent completed in {result1['execution_time']:.2f}s")
        
        # Test 2: Specialized Agents
        result2 = run_specialized_agent_test()
        results.append(result2)
        
        print(f"✅ Multi-agent completed in {result2['execution_time']:.2f}s")
        
        # Analyze results
        analyze_results(results)
        
        # Save results
        results_file = save_results(results)
        
        print("\n🎉 Experiment completed successfully!")
        print(f"Check {results_file} for detailed results")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Experiment interrupted by user")
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

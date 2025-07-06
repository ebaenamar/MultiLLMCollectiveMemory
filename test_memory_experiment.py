#!/usr/bin/env python3
"""
Test experiment with memory systems to demonstrate collective memory benefits.
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

class SimpleMemorySystem:
    """Simple in-memory storage for agent interactions."""
    
    def __init__(self):
        self.shared_memory = []
        self.private_memories = {}
    
    def add_to_shared_memory(self, agent_id, content, content_type="insight"):
        """Add content to shared memory."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "content": content,
            "type": content_type
        }
        self.shared_memory.append(entry)
        return entry
    
    def get_shared_memory(self, limit=10):
        """Get recent shared memory entries."""
        return self.shared_memory[-limit:] if self.shared_memory else []
    
    def add_to_private_memory(self, agent_id, content):
        """Add content to agent's private memory."""
        if agent_id not in self.private_memories:
            self.private_memories[agent_id] = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        self.private_memories[agent_id].append(entry)
        return entry
    
    def get_private_memory(self, agent_id, limit=5):
        """Get agent's private memory."""
        if agent_id not in self.private_memories:
            return []
        return self.private_memories[agent_id][-limit:]

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

def call_openai_api(prompt, model="gpt-4", max_tokens=1500):
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

def run_multi_agent_with_shared_memory():
    """Run multi-agent experiment with shared memory."""
    print("🧠 Running Multi-Agent with Shared Memory...")
    
    memory_system = SimpleMemorySystem()
    
    agents = [
        {
            "id": "system_architect",
            "role": "System Architect",
            "focus": "overall system design, architecture patterns, component integration, and technology stack"
        },
        {
            "id": "sensor_expert", 
            "role": "Sensor Hardware Expert",
            "focus": "sensor technology selection, deployment topology, hardware specifications, and network architecture"
        },
        {
            "id": "ml_engineer",
            "role": "ML Engineer", 
            "focus": "traffic prediction algorithms, model architecture, real-time inference requirements, and training strategies"
        }
    ]
    
    results = {}
    total_tokens = 0
    start_time = time.time()
    
    base_prompt = get_traffic_control_prompt()
    
    # Phase 1: Each agent works independently and shares insights
    print("  📝 Phase 1: Independent analysis and insight sharing...")
    
    for agent in agents:
        print(f"    🤖 {agent['role']} analyzing...")
        
        # Get shared memory context
        shared_context = ""
        shared_memories = memory_system.get_shared_memory()
        if shared_memories:
            shared_context = "\n\n**SHARED INSIGHTS FROM OTHER AGENTS:**\n"
            for memory in shared_memories:
                shared_context += f"- {memory['agent_id']}: {memory['content'][:200]}...\n"
        
        specialized_prompt = f"""As a {agent['role']}, focus on {agent['focus']} for the traffic control system.

{shared_context}

{base_prompt}

After your analysis, provide 2-3 key insights that would be valuable for other team members to know."""
        
        result = call_openai_api(specialized_prompt, max_tokens=1200)
        
        if result["success"]:
            total_tokens += result["usage"]["total_tokens"]
            results[agent["id"]] = {
                "content": result["content"],
                "token_usage": result["usage"],
                "phase": "independent"
            }
            
            # Extract and store key insights in shared memory
            insights = extract_key_insights(result["content"])
            for insight in insights:
                memory_system.add_to_shared_memory(agent["id"], insight, "insight")
            
            # Store full analysis in private memory
            memory_system.add_to_private_memory(agent["id"], result["content"])
            
        else:
            results[agent["id"]] = {
                "error": result["error"],
                "content": None,
                "phase": "independent"
            }
    
    # Phase 2: Collaborative refinement based on shared insights
    print("  🤝 Phase 2: Collaborative refinement...")
    
    for agent in agents:
        print(f"    🔄 {agent['role']} refining based on team insights...")
        
        # Get all shared insights
        shared_memories = memory_system.get_shared_memory()
        shared_context = "\n\n**TEAM INSIGHTS:**\n"
        for memory in shared_memories:
            if memory['agent_id'] != agent['id']:  # Don't include own insights
                shared_context += f"- {memory['agent_id']}: {memory['content']}\n"
        
        # Get own previous work
        private_memories = memory_system.get_private_memory(agent["id"])
        previous_work = private_memories[-1]["content"] if private_memories else ""
        
        refinement_prompt = f"""As a {agent['role']}, you previously analyzed the traffic control system.

**YOUR PREVIOUS ANALYSIS:**
{previous_work[:500]}...

{shared_context}

Based on the insights from your teammates, refine and enhance your analysis. Focus on:
1. How your component integrates with others' designs
2. Addressing any gaps or conflicts identified
3. Leveraging synergies with other components

Provide an enhanced solution that builds on team collaboration."""
        
        result = call_openai_api(refinement_prompt, max_tokens=1000)
        
        if result["success"]:
            total_tokens += result["usage"]["total_tokens"]
            results[agent["id"] + "_refined"] = {
                "content": result["content"],
                "token_usage": result["usage"],
                "phase": "collaborative"
            }
            
            # Store refined insights
            insights = extract_key_insights(result["content"])
            for insight in insights:
                memory_system.add_to_shared_memory(agent["id"], f"[REFINED] {insight}", "refined_insight")
        else:
            results[agent["id"] + "_refined"] = {
                "error": result["error"],
                "content": None,
                "phase": "collaborative"
            }
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Combine all results
    all_content = []
    for key, result in results.items():
        if result.get('content'):
            phase = result.get('phase', 'unknown')
            agent_name = key.replace('_refined', '').replace('_', ' ').title()
            all_content.append(f"## {agent_name} ({phase.title()} Phase):\n{result['content']}")
    
    combined_solution = "\n\n".join(all_content)
    
    experiment_result = {
        "configuration": "multi_agent_shared_memory",
        "timestamp": datetime.now().isoformat(),
        "execution_time": execution_time,
        "success": len([r for r in results.values() if r.get('content')]) > 0,
        "solution": combined_solution,
        "individual_results": results,
        "total_token_usage": total_tokens,
        "memory_interactions": len(memory_system.shared_memory),
        "quality_metrics": {
            "solution_length": len(combined_solution),
            "estimated_completeness": estimate_completeness(combined_solution),
            "agent_contributions": len([r for r in results.values() if r.get('content')]),
            "collaboration_rounds": 2
        }
    }
    
    return experiment_result

def extract_key_insights(content):
    """Extract key insights from agent content (simplified)."""
    # Simple heuristic: look for bullet points or numbered lists
    insights = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if (line.startswith('- ') or line.startswith('* ') or 
            any(line.startswith(f'{i}.') for i in range(1, 10))):
            # Clean up the insight
            insight = line.lstrip('- *0123456789. ').strip()
            if len(insight) > 20 and len(insight) < 200:  # Reasonable length
                insights.append(insight)
    
    # If no structured insights found, extract first few sentences
    if not insights and content:
        sentences = content.split('. ')
        for sentence in sentences[:3]:
            if len(sentence) > 30:
                insights.append(sentence.strip() + '.')
    
    return insights[:3]  # Limit to 3 insights

def estimate_completeness(solution_text):
    """Estimate solution completeness based on key terms."""
    if not solution_text:
        return 0
    
    key_terms = [
        "architecture", "sensor", "machine learning", "implementation", "evaluation",
        "traffic", "intersection", "real-time", "prediction", "deployment",
        "budget", "timeline", "infrastructure", "monitoring", "performance",
        "integration", "collaboration", "synergy", "refinement"
    ]
    
    text_lower = solution_text.lower()
    found_terms = sum(1 for term in key_terms if term in text_lower)
    
    return (found_terms / len(key_terms)) * 100

def main():
    """Run the memory system experiment."""
    print("🧠 Multi-LLM Collective Memory - Memory System Test")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Create directories
    Path("results").mkdir(exist_ok=True)
    
    try:
        # Run memory experiment
        result = run_multi_agent_with_shared_memory()
        
        print(f"✅ Memory experiment completed in {result['execution_time']:.2f}s")
        print(f"🎯 Total tokens used: {result['total_token_usage']}")
        print(f"🧠 Memory interactions: {result['memory_interactions']}")
        print(f"📋 Solution completeness: {result['quality_metrics']['estimated_completeness']:.1f}%")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/memory_experiment_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        print("\n🎉 Memory experiment completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Experiment interrupted by user")
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

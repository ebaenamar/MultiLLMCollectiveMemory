#!/usr/bin/env python3
"""
Collective Memory vs MetaGPT Experiment
Compares YOUR collective memory system against MetaGPT baseline
"""

import os
import sys
import json
import time
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'human-eval'))
sys.path.append(os.path.dirname(__file__))

from human_eval.data import read_problems, write_jsonl
from memory_systems.shared_memory import SharedMemorySystem
from memory_systems.private_memory import PrivateMemorySystem, PrivateMemoryManager
from memory_systems.base_memory import MemoryEntry
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ExperimentResult:
    task_id: str
    approach: str  # 'single_agent', 'multi_agent_standard', 'multi_agent_collective_memory'
    completion: str
    execution_time: float
    total_tokens: int
    cost: float
    memory_insights_used: int
    memory_insights_stored: int
    quality_score: float

class CollectiveMemoryAgent:
    """Agent with access to collective memory system"""
    
    def __init__(self, role: str, client: openai.OpenAI, 
                 shared_memory: SharedMemorySystem, 
                 private_memory: PrivateMemorySystem):
        self.role = role
        self.client = client
        self.shared_memory = shared_memory
        self.private_memory = private_memory
        self.agent_id = f"{role}_agent"
        
        self.role_prompts = {
            "product_manager": """You are a Product Manager with access to collective memory from past projects. 
Your job is to:
1. Search collective memory for similar past requirements
2. Analyze the current requirements using past insights
3. Define clear functional specifications
4. Store valuable insights for future projects

Focus on WHAT needs to be built, leveraging past experience.""",
            
            "architect": """You are a Software Architect with access to collective memory from past designs.
Your job is to:
1. Search for similar architectural patterns from past projects
2. Design system architecture using proven patterns
3. Avoid past architectural mistakes documented in memory
4. Store new architectural insights for future use

Focus on HIGH-LEVEL design using collective knowledge.""",
            
            "engineer": """You are a Software Engineer with access to collective memory of past implementations.
Your job is to:
1. Search for similar implementation patterns from past projects
2. Reuse proven code patterns and solutions
3. Avoid past implementation pitfalls documented in memory
4. Store new implementation insights for future use

Focus on IMPLEMENTATION using collective experience.""",
            
            "qa_engineer": """You are a QA Engineer with access to collective memory of past testing strategies.
Your job is to:
1. Search for similar testing approaches from past projects
2. Apply proven testing patterns and edge cases
3. Learn from past quality issues documented in memory
4. Store new testing insights for future use

Focus on QUALITY using collective testing knowledge."""
        }
    
    def search_collective_memory(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search collective memory for relevant insights"""
        try:
            # Search shared memory using retrieve method
            shared_results = self.shared_memory.retrieve(query, self.agent_id, max_results)
            
            # Search private memory using retrieve method
            private_results = self.private_memory.retrieve(query, self.agent_id, max_results)
            
            # Combine and format results
            all_results = []
            
            for entry in shared_results:
                all_results.append({
                    "source": "shared",
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "relevance": entry.metadata.get("relevance_score", 0.5)
                })
            
            for entry in private_results:
                all_results.append({
                    "source": "private",
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "relevance": entry.metadata.get("relevance_score", 0.5)
                })
            
            # Sort by relevance
            all_results.sort(key=lambda x: x["relevance"], reverse=True)
            
            return all_results[:max_results]
            
        except Exception as e:
            print(f"Memory search error: {e}")
            return []
    
    def store_insight(self, insight: str, task_context: str, insight_type: str):
        """Store valuable insight in collective memory"""
        try:
            import uuid
            # Create memory entry with all required fields
            entry = MemoryEntry(
                id=str(uuid.uuid4()),
                content=insight,
                agent_id=self.agent_id,
                timestamp=datetime.now(),
                tags=[insight_type, self.role, "collective_memory"],
                metadata={
                    "task_context": task_context,
                    "insight_type": insight_type,
                    "role": self.role,
                    "timestamp": datetime.now().isoformat()
                },
                importance_score=0.5
            )
            
            # Store in both shared and private memory
            self.shared_memory.store(entry)
            self.private_memory.store(entry)
            
            return True
            
        except Exception as e:
            print(f"Memory storage error: {e}")
            return False
    
    def process_with_memory(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process task using collective memory"""
        
        if context is None:
            context = {}
        
        # 1. Search collective memory for relevant insights
        memory_query = f"{self.role} {task}"
        memory_insights = self.search_collective_memory(memory_query)
        
        # 2. Build context with memory insights
        memory_context = ""
        if memory_insights:
            memory_context = "\n\nRELEVANT INSIGHTS FROM COLLECTIVE MEMORY:\n"
            for i, insight in enumerate(memory_insights, 1):
                memory_context += f"{i}. [{insight['source']}] {insight['content']}\n"
        
        # 3. Build prompt based on role and context
        system_prompt = self.role_prompts[self.role]
        
        if self.role == "product_manager":
            user_prompt = f"""
Task: {task}

{memory_context}

Analyze this programming task and provide:
1. Clear problem understanding (using past insights)
2. Key requirements and constraints
3. Expected input/output behavior
4. Success criteria
5. NEW INSIGHTS to store for future projects

Be specific and leverage collective memory."""
            
        elif self.role == "architect":
            pm_analysis = context.get('product_manager', '')
            user_prompt = f"""
Task: {task}

Product Manager Analysis:
{pm_analysis}

{memory_context}

Design the solution architecture:
1. Overall approach using proven patterns from memory
2. Key data structures (reuse successful patterns)
3. Main functions/methods to implement
4. Error handling strategy (avoid past mistakes)
5. NEW ARCHITECTURAL INSIGHTS to store

Provide a clear technical design leveraging collective knowledge."""
            
        elif self.role == "engineer":
            pm_analysis = context.get('product_manager', '')
            arch_design = context.get('architect', '')
            user_prompt = f"""
Task: {task}

Product Manager Analysis:
{pm_analysis}

Architecture Design:
{arch_design}

{memory_context}

Implement the complete Python solution:
1. Use proven implementation patterns from memory
2. Follow the architectural design
3. Apply successful code patterns from past projects
4. Handle edge cases learned from collective experience
5. Identify NEW IMPLEMENTATION INSIGHTS to store

Provide ONLY the Python function implementation, no explanations."""
            
        elif self.role == "qa_engineer":
            pm_analysis = context.get('product_manager', '')
            arch_design = context.get('architect', '')
            engineer_code = context.get('engineer', '')
            user_prompt = f"""
Task: {task}

Product Manager Analysis:
{pm_analysis}

Architecture Design:
{arch_design}

Engineer Implementation:
{engineer_code}

{memory_context}

Review and improve the code using collective testing knowledge:
1. Apply proven testing patterns from memory
2. Check for issues documented in past projects
3. Verify it meets requirements using past criteria
4. Improve robustness based on collective experience
5. Identify NEW TESTING INSIGHTS to store

Provide the FINAL improved Python function, no explanations."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            # 4. Extract and store new insights
            insights_stored = 0
            if "NEW" in content.upper() and "INSIGHT" in content.upper():
                # Simple extraction of insights (could be more sophisticated)
                lines = content.split('\n')
                for line in lines:
                    if "insight" in line.lower() and len(line.strip()) > 20:
                        if self.store_insight(line.strip(), task, f"{self.role}_insight"):
                            insights_stored += 1
            
            return {
                "content": content,
                "tokens": tokens,
                "role": self.role,
                "memory_insights_used": len(memory_insights),
                "memory_insights_stored": insights_stored
            }
            
        except Exception as e:
            print(f"Error in {self.role}: {e}")
            return {
                "content": f"# Error in {self.role}: {str(e)}",
                "tokens": 0,
                "role": self.role,
                "memory_insights_used": 0,
                "memory_insights_stored": 0
            }

class CollectiveMemoryExperiment:
    """Main experiment comparing collective memory vs standard approaches"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize memory systems
        self.shared_memory = SharedMemorySystem("experiment_2025")
        self.private_memory_manager = PrivateMemoryManager("experiment_2025")
        
        # Initialize agents with collective memory
        self.memory_agents = {}
        for role in ["product_manager", "architect", "engineer", "qa_engineer"]:
            private_mem = self.private_memory_manager.get_agent_memory(f"{role}_agent")
            self.memory_agents[role] = CollectiveMemoryAgent(
                role, self.client, self.shared_memory, private_mem
            )
        
        self.results = []
    
    def run_single_agent(self, task_id: str, prompt: str) -> ExperimentResult:
        """Baseline: Single agent without memory"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer. Implement the requested function correctly and efficiently."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            completion = response.choices[0].message.content
            tokens = response.usage.total_tokens
            cost = self.calculate_cost(tokens)
            
        except Exception as e:
            print(f"Error in single agent for {task_id}: {e}")
            completion = f"# Error: {str(e)}"
            tokens = 0
            cost = 0
        
        execution_time = time.time() - start_time
        
        return ExperimentResult(
            task_id=task_id,
            approach="single_agent",
            completion=completion,
            execution_time=execution_time,
            total_tokens=tokens,
            cost=cost,
            memory_insights_used=0,
            memory_insights_stored=0,
            quality_score=0.0  # Will be calculated later
        )
    
    def run_multi_agent_standard(self, task_id: str, prompt: str) -> ExperimentResult:
        """MetaGPT-style multi-agent without collective memory"""
        start_time = time.time()
        total_tokens = 0
        context = {}
        
        roles_sequence = ["product_manager", "architect", "engineer", "qa_engineer"]
        
        for role in roles_sequence:
            print(f"    Running {role} (standard)...")
            
            # Standard role processing without memory
            try:
                if role == "product_manager":
                    system_prompt = "You are a Product Manager. Analyze requirements and define specifications."
                    user_prompt = f"Task: {prompt}\n\nProvide clear requirements analysis."
                    
                elif role == "architect":
                    system_prompt = "You are a Software Architect. Design system architecture."
                    user_prompt = f"Task: {prompt}\n\nPM Analysis: {context.get('product_manager', '')}\n\nProvide technical design."
                    
                elif role == "engineer":
                    system_prompt = "You are a Software Engineer. Implement the solution."
                    user_prompt = f"Task: {prompt}\n\nArchitecture: {context.get('architect', '')}\n\nImplement Python function."
                    
                elif role == "qa_engineer":
                    system_prompt = "You are a QA Engineer. Review and improve code quality."
                    user_prompt = f"Task: {prompt}\n\nCode: {context.get('engineer', '')}\n\nProvide final improved code."
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                
                context[role] = response.choices[0].message.content
                total_tokens += response.usage.total_tokens
                
            except Exception as e:
                print(f"Error in {role}: {e}")
                context[role] = f"# Error: {str(e)}"
            
            time.sleep(0.5)  # Rate limiting
        
        completion = context.get("qa_engineer", context.get("engineer", "# No completion"))
        execution_time = time.time() - start_time
        cost = self.calculate_cost(total_tokens)
        
        return ExperimentResult(
            task_id=task_id,
            approach="multi_agent_standard",
            completion=completion,
            execution_time=execution_time,
            total_tokens=total_tokens,
            cost=cost,
            memory_insights_used=0,
            memory_insights_stored=0,
            quality_score=0.0
        )
    
    def run_multi_agent_collective_memory(self, task_id: str, prompt: str) -> ExperimentResult:
        """YOUR CONTRIBUTION: Multi-agent with collective memory"""
        start_time = time.time()
        total_tokens = 0
        total_insights_used = 0
        total_insights_stored = 0
        context = {}
        
        roles_sequence = ["product_manager", "architect", "engineer", "qa_engineer"]
        
        for role in roles_sequence:
            print(f"    Running {role} (with collective memory)...")
            
            result = self.memory_agents[role].process_with_memory(prompt, context)
            context[role] = result["content"]
            total_tokens += result["tokens"]
            total_insights_used += result["memory_insights_used"]
            total_insights_stored += result["memory_insights_stored"]
            
            time.sleep(0.5)  # Rate limiting
        
        completion = context.get("qa_engineer", context.get("engineer", "# No completion"))
        execution_time = time.time() - start_time
        cost = self.calculate_cost(total_tokens)
        
        return ExperimentResult(
            task_id=task_id,
            approach="multi_agent_collective_memory",
            completion=completion,
            execution_time=execution_time,
            total_tokens=total_tokens,
            cost=cost,
            memory_insights_used=total_insights_used,
            memory_insights_stored=total_insights_stored,
            quality_score=0.0
        )
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on GPT-4 pricing"""
        input_tokens = tokens * 0.5
        output_tokens = tokens * 0.5
        cost = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
        return cost
    
    def run_experiment(self, num_problems: int = 15, random_seed: int = 42):
        """Run the complete experiment comparing all three approaches"""
        
        print("🧠 Collective Memory vs MetaGPT Experiment")
        print(f"📊 Testing {num_problems} problems from HumanEval")
        print("🔬 Comparing: Single Agent | Multi-Agent Standard | Multi-Agent + Collective Memory")
        print("=" * 80)
        
        # Load HumanEval problems
        problems = read_problems()
        
        # Select random subset
        random.seed(random_seed)
        selected_tasks = random.sample(list(problems.keys()), num_problems)
        
        for i, task_id in enumerate(selected_tasks, 1):
            problem = problems[task_id]
            prompt = problem["prompt"]
            
            print(f"\n[{i}/{num_problems}] Processing {task_id}")
            print(f"Problem: {problem['prompt'][:100]}...")
            
            # 1. Single Agent (Baseline)
            print("  🤖 Running Single Agent...")
            single_result = self.run_single_agent(task_id, prompt)
            self.results.append(single_result)
            
            # 2. Multi-Agent Standard (MetaGPT-style)
            print("  👥 Running Multi-Agent Standard...")
            standard_result = self.run_multi_agent_standard(task_id, prompt)
            self.results.append(standard_result)
            
            # 3. Multi-Agent with Collective Memory (YOUR CONTRIBUTION)
            print("  🧠 Running Multi-Agent + Collective Memory...")
            memory_result = self.run_multi_agent_collective_memory(task_id, prompt)
            self.results.append(memory_result)
            
            print(f"  ✅ Completed {task_id}")
            print(f"     Single:    {single_result.total_tokens:4d} tokens, ${single_result.cost:.4f}")
            print(f"     Standard:  {standard_result.total_tokens:4d} tokens, ${standard_result.cost:.4f}")
            print(f"     Memory:    {memory_result.total_tokens:4d} tokens, ${memory_result.cost:.4f}")
            print(f"     Memory insights: {memory_result.memory_insights_used} used, {memory_result.memory_insights_stored} stored")
        
        # Save results
        self.save_results()
        print(f"\n✅ Experiment completed! Results saved.")
    
    def save_results(self):
        """Save experiment results"""
        
        # Convert results to JSON-serializable format
        results_data = []
        for result in self.results:
            results_data.append({
                "task_id": result.task_id,
                "approach": result.approach,
                "completion": result.completion,
                "execution_time": result.execution_time,
                "total_tokens": result.total_tokens,
                "cost": result.cost,
                "memory_insights_used": result.memory_insights_used,
                "memory_insights_stored": result.memory_insights_stored,
                "quality_score": result.quality_score,
                "timestamp": datetime.now().isoformat()
            })
        
        # Save to file
        with open("collective_memory_results.json", "w") as f:
            json.dump(results_data, f, indent=2)

def main():
    """Main execution function"""
    
    # Verify API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Create and run experiment
    experiment = CollectiveMemoryExperiment()
    
    # Run with moderate number of problems
    experiment.run_experiment(num_problems=12, random_seed=42)

if __name__ == "__main__":
    main()

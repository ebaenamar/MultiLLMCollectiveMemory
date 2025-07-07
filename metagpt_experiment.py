#!/usr/bin/env python3
"""
MetaGPT Replication Experiment
Replicates the exact methodology from MetaGPT paper using HumanEval benchmark
"""

import os
import sys
import json
import time
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add human-eval to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'human-eval'))

from human_eval.data import read_problems, write_jsonl
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ExperimentResult:
    task_id: str
    approach: str  # 'single_agent', 'multi_agent'
    completion: str
    execution_time: float
    total_tokens: int
    cost: float
    roles_used: List[str]
    memory_shared: Dict[str, Any]

class MetaGPTAgent:
    """Individual agent with specific role in MetaGPT framework"""
    
    def __init__(self, role: str, client: openai.OpenAI):
        self.role = role
        self.client = client
        self.role_prompts = {
            "product_manager": """You are a Product Manager. Your job is to:
1. Analyze the user requirements
2. Define clear functional specifications
3. Identify key features and constraints
4. Create user stories and acceptance criteria

Focus on WHAT needs to be built, not HOW.""",
            
            "architect": """You are a Software Architect. Your job is to:
1. Review the product requirements
2. Design the overall system architecture
3. Define data structures and interfaces
4. Choose appropriate algorithms and patterns
5. Create technical specifications

Focus on the HIGH-LEVEL design and structure.""",
            
            "engineer": """You are a Software Engineer. Your job is to:
1. Review the architecture and requirements
2. Implement the actual code
3. Follow the architectural decisions
4. Write clean, functional code
5. Handle edge cases and error conditions

Focus on IMPLEMENTATION and making it work.""",
            
            "qa_engineer": """You are a QA Engineer. Your job is to:
1. Review the implemented code
2. Identify potential bugs and issues
3. Suggest improvements for robustness
4. Verify the code meets requirements
5. Ensure code quality and reliability

Focus on TESTING and QUALITY assurance."""
        }
    
    def process(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process task according to role"""
        
        if context is None:
            context = {}
            
        # Build prompt based on role and context
        system_prompt = self.role_prompts[self.role]
        
        if self.role == "product_manager":
            user_prompt = f"""
Task: {task}

Analyze this programming task and provide:
1. Clear problem understanding
2. Key requirements and constraints
3. Expected input/output behavior
4. Success criteria

Be specific and detailed."""
            
        elif self.role == "architect":
            pm_analysis = context.get('product_manager', '')
            user_prompt = f"""
Task: {task}

Product Manager Analysis:
{pm_analysis}

Design the solution architecture:
1. Overall approach and algorithm
2. Key data structures needed
3. Main functions/methods to implement
4. Error handling strategy

Provide a clear technical design."""
            
        elif self.role == "engineer":
            pm_analysis = context.get('product_manager', '')
            arch_design = context.get('architect', '')
            user_prompt = f"""
Task: {task}

Product Manager Analysis:
{pm_analysis}

Architecture Design:
{arch_design}

Implement the complete Python solution:
1. Write the actual function code
2. Follow the architectural design
3. Handle all edge cases
4. Make it clean and readable

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

Review and improve the code:
1. Check for bugs and issues
2. Verify it meets requirements
3. Improve robustness if needed
4. Ensure proper error handling

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
            
            return {
                "content": content,
                "tokens": tokens,
                "role": self.role
            }
            
        except Exception as e:
            print(f"Error in {self.role}: {e}")
            return {
                "content": f"# Error in {self.role}: {str(e)}",
                "tokens": 0,
                "role": self.role
            }

class MetaGPTExperiment:
    """Main experiment class replicating MetaGPT methodology"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.agents = {
            role: MetaGPTAgent(role, self.client) 
            for role in ["product_manager", "architect", "engineer", "qa_engineer"]
        }
        self.results = []
    
    def run_single_agent(self, task_id: str, prompt: str) -> ExperimentResult:
        """Run single agent approach (baseline)"""
        
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
            roles_used=["single_agent"],
            memory_shared={}
        )
    
    def run_multi_agent(self, task_id: str, prompt: str) -> ExperimentResult:
        """Run multi-agent approach following MetaGPT methodology"""
        
        start_time = time.time()
        total_tokens = 0
        memory = {}
        
        # Sequential execution following MetaGPT pipeline
        roles_sequence = ["product_manager", "architect", "engineer", "qa_engineer"]
        
        for role in roles_sequence:
            print(f"  Running {role}...")
            
            result = self.agents[role].process(prompt, memory)
            memory[role] = result["content"]
            total_tokens += result["tokens"]
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Final completion is from QA engineer (final refined code)
        completion = memory.get("qa_engineer", memory.get("engineer", "# No completion generated"))
        
        execution_time = time.time() - start_time
        cost = self.calculate_cost(total_tokens)
        
        return ExperimentResult(
            task_id=task_id,
            approach="multi_agent",
            completion=completion,
            execution_time=execution_time,
            total_tokens=total_tokens,
            cost=cost,
            roles_used=roles_sequence,
            memory_shared=memory
        )
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on GPT-4 pricing"""
        # GPT-4 pricing: $0.03 per 1K input tokens, $0.06 per 1K output tokens
        # Approximating 50/50 split
        input_tokens = tokens * 0.5
        output_tokens = tokens * 0.5
        
        cost = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
        return cost
    
    def extract_function_code(self, completion: str) -> str:
        """Extract just the function code from completion"""
        lines = completion.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip().startswith('```') and in_code_block:
                break
            elif in_code_block or line.strip().startswith('def '):
                code_lines.append(line)
            elif code_lines and line.strip() and not line.strip().startswith('#'):
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def run_experiment(self, num_problems: int = 20, random_seed: int = 42):
        """Run the complete experiment"""
        
        print("🚀 Starting MetaGPT Replication Experiment")
        print(f"📊 Testing {num_problems} problems from HumanEval")
        print("=" * 60)
        
        # Load HumanEval problems
        problems = read_problems()
        
        # Select random subset of problems
        random.seed(random_seed)
        selected_tasks = random.sample(list(problems.keys()), num_problems)
        
        for i, task_id in enumerate(selected_tasks, 1):
            problem = problems[task_id]
            prompt = problem["prompt"]
            
            print(f"\n[{i}/{num_problems}] Processing {task_id}")
            print(f"Problem: {problem['prompt'][:100]}...")
            
            # Run single agent
            print("  🤖 Running Single Agent...")
            single_result = self.run_single_agent(task_id, prompt)
            self.results.append(single_result)
            
            # Run multi-agent
            print("  👥 Running Multi-Agent...")
            multi_result = self.run_multi_agent(task_id, prompt)
            self.results.append(multi_result)
            
            print(f"  ✅ Completed {task_id}")
            print(f"     Single: {single_result.total_tokens} tokens, ${single_result.cost:.4f}")
            print(f"     Multi:  {multi_result.total_tokens} tokens, ${multi_result.cost:.4f}")
        
        # Save results
        self.save_results()
        print(f"\n✅ Experiment completed! Results saved to metagpt_results.json")
    
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
                "roles_used": result.roles_used,
                "memory_shared": result.memory_shared,
                "timestamp": datetime.now().isoformat()
            })
        
        # Save to file
        with open("metagpt_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        # Also save in HumanEval format for evaluation
        single_agent_samples = []
        multi_agent_samples = []
        
        for result in self.results:
            completion = self.extract_function_code(result.completion)
            
            sample = {
                "task_id": result.task_id,
                "completion": completion
            }
            
            if result.approach == "single_agent":
                single_agent_samples.append(sample)
            else:
                multi_agent_samples.append(sample)
        
        # Save samples for HumanEval evaluation
        write_jsonl("single_agent_samples.jsonl", single_agent_samples)
        write_jsonl("multi_agent_samples.jsonl", multi_agent_samples)

def main():
    """Main execution function"""
    
    # Verify API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Create and run experiment
    experiment = MetaGPTExperiment()
    
    # Start with smaller number for testing
    experiment.run_experiment(num_problems=10, random_seed=42)

if __name__ == "__main__":
    main()

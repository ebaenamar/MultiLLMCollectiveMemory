#!/usr/bin/env python3
"""
Single Agent System - Baseline for comparison
Simple single LLM approach without memory or collaboration
"""

import os
import time
import openai
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SingleAgentSystem:
    """Simple single agent system for baseline comparison"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4"
        
    def solve_problem(self, problem_description: str) -> Dict[str, Any]:
        """Solve a coding problem using single agent approach"""
        
        prompt = f"""You are an expert Python programmer. Solve the following coding problem:

{problem_description}

Requirements:
1. Provide a complete, working Python function
2. Include proper error handling
3. Add clear comments explaining the logic
4. Ensure the solution is efficient and follows best practices

Return only the Python code solution."""

        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            execution_time = time.time() - start_time
            
            # Extract solution
            solution = response.choices[0].message.content.strip()
            
            # Calculate cost (approximate)
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # GPT-4 pricing (approximate)
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
            
            return {
                "solution": solution,
                "execution_time": execution_time,
                "tokens_used": total_tokens,
                "cost": cost,
                "success": True
            }
            
        except Exception as e:
            return {
                "solution": "",
                "execution_time": time.time() - start_time,
                "tokens_used": 0,
                "cost": 0,
                "success": False,
                "error": str(e)
            }

def test_single_agent():
    """Test the single agent system"""
    system = SingleAgentSystem()
    
    test_problem = """
def sort_array(array):
    '''
    Given an array of non-negative integers, return a copy of the given array after sorting,
    you will sort the given array in ascending order if the sum of first index value and last index value is odd,
    or sort it in descending order if the sum of first index value and last index value is even.

    Note:
    * don't change the given array.

    Examples:
    * sort_array([]) => []
    * sort_array([5]) => [5]
    * sort_array([2, 4, 3, 0, 1, 5]) => [0, 1, 2, 3, 4, 5]
    * sort_array([2, 4, 3, 0, 1, 5, 6]) => [6, 5, 4, 3, 2, 1, 0]
    '''
    """
    
    print("🤖 Testing Single Agent System...")
    result = system.solve_problem(test_problem)
    
    if result['success']:
        print(f"✅ Solution generated successfully")
        print(f"💰 Cost: ${result['cost']:.4f}")
        print(f"⏱️  Time: {result['execution_time']:.2f}s")
        print(f"🔤 Tokens: {result['tokens_used']}")
        print(f"📝 Solution length: {len(result['solution'])} characters")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_single_agent()

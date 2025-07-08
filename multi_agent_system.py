#!/usr/bin/env python3
"""
Multi-Agent System without Memory - Baseline for comparison
Multiple specialized agents collaborate on problems without persistent memory
"""

import os
import time
import openai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MultiAgentSystem:
    """Multi-agent system without persistent memory for baseline comparison"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4"
        
        # Define agent roles
        self.agents = {
            "analyst": {
                "role": "Problem Analyst",
                "prompt": "You are a problem analyst. Break down coding problems into key requirements and constraints."
            },
            "architect": {
                "role": "Solution Architect", 
                "prompt": "You are a solution architect. Design the overall approach and algorithm for coding problems."
            },
            "coder": {
                "role": "Implementation Specialist",
                "prompt": "You are an implementation specialist. Write clean, efficient Python code based on requirements and design."
            },
            "tester": {
                "role": "Quality Assurance",
                "prompt": "You are a QA specialist. Review code for correctness, edge cases, and potential improvements."
            }
        }
    
    def get_agent_response(self, agent_key: str, user_message: str, context: str = "") -> str:
        """Get response from a specific agent"""
        agent = self.agents[agent_key]
        
        messages = [
            {"role": "system", "content": agent["prompt"]},
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Context from previous agents:\n{context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error from {agent['role']}: {str(e)}"
    
    def solve_problem_collaborative(self, problem_description: str) -> Dict[str, Any]:
        """Solve problem using collaborative multi-agent approach"""
        
        start_time = time.time()
        total_tokens = 0
        total_cost = 0
        
        try:
            # Step 1: Problem Analysis
            analysis_prompt = f"""Analyze this coding problem and identify:
1. Key requirements
2. Input/output specifications  
3. Edge cases to consider
4. Constraints and assumptions

Problem:
{problem_description}"""
            
            analysis = self.get_agent_response("analyst", analysis_prompt)
            
            # Step 2: Solution Architecture
            architecture_prompt = f"""Based on the problem analysis, design a solution approach:
1. Overall algorithm strategy
2. Key data structures needed
3. Step-by-step approach
4. Time/space complexity considerations

Problem Analysis:
{analysis}"""
            
            architecture = self.get_agent_response("architect", architecture_prompt, analysis)
            
            # Step 3: Implementation
            implementation_prompt = f"""Implement the solution in Python based on the analysis and architecture:
1. Write complete, working Python code
2. Include proper error handling
3. Add clear comments
4. Follow best practices

Return only the Python code solution.

Architecture:
{architecture}"""
            
            implementation = self.get_agent_response("coder", implementation_prompt, 
                                                   f"Analysis: {analysis}\nArchitecture: {architecture}")
            
            # Step 4: Quality Review
            review_prompt = f"""Review this implementation for:
1. Correctness and logic
2. Edge case handling
3. Code quality and efficiency
4. Potential improvements

If issues are found, provide the corrected code. Otherwise, confirm the solution is good.

Implementation:
{implementation}"""
            
            review = self.get_agent_response("tester", review_prompt,
                                           f"Analysis: {analysis}\nArchitecture: {architecture}\nImplementation: {implementation}")
            
            # Extract final solution (prefer reviewed version if it contains code)
            if "def " in review and len(review) > len(implementation) * 0.5:
                final_solution = review
            else:
                final_solution = implementation
            
            execution_time = time.time() - start_time
            
            # Estimate tokens and cost (4 API calls)
            estimated_tokens = len(problem_description + analysis + architecture + implementation + review) // 3
            estimated_cost = (estimated_tokens * 0.03 + estimated_tokens * 0.06) / 1000
            
            return {
                "solution": final_solution,
                "execution_time": execution_time,
                "tokens_used": estimated_tokens,
                "cost": estimated_cost,
                "success": True,
                "collaboration_details": {
                    "analysis": analysis[:200] + "...",
                    "architecture": architecture[:200] + "...", 
                    "review": review[:200] + "..."
                }
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

def test_multi_agent():
    """Test the multi-agent system"""
    system = MultiAgentSystem()
    
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
    
    print("👥 Testing Multi-Agent System (no memory)...")
    result = system.solve_problem_collaborative(test_problem)
    
    if result['success']:
        print(f"✅ Solution generated successfully")
        print(f"💰 Cost: ${result['cost']:.4f}")
        print(f"⏱️  Time: {result['execution_time']:.2f}s")
        print(f"🔤 Tokens: {result['tokens_used']}")
        print(f"📝 Solution length: {len(result['solution'])} characters")
        print(f"🤝 Collaboration: Analysis, Architecture, Implementation, Review")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_multi_agent()

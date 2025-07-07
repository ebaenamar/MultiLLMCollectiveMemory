#!/usr/bin/env python3
"""
Improved Multi-LLM Collective Memory Experiment
- Statistical rigor with multiple test cases
- LLM-as-a-judge evaluation
- Confidence intervals and significance testing
"""

import os
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any
import openai
from dotenv import load_dotenv
import numpy as np
from scipy import stats

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class ImprovedExperimentRunner:
    def __init__(self):
        self.client = openai.OpenAI()
        self.test_problems = self.generate_test_problems()
        self.results = []
        
    def generate_test_problems(self) -> List[Dict[str, str]]:
        """Generate 10 diverse test problems for robust evaluation"""
        problems = [
            {
                "id": 1,
                "domain": "traffic_control",
                "title": "Smart Traffic System Design",
                "prompt": "Design an intelligent traffic control system for a medium-sized city (500,000 residents, 200+ intersections, $15-20M budget). Include sensor networks, data processing, ML algorithms, and integration with existing infrastructure."
            },
            {
                "id": 2,
                "domain": "healthcare",
                "title": "Hospital Resource Management",
                "prompt": "Design a comprehensive hospital resource management system for a 500-bed hospital. Include patient flow optimization, staff scheduling, equipment tracking, and emergency response protocols. Budget: $5-8M."
            },
            {
                "id": 3,
                "domain": "education",
                "title": "Adaptive Learning Platform",
                "prompt": "Create an AI-powered adaptive learning platform for K-12 education serving 50,000 students. Include personalized curriculum, progress tracking, teacher analytics, and parent engagement tools. Budget: $3-5M."
            },
            {
                "id": 4,
                "domain": "logistics",
                "title": "Supply Chain Optimization",
                "prompt": "Design a supply chain optimization system for a retail company with 1000+ stores. Include demand forecasting, inventory management, distribution optimization, and supplier coordination. Budget: $10-15M."
            },
            {
                "id": 5,
                "domain": "energy",
                "title": "Smart Grid Management",
                "prompt": "Develop a smart grid management system for a city of 300,000 residents. Include renewable energy integration, demand response, outage prediction, and consumer engagement. Budget: $20-30M."
            },
            {
                "id": 6,
                "domain": "finance",
                "title": "Fraud Detection System",
                "prompt": "Create a real-time fraud detection system for a bank processing 1M+ transactions daily. Include ML models, risk scoring, alert management, and regulatory compliance. Budget: $8-12M."
            },
            {
                "id": 7,
                "domain": "manufacturing",
                "title": "Predictive Maintenance Platform",
                "prompt": "Design a predictive maintenance platform for a manufacturing facility with 500+ machines. Include sensor integration, failure prediction, maintenance scheduling, and cost optimization. Budget: $4-6M."
            },
            {
                "id": 8,
                "domain": "agriculture",
                "title": "Precision Agriculture System",
                "prompt": "Develop a precision agriculture system for farms covering 100,000 acres. Include crop monitoring, irrigation optimization, pest detection, and yield prediction. Budget: $6-10M."
            },
            {
                "id": 9,
                "domain": "transportation",
                "title": "Autonomous Fleet Management",
                "prompt": "Create an autonomous vehicle fleet management system for 1000+ vehicles. Include route optimization, maintenance scheduling, safety monitoring, and passenger experience. Budget: $25-35M."
            },
            {
                "id": 10,
                "domain": "cybersecurity",
                "title": "Enterprise Security Platform",
                "prompt": "Design a comprehensive cybersecurity platform for an enterprise with 10,000+ employees. Include threat detection, incident response, compliance monitoring, and user behavior analytics. Budget: $12-18M."
            }
        ]
        return problems

    def run_single_agent_experiment(self, problem: Dict[str, str]) -> Dict[str, Any]:
        """Run single agent experiment on one problem"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert consultant capable of designing comprehensive technical solutions across multiple domains."},
                    {"role": "user", "content": problem["prompt"]}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            end_time = time.time()
            solution = response.choices[0].message.content
            
            return {
                "approach": "single_agent",
                "problem_id": problem["id"],
                "domain": problem["domain"],
                "solution": solution,
                "execution_time": end_time - start_time,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "cost": self.calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
            }
        except Exception as e:
            print(f"Error in single agent experiment: {e}")
            return None

    def run_multi_agent_experiment(self, problem: Dict[str, str], use_memory: bool = False) -> Dict[str, Any]:
        """Run multi-agent experiment with optional memory"""
        start_time = time.time()
        
        # Define specialized agents
        agents = {
            "architect": "You are a System Architect expert specializing in overall system design, integration, and technical architecture.",
            "technical": "You are a Technical Specialist expert in implementation details, technology selection, and technical feasibility.",
            "business": "You are a Business Analyst expert in requirements analysis, cost-benefit analysis, and stakeholder management."
        }
        
        shared_memory = [] if use_memory else None
        agent_responses = {}
        total_tokens = 0
        total_cost = 0.0
        
        # Phase 1: Independent analysis
        for agent_name, agent_role in agents.items():
            try:
                messages = [
                    {"role": "system", "content": agent_role},
                    {"role": "user", "content": f"Analyze this problem from your expertise perspective:\n\n{problem['prompt']}"}
                ]
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                agent_response = response.choices[0].message.content
                agent_responses[agent_name] = agent_response
                total_tokens += response.usage.total_tokens
                total_cost += self.calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
                
                # Add to shared memory if enabled
                if use_memory:
                    key_insights = self.extract_key_insights(agent_response, agent_name)
                    shared_memory.extend(key_insights)
                    
            except Exception as e:
                print(f"Error in {agent_name} agent: {e}")
                agent_responses[agent_name] = f"Error: {str(e)}"
        
        # Phase 2: Collaborative synthesis
        if use_memory and shared_memory:
            memory_context = "\n".join([f"- {insight}" for insight in shared_memory])
            synthesis_prompt = f"""
Based on the shared insights from the team:

{memory_context}

And the individual analyses, create a comprehensive integrated solution for:
{problem['prompt']}

Synthesize the best ideas from all perspectives into a cohesive solution.
"""
        else:
            # Simple combination without memory
            all_analyses = "\n\n".join([f"{name.upper()} ANALYSIS:\n{response}" 
                                      for name, response in agent_responses.items()])
            synthesis_prompt = f"""
Based on these expert analyses:

{all_analyses}

Create a comprehensive integrated solution for:
{problem['prompt']}
"""
        
        try:
            synthesis_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior consultant who synthesizes expert input into comprehensive solutions."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            final_solution = synthesis_response.choices[0].message.content
            total_tokens += synthesis_response.usage.total_tokens
            total_cost += self.calculate_cost(synthesis_response.usage.prompt_tokens, synthesis_response.usage.completion_tokens)
            
        except Exception as e:
            print(f"Error in synthesis: {e}")
            final_solution = f"Synthesis error: {str(e)}"
        
        end_time = time.time()
        
        return {
            "approach": "multi_agent_with_memory" if use_memory else "multi_agent_no_memory",
            "problem_id": problem["id"],
            "domain": problem["domain"],
            "solution": final_solution,
            "execution_time": end_time - start_time,
            "total_tokens": total_tokens,
            "cost": total_cost,
            "agent_responses": agent_responses,
            "shared_memory": shared_memory if use_memory else None,
            "memory_interactions": len(shared_memory) if shared_memory else 0
        }

    def extract_key_insights(self, response: str, agent_name: str) -> List[str]:
        """Extract key insights from agent response for shared memory"""
        try:
            extraction_prompt = f"""
Extract 2-3 key insights from this {agent_name} analysis that would be valuable for other team members:

{response}

Return only the key insights, one per line, starting with '-'.
"""
            
            extraction_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You extract key insights from technical analyses."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            insights_text = extraction_response.choices[0].message.content
            insights = [line.strip().lstrip('- ') for line in insights_text.split('\n') 
                       if line.strip() and line.strip().startswith('-')]
            
            return [f"{agent_name}: {insight}" for insight in insights[:3]]
            
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return []

    def evaluate_solution_with_llm_judge(self, solution: str, problem: Dict[str, str]) -> Dict[str, float]:
        """Evaluate solution using LLM-as-a-judge with multiple criteria"""
        
        evaluation_prompt = f"""
Evaluate this solution for the following problem:

PROBLEM: {problem['prompt']}

SOLUTION: {solution}

Rate the solution on the following criteria (scale 1-10):

1. COMPLETENESS: How thoroughly does the solution address all requirements?
2. TECHNICAL_FEASIBILITY: How realistic and implementable is the technical approach?
3. COST_EFFECTIVENESS: How well does the solution balance features with budget constraints?
4. SCALABILITY: How well would this solution scale and adapt to growth?
5. INNOVATION: How creative and innovative are the proposed approaches?

Provide your ratings in this exact format:
COMPLETENESS: X
TECHNICAL_FEASIBILITY: X
COST_EFFECTIVENESS: X
SCALABILITY: X
INNOVATION: X

Then provide a brief justification for each score.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert technical evaluator who provides objective assessments of solution quality."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            evaluation_text = response.choices[0].message.content
            scores = {}
            
            # Parse scores
            for line in evaluation_text.split('\n'):
                if ':' in line:
                    for criterion in ['COMPLETENESS', 'TECHNICAL_FEASIBILITY', 'COST_EFFECTIVENESS', 'SCALABILITY', 'INNOVATION']:
                        if line.strip().startswith(criterion):
                            try:
                                score = float(line.split(':')[1].strip())
                                scores[criterion.lower()] = score
                            except:
                                pass
            
            # Calculate overall score
            if scores:
                scores['overall'] = sum(scores.values()) / len(scores)
            
            return scores
            
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {"overall": 0.0}

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on GPT-4 pricing"""
        input_cost = input_tokens * 0.03 / 1000  # $0.03 per 1K input tokens
        output_cost = output_tokens * 0.06 / 1000  # $0.06 per 1K output tokens
        return input_cost + output_cost

    def run_comprehensive_experiment(self):
        """Run comprehensive experiment with statistical analysis"""
        print("Starting comprehensive multi-LLM experiment with 10 test cases...")
        
        all_results = []
        
        for i, problem in enumerate(self.test_problems, 1):
            print(f"\nRunning experiment {i}/10: {problem['title']}")
            
            # Run all three approaches
            single_result = self.run_single_agent_experiment(problem)
            multi_result = self.run_multi_agent_experiment(problem, use_memory=False)
            memory_result = self.run_multi_agent_experiment(problem, use_memory=True)
            
            # Evaluate solutions
            if single_result:
                single_result['evaluation'] = self.evaluate_solution_with_llm_judge(
                    single_result['solution'], problem)
            
            if multi_result:
                multi_result['evaluation'] = self.evaluate_solution_with_llm_judge(
                    multi_result['solution'], problem)
            
            if memory_result:
                memory_result['evaluation'] = self.evaluate_solution_with_llm_judge(
                    memory_result['solution'], problem)
            
            all_results.extend([single_result, multi_result, memory_result])
            
            # Save intermediate results
            self.save_results(all_results, f"intermediate_results_{i}.json")
            
            print(f"Completed {i}/10 experiments")
        
        # Perform statistical analysis
        self.perform_statistical_analysis(all_results)
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_results(all_results, f"comprehensive_results_{timestamp}.json")
        
        return all_results

    def perform_statistical_analysis(self, results: List[Dict[str, Any]]):
        """Perform comprehensive statistical analysis"""
        print("\n" + "="*50)
        print("STATISTICAL ANALYSIS")
        print("="*50)
        
        # Group results by approach
        single_agent = [r for r in results if r and r['approach'] == 'single_agent']
        multi_agent = [r for r in results if r and r['approach'] == 'multi_agent_no_memory']
        memory_agent = [r for r in results if r and r['approach'] == 'multi_agent_with_memory']
        
        # Extract metrics
        metrics = ['execution_time', 'cost', 'total_tokens']
        eval_metrics = ['completeness', 'technical_feasibility', 'cost_effectiveness', 'scalability', 'innovation', 'overall']
        
        for metric in metrics + eval_metrics:
            print(f"\n{metric.upper()} ANALYSIS:")
            
            if metric in metrics:
                single_values = [r[metric] for r in single_agent if metric in r]
                multi_values = [r[metric] for r in multi_agent if metric in r]
                memory_values = [r[metric] for r in memory_agent if metric in r]
            else:
                single_values = [r['evaluation'].get(metric, 0) for r in single_agent if 'evaluation' in r]
                multi_values = [r['evaluation'].get(metric, 0) for r in multi_agent if 'evaluation' in r]
                memory_values = [r['evaluation'].get(metric, 0) for r in memory_agent if 'evaluation' in r]
            
            if single_values and multi_values and memory_values:
                # Calculate statistics
                single_stats = self.calculate_statistics(single_values)
                multi_stats = self.calculate_statistics(multi_values)
                memory_stats = self.calculate_statistics(memory_values)
                
                print(f"Single Agent: {single_stats}")
                print(f"Multi Agent: {multi_stats}")
                print(f"Memory Agent: {memory_stats}")
                
                # Perform t-tests
                if len(single_values) > 1 and len(multi_values) > 1:
                    t_stat, p_value = stats.ttest_ind(single_values, multi_values)
                    print(f"Single vs Multi t-test: t={t_stat:.3f}, p={p_value:.3f}")
                
                if len(multi_values) > 1 and len(memory_values) > 1:
                    t_stat, p_value = stats.ttest_ind(multi_values, memory_values)
                    print(f"Multi vs Memory t-test: t={t_stat:.3f}, p={p_value:.3f}")

    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate descriptive statistics with confidence intervals"""
        if not values:
            return {}
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # 95% confidence interval
        if len(values) > 1:
            sem = std_dev / (len(values) ** 0.5)  # Standard error of mean
            ci_margin = 1.96 * sem  # 95% CI for normal distribution
            ci_lower = mean - ci_margin
            ci_upper = mean + ci_margin
        else:
            ci_lower = ci_upper = mean
        
        return {
            "mean": round(mean, 3),
            "std_dev": round(std_dev, 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "ci_lower": round(ci_lower, 3),
            "ci_upper": round(ci_upper, 3),
            "n": len(values)
        }

    def save_results(self, results: List[Dict[str, Any]], filename: str):
        """Save results to JSON file"""
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved to {filepath}")

if __name__ == "__main__":
    runner = ImprovedExperimentRunner()
    results = runner.run_comprehensive_experiment()
    print("\nComprehensive experiment completed!")

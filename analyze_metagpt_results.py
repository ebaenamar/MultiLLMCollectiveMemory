#!/usr/bin/env python3
"""
MetaGPT Results Analysis
Analyzes results using exact metrics from MetaGPT paper
"""

import json
import sys
import os
import subprocess
import tempfile
from typing import Dict, List, Any
import statistics
import matplotlib.pyplot as plt
import numpy as np

# Add human-eval to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'human-eval'))

from human_eval.data import read_problems

class MetaGPTAnalyzer:
    """Analyzer for MetaGPT experiment results"""
    
    def __init__(self, results_file: str = "metagpt_results.json"):
        self.results_file = results_file
        self.results = self.load_results()
        self.problems = read_problems()
    
    def load_results(self) -> List[Dict]:
        """Load experiment results"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Results file {self.results_file} not found")
            return []
    
    def evaluate_code_execution(self, task_id: str, completion: str) -> Dict[str, Any]:
        """Evaluate if code executes correctly (simplified version)"""
        
        if not completion.strip() or "Error:" in completion:
            return {
                "executable": False,
                "error": "No valid code generated",
                "score": 0.0
            }
        
        try:
            # Create a temporary file with the completion
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(completion)
                temp_file = f.name
            
            # Try to compile the code
            with open(temp_file, 'r') as f:
                code = f.read()
            
            try:
                compile(code, temp_file, 'exec')
                executable = True
                error = None
                score = 1.0
            except SyntaxError as e:
                executable = False
                error = f"Syntax Error: {str(e)}"
                score = 0.0
            except Exception as e:
                executable = False
                error = f"Compilation Error: {str(e)}"
                score = 0.0
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "executable": executable,
                "error": error,
                "score": score
            }
            
        except Exception as e:
            return {
                "executable": False,
                "error": f"Evaluation error: {str(e)}",
                "score": 0.0
            }
    
    def calculate_code_quality_metrics(self, completion: str) -> Dict[str, float]:
        """Calculate code quality metrics similar to MetaGPT paper"""
        
        if not completion.strip():
            return {
                "lines_of_code": 0,
                "complexity_score": 0.0,
                "completeness_score": 0.0
            }
        
        lines = [line.strip() for line in completion.split('\n') if line.strip()]
        code_lines = [line for line in lines if not line.startswith('#')]
        
        # Lines of code
        loc = len(code_lines)
        
        # Simple complexity score based on control structures
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
        complexity_count = sum(1 for line in code_lines for keyword in complexity_keywords if keyword in line)
        complexity_score = min(complexity_count / max(loc, 1) * 10, 10.0)
        
        # Completeness score based on function definition and return statement
        has_def = any('def ' in line for line in code_lines)
        has_return = any('return' in line for line in code_lines)
        has_docstring = any('"""' in line or "'''" in line for line in lines)
        
        completeness_score = 0.0
        if has_def:
            completeness_score += 4.0
        if has_return:
            completeness_score += 3.0
        if has_docstring:
            completeness_score += 1.0
        if loc > 3:
            completeness_score += 2.0
        
        return {
            "lines_of_code": loc,
            "complexity_score": complexity_score,
            "completeness_score": min(completeness_score, 10.0)
        }
    
    def analyze_results(self):
        """Perform comprehensive analysis following MetaGPT methodology"""
        
        print("🔍 MetaGPT Results Analysis")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Separate results by approach
        single_agent_results = [r for r in self.results if r['approach'] == 'single_agent']
        multi_agent_results = [r for r in self.results if r['approach'] == 'multi_agent']
        
        print(f"📊 Analyzing {len(single_agent_results)} single-agent and {len(multi_agent_results)} multi-agent results")
        
        # 1. Executability Analysis (Key MetaGPT metric)
        print("\n1️⃣ EXECUTABILITY ANALYSIS")
        print("-" * 30)
        
        single_exec_scores = []
        multi_exec_scores = []
        
        for result in single_agent_results:
            exec_result = self.evaluate_code_execution(result['task_id'], result['completion'])
            single_exec_scores.append(exec_result['score'])
        
        for result in multi_agent_results:
            exec_result = self.evaluate_code_execution(result['task_id'], result['completion'])
            multi_exec_scores.append(exec_result['score'])
        
        single_exec_avg = statistics.mean(single_exec_scores) if single_exec_scores else 0
        multi_exec_avg = statistics.mean(multi_exec_scores) if multi_exec_scores else 0
        
        print(f"Single Agent Executability: {single_exec_avg:.3f}/1.000")
        print(f"Multi Agent Executability:  {multi_exec_avg:.3f}/1.000")
        print(f"Improvement: {((multi_exec_avg - single_exec_avg) / max(single_exec_avg, 0.001) * 100):+.1f}%")
        
        # 2. Code Quality Analysis
        print("\n2️⃣ CODE QUALITY ANALYSIS")
        print("-" * 30)
        
        single_quality = []
        multi_quality = []
        
        for result in single_agent_results:
            quality = self.calculate_code_quality_metrics(result['completion'])
            single_quality.append(quality)
        
        for result in multi_agent_results:
            quality = self.calculate_code_quality_metrics(result['completion'])
            multi_quality.append(quality)
        
        # Average metrics
        single_completeness = statistics.mean([q['completeness_score'] for q in single_quality])
        multi_completeness = statistics.mean([q['completeness_score'] for q in multi_quality])
        
        single_complexity = statistics.mean([q['complexity_score'] for q in single_quality])
        multi_complexity = statistics.mean([q['complexity_score'] for q in multi_quality])
        
        single_loc = statistics.mean([q['lines_of_code'] for q in single_quality])
        multi_loc = statistics.mean([q['lines_of_code'] for q in multi_quality])
        
        print(f"Completeness Score:")
        print(f"  Single Agent: {single_completeness:.2f}/10.0")
        print(f"  Multi Agent:  {multi_completeness:.2f}/10.0")
        print(f"  Improvement: {((multi_completeness - single_completeness) / max(single_completeness, 0.1) * 100):+.1f}%")
        
        print(f"\nComplexity Score:")
        print(f"  Single Agent: {single_complexity:.2f}/10.0")
        print(f"  Multi Agent:  {multi_complexity:.2f}/10.0")
        
        print(f"\nAverage Lines of Code:")
        print(f"  Single Agent: {single_loc:.1f}")
        print(f"  Multi Agent:  {multi_loc:.1f}")
        
        # 3. Cost and Efficiency Analysis
        print("\n3️⃣ COST & EFFICIENCY ANALYSIS")
        print("-" * 30)
        
        single_tokens = [r['total_tokens'] for r in single_agent_results]
        multi_tokens = [r['total_tokens'] for r in multi_agent_results]
        
        single_costs = [r['cost'] for r in single_agent_results]
        multi_costs = [r['cost'] for r in multi_agent_results]
        
        single_times = [r['execution_time'] for r in single_agent_results]
        multi_times = [r['execution_time'] for r in multi_agent_results]
        
        print(f"Average Tokens:")
        print(f"  Single Agent: {statistics.mean(single_tokens):.0f}")
        print(f"  Multi Agent:  {statistics.mean(multi_tokens):.0f}")
        print(f"  Ratio: {statistics.mean(multi_tokens) / statistics.mean(single_tokens):.1f}x")
        
        print(f"\nAverage Cost:")
        print(f"  Single Agent: ${statistics.mean(single_costs):.4f}")
        print(f"  Multi Agent:  ${statistics.mean(multi_costs):.4f}")
        print(f"  Ratio: {statistics.mean(multi_costs) / statistics.mean(single_costs):.1f}x")
        
        print(f"\nAverage Execution Time:")
        print(f"  Single Agent: {statistics.mean(single_times):.1f}s")
        print(f"  Multi Agent:  {statistics.mean(multi_times):.1f}s")
        print(f"  Ratio: {statistics.mean(multi_times) / statistics.mean(single_times):.1f}x")
        
        # 4. Productivity Analysis (MetaGPT metric)
        print("\n4️⃣ PRODUCTIVITY ANALYSIS")
        print("-" * 30)
        
        # Tokens per line of code (lower is better)
        single_productivity = []
        multi_productivity = []
        
        for i, result in enumerate(single_agent_results):
            loc = single_quality[i]['lines_of_code']
            if loc > 0:
                productivity = result['total_tokens'] / loc
                single_productivity.append(productivity)
        
        for i, result in enumerate(multi_agent_results):
            loc = multi_quality[i]['lines_of_code']
            if loc > 0:
                productivity = result['total_tokens'] / loc
                multi_productivity.append(productivity)
        
        if single_productivity and multi_productivity:
            single_prod_avg = statistics.mean(single_productivity)
            multi_prod_avg = statistics.mean(multi_productivity)
            
            print(f"Tokens per Line of Code (lower is better):")
            print(f"  Single Agent: {single_prod_avg:.1f}")
            print(f"  Multi Agent:  {multi_prod_avg:.1f}")
            
            if multi_prod_avg < single_prod_avg:
                print(f"  ✅ Multi-Agent is {((single_prod_avg - multi_prod_avg) / single_prod_avg * 100):.1f}% more efficient")
            else:
                print(f"  ❌ Multi-Agent is {((multi_prod_avg - single_prod_avg) / single_prod_avg * 100):.1f}% less efficient")
        
        # 5. Summary and Conclusion
        print("\n5️⃣ SUMMARY & CONCLUSION")
        print("-" * 30)
        
        improvements = []
        if multi_exec_avg > single_exec_avg:
            improvements.append(f"Executability: +{((multi_exec_avg - single_exec_avg) / max(single_exec_avg, 0.001) * 100):.1f}%")
        
        if multi_completeness > single_completeness:
            improvements.append(f"Completeness: +{((multi_completeness - single_completeness) / max(single_completeness, 0.1) * 100):.1f}%")
        
        cost_ratio = statistics.mean(multi_costs) / statistics.mean(single_costs)
        
        print(f"🎯 Key Findings:")
        if improvements:
            print(f"  ✅ Multi-Agent improvements: {', '.join(improvements)}")
        else:
            print(f"  ❌ No significant improvements found")
        
        print(f"  💰 Cost increase: {cost_ratio:.1f}x ({((cost_ratio - 1) * 100):+.0f}%)")
        
        if multi_exec_avg > single_exec_avg and cost_ratio < 3.0:
            print(f"  🏆 CONCLUSION: Multi-Agent approach shows promise")
        elif multi_exec_avg > single_exec_avg:
            print(f"  ⚠️  CONCLUSION: Multi-Agent improves quality but at high cost")
        else:
            print(f"  ❌ CONCLUSION: Multi-Agent approach not justified for these tasks")
        
        # 6. Generate visualization
        self.create_visualizations(single_exec_scores, multi_exec_scores, 
                                 single_costs, multi_costs)
    
    def create_visualizations(self, single_exec, multi_exec, single_costs, multi_costs):
        """Create visualizations of results"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Executability comparison
        ax1.bar(['Single Agent', 'Multi Agent'], 
                [statistics.mean(single_exec), statistics.mean(multi_exec)],
                color=['#3498db', '#e74c3c'])
        ax1.set_ylabel('Executability Score')
        ax1.set_title('Code Executability Comparison')
        ax1.set_ylim(0, 1)
        
        # 2. Cost comparison
        ax2.bar(['Single Agent', 'Multi Agent'], 
                [statistics.mean(single_costs), statistics.mean(multi_costs)],
                color=['#3498db', '#e74c3c'])
        ax2.set_ylabel('Average Cost ($)')
        ax2.set_title('Cost Comparison')
        
        # 3. Executability distribution
        ax3.hist(single_exec, alpha=0.7, label='Single Agent', bins=5, color='#3498db')
        ax3.hist(multi_exec, alpha=0.7, label='Multi Agent', bins=5, color='#e74c3c')
        ax3.set_xlabel('Executability Score')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Executability Score Distribution')
        ax3.legend()
        
        # 4. Cost vs Executability scatter
        ax4.scatter(single_costs, single_exec, alpha=0.7, label='Single Agent', color='#3498db')
        ax4.scatter(multi_costs, multi_exec, alpha=0.7, label='Multi Agent', color='#e74c3c')
        ax4.set_xlabel('Cost ($)')
        ax4.set_ylabel('Executability Score')
        ax4.set_title('Cost vs Executability')
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig('metagpt_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n📊 Visualization saved as 'metagpt_analysis.png'")

def main():
    """Main analysis function"""
    
    analyzer = MetaGPTAnalyzer()
    analyzer.analyze_results()

if __name__ == "__main__":
    main()

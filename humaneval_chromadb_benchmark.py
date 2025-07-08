#!/usr/bin/env python3
"""
HumanEval ChromaDB Benchmark
Compares three approaches:
1. Single Agent (baseline)
2. Multi-Agent without memory
3. Enhanced Multi-Agent with ChromaDB memory
"""

import os
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime

# Import our systems
from single_agent_system import SingleAgentSystem
from multi_agent_system import MultiAgentSystem  
from enhanced_collective_memory import EnhancedCollectiveMemoryAgent

# Import HumanEval
from human_eval.data import read_problems
from human_eval.evaluation import evaluate_functional_correctness

def load_test_problems(limit: int = 20) -> List[Dict]:
    """Load a subset of HumanEval problems for testing"""
    problems = read_problems()
    
    # Select diverse problems for testing
    selected_keys = [
        "HumanEval/0",   # two_sum - arrays
        "HumanEval/1",   # separate_paren_groups - string processing
        "HumanEval/2",   # truncate_number - math
        "HumanEval/3",   # below_zero - logic
        "HumanEval/4",   # mean_absolute_deviation - statistics
        "HumanEval/5",   # intersperse - list manipulation
        "HumanEval/6",   # parse_nested_parens - parsing
        "HumanEval/7",   # filter_by_substring - filtering
        "HumanEval/8",   # sum_product - math operations
        "HumanEval/9",   # rolling_max - algorithms
        "HumanEval/10",  # make_palindrome - string algorithms
        "HumanEval/11",  # string_xor - bitwise operations
        "HumanEval/12",  # longest - string comparison
        "HumanEval/13",  # greatest_common_divisor - math
        "HumanEval/14",  # all_prefixes - string generation
        "HumanEval/15",  # string_sequence - sequences
        "HumanEval/16",  # count_distinct_characters - counting
        "HumanEval/17",  # parse_music - parsing
        "HumanEval/18",  # how_many_times - string search
        "HumanEval/19",  # sort_numbers - sorting
    ]
    
    return [{"task_id": key, **problems[key]} for key in selected_keys[:limit]]

def run_single_agent_baseline(problems: List[Dict]) -> Dict[str, Any]:
    """Run single agent baseline"""
    print("🤖 Running Single Agent Baseline...")
    
    system = SingleAgentSystem()
    results = []
    total_cost = 0
    total_time = 0
    
    for i, problem in enumerate(problems, 1):
        print(f"  Problem {i}/{len(problems)}: {problem['task_id']}")
        
        start_time = time.time()
        try:
            result = system.solve_problem(problem['prompt'])
            execution_time = time.time() - start_time
            
            results.append({
                "task_id": problem['task_id'],
                "solution": result.get('solution', ''),
                "execution_time": execution_time,
                "cost": result.get('cost', 0),
                "tokens": result.get('tokens_used', 0),
                "success": True
            })
            
            total_cost += result.get('cost', 0)
            total_time += execution_time
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "task_id": problem['task_id'],
                "solution": "",
                "execution_time": time.time() - start_time,
                "cost": 0,
                "tokens": 0,
                "success": False,
                "error": str(e)
            })
    
    return {
        "approach": "single_agent",
        "results": results,
        "summary": {
            "total_problems": len(problems),
            "successful": sum(1 for r in results if r['success']),
            "total_cost": total_cost,
            "total_time": total_time,
            "avg_cost": total_cost / len(problems),
            "avg_time": total_time / len(problems)
        }
    }

def run_multi_agent_baseline(problems: List[Dict]) -> Dict[str, Any]:
    """Run multi-agent without memory baseline"""
    print("👥 Running Multi-Agent Baseline (no memory)...")
    
    system = MultiAgentSystem()
    results = []
    total_cost = 0
    total_time = 0
    
    for i, problem in enumerate(problems, 1):
        print(f"  Problem {i}/{len(problems)}: {problem['task_id']}")
        
        start_time = time.time()
        try:
            result = system.solve_problem_collaborative(problem['prompt'])
            execution_time = time.time() - start_time
            
            results.append({
                "task_id": problem['task_id'],
                "solution": result.get('solution', ''),
                "execution_time": execution_time,
                "cost": result.get('cost', 0),
                "tokens": result.get('tokens_used', 0),
                "success": True
            })
            
            total_cost += result.get('cost', 0)
            total_time += execution_time
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "task_id": problem['task_id'],
                "solution": "",
                "execution_time": time.time() - start_time,
                "cost": 0,
                "tokens": 0,
                "success": False,
                "error": str(e)
            })
    
    return {
        "approach": "multi_agent_no_memory",
        "results": results,
        "summary": {
            "total_problems": len(problems),
            "successful": sum(1 for r in results if r['success']),
            "total_cost": total_cost,
            "total_time": total_time,
            "avg_cost": total_cost / len(problems),
            "avg_time": total_time / len(problems)
        }
    }

def run_enhanced_memory_system(problems: List[Dict]) -> Dict[str, Any]:
    """Run enhanced system with ChromaDB memory"""
    print("🧠 Running Enhanced System with ChromaDB Memory...")
    
    # Create enhanced agent
    agent = EnhancedCollectiveMemoryAgent("problem_solver")
    results = []
    total_cost = 0
    total_time = 0
    total_insights_used = 0
    total_insights_stored = 0
    
    for i, problem in enumerate(problems, 1):
        print(f"  Problem {i}/{len(problems)}: {problem['task_id']}")
        
        start_time = time.time()
        try:
            result = agent.solve_task_with_enhanced_memory(problem['prompt'])
            execution_time = time.time() - start_time
            
            insights_used = result.get('insights_used', 0)
            total_insights_used += insights_used
            
            results.append({
                "task_id": problem['task_id'],
                "solution": result.get('solution', ''),
                "execution_time": execution_time,
                "cost": result.get('cost', 0),
                "tokens": result.get('tokens_used', 0),
                "insights_used": insights_used,
                "insights_details": result.get('insights_details', []),
                "success": True
            })
            
            total_cost += result.get('cost', 0)
            total_time += execution_time
            
            print(f"    ✅ Used {insights_used} insights, Cost: ${result.get('cost', 0):.4f}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "task_id": problem['task_id'],
                "solution": "",
                "execution_time": time.time() - start_time,
                "cost": 0,
                "tokens": 0,
                "insights_used": 0,
                "success": False,
                "error": str(e)
            })
    
    return {
        "approach": "enhanced_chromadb_memory",
        "results": results,
        "summary": {
            "total_problems": len(problems),
            "successful": sum(1 for r in results if r['success']),
            "total_cost": total_cost,
            "total_time": total_time,
            "avg_cost": total_cost / len(problems),
            "avg_time": total_time / len(problems),
            "total_insights_used": total_insights_used,
            "avg_insights_per_problem": total_insights_used / len(problems)
        }
    }

def analyze_results(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze and compare results across approaches"""
    print("\n📊 ANALYZING RESULTS...")
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "comparison": {},
        "insights": []
    }
    
    # Extract metrics for each approach
    for result_set in all_results:
        approach = result_set['approach']
        summary = result_set['summary']
        
        analysis['comparison'][approach] = {
            "success_rate": summary['successful'] / summary['total_problems'],
            "avg_cost": summary['avg_cost'],
            "avg_time": summary['avg_time'],
            "total_cost": summary['total_cost'],
            "total_time": summary['total_time']
        }
        
        # Add memory-specific metrics
        if approach == "enhanced_chromadb_memory":
            analysis['comparison'][approach].update({
                "avg_insights_used": summary['avg_insights_per_problem'],
                "total_insights_used": summary['total_insights_used']
            })
    
    # Calculate improvements
    baseline = analysis['comparison']['single_agent']
    multi_agent = analysis['comparison']['multi_agent_no_memory']
    enhanced = analysis['comparison']['enhanced_chromadb_memory']
    
    # Cost efficiency analysis
    cost_vs_single = ((enhanced['avg_cost'] - baseline['avg_cost']) / baseline['avg_cost']) * 100
    cost_vs_multi = ((enhanced['avg_cost'] - multi_agent['avg_cost']) / multi_agent['avg_cost']) * 100
    
    # Time efficiency analysis  
    time_vs_single = ((enhanced['avg_time'] - baseline['avg_time']) / baseline['avg_time']) * 100
    time_vs_multi = ((enhanced['avg_time'] - multi_agent['avg_time']) / multi_agent['avg_time']) * 100
    
    analysis['insights'] = [
        f"Enhanced system uses {enhanced.get('avg_insights_used', 0):.1f} insights per problem on average",
        f"Cost vs Single Agent: {cost_vs_single:+.1f}%",
        f"Cost vs Multi-Agent: {cost_vs_multi:+.1f}%", 
        f"Time vs Single Agent: {time_vs_single:+.1f}%",
        f"Time vs Multi-Agent: {time_vs_multi:+.1f}%",
        f"Success rates: Single={baseline['success_rate']:.1%}, Multi={multi_agent['success_rate']:.1%}, Enhanced={enhanced['success_rate']:.1%}"
    ]
    
    return analysis

def save_results(all_results: List[Dict], analysis: Dict, filename: str = None):
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"humaneval_chromadb_benchmark_{timestamp}.json"
    
    output = {
        "benchmark_info": {
            "timestamp": datetime.now().isoformat(),
            "approaches_tested": len(all_results),
            "problems_per_approach": len(all_results[0]['results']) if all_results else 0
        },
        "results": all_results,
        "analysis": analysis
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"📁 Results saved to: {filename}")
    return filename

def print_summary(analysis: Dict):
    """Print summary of results"""
    print("\n" + "="*80)
    print("🏆 HUMANEVAL CHROMADB BENCHMARK RESULTS")
    print("="*80)
    
    comparison = analysis['comparison']
    
    print("\n📊 PERFORMANCE COMPARISON:")
    print("-" * 60)
    print(f"{'Approach':<25} {'Success Rate':<12} {'Avg Cost':<10} {'Avg Time':<10}")
    print("-" * 60)
    
    for approach, metrics in comparison.items():
        approach_name = approach.replace('_', ' ').title()
        print(f"{approach_name:<25} {metrics['success_rate']:<11.1%} ${metrics['avg_cost']:<9.4f} {metrics['avg_time']:<9.1f}s")
    
    print("\n🔍 KEY INSIGHTS:")
    print("-" * 40)
    for insight in analysis['insights']:
        print(f"• {insight}")
    
    # Memory utilization for enhanced system
    if 'enhanced_chromadb_memory' in comparison:
        enhanced = comparison['enhanced_chromadb_memory']
        if 'avg_insights_used' in enhanced:
            print(f"\n🧠 MEMORY UTILIZATION:")
            print(f"• Average insights used per problem: {enhanced['avg_insights_used']:.1f}")
            print(f"• Total insights utilized: {enhanced.get('total_insights_used', 0)}")

def main():
    """Main benchmark execution"""
    print("🚀 HUMANEVAL CHROMADB BENCHMARK")
    print("="*80)
    print("Comparing three approaches:")
    print("1. Single Agent (baseline)")
    print("2. Multi-Agent without memory") 
    print("3. Enhanced Multi-Agent with ChromaDB memory")
    print("="*80)
    
    # Load test problems
    print("\n📚 Loading HumanEval problems...")
    problems = load_test_problems(limit=10)  # Reduced for faster testing
    print(f"✅ Loaded {len(problems)} problems for testing")
    
    # Run all approaches
    all_results = []
    
    try:
        # 1. Single Agent Baseline
        single_results = run_single_agent_baseline(problems)
        all_results.append(single_results)
        
        # 2. Multi-Agent Baseline  
        multi_results = run_multi_agent_baseline(problems)
        all_results.append(multi_results)
        
        # 3. Enhanced ChromaDB System
        enhanced_results = run_enhanced_memory_system(problems)
        all_results.append(enhanced_results)
        
        # Analyze results
        analysis = analyze_results(all_results)
        
        # Save and display results
        filename = save_results(all_results, analysis)
        print_summary(analysis)
        
        print(f"\n✅ Benchmark completed successfully!")
        print(f"📁 Detailed results saved to: {filename}")
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

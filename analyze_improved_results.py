#!/usr/bin/env python3
"""
Analysis script for improved experiment results
"""

import json
import os
import statistics
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def load_latest_results():
    """Load the most recent comprehensive results"""
    results_dir = "results"
    if not os.path.exists(results_dir):
        print("No results directory found")
        return None
    
    # Find the latest comprehensive results file
    files = [f for f in os.listdir(results_dir) if f.startswith("comprehensive_results_")]
    if not files:
        print("No comprehensive results found")
        return None
    
    latest_file = max(files)
    filepath = os.path.join(results_dir, latest_file)
    
    with open(filepath, 'r') as f:
        results = json.load(f)
    
    print(f"Loaded results from: {filepath}")
    return results

def analyze_results(results):
    """Perform comprehensive analysis of results"""
    if not results:
        return
    
    # Group results by approach
    single_agent = [r for r in results if r and r['approach'] == 'single_agent']
    multi_agent = [r for r in results if r and r['approach'] == 'multi_agent_no_memory']
    memory_agent = [r for r in results if r and r['approach'] == 'multi_agent_with_memory']
    
    print("\n" + "="*60)
    print("COMPREHENSIVE EXPERIMENT ANALYSIS")
    print("="*60)
    
    print(f"\nSample sizes:")
    print(f"Single Agent: {len(single_agent)} experiments")
    print(f"Multi Agent (no memory): {len(multi_agent)} experiments")
    print(f"Multi Agent (with memory): {len(memory_agent)} experiments")
    
    # Performance Analysis
    print("\n" + "-"*40)
    print("PERFORMANCE METRICS ANALYSIS")
    print("-"*40)
    
    metrics = ['execution_time', 'cost', 'total_tokens']
    eval_metrics = ['completeness', 'technical_feasibility', 'cost_effectiveness', 'scalability', 'innovation', 'overall']
    
    results_summary = {}
    
    for metric in metrics + eval_metrics:
        print(f"\n{metric.upper()}:")
        
        if metric in metrics:
            single_values = [r[metric] for r in single_agent if metric in r]
            multi_values = [r[metric] for r in multi_agent if metric in r]
            memory_values = [r[metric] for r in memory_agent if metric in r]
        else:
            single_values = [r['evaluation'].get(metric, 0) for r in single_agent if 'evaluation' in r and r['evaluation']]
            multi_values = [r['evaluation'].get(metric, 0) for r in multi_agent if 'evaluation' in r and r['evaluation']]
            memory_values = [r['evaluation'].get(metric, 0) for r in memory_agent if 'evaluation' in r and r['evaluation']]
        
        if single_values and multi_values and memory_values:
            single_stats = calculate_stats(single_values)
            multi_stats = calculate_stats(multi_values)
            memory_stats = calculate_stats(memory_values)
            
            print(f"  Single Agent: μ={single_stats['mean']:.3f} ±{single_stats['std']:.3f} (CI: {single_stats['ci_lower']:.3f}-{single_stats['ci_upper']:.3f})")
            print(f"  Multi Agent:  μ={multi_stats['mean']:.3f} ±{multi_stats['std']:.3f} (CI: {multi_stats['ci_lower']:.3f}-{multi_stats['ci_upper']:.3f})")
            print(f"  Memory Agent: μ={memory_stats['mean']:.3f} ±{memory_stats['std']:.3f} (CI: {memory_stats['ci_lower']:.3f}-{memory_stats['ci_upper']:.3f})")
            
            # Calculate improvements
            if single_stats['mean'] > 0:
                multi_improvement = ((multi_stats['mean'] - single_stats['mean']) / single_stats['mean']) * 100
                memory_improvement = ((memory_stats['mean'] - single_stats['mean']) / single_stats['mean']) * 100
                memory_vs_multi = ((memory_stats['mean'] - multi_stats['mean']) / multi_stats['mean']) * 100
                
                print(f"  Improvements: Multi vs Single: {multi_improvement:+.1f}%, Memory vs Single: {memory_improvement:+.1f}%, Memory vs Multi: {memory_vs_multi:+.1f}%")
            
            results_summary[metric] = {
                'single': single_stats,
                'multi': multi_stats,
                'memory': memory_stats
            }
    
    # Domain Analysis
    print("\n" + "-"*40)
    print("DOMAIN-SPECIFIC ANALYSIS")
    print("-"*40)
    
    domains = set(r['domain'] for r in results if r and 'domain' in r)
    for domain in sorted(domains):
        print(f"\n{domain.upper()}:")
        domain_results = [r for r in results if r and r.get('domain') == domain]
        
        domain_single = [r for r in domain_results if r['approach'] == 'single_agent']
        domain_multi = [r for r in domain_results if r['approach'] == 'multi_agent_no_memory']
        domain_memory = [r for r in domain_results if r['approach'] == 'multi_agent_with_memory']
        
        if domain_single and domain_multi and domain_memory:
            single_score = domain_single[0]['evaluation'].get('overall', 0) if 'evaluation' in domain_single[0] else 0
            multi_score = domain_multi[0]['evaluation'].get('overall', 0) if 'evaluation' in domain_multi[0] else 0
            memory_score = domain_memory[0]['evaluation'].get('overall', 0) if 'evaluation' in domain_memory[0] else 0
            
            print(f"  Single: {single_score:.2f}, Multi: {multi_score:.2f}, Memory: {memory_score:.2f}")
            if single_score > 0:
                print(f"  Improvement: Multi: {((multi_score-single_score)/single_score)*100:+.1f}%, Memory: {((memory_score-single_score)/single_score)*100:+.1f}%")
    
    # Cost-Benefit Analysis
    print("\n" + "-"*40)
    print("COST-BENEFIT ANALYSIS")
    print("-"*40)
    
    if 'cost' in results_summary and 'overall' in results_summary:
        single_cost = results_summary['cost']['single']['mean']
        multi_cost = results_summary['cost']['multi']['mean']
        memory_cost = results_summary['cost']['memory']['mean']
        
        single_quality = results_summary['overall']['single']['mean']
        multi_quality = results_summary['overall']['multi']['mean']
        memory_quality = results_summary['overall']['memory']['mean']
        
        print(f"Cost per Quality Point:")
        if single_quality > 0:
            print(f"  Single Agent: ${single_cost/single_quality:.4f}")
        if multi_quality > 0:
            print(f"  Multi Agent: ${multi_cost/multi_quality:.4f}")
        if memory_quality > 0:
            print(f"  Memory Agent: ${memory_cost/memory_quality:.4f}")
        
        print(f"\nCost Multipliers:")
        print(f"  Multi vs Single: {multi_cost/single_cost:.1f}x")
        print(f"  Memory vs Single: {memory_cost/single_cost:.1f}x")
        print(f"  Memory vs Multi: {memory_cost/multi_cost:.1f}x")
    
    # Statistical Significance (simplified)
    print("\n" + "-"*40)
    print("STATISTICAL SIGNIFICANCE ASSESSMENT")
    print("-"*40)
    
    if 'overall' in results_summary:
        single_vals = [r['evaluation'].get('overall', 0) for r in single_agent if 'evaluation' in r and r['evaluation']]
        multi_vals = [r['evaluation'].get('overall', 0) for r in multi_agent if 'evaluation' in r and r['evaluation']]
        memory_vals = [r['evaluation'].get('overall', 0) for r in memory_agent if 'evaluation' in r and r['evaluation']]
        
        if len(single_vals) >= 3 and len(multi_vals) >= 3:
            # Simple t-test approximation
            single_mean = statistics.mean(single_vals)
            multi_mean = statistics.mean(multi_vals)
            
            effect_size = abs(multi_mean - single_mean) / statistics.stdev(single_vals + multi_vals)
            print(f"Single vs Multi Effect Size: {effect_size:.3f}")
            
            if effect_size > 0.8:
                print("  → Large effect (Cohen's d > 0.8)")
            elif effect_size > 0.5:
                print("  → Medium effect (Cohen's d > 0.5)")
            elif effect_size > 0.2:
                print("  → Small effect (Cohen's d > 0.2)")
            else:
                print("  → Negligible effect (Cohen's d < 0.2)")
        
        if len(multi_vals) >= 3 and len(memory_vals) >= 3:
            multi_mean = statistics.mean(multi_vals)
            memory_mean = statistics.mean(memory_vals)
            
            effect_size = abs(memory_mean - multi_mean) / statistics.stdev(multi_vals + memory_vals)
            print(f"Multi vs Memory Effect Size: {effect_size:.3f}")
            
            if effect_size > 0.8:
                print("  → Large effect (Cohen's d > 0.8)")
            elif effect_size > 0.5:
                print("  → Medium effect (Cohen's d > 0.5)")
            elif effect_size > 0.2:
                print("  → Small effect (Cohen's d > 0.2)")
            else:
                print("  → Negligible effect (Cohen's d < 0.2)")
    
    return results_summary

def calculate_stats(values):
    """Calculate descriptive statistics"""
    if not values:
        return {}
    
    mean = statistics.mean(values)
    std_dev = statistics.stdev(values) if len(values) > 1 else 0
    
    # 95% confidence interval (simplified)
    if len(values) > 1:
        sem = std_dev / (len(values) ** 0.5)
        ci_margin = 1.96 * sem
        ci_lower = mean - ci_margin
        ci_upper = mean + ci_margin
    else:
        ci_lower = ci_upper = mean
    
    return {
        'mean': mean,
        'std': std_dev,
        'min': min(values),
        'max': max(values),
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'n': len(values)
    }

def create_visualizations(results_summary):
    """Create visualizations of the results"""
    if not results_summary:
        return
    
    # Quality metrics comparison
    quality_metrics = ['completeness', 'technical_feasibility', 'cost_effectiveness', 'scalability', 'innovation', 'overall']
    
    single_scores = [results_summary.get(metric, {}).get('single', {}).get('mean', 0) for metric in quality_metrics]
    multi_scores = [results_summary.get(metric, {}).get('multi', {}).get('mean', 0) for metric in quality_metrics]
    memory_scores = [results_summary.get(metric, {}).get('memory', {}).get('mean', 0) for metric in quality_metrics]
    
    x = np.arange(len(quality_metrics))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - width, single_scores, width, label='Single Agent', alpha=0.8)
    ax.bar(x, multi_scores, width, label='Multi Agent', alpha=0.8)
    ax.bar(x + width, memory_scores, width, label='Memory Agent', alpha=0.8)
    
    ax.set_xlabel('Quality Metrics')
    ax.set_ylabel('Score (1-10)')
    ax.set_title('Quality Metrics Comparison Across Approaches')
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', ' ').title() for m in quality_metrics], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/quality_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved to results/quality_comparison.png")

if __name__ == "__main__":
    results = load_latest_results()
    if results:
        summary = analyze_results(results)
        create_visualizations(summary)
    else:
        print("No results to analyze. Run the experiment first.")

#!/usr/bin/env python3
"""
Comparative Analysis: Enhanced vs Original Collective Memory System
Generates comprehensive comparison metrics and visualizations
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import os

def load_results():
    """Load all experimental results"""
    results = {}
    
    # Load original collective memory results
    if os.path.exists('collective_memory_results.json'):
        with open('collective_memory_results.json', 'r') as f:
            results['original'] = json.load(f)
    else:
        print("⚠️  Original collective memory results not found")
        results['original'] = []
    
    # Load enhanced collective memory results
    if os.path.exists('enhanced_memory_results.json'):
        with open('enhanced_memory_results.json', 'r') as f:
            results['enhanced'] = json.load(f)
    else:
        print("⚠️  Enhanced memory results not found")
        results['enhanced'] = []
    
    return results

def analyze_cost_efficiency(results):
    """Analyze cost efficiency improvements"""
    print("\n💰 COST EFFICIENCY ANALYSIS")
    print("-" * 50)
    
    if not results['original'] or not results['enhanced']:
        print("❌ Missing results for comparison")
        return
    
    # Extract costs from original system (memory approach)
    original_costs = []
    for result in results['original']:
        if result['approach'] == 'multi_agent_collective_memory':
            original_costs.append(result['cost'])
    
    # Extract costs from enhanced system
    enhanced_costs = []
    for task in results['enhanced']:
        task_cost = 0
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                task_cost += task[role]['cost']
        enhanced_costs.append(task_cost)
    
    if original_costs and enhanced_costs:
        original_avg = np.mean(original_costs)
        enhanced_avg = np.mean(enhanced_costs)
        cost_reduction = ((original_avg - enhanced_avg) / original_avg) * 100
        
        print(f"Original system average cost: ${original_avg:.4f}")
        print(f"Enhanced system average cost: ${enhanced_avg:.4f}")
        print(f"Cost reduction: {cost_reduction:+.1f}%")
        
        # Statistical significance
        if len(original_costs) > 1 and len(enhanced_costs) > 1:
            from scipy import stats
            try:
                t_stat, p_value = stats.ttest_ind(original_costs, enhanced_costs)
                print(f"Statistical significance (p-value): {p_value:.4f}")
            except ImportError:
                print("Install scipy for statistical significance testing")
    
    return {
        'original_avg': np.mean(original_costs) if original_costs else 0,
        'enhanced_avg': np.mean(enhanced_costs) if enhanced_costs else 0,
        'cost_reduction': cost_reduction if original_costs and enhanced_costs else 0
    }

def analyze_insight_utilization(results):
    """Analyze insight utilization improvements"""
    print("\n🧠 INSIGHT UTILIZATION ANALYSIS")
    print("-" * 50)
    
    if not results['original'] or not results['enhanced']:
        print("❌ Missing results for comparison")
        return
    
    # Original system insights
    original_insights = []
    for result in results['original']:
        if result['approach'] == 'multi_agent_collective_memory':
            original_insights.append(result.get('insights_used', 0))
    
    # Enhanced system insights
    enhanced_insights = []
    for task in results['enhanced']:
        task_insights = 0
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                task_insights += task[role]['insights_used']
        enhanced_insights.append(task_insights)
    
    if original_insights and enhanced_insights:
        original_avg = np.mean(original_insights)
        enhanced_avg = np.mean(enhanced_insights)
        utilization_improvement = enhanced_avg - original_avg
        
        print(f"Original system insights per task: {original_avg:.1f}")
        print(f"Enhanced system insights per task: {enhanced_avg:.1f}")
        print(f"Utilization improvement: {utilization_improvement:+.1f} insights/task")
    
    return {
        'original_avg': np.mean(original_insights) if original_insights else 0,
        'enhanced_avg': np.mean(enhanced_insights) if enhanced_insights else 0,
        'improvement': utilization_improvement if original_insights and enhanced_insights else 0
    }

def analyze_learning_curve(results):
    """Analyze learning curve improvements"""
    print("\n📈 LEARNING CURVE ANALYSIS")
    print("-" * 50)
    
    if not results['enhanced']:
        print("❌ Enhanced results not available")
        return
    
    # Enhanced system learning progression
    enhanced_insights = []
    for task in results['enhanced']:
        task_insights = 0
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                task_insights += task[role]['insights_used']
        enhanced_insights.append(task_insights)
    
    if len(enhanced_insights) >= 2:
        early_tasks = enhanced_insights[:len(enhanced_insights)//2]
        late_tasks = enhanced_insights[len(enhanced_insights)//2:]
        
        early_avg = np.mean(early_tasks)
        late_avg = np.mean(late_tasks)
        learning_improvement = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        
        print(f"Early tasks insight usage: {early_avg:.1f}")
        print(f"Late tasks insight usage: {late_avg:.1f}")
        print(f"Learning improvement: {learning_improvement:+.1f}%")
        
        return {
            'early_avg': early_avg,
            'late_avg': late_avg,
            'learning_rate': learning_improvement
        }
    
    return {'learning_rate': 0}

def analyze_domain_specialization(results):
    """Analyze domain specialization effectiveness"""
    print("\n🎯 DOMAIN SPECIALIZATION ANALYSIS")
    print("-" * 50)
    
    if not results['enhanced']:
        print("❌ Enhanced results not available")
        return
    
    domain_usage = defaultdict(int)
    domain_quality = defaultdict(list)
    
    for task in results['enhanced']:
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                for insight in task[role].get('insights_details', []):
                    domain = insight.get('domain', 'unknown')
                    quality = insight.get('quality', 0)
                    domain_usage[domain] += 1
                    domain_quality[domain].append(quality)
    
    print("Domain utilization:")
    total_insights = sum(domain_usage.values())
    for domain, count in sorted(domain_usage.items()):
        percentage = (count / total_insights * 100) if total_insights > 0 else 0
        avg_quality = np.mean(domain_quality[domain]) if domain_quality[domain] else 0
        print(f"  {domain}: {count} insights ({percentage:.1f}%, Q: {avg_quality:.3f})")
    
    return {
        'domain_count': len(domain_usage),
        'total_insights': total_insights,
        'avg_quality': np.mean([q for qualities in domain_quality.values() for q in qualities]) if domain_quality else 0
    }

def create_comparative_visualizations(results, metrics):
    """Create comparative visualizations"""
    print("\n📊 GENERATING COMPARATIVE VISUALIZATIONS")
    print("-" * 50)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Cost Comparison
    systems = ['Original\nSystem', 'Enhanced\nSystem']
    costs = [metrics['cost']['original_avg'], metrics['cost']['enhanced_avg']]
    colors = ['#ff7f7f', '#7fbf7f']
    
    bars1 = ax1.bar(systems, costs, color=colors, alpha=0.7)
    ax1.set_ylabel('Average Cost ($)')
    ax1.set_title('Cost Efficiency Comparison')
    ax1.grid(True, alpha=0.3)
    
    # Add cost reduction annotation
    if metrics['cost']['cost_reduction'] != 0:
        ax1.annotate(f'{metrics["cost"]["cost_reduction"]:+.1f}%', 
                    xy=(1, costs[1]), xytext=(1, costs[1] + max(costs) * 0.1),
                    ha='center', fontweight='bold', color='green' if metrics['cost']['cost_reduction'] > 0 else 'red',
                    arrowprops=dict(arrowstyle='->', color='green' if metrics['cost']['cost_reduction'] > 0 else 'red'))
    
    # 2. Insight Utilization Comparison
    insights = [metrics['insights']['original_avg'], metrics['insights']['enhanced_avg']]
    bars2 = ax2.bar(systems, insights, color=colors, alpha=0.7)
    ax2.set_ylabel('Insights per Task')
    ax2.set_title('Insight Utilization Comparison')
    ax2.grid(True, alpha=0.3)
    
    # 3. Learning Curve (Enhanced System Only)
    if results['enhanced']:
        enhanced_insights = []
        for task in results['enhanced']:
            task_insights = 0
            for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
                if role in task:
                    task_insights += task[role]['insights_used']
            enhanced_insights.append(task_insights)
        
        ax3.plot(range(1, len(enhanced_insights) + 1), enhanced_insights, 
                marker='o', linewidth=2, markersize=6, color='#7fbf7f')
        ax3.set_xlabel('Task Number')
        ax3.set_ylabel('Insights Used')
        ax3.set_title('Enhanced System Learning Curve')
        ax3.grid(True, alpha=0.3)
        
        # Add trend line
        if len(enhanced_insights) > 1:
            z = np.polyfit(range(len(enhanced_insights)), enhanced_insights, 1)
            p = np.poly1d(z)
            ax3.plot(range(1, len(enhanced_insights) + 1), p(range(len(enhanced_insights))), 
                    "r--", alpha=0.8, label=f'Trend (slope: {z[0]:.2f})')
            ax3.legend()
    
    # 4. System Architecture Comparison
    features = ['Basic\nMemory', 'Insight\nFiltering', 'Domain\nSpecialization', 'Federation', 'Optimization']
    original_features = [1, 0, 0, 0, 0]  # Only basic memory
    enhanced_features = [1, 1, 1, 1, 1]  # All features
    
    x = np.arange(len(features))
    width = 0.35
    
    ax4.bar(x - width/2, original_features, width, label='Original System', color='#ff7f7f', alpha=0.7)
    ax4.bar(x + width/2, enhanced_features, width, label='Enhanced System', color='#7fbf7f', alpha=0.7)
    
    ax4.set_xlabel('Features')
    ax4.set_ylabel('Available')
    ax4.set_title('System Feature Comparison')
    ax4.set_xticks(x)
    ax4.set_xticklabels(features, rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparative_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Comparative visualization saved as 'comparative_analysis.png'")

def generate_executive_summary(metrics):
    """Generate executive summary of improvements"""
    print("\n🏆 EXECUTIVE SUMMARY")
    print("=" * 60)
    
    improvements = []
    
    if metrics['cost']['cost_reduction'] > 0:
        improvements.append(f"💰 {metrics['cost']['cost_reduction']:.1f}% cost reduction")
    
    if metrics['insights']['improvement'] > 0:
        improvements.append(f"🧠 +{metrics['insights']['improvement']:.1f} insights per task")
    
    if metrics['learning']['learning_rate'] > 0:
        improvements.append(f"📈 {metrics['learning']['learning_rate']:.1f}% learning improvement")
    
    if metrics['domains']['domain_count'] > 0:
        improvements.append(f"🎯 {metrics['domains']['domain_count']} specialized domains")
    
    print("Key Improvements:")
    for improvement in improvements:
        print(f"  ✅ {improvement}")
    
    if not improvements:
        print("  ⚠️  Limited improvements detected - may need more data or tuning")
    
    print(f"\nOverall Assessment:")
    if len(improvements) >= 3:
        print("  🌟 EXCELLENT: Enhanced system shows significant improvements")
    elif len(improvements) >= 2:
        print("  ✅ GOOD: Enhanced system shows measurable improvements")
    elif len(improvements) >= 1:
        print("  ⚠️  MODERATE: Enhanced system shows some improvements")
    else:
        print("  ❌ NEEDS WORK: Enhanced system needs further optimization")

def main():
    """Main comparative analysis"""
    print("🔬 ENHANCED vs ORIGINAL COLLECTIVE MEMORY COMPARISON")
    print("=" * 70)
    
    # Load all results
    results = load_results()
    
    # Perform analyses
    metrics = {
        'cost': analyze_cost_efficiency(results),
        'insights': analyze_insight_utilization(results),
        'learning': analyze_learning_curve(results),
        'domains': analyze_domain_specialization(results)
    }
    
    # Create visualizations
    create_comparative_visualizations(results, metrics)
    
    # Generate executive summary
    generate_executive_summary(metrics)
    
    print(f"\n✅ Comparative analysis completed!")
    return metrics

if __name__ == "__main__":
    main()

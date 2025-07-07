#!/usr/bin/env python3
"""
Enhanced Collective Memory Analysis
Analyzes the performance improvements from the enhanced system
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

def analyze_enhanced_results():
    """Analyze enhanced collective memory experiment results"""
    
    print("🔬 ENHANCED COLLECTIVE MEMORY ANALYSIS")
    print("=" * 60)
    
    # Load results
    try:
        with open('enhanced_memory_results.json', 'r') as f:
            enhanced_results = json.load(f)
    except FileNotFoundError:
        print("❌ Enhanced results file not found. Run the enhanced experiment first.")
        return
    
    # Load original results for comparison
    try:
        with open('collective_memory_results.json', 'r') as f:
            original_results = json.load(f)
    except FileNotFoundError:
        print("⚠️  Original results not found. Analysis will be limited.")
        original_results = []
    
    # 1. INSIGHT UTILIZATION ANALYSIS
    print("\n1️⃣ ENHANCED INSIGHT UTILIZATION")
    print("-" * 40)
    
    enhanced_insights = []
    domain_distribution = defaultdict(int)
    quality_scores = []
    federation_sources = defaultdict(int)
    
    for task in enhanced_results:
        task_insights = 0
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                role_insights = task[role]['insights_used']
                task_insights += role_insights
                
                # Analyze insight details
                for insight in task[role].get('insights_details', []):
                    domain_distribution[insight['domain']] += 1
                    quality_scores.append(insight['quality'])
                    federation_sources[insight['source']] += 1
        
        enhanced_insights.append(task_insights)
    
    print(f"Average insights per task: {np.mean(enhanced_insights):.1f}")
    print(f"Total insights utilized: {sum(enhanced_insights)}")
    print(f"Average insight quality: {np.mean(quality_scores):.3f}")
    
    print(f"\nDomain Distribution:")
    for domain, count in sorted(domain_distribution.items()):
        percentage = (count / sum(domain_distribution.values())) * 100
        print(f"  {domain}: {count} ({percentage:.1f}%)")
    
    print(f"\nInsight Sources:")
    for source, count in sorted(federation_sources.items()):
        percentage = (count / sum(federation_sources.values())) * 100
        print(f"  {source}: {count} ({percentage:.1f}%)")
    
    # 2. COST-EFFICIENCY ANALYSIS
    print("\n2️⃣ ENHANCED COST-EFFICIENCY")
    print("-" * 40)
    
    enhanced_costs = []
    enhanced_tokens = []
    
    for task in enhanced_results:
        task_cost = 0
        task_tokens = 0
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                task_cost += task[role]['cost']
                task_tokens += task[role]['tokens_used']
        enhanced_costs.append(task_cost)
        enhanced_tokens.append(task_tokens)
    
    print(f"Average cost per task: ${np.mean(enhanced_costs):.4f}")
    print(f"Average tokens per task: {np.mean(enhanced_tokens):.0f}")
    
    # Compare with original if available
    if original_results:
        original_memory_costs = []
        for result in original_results:
            if result['approach'] == 'multi_agent_collective_memory':
                original_memory_costs.append(result['cost'])
        
        if original_memory_costs:
            original_avg = np.mean(original_memory_costs)
            enhanced_avg = np.mean(enhanced_costs)
            improvement = ((original_avg - enhanced_avg) / original_avg) * 100
            
            print(f"\nComparison with Original System:")
            print(f"  Original average cost: ${original_avg:.4f}")
            print(f"  Enhanced average cost: ${enhanced_avg:.4f}")
            print(f"  Cost improvement: {improvement:+.1f}%")
    
    # 3. LEARNING CURVE ANALYSIS
    print("\n3️⃣ ENHANCED LEARNING CURVE")
    print("-" * 40)
    
    # Analyze learning progression
    early_tasks = enhanced_insights[:len(enhanced_insights)//2]
    late_tasks = enhanced_insights[len(enhanced_insights)//2:]
    
    early_avg = np.mean(early_tasks) if early_tasks else 0
    late_avg = np.mean(late_tasks) if late_tasks else 0
    learning_improvement = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
    
    print(f"Early tasks insight usage: {early_avg:.1f}")
    print(f"Late tasks insight usage: {late_avg:.1f}")
    print(f"Learning improvement: {learning_improvement:+.1f}%")
    
    # 4. QUALITY ASSESSMENT
    print("\n4️⃣ ENHANCED QUALITY METRICS")
    print("-" * 40)
    
    # Quality distribution analysis
    quality_ranges = {
        'High (0.8-1.0)': sum(1 for q in quality_scores if q >= 0.8),
        'Medium (0.6-0.8)': sum(1 for q in quality_scores if 0.6 <= q < 0.8),
        'Low (0.0-0.6)': sum(1 for q in quality_scores if q < 0.6)
    }
    
    total_insights = sum(quality_ranges.values())
    for range_name, count in quality_ranges.items():
        percentage = (count / total_insights * 100) if total_insights > 0 else 0
        print(f"  {range_name}: {count} ({percentage:.1f}%)")
    
    # 5. DOMAIN SPECIALIZATION EFFECTIVENESS
    print("\n5️⃣ DOMAIN SPECIALIZATION ANALYSIS")
    print("-" * 40)
    
    domain_quality = defaultdict(list)
    for task in enhanced_results:
        for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']:
            if role in task:
                for insight in task[role].get('insights_details', []):
                    domain_quality[insight['domain']].append(insight['quality'])
    
    print("Average quality by domain:")
    for domain, qualities in sorted(domain_quality.items()):
        avg_quality = np.mean(qualities)
        print(f"  {domain}: {avg_quality:.3f} (n={len(qualities)})")
    
    # 6. FEDERATION IMPACT
    print("\n6️⃣ FEDERATION SYSTEM ANALYSIS")
    print("-" * 40)
    
    local_insights = [q for task in enhanced_results 
                     for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']
                     if role in task
                     for insight in task[role].get('insights_details', [])
                     if insight['source'] == 'local']
    
    federated_insights = [q for task in enhanced_results 
                         for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']
                         if role in task
                         for insight in task[role].get('insights_details', [])
                         if insight['source'] != 'local']
    
    if local_insights and federated_insights:
        local_quality = np.mean([i['quality'] for i in local_insights])
        federated_quality = np.mean([i['quality'] for i in federated_insights])
        
        print(f"Local insights: {len(local_insights)} (avg quality: {local_quality:.3f})")
        print(f"Federated insights: {len(federated_insights)} (avg quality: {federated_quality:.3f})")
        
        quality_diff = federated_quality - local_quality
        print(f"Federation quality advantage: {quality_diff:+.3f}")
    else:
        print("Federation system not yet active (no federated insights found)")
    
    # 7. VISUALIZATION
    create_enhanced_visualizations(enhanced_results, domain_distribution, quality_scores)
    
    # 8. RECOMMENDATIONS
    print("\n8️⃣ ENHANCEMENT RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if np.mean(quality_scores) < 0.7:
        recommendations.append("🔧 Increase minimum quality threshold for insight filtering")
    
    if learning_improvement < 10:
        recommendations.append("📈 Improve learning curve by enhancing insight extraction")
    
    if len(set(domain_distribution.keys())) < 4:
        recommendations.append("🎯 Expand domain classification patterns")
    
    if federation_sources.get('local', 0) == sum(federation_sources.values()):
        recommendations.append("🌐 Activate federation system for knowledge sharing")
    
    if not recommendations:
        recommendations.append("✅ System performing well - continue monitoring")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\n✅ Enhanced analysis completed!")
    return {
        'insights_per_task': np.mean(enhanced_insights),
        'average_cost': np.mean(enhanced_costs),
        'average_quality': np.mean(quality_scores),
        'learning_improvement': learning_improvement,
        'domain_count': len(domain_distribution),
        'recommendations': recommendations
    }

def create_enhanced_visualizations(results, domain_dist, quality_scores):
    """Create visualizations for enhanced system analysis"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Domain Distribution
    domains = list(domain_dist.keys())
    counts = list(domain_dist.values())
    colors = plt.cm.Set3(np.linspace(0, 1, len(domains)))
    
    ax1.pie(counts, labels=domains, autopct='%1.1f%%', colors=colors)
    ax1.set_title('Domain Specialization Distribution')
    
    # 2. Quality Score Distribution
    ax2.hist(quality_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.axvline(np.mean(quality_scores), color='red', linestyle='--', 
                label=f'Mean: {np.mean(quality_scores):.3f}')
    ax2.set_xlabel('Quality Score')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Insight Quality Distribution')
    ax2.legend()
    
    # 3. Insights Usage Over Time
    insights_per_task = []
    for task in results:
        task_insights = sum(task[role]['insights_used'] 
                           for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']
                           if role in task)
        insights_per_task.append(task_insights)
    
    ax3.plot(range(1, len(insights_per_task) + 1), insights_per_task, 
             marker='o', linewidth=2, markersize=6)
    ax3.set_xlabel('Task Number')
    ax3.set_ylabel('Insights Used')
    ax3.set_title('Learning Curve: Insights Usage Over Time')
    ax3.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(range(len(insights_per_task)), insights_per_task, 1)
    p = np.poly1d(z)
    ax3.plot(range(1, len(insights_per_task) + 1), p(range(len(insights_per_task))), 
             "r--", alpha=0.8, label=f'Trend (slope: {z[0]:.2f})')
    ax3.legend()
    
    # 4. Cost vs Insights Efficiency
    costs = []
    insights = []
    for task in results:
        task_cost = sum(task[role]['cost'] 
                       for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']
                       if role in task)
        task_insights = sum(task[role]['insights_used'] 
                           for role in ['product_manager', 'architect', 'engineer', 'qa_engineer']
                           if role in task)
        costs.append(task_cost)
        insights.append(task_insights)
    
    ax4.scatter(insights, costs, alpha=0.7, s=60)
    ax4.set_xlabel('Insights Used')
    ax4.set_ylabel('Cost ($)')
    ax4.set_title('Cost vs Insights Efficiency')
    ax4.grid(True, alpha=0.3)
    
    # Add efficiency line
    if len(insights) > 1:
        z = np.polyfit(insights, costs, 1)
        p = np.poly1d(z)
        ax4.plot(insights, p(insights), "r--", alpha=0.8, 
                label=f'Efficiency: ${z[0]:.4f} per insight')
        ax4.legend()
    
    plt.tight_layout()
    plt.savefig('enhanced_memory_analysis.png', dpi=300, bbox_inches='tight')
    print(f"📊 Enhanced visualization saved as 'enhanced_memory_analysis.png'")

if __name__ == "__main__":
    analyze_enhanced_results()

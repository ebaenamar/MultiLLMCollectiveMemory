#!/usr/bin/env python3
"""
Analyze HumanEval ChromaDB Benchmark Results
Creates visualizations and detailed analysis of the benchmark results
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os

def load_latest_results():
    """Load the most recent benchmark results"""
    result_files = glob.glob("humaneval_chromadb_benchmark_*.json")
    if not result_files:
        print("❌ No benchmark result files found!")
        return None
    
    # Get the most recent file
    latest_file = max(result_files, key=os.path.getctime)
    print(f"📁 Loading results from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def create_performance_comparison_chart(data):
    """Create performance comparison charts"""
    approaches = []
    success_rates = []
    avg_costs = []
    avg_times = []
    
    for approach, metrics in data['analysis']['comparison'].items():
        approaches.append(approach.replace('_', ' ').title())
        success_rates.append(metrics['success_rate'] * 100)
        avg_costs.append(metrics['avg_cost'])
        avg_times.append(metrics['avg_time'])
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('HumanEval ChromaDB Benchmark Results', fontsize=16, fontweight='bold')
    
    # Success Rate
    bars1 = ax1.bar(approaches, success_rates, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax1.set_title('Success Rate (%)', fontweight='bold')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_ylim(0, 100)
    for bar, rate in zip(bars1, success_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Average Cost
    bars2 = ax2.bar(approaches, avg_costs, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax2.set_title('Average Cost per Problem ($)', fontweight='bold')
    ax2.set_ylabel('Cost ($)')
    for bar, cost in zip(bars2, avg_costs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_costs)*0.01, 
                f'${cost:.4f}', ha='center', va='bottom', fontweight='bold')
    
    # Average Time
    bars3 = ax3.bar(approaches, avg_times, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax3.set_title('Average Time per Problem (seconds)', fontweight='bold')
    ax3.set_ylabel('Time (seconds)')
    for bar, time_val in zip(bars3, avg_times):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_times)*0.01, 
                f'{time_val:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    # Memory Usage (if available)
    if 'enhanced_chromadb_memory' in data['analysis']['comparison']:
        enhanced_metrics = data['analysis']['comparison']['enhanced_chromadb_memory']
        if 'avg_insights_used' in enhanced_metrics:
            insights_data = [0, 0, enhanced_metrics['avg_insights_used']]
            bars4 = ax4.bar(approaches, insights_data, color=['#3498db', '#e74c3c', '#2ecc71'])
            ax4.set_title('Average Insights Used per Problem', fontweight='bold')
            ax4.set_ylabel('Insights Used')
            for bar, insights in zip(bars4, insights_data):
                if insights > 0:
                    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                            f'{insights:.1f}', ha='center', va='bottom', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'Memory metrics\nnot available', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Memory Usage', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('humaneval_chromadb_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 Performance comparison chart saved as: humaneval_chromadb_comparison.png")
    
    return fig

def create_detailed_analysis_report(data):
    """Create detailed analysis report"""
    report = []
    report.append("# HumanEval ChromaDB Benchmark Analysis Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    comparison = data['analysis']['comparison']
    
    single_agent = comparison['single_agent']
    multi_agent = comparison['multi_agent_no_memory']
    enhanced = comparison['enhanced_chromadb_memory']
    
    report.append(f"- **Single Agent**: {single_agent['success_rate']:.1%} success, ${single_agent['avg_cost']:.4f} avg cost, {single_agent['avg_time']:.1f}s avg time")
    report.append(f"- **Multi-Agent (no memory)**: {multi_agent['success_rate']:.1%} success, ${multi_agent['avg_cost']:.4f} avg cost, {multi_agent['avg_time']:.1f}s avg time")
    report.append(f"- **Enhanced (ChromaDB)**: {enhanced['success_rate']:.1%} success, ${enhanced['avg_cost']:.4f} avg cost, {enhanced['avg_time']:.1f}s avg time")
    
    if 'avg_insights_used' in enhanced:
        report.append(f"- **Memory Utilization**: {enhanced['avg_insights_used']:.1f} insights used per problem on average")
    
    report.append("")
    
    # Cost Analysis
    report.append("## Cost Analysis")
    cost_vs_single = ((enhanced['avg_cost'] - single_agent['avg_cost']) / single_agent['avg_cost']) * 100
    cost_vs_multi = ((enhanced['avg_cost'] - multi_agent['avg_cost']) / multi_agent['avg_cost']) * 100
    
    report.append(f"- Enhanced system cost vs Single Agent: **{cost_vs_single:+.1f}%**")
    report.append(f"- Enhanced system cost vs Multi-Agent: **{cost_vs_multi:+.1f}%**")
    report.append("")
    
    # Time Analysis
    report.append("## Time Analysis")
    time_vs_single = ((enhanced['avg_time'] - single_agent['avg_time']) / single_agent['avg_time']) * 100
    time_vs_multi = ((enhanced['avg_time'] - multi_agent['avg_time']) / multi_agent['avg_time']) * 100
    
    report.append(f"- Enhanced system time vs Single Agent: **{time_vs_single:+.1f}%**")
    report.append(f"- Enhanced system time vs Multi-Agent: **{time_vs_multi:+.1f}%**")
    report.append("")
    
    # Key Insights
    report.append("## Key Insights")
    for insight in data['analysis']['insights']:
        report.append(f"- {insight}")
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    
    if enhanced['success_rate'] >= max(single_agent['success_rate'], multi_agent['success_rate']):
        report.append("✅ **Enhanced ChromaDB system shows competitive or superior success rates**")
    else:
        report.append("⚠️ **Enhanced system success rate needs improvement**")
    
    if cost_vs_single < 50:  # Less than 50% cost increase
        report.append("✅ **Cost overhead is reasonable for the added memory capabilities**")
    else:
        report.append("⚠️ **Cost overhead is significant - consider optimization**")
    
    if 'avg_insights_used' in enhanced and enhanced['avg_insights_used'] > 2:
        report.append("✅ **Memory system is actively utilized with good insight retrieval**")
    else:
        report.append("⚠️ **Memory utilization is low - may need tuning**")
    
    # Save report
    with open('humaneval_chromadb_analysis_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("📄 Analysis report saved as: humaneval_chromadb_analysis_report.md")
    
    return report

def create_cost_efficiency_analysis(data):
    """Analyze cost efficiency across approaches"""
    results_data = []
    
    for result_set in data['results']:
        approach = result_set['approach']
        for result in result_set['results']:
            if result['success']:
                results_data.append({
                    'approach': approach.replace('_', ' ').title(),
                    'task_id': result['task_id'],
                    'cost': result['cost'],
                    'time': result['execution_time'],
                    'tokens': result['tokens'],
                    'insights_used': result.get('insights_used', 0)
                })
    
    df = pd.DataFrame(results_data)
    
    # Create cost distribution plot
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    sns.boxplot(data=df, x='approach', y='cost')
    plt.title('Cost Distribution by Approach')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 2)
    sns.boxplot(data=df, x='approach', y='time')
    plt.title('Time Distribution by Approach')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 3)
    sns.boxplot(data=df, x='approach', y='tokens')
    plt.title('Token Usage Distribution by Approach')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 4)
    if df['insights_used'].sum() > 0:
        enhanced_df = df[df['approach'] == 'Enhanced Chromadb Memory']
        if not enhanced_df.empty:
            plt.hist(enhanced_df['insights_used'], bins=10, alpha=0.7, color='green')
            plt.title('Insights Used Distribution (Enhanced System)')
            plt.xlabel('Insights Used')
            plt.ylabel('Frequency')
    else:
        plt.text(0.5, 0.5, 'No insight data\navailable', ha='center', va='center', 
                transform=plt.gca().transAxes)
        plt.title('Insights Usage')
    
    plt.tight_layout()
    plt.savefig('cost_efficiency_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Cost efficiency analysis saved as: cost_efficiency_analysis.png")

def main():
    """Main analysis function"""
    print("📊 ANALYZING HUMANEVAL CHROMADB BENCHMARK RESULTS")
    print("="*60)
    
    # Load results
    data = load_latest_results()
    if not data:
        return
    
    print(f"✅ Loaded benchmark data with {len(data['results'])} approaches")
    
    # Create visualizations
    create_performance_comparison_chart(data)
    create_cost_efficiency_analysis(data)
    
    # Generate report
    create_detailed_analysis_report(data)
    
    print("\n🎉 Analysis complete! Generated files:")
    print("  - humaneval_chromadb_comparison.png")
    print("  - cost_efficiency_analysis.png") 
    print("  - humaneval_chromadb_analysis_report.md")

if __name__ == "__main__":
    main()

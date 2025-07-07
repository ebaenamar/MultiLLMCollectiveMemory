#!/usr/bin/env python3
"""
Collective Memory Analysis
Analyzes the specific contribution of collective memory to multi-agent performance
"""

import json
import statistics
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class CollectiveMemoryAnalyzer:
    """Analyzer for collective memory experiment results"""
    
    def __init__(self, results_file: str = "collective_memory_results.json"):
        self.results_file = results_file
        self.results = self.load_results()
    
    def load_results(self) -> List[Dict]:
        """Load experiment results"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Results file {self.results_file} not found")
            return []
    
    def analyze_collective_memory_contribution(self):
        """Analyze the specific contribution of collective memory"""
        
        print("🧠 COLLECTIVE MEMORY CONTRIBUTION ANALYSIS")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Separate results by approach
        single_results = [r for r in self.results if r['approach'] == 'single_agent']
        standard_results = [r for r in self.results if r['approach'] == 'multi_agent_standard']
        memory_results = [r for r in self.results if r['approach'] == 'multi_agent_collective_memory']
        
        print(f"📊 Analyzing {len(single_results)} single-agent, {len(standard_results)} standard multi-agent,")
        print(f"    and {len(memory_results)} collective memory results")
        
        # 1. MEMORY UTILIZATION ANALYSIS
        print("\n1️⃣ MEMORY UTILIZATION ANALYSIS")
        print("-" * 40)
        
        total_insights_used = sum(r['memory_insights_used'] for r in memory_results)
        total_insights_stored = sum(r['memory_insights_stored'] for r in memory_results)
        avg_insights_used = statistics.mean([r['memory_insights_used'] for r in memory_results]) if memory_results else 0
        avg_insights_stored = statistics.mean([r['memory_insights_stored'] for r in memory_results]) if memory_results else 0
        
        print(f"Total Insights Used: {total_insights_used}")
        print(f"Total Insights Stored: {total_insights_stored}")
        print(f"Average Insights Used per Task: {avg_insights_used:.1f}")
        print(f"Average Insights Stored per Task: {avg_insights_stored:.1f}")
        
        # Memory utilization trend (should increase over time)
        memory_usage_trend = []
        for i, result in enumerate(memory_results):
            memory_usage_trend.append({
                'task_number': i + 1,
                'insights_used': result['memory_insights_used'],
                'insights_stored': result['memory_insights_stored']
            })
        
        if len(memory_usage_trend) > 5:
            early_usage = statistics.mean([t['insights_used'] for t in memory_usage_trend[:5]])
            late_usage = statistics.mean([t['insights_used'] for t in memory_usage_trend[-5:]])
            
            if late_usage > early_usage:
                improvement = ((late_usage - early_usage) / max(early_usage, 0.1)) * 100
                print(f"📈 Memory Usage Trend: +{improvement:.1f}% increase from early to late tasks")
                print("   ✅ This indicates the system is learning and reusing knowledge!")
            else:
                print("📉 Memory Usage Trend: No significant increase over time")
        
        # 2. COST-BENEFIT ANALYSIS
        print("\n2️⃣ COST-BENEFIT ANALYSIS")
        print("-" * 40)
        
        single_cost = statistics.mean([r['cost'] for r in single_results]) if single_results else 0
        standard_cost = statistics.mean([r['cost'] for r in standard_results]) if standard_results else 0
        memory_cost = statistics.mean([r['cost'] for r in memory_results]) if memory_results else 0
        
        single_tokens = statistics.mean([r['total_tokens'] for r in single_results]) if single_results else 0
        standard_tokens = statistics.mean([r['total_tokens'] for r in standard_results]) if standard_results else 0
        memory_tokens = statistics.mean([r['total_tokens'] for r in memory_results]) if memory_results else 0
        
        print(f"Average Cost per Task:")
        print(f"  Single Agent:           ${single_cost:.4f}")
        print(f"  Multi-Agent Standard:   ${standard_cost:.4f}")
        print(f"  Multi-Agent + Memory:   ${memory_cost:.4f}")
        
        if standard_cost > 0:
            memory_overhead = ((memory_cost - standard_cost) / standard_cost) * 100
            print(f"\nMemory System Overhead: {memory_overhead:+.1f}%")
            
            if memory_overhead < 20:
                print("  ✅ Low overhead - memory system is efficient")
            elif memory_overhead < 50:
                print("  ⚠️  Moderate overhead - acceptable for learning benefits")
            else:
                print("  ❌ High overhead - may need optimization")
        
        print(f"\nAverage Tokens per Task:")
        print(f"  Single Agent:           {single_tokens:.0f}")
        print(f"  Multi-Agent Standard:   {standard_tokens:.0f}")
        print(f"  Multi-Agent + Memory:   {memory_tokens:.0f}")
        
        # 3. PERFORMANCE COMPARISON
        print("\n3️⃣ PERFORMANCE COMPARISON")
        print("-" * 40)
        
        # Simple code quality metrics
        single_quality = self.calculate_simple_quality_scores(single_results)
        standard_quality = self.calculate_simple_quality_scores(standard_results)
        memory_quality = self.calculate_simple_quality_scores(memory_results)
        
        print(f"Average Quality Scores (0-10):")
        print(f"  Single Agent:           {single_quality:.2f}")
        print(f"  Multi-Agent Standard:   {standard_quality:.2f}")
        print(f"  Multi-Agent + Memory:   {memory_quality:.2f}")
        
        if memory_quality > standard_quality:
            improvement = ((memory_quality - standard_quality) / standard_quality) * 100
            print(f"\n🎯 Collective Memory Improvement: +{improvement:.1f}%")
            
            if improvement > 10:
                print("  🏆 SIGNIFICANT improvement from collective memory!")
            elif improvement > 5:
                print("  ✅ Moderate improvement from collective memory")
            else:
                print("  📈 Small but positive improvement from collective memory")
        else:
            decline = ((standard_quality - memory_quality) / standard_quality) * 100
            print(f"\n📉 Quality Decline: -{decline:.1f}%")
            print("  ⚠️  Collective memory may need tuning")
        
        # 4. LEARNING CURVE ANALYSIS
        print("\n4️⃣ LEARNING CURVE ANALYSIS")
        print("-" * 40)
        
        if len(memory_results) >= 8:
            # Split into early and late tasks
            mid_point = len(memory_results) // 2
            early_memory = memory_results[:mid_point]
            late_memory = memory_results[mid_point:]
            
            early_quality = self.calculate_simple_quality_scores(early_memory)
            late_quality = self.calculate_simple_quality_scores(late_memory)
            
            early_cost = statistics.mean([r['cost'] for r in early_memory])
            late_cost = statistics.mean([r['cost'] for r in late_memory])
            
            print(f"Early Tasks (1-{mid_point}):")
            print(f"  Quality: {early_quality:.2f}")
            print(f"  Cost: ${early_cost:.4f}")
            
            print(f"Late Tasks ({mid_point+1}-{len(memory_results)}):")
            print(f"  Quality: {late_quality:.2f}")
            print(f"  Cost: ${late_cost:.4f}")
            
            if late_quality > early_quality:
                learning_improvement = ((late_quality - early_quality) / early_quality) * 100
                print(f"\n📚 Learning Effect: +{learning_improvement:.1f}% quality improvement")
                print("  ✅ System is learning and improving over time!")
            else:
                print(f"\n📉 No clear learning trend detected")
            
            if late_cost < early_cost:
                efficiency_gain = ((early_cost - late_cost) / early_cost) * 100
                print(f"💰 Efficiency Gain: -{efficiency_gain:.1f}% cost reduction")
                print("  ✅ System becoming more efficient with experience!")
        
        # 5. COLLECTIVE MEMORY VALUE PROPOSITION
        print("\n5️⃣ COLLECTIVE MEMORY VALUE PROPOSITION")
        print("-" * 50)
        
        # Calculate value metrics
        quality_gain = memory_quality - standard_quality if standard_quality > 0 else 0
        cost_overhead = memory_cost - standard_cost if standard_cost > 0 else 0
        
        # Value score: quality gain per dollar of overhead
        if cost_overhead > 0:
            value_score = quality_gain / cost_overhead
            print(f"Value Score: {value_score:.2f} quality points per $0.01 overhead")
        else:
            value_score = float('inf') if quality_gain > 0 else 0
            print(f"Value Score: Infinite (no cost overhead with quality gain)")
        
        # Memory utilization efficiency
        if total_insights_used > 0:
            memory_efficiency = quality_gain / total_insights_used
            print(f"Memory Efficiency: {memory_efficiency:.3f} quality gain per insight used")
        
        # Final recommendation
        print(f"\n🎯 FINAL ASSESSMENT:")
        
        conditions_met = 0
        total_conditions = 4
        
        if memory_quality > standard_quality:
            print("  ✅ Quality improvement achieved")
            conditions_met += 1
        else:
            print("  ❌ No quality improvement")
        
        if memory_overhead < 50:  # Less than 50% cost overhead
            print("  ✅ Reasonable cost overhead")
            conditions_met += 1
        else:
            print("  ❌ High cost overhead")
        
        if avg_insights_used > 1:  # Actually using memory
            print("  ✅ Memory system actively utilized")
            conditions_met += 1
        else:
            print("  ❌ Memory system underutilized")
        
        if len(memory_results) >= 8 and late_quality > early_quality:
            print("  ✅ Learning effect demonstrated")
            conditions_met += 1
        else:
            print("  ❌ No clear learning effect")
        
        success_rate = (conditions_met / total_conditions) * 100
        
        print(f"\n📊 Success Rate: {conditions_met}/{total_conditions} ({success_rate:.0f}%)")
        
        if success_rate >= 75:
            print("🏆 CONCLUSION: Collective Memory system shows STRONG promise!")
            print("   Recommendation: Continue development and scale up")
        elif success_rate >= 50:
            print("✅ CONCLUSION: Collective Memory system shows promise")
            print("   Recommendation: Optimize and refine the system")
        else:
            print("⚠️  CONCLUSION: Collective Memory system needs improvement")
            print("   Recommendation: Investigate and address key issues")
        
        # 6. Generate visualizations
        self.create_visualizations(single_results, standard_results, memory_results, memory_usage_trend)
    
    def calculate_simple_quality_scores(self, results: List[Dict]) -> float:
        """Calculate simple quality scores based on code characteristics"""
        
        if not results:
            return 0.0
        
        scores = []
        for result in results:
            completion = result['completion']
            
            if not completion.strip() or "Error:" in completion:
                scores.append(0.0)
                continue
            
            score = 0.0
            
            # Basic completeness checks
            if 'def ' in completion:
                score += 3.0
            if 'return' in completion:
                score += 2.0
            if len(completion.split('\n')) > 3:
                score += 2.0
            if any(keyword in completion for keyword in ['if', 'for', 'while']):
                score += 1.5
            if '"""' in completion or "'''" in completion:
                score += 1.0
            if 'try:' in completion or 'except' in completion:
                score += 0.5
            
            scores.append(min(score, 10.0))
        
        return statistics.mean(scores)
    
    def create_visualizations(self, single_results, standard_results, memory_results, memory_trend):
        """Create visualizations of collective memory analysis"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Quality comparison
        qualities = [
            self.calculate_simple_quality_scores(single_results),
            self.calculate_simple_quality_scores(standard_results),
            self.calculate_simple_quality_scores(memory_results)
        ]
        
        ax1.bar(['Single\nAgent', 'Multi-Agent\nStandard', 'Multi-Agent\n+ Memory'], 
                qualities, color=['#3498db', '#f39c12', '#e74c3c'])
        ax1.set_ylabel('Quality Score')
        ax1.set_title('Quality Comparison')
        ax1.set_ylim(0, 10)
        
        # 2. Cost comparison
        costs = [
            statistics.mean([r['cost'] for r in single_results]) if single_results else 0,
            statistics.mean([r['cost'] for r in standard_results]) if standard_results else 0,
            statistics.mean([r['cost'] for r in memory_results]) if memory_results else 0
        ]
        
        ax2.bar(['Single\nAgent', 'Multi-Agent\nStandard', 'Multi-Agent\n+ Memory'], 
                costs, color=['#3498db', '#f39c12', '#e74c3c'])
        ax2.set_ylabel('Average Cost ($)')
        ax2.set_title('Cost Comparison')
        
        # 3. Memory utilization over time
        if memory_trend:
            task_numbers = [t['task_number'] for t in memory_trend]
            insights_used = [t['insights_used'] for t in memory_trend]
            insights_stored = [t['insights_stored'] for t in memory_trend]
            
            ax3.plot(task_numbers, insights_used, 'o-', label='Insights Used', color='#e74c3c')
            ax3.plot(task_numbers, insights_stored, 's-', label='Insights Stored', color='#2ecc71')
            ax3.set_xlabel('Task Number')
            ax3.set_ylabel('Number of Insights')
            ax3.set_title('Memory Utilization Over Time')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Value proposition scatter
        if len(memory_results) > 1:
            memory_costs = [r['cost'] for r in memory_results]
            memory_qualities = [self.calculate_simple_quality_scores([r]) for r in memory_results]
            memory_insights = [r['memory_insights_used'] for r in memory_results]
            
            scatter = ax4.scatter(memory_costs, memory_qualities, 
                                c=memory_insights, cmap='viridis', 
                                s=100, alpha=0.7)
            ax4.set_xlabel('Cost ($)')
            ax4.set_ylabel('Quality Score')
            ax4.set_title('Cost vs Quality (Color = Insights Used)')
            plt.colorbar(scatter, ax=ax4, label='Insights Used')
        
        plt.tight_layout()
        plt.savefig('collective_memory_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n📊 Analysis visualization saved as 'collective_memory_analysis.png'")

def main():
    """Main analysis function"""
    
    analyzer = CollectiveMemoryAnalyzer()
    analyzer.analyze_collective_memory_contribution()

if __name__ == "__main__":
    main()

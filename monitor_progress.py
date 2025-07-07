#!/usr/bin/env python3
"""
Monitor experiment progress by checking intermediate results
"""

import os
import json
import glob
from datetime import datetime

def monitor_progress():
    """Monitor the progress of the running experiment"""
    results_dir = "results"
    
    if not os.path.exists(results_dir):
        print("No results directory found. Experiment may not have started yet.")
        return
    
    # Look for intermediate results
    intermediate_files = glob.glob(os.path.join(results_dir, "intermediate_results_*.json"))
    
    if not intermediate_files:
        print("No intermediate results found yet. Experiment may be starting...")
        return
    
    # Get the latest intermediate file
    latest_file = max(intermediate_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        # Extract progress info
        completed_experiments = len(set(r['problem_id'] for r in results if r and 'problem_id' in r))
        total_results = len([r for r in results if r])
        
        print(f"Progress Update ({datetime.now().strftime('%H:%M:%S')}):")
        print(f"  Latest file: {os.path.basename(latest_file)}")
        print(f"  Completed experiments: {completed_experiments}/10")
        print(f"  Total results recorded: {total_results}")
        
        # Show recent results summary
        if results:
            recent_results = [r for r in results[-6:] if r]  # Last 6 results
            
            print(f"\nRecent Results:")
            for result in recent_results:
                if 'evaluation' in result and result['evaluation']:
                    overall_score = result['evaluation'].get('overall', 0)
                    print(f"  {result['approach'][:15]:15} | Problem {result.get('problem_id', '?')} | Score: {overall_score:.2f}")
                else:
                    print(f"  {result['approach'][:15]:15} | Problem {result.get('problem_id', '?')} | Evaluating...")
        
        # Estimate remaining time
        if completed_experiments > 0:
            avg_time_per_experiment = 180  # Rough estimate: 3 minutes per experiment set
            remaining_experiments = 10 - completed_experiments
            estimated_remaining = remaining_experiments * avg_time_per_experiment / 60
            print(f"\nEstimated remaining time: ~{estimated_remaining:.1f} minutes")
        
    except Exception as e:
        print(f"Error reading progress: {e}")

if __name__ == "__main__":
    monitor_progress()

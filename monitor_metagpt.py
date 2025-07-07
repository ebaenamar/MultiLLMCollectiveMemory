#!/usr/bin/env python3
"""
MetaGPT Experiment Monitor
Real-time monitoring of MetaGPT experiment progress
"""

import json
import time
import os
from datetime import datetime

def monitor_experiment():
    """Monitor MetaGPT experiment progress"""
    
    print("🔍 MetaGPT Experiment Monitor")
    print("=" * 50)
    
    while True:
        try:
            # Check if results file exists
            if os.path.exists("metagpt_results.json"):
                with open("metagpt_results.json", 'r') as f:
                    results = json.load(f)
                
                if results:
                    # Count completed tasks
                    tasks_completed = len(set(r['task_id'] for r in results))
                    single_agent_count = len([r for r in results if r['approach'] == 'single_agent'])
                    multi_agent_count = len([r for r in results if r['approach'] == 'multi_agent'])
                    
                    # Calculate costs
                    total_cost = sum(r['cost'] for r in results)
                    single_cost = sum(r['cost'] for r in results if r['approach'] == 'single_agent')
                    multi_cost = sum(r['cost'] for r in results if r['approach'] == 'multi_agent')
                    
                    # Calculate tokens
                    total_tokens = sum(r['total_tokens'] for r in results)
                    
                    print(f"\n📊 Progress Update - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"Tasks Completed: {tasks_completed}/10")
                    print(f"Single Agent: {single_agent_count} | Multi Agent: {multi_agent_count}")
                    print(f"Total Cost: ${total_cost:.4f}")
                    print(f"  Single: ${single_cost:.4f} | Multi: ${multi_cost:.4f}")
                    print(f"Total Tokens: {total_tokens:,}")
                    
                    if tasks_completed >= 10:
                        print("\n✅ Experiment completed!")
                        break
                else:
                    print(f"📝 Results file exists but empty - {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"⏳ Waiting for results file - {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_experiment()

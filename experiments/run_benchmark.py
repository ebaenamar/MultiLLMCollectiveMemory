"""
Main benchmark execution script for multi-LLM collective memory research.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path

# Import memory systems
from memory_systems.base_memory import NoMemorySystem, MemoryMetrics
from memory_systems.shared_memory import SharedMemorySystem
from memory_systems.private_memory import PrivateMemoryManager

# Import agents
from agents.specialized_agents import (
    SystemArchitectAgent, SensorExpertAgent, MLEngineerAgent,
    ImplementationPlannerAgent, EvaluatorAgent, AgentOrchestrator
)


class BenchmarkConfiguration:
    """Configuration for benchmark experiments."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.experiment_id = config_dict.get('experiment_id', f"exp_{uuid.uuid4().hex[:8]}")
        self.configurations = config_dict.get('configurations', [])
        self.task_description = config_dict.get('task_description', "")
        self.output_dir = config_dict.get('output_dir', "./results")
        self.iterations = config_dict.get('iterations', 1)
        self.timeout_minutes = config_dict.get('timeout_minutes', 30)


class BenchmarkRunner:
    """Main benchmark execution engine."""
    
    def __init__(self, config: BenchmarkConfiguration):
        self.config = config
        self.results = {}
        
        # Ensure output directory exists
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def run_single_agent_baseline(self, task: str, iteration: int) -> Dict[str, Any]:
        """Run single agent baseline configuration."""
        print(f"Running Single Agent Baseline - Iteration {iteration}")
        
        start_time = time.time()
        
        # Use no memory system for baseline
        memory_system = NoMemorySystem("single_agent_baseline")
        
        # Create a single "generalist" agent that handles all aspects
        architect = SystemArchitectAgent(memory_system)
        
        # Process the complete task
        response = architect.process_task(task)
        
        end_time = time.time()
        
        return {
            'configuration': 'single_agent_baseline',
            'iteration': iteration,
            'execution_time_seconds': end_time - start_time,
            'response': {
                'content': response.content,
                'confidence_score': response.confidence_score,
                'reasoning_steps': response.reasoning_steps
            },
            'memory_stats': memory_system.get_access_stats(),
            'token_usage_estimate': len(response.content.split()) * 1.3,  # Rough estimate
            'timestamp': datetime.now().isoformat()
        }
    
    def run_multi_agent_no_memory(self, task: str, iteration: int) -> Dict[str, Any]:
        """Run multi-agent configuration without persistent memory."""
        print(f"Running Multi-Agent No Memory - Iteration {iteration}")
        
        start_time = time.time()
        
        # Use no memory system
        memory_system = NoMemorySystem("multi_agent_no_memory")
        
        # Create specialized agents
        agents = [
            SystemArchitectAgent(memory_system),
            SensorExpertAgent(memory_system),
            MLEngineerAgent(memory_system),
            ImplementationPlannerAgent(memory_system),
            EvaluatorAgent(memory_system)
        ]
        
        orchestrator = AgentOrchestrator(agents)
        responses = orchestrator.coordinate_task(task)
        
        end_time = time.time()
        
        # Combine responses
        combined_content = "\n\n".join([
            f"## {agent_id.replace('_', ' ').title()} Response:\n{response.content}"
            for agent_id, response in responses.items()
        ])
        
        avg_confidence = sum(r.confidence_score for r in responses.values()) / len(responses)
        total_tokens = sum(len(r.content.split()) * 1.3 for r in responses.values())
        
        return {
            'configuration': 'multi_agent_no_memory',
            'iteration': iteration,
            'execution_time_seconds': end_time - start_time,
            'responses': {
                agent_id: {
                    'content': response.content,
                    'confidence_score': response.confidence_score,
                    'reasoning_steps': response.reasoning_steps
                }
                for agent_id, response in responses.items()
            },
            'combined_response': combined_content,
            'average_confidence': avg_confidence,
            'memory_stats': memory_system.get_access_stats(),
            'collaboration_metrics': orchestrator.get_collaboration_metrics(),
            'token_usage_estimate': total_tokens,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_multi_agent_shared_memory(self, task: str, iteration: int) -> Dict[str, Any]:
        """Run multi-agent configuration with shared memory."""
        print(f"Running Multi-Agent Shared Memory - Iteration {iteration}")
        
        start_time = time.time()
        
        # Use shared memory system
        memory_system = SharedMemorySystem(
            f"shared_memory_exp_{iteration}",
            storage_path=os.path.join(self.config.output_dir, "memory_data")
        )
        
        # Create specialized agents sharing the same memory
        agents = [
            SystemArchitectAgent(memory_system),
            SensorExpertAgent(memory_system),
            MLEngineerAgent(memory_system),
            ImplementationPlannerAgent(memory_system),
            EvaluatorAgent(memory_system)
        ]
        
        orchestrator = AgentOrchestrator(agents)
        responses = orchestrator.coordinate_task(task)
        
        end_time = time.time()
        
        # Export memory for analysis
        memory_export_path = os.path.join(
            self.config.output_dir, 
            f"shared_memory_export_iter_{iteration}.json"
        )
        memory_system.export_memory(memory_export_path)
        
        # Combine responses
        combined_content = "\n\n".join([
            f"## {agent_id.replace('_', ' ').title()} Response:\n{response.content}"
            for agent_id, response in responses.items()
        ])
        
        avg_confidence = sum(r.confidence_score for r in responses.values()) / len(responses)
        total_tokens = sum(len(r.content.split()) * 1.3 for r in responses.values())
        
        # Calculate memory metrics
        memory_stats = memory_system.get_access_stats()
        redundancy_reduction = MemoryMetrics.calculate_redundancy_reduction(memory_stats['access_log'])
        knowledge_reuse = MemoryMetrics.calculate_knowledge_reuse_rate(memory_stats['access_log'])
        memory_utilization = MemoryMetrics.calculate_memory_utilization(memory_system)
        
        return {
            'configuration': 'multi_agent_shared_memory',
            'iteration': iteration,
            'execution_time_seconds': end_time - start_time,
            'responses': {
                agent_id: {
                    'content': response.content,
                    'confidence_score': response.confidence_score,
                    'reasoning_steps': response.reasoning_steps,
                    'memory_entries_created': response.memory_entries_created,
                    'memory_queries_made': response.memory_queries_made
                }
                for agent_id, response in responses.items()
            },
            'combined_response': combined_content,
            'average_confidence': avg_confidence,
            'memory_stats': memory_stats,
            'memory_metrics': {
                'redundancy_reduction_percent': redundancy_reduction,
                'knowledge_reuse_rate_percent': knowledge_reuse,
                'memory_utilization': memory_utilization
            },
            'memory_summary': memory_system.get_memory_summary(),
            'collaboration_metrics': orchestrator.get_collaboration_metrics(),
            'token_usage_estimate': total_tokens,
            'memory_export_path': memory_export_path,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_multi_agent_private_memory(self, task: str, iteration: int) -> Dict[str, Any]:
        """Run multi-agent configuration with private memory per agent."""
        print(f"Running Multi-Agent Private Memory - Iteration {iteration}")
        
        start_time = time.time()
        
        # Use private memory manager
        memory_manager = PrivateMemoryManager(
            f"private_memory_exp_{iteration}",
            storage_path=os.path.join(self.config.output_dir, "memory_data")
        )
        
        # Create specialized agents with individual private memories
        agents = [
            SystemArchitectAgent(memory_manager.get_agent_memory("system_architect")),
            SensorExpertAgent(memory_manager.get_agent_memory("sensor_expert")),
            MLEngineerAgent(memory_manager.get_agent_memory("ml_engineer")),
            ImplementationPlannerAgent(memory_manager.get_agent_memory("implementation_planner")),
            EvaluatorAgent(memory_manager.get_agent_memory("evaluator"))
        ]
        
        orchestrator = AgentOrchestrator(agents)
        responses = orchestrator.coordinate_task(task)
        
        end_time = time.time()
        
        # Export all private memories
        private_memory_dir = os.path.join(self.config.output_dir, f"private_memories_iter_{iteration}")
        memory_manager.export_all_memories(private_memory_dir)
        
        # Combine responses
        combined_content = "\n\n".join([
            f"## {agent_id.replace('_', ' ').title()} Response:\n{response.content}"
            for agent_id, response in responses.items()
        ])
        
        avg_confidence = sum(r.confidence_score for r in responses.values()) / len(responses)
        total_tokens = sum(len(r.content.split()) * 1.3 for r in responses.values())
        
        # Aggregate memory stats from all agents
        all_memory_stats = {}
        total_memory_ops = 0
        
        for agent_id, memory_system in memory_manager.get_all_memories().items():
            stats = memory_system.get_access_stats()
            all_memory_stats[agent_id] = stats
            total_memory_ops += stats['total_accesses']
        
        return {
            'configuration': 'multi_agent_private_memory',
            'iteration': iteration,
            'execution_time_seconds': end_time - start_time,
            'responses': {
                agent_id: {
                    'content': response.content,
                    'confidence_score': response.confidence_score,
                    'reasoning_steps': response.reasoning_steps,
                    'memory_entries_created': response.memory_entries_created,
                    'memory_queries_made': response.memory_queries_made
                }
                for agent_id, response in responses.items()
            },
            'combined_response': combined_content,
            'average_confidence': avg_confidence,
            'memory_stats_by_agent': all_memory_stats,
            'total_memory_operations': total_memory_ops,
            'collaboration_metrics': orchestrator.get_collaboration_metrics(),
            'token_usage_estimate': total_tokens,
            'private_memory_export_dir': private_memory_dir,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_configuration(self, config_name: str, task: str, iteration: int) -> Dict[str, Any]:
        """Run a specific configuration."""
        if config_name == "single_agent_baseline":
            return self.run_single_agent_baseline(task, iteration)
        elif config_name == "multi_agent_no_memory":
            return self.run_multi_agent_no_memory(task, iteration)
        elif config_name == "multi_agent_shared_memory":
            return self.run_multi_agent_shared_memory(task, iteration)
        elif config_name == "multi_agent_private_memory":
            return self.run_multi_agent_private_memory(task, iteration)
        else:
            raise ValueError(f"Unknown configuration: {config_name}")
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run the complete benchmark across all configurations."""
        print(f"Starting benchmark experiment: {self.config.experiment_id}")
        print(f"Task: {self.config.task_description}")
        print(f"Configurations: {self.config.configurations}")
        print(f"Iterations per configuration: {self.config.iterations}")
        
        benchmark_start_time = time.time()
        
        for config_name in self.config.configurations:
            print(f"\n{'='*60}")
            print(f"Running configuration: {config_name}")
            print(f"{'='*60}")
            
            config_results = []
            
            for iteration in range(1, self.config.iterations + 1):
                try:
                    result = self.run_configuration(config_name, self.config.task_description, iteration)
                    config_results.append(result)
                    
                    print(f"Completed iteration {iteration}/{self.config.iterations}")
                    
                except Exception as e:
                    print(f"Error in iteration {iteration}: {e}")
                    config_results.append({
                        'configuration': config_name,
                        'iteration': iteration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.results[config_name] = config_results
        
        benchmark_end_time = time.time()
        
        # Save results
        results_summary = {
            'experiment_id': self.config.experiment_id,
            'task_description': self.config.task_description,
            'configurations_tested': self.config.configurations,
            'iterations_per_config': self.config.iterations,
            'total_execution_time_seconds': benchmark_end_time - benchmark_start_time,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        results_file = os.path.join(
            self.config.output_dir, 
            f"benchmark_results_{self.config.experiment_id}.json"
        )
        
        with open(results_file, 'w') as f:
            json.dump(results_summary, f, indent=2, default=str)
        
        print(f"\n{'='*60}")
        print(f"Benchmark completed!")
        print(f"Total execution time: {benchmark_end_time - benchmark_start_time:.2f} seconds")
        print(f"Results saved to: {results_file}")
        print(f"{'='*60}")
        
        return results_summary


def load_config(config_path: str) -> BenchmarkConfiguration:
    """Load benchmark configuration from file."""
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    return BenchmarkConfiguration(config_dict)


def create_default_config() -> Dict[str, Any]:
    """Create default benchmark configuration."""
    return {
        "experiment_id": f"traffic_control_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "task_description": """Design an intelligent traffic control system using sensors, edge computing, and AI-based prediction for a medium-sized city. Provide:
1. Overall system architecture and component integration
2. Sensor hardware specifications and deployment strategy  
3. Machine learning algorithms and model architecture
4. Implementation phases and timeline
5. Success metrics and evaluation framework

The system should handle 200+ intersections, support real-time decision making (<100ms), and achieve 20-30% reduction in travel times.""",
        "configurations": [
            "single_agent_baseline",
            "multi_agent_no_memory", 
            "multi_agent_shared_memory",
            "multi_agent_private_memory"
        ],
        "iterations": 3,
        "timeout_minutes": 30,
        "output_dir": "./results"
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Multi-LLM Collective Memory Benchmark")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--create-config", action="store_true", help="Create default config file")
    parser.add_argument("--output-dir", type=str, default="./results", help="Output directory")
    
    args = parser.parse_args()
    
    if args.create_config:
        config_dict = create_default_config()
        config_dict["output_dir"] = args.output_dir
        
        config_path = "benchmark_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"Default configuration created: {config_path}")
        print("Edit the configuration file and run with --config flag")
        return
    
    if args.config:
        config = load_config(args.config)
    else:
        print("Creating default configuration...")
        config_dict = create_default_config()
        config_dict["output_dir"] = args.output_dir
        config = BenchmarkConfiguration(config_dict)
    
    # Run benchmark
    runner = BenchmarkRunner(config)
    results = runner.run_benchmark()
    
    print(f"\nBenchmark Summary:")
    print(f"Experiment ID: {results['experiment_id']}")
    print(f"Configurations tested: {len(results['configurations_tested'])}")
    print(f"Total execution time: {results['total_execution_time_seconds']:.2f} seconds")


if __name__ == "__main__":
    main()

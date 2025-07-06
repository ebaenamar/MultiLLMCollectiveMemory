"""
Base memory system interface for multi-LLM collective memory research.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    agent_id: str
    tags: List[str]
    importance_score: float = 0.0


class BaseMemorySystem(ABC):
    """Abstract base class for memory systems."""
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.access_log: List[Dict[str, Any]] = []
    
    @abstractmethod
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve relevant memory entries."""
        pass
    
    @abstractmethod
    def update(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        pass
    
    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        pass
    
    def log_access(self, operation: str, agent_id: str, details: Dict[str, Any]):
        """Log memory access for analysis."""
        self.access_log.append({
            'timestamp': datetime.now(),
            'operation': operation,
            'agent_id': agent_id,
            'details': details
        })
    
    def get_access_stats(self) -> Dict[str, Any]:
        """Get memory access statistics."""
        total_accesses = len(self.access_log)
        operations = {}
        agents = {}
        
        for log in self.access_log:
            op = log['operation']
            agent = log['agent_id']
            
            operations[op] = operations.get(op, 0) + 1
            agents[agent] = agents.get(agent, 0) + 1
        
        return {
            'total_accesses': total_accesses,
            'operations': operations,
            'agents': agents,
            'access_log': self.access_log
        }


class NoMemorySystem(BaseMemorySystem):
    """Memory system that stores nothing - for baseline comparison."""
    
    def store(self, entry: MemoryEntry) -> bool:
        self.log_access('store_attempted', entry.agent_id, {'entry_id': entry.id})
        return True  # Pretend to store but do nothing
    
    def retrieve(self, query: str, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        self.log_access('retrieve', agent_id, {'query': query, 'limit': limit})
        return []  # Always return empty
    
    def update(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        return True
    
    def delete(self, entry_id: str) -> bool:
        return True


class MemoryMetrics:
    """Utility class for calculating memory-related metrics."""
    
    @staticmethod
    def calculate_redundancy_reduction(access_logs: List[Dict[str, Any]]) -> float:
        """Calculate percentage of redundant computations avoided."""
        retrieval_queries = [log for log in access_logs if log['operation'] == 'retrieve']
        if not retrieval_queries:
            return 0.0
        
        successful_retrievals = sum(1 for log in retrieval_queries 
                                  if log['details'].get('results_found', 0) > 0)
        
        return (successful_retrievals / len(retrieval_queries)) * 100
    
    @staticmethod
    def calculate_knowledge_reuse_rate(access_logs: List[Dict[str, Any]]) -> float:
        """Calculate rate of knowledge reuse across agents."""
        cross_agent_retrievals = 0
        total_retrievals = 0
        
        for log in access_logs:
            if log['operation'] == 'retrieve':
                total_retrievals += 1
                # Check if retrieved content was created by different agent
                # This would need to be tracked in the details
                if log['details'].get('cross_agent_access', False):
                    cross_agent_retrievals += 1
        
        return (cross_agent_retrievals / total_retrievals * 100) if total_retrievals > 0 else 0.0
    
    @staticmethod
    def calculate_memory_utilization(memory_system: BaseMemorySystem) -> Dict[str, float]:
        """Calculate various memory utilization metrics."""
        stats = memory_system.get_access_stats()
        
        reads = stats['operations'].get('retrieve', 0)
        writes = stats['operations'].get('store', 0)
        total_ops = reads + writes
        
        return {
            'read_write_ratio': reads / writes if writes > 0 else 0,
            'total_operations': total_ops,
            'unique_agents': len(stats['agents']),
            'avg_ops_per_agent': total_ops / len(stats['agents']) if stats['agents'] else 0
        }

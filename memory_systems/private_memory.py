"""
Private memory system implementation - each agent has isolated memory.
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_memory import BaseMemorySystem, MemoryEntry


class PrivateMemorySystem(BaseMemorySystem):
    """Private memory system - each agent has isolated memory storage."""
    
    def __init__(self, system_id: str, agent_id: str, storage_path: str = "./memory_data"):
        super().__init__(system_id)
        self.agent_id = agent_id
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, f"private_memory_{system_id}_{agent_id}.json")
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize JSON storage
        if not os.path.exists(self.json_file):
            self._save_json({})
    
    def _load_json(self) -> Dict[str, Any]:
        """Load memory data from JSON file."""
        try:
            with open(self.json_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, data: Dict[str, Any]):
        """Save memory data to JSON file."""
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry (only for the owning agent)."""
        # Ensure only the owning agent can store in their private memory
        if entry.agent_id != self.agent_id:
            self.log_access('store_denied', entry.agent_id, {
                'entry_id': entry.id,
                'reason': 'cross_agent_access_denied'
            })
            return False
        
        try:
            data = self._load_json()
            data[entry.id] = {
                'content': entry.content,
                'metadata': entry.metadata,
                'timestamp': entry.timestamp.isoformat(),
                'agent_id': entry.agent_id,
                'tags': entry.tags,
                'importance_score': entry.importance_score
            }
            self._save_json(data)
            
            self.log_access('store', entry.agent_id, {
                'entry_id': entry.id,
                'content_length': len(entry.content),
                'tags': entry.tags
            })
            
            return True
            
        except Exception as e:
            print(f"Error storing private memory entry: {e}")
            return False
    
    def retrieve(self, query: str, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memory entries (only for the owning agent)."""
        # Only the owning agent can access their private memory
        if agent_id != self.agent_id:
            self.log_access('retrieve_denied', agent_id, {
                'query': query,
                'reason': 'cross_agent_access_denied'
            })
            return []
        
        try:
            data = self._load_json()
            results = []
            query_lower = query.lower()
            
            # Simple keyword-based search within private memory
            for entry_id, entry_data in data.items():
                content_lower = entry_data['content'].lower()
                if (query_lower in content_lower or 
                    any(tag.lower() in query_lower for tag in entry_data['tags']) or
                    any(query_lower in str(v).lower() for v in entry_data['metadata'].values())):
                    
                    entry = MemoryEntry(
                        id=entry_id,
                        content=entry_data['content'],
                        metadata=entry_data['metadata'],
                        timestamp=datetime.fromisoformat(entry_data['timestamp']),
                        agent_id=entry_data['agent_id'],
                        tags=entry_data['tags'],
                        importance_score=entry_data['importance_score']
                    )
                    results.append(entry)
            
            # Sort by importance score and timestamp, then limit
            results.sort(key=lambda x: (x.importance_score, x.timestamp), reverse=True)
            results = results[:limit]
            
            self.log_access('retrieve', agent_id, {
                'query': query,
                'results_found': len(results),
                'cross_agent_access': False,  # Always false for private memory
                'limit': limit
            })
            
            return results
            
        except Exception as e:
            print(f"Error retrieving private memory entries: {e}")
            self.log_access('retrieve_error', agent_id, {'query': query, 'error': str(e)})
            return []
    
    def update(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        try:
            data = self._load_json()
            
            if entry_id not in data:
                return False
            
            # Ensure only the owning agent can update their entries
            if data[entry_id]['agent_id'] != self.agent_id:
                return False
            
            # Update data
            for key, value in updates.items():
                if key in data[entry_id]:
                    data[entry_id][key] = value
            
            data[entry_id]['timestamp'] = datetime.now().isoformat()
            self._save_json(data)
            
            self.log_access('update', self.agent_id, {
                'entry_id': entry_id,
                'updates': list(updates.keys())
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating private memory entry: {e}")
            return False
    
    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        try:
            data = self._load_json()
            
            if entry_id not in data:
                return False
            
            # Ensure only the owning agent can delete their entries
            if data[entry_id]['agent_id'] != self.agent_id:
                return False
            
            del data[entry_id]
            self._save_json(data)
            
            self.log_access('delete', self.agent_id, {'entry_id': entry_id})
            return True
            
        except Exception as e:
            print(f"Error deleting private memory entry: {e}")
            return False
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the private memory contents."""
        data = self._load_json()
        
        if not data:
            return {
                'total_entries': 0,
                'agent_id': self.agent_id,
                'tags': [],
                'latest_update': None
            }
        
        all_tags = set()
        for entry_data in data.values():
            all_tags.update(entry_data['tags'])
        
        return {
            'total_entries': len(data),
            'agent_id': self.agent_id,
            'tags': list(all_tags),
            'latest_update': max(
                datetime.fromisoformat(entry['timestamp']) 
                for entry in data.values()
            ).isoformat() if data else None
        }
    
    def export_memory(self, filepath: str) -> bool:
        """Export private memory data to a file for analysis."""
        try:
            data = self._load_json()
            stats = self.get_access_stats()
            summary = self.get_memory_summary()
            
            export_data = {
                'agent_id': self.agent_id,
                'memory_data': data,
                'access_stats': stats,
                'summary': summary,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting private memory: {e}")
            return False
    
    def share_knowledge(self, entry_ids: List[str], target_agent_memory: 'PrivateMemorySystem') -> bool:
        """
        Share specific knowledge entries with another agent's private memory.
        This simulates controlled knowledge sharing between agents.
        """
        try:
            data = self._load_json()
            shared_count = 0
            
            for entry_id in entry_ids:
                if entry_id in data:
                    entry_data = data[entry_id]
                    
                    # Create a new entry for the target agent
                    shared_entry = MemoryEntry(
                        id=f"shared_{uuid.uuid4().hex[:8]}_{entry_id}",
                        content=f"[SHARED FROM {self.agent_id}] {entry_data['content']}",
                        metadata={
                            **entry_data['metadata'],
                            'shared_from': self.agent_id,
                            'original_id': entry_id
                        },
                        timestamp=datetime.now(),
                        agent_id=target_agent_memory.agent_id,
                        tags=entry_data['tags'] + ['shared_knowledge'],
                        importance_score=entry_data['importance_score'] * 0.8  # Slightly reduce importance
                    )
                    
                    if target_agent_memory.store(shared_entry):
                        shared_count += 1
            
            self.log_access('share_knowledge', self.agent_id, {
                'target_agent': target_agent_memory.agent_id,
                'entries_shared': shared_count,
                'total_requested': len(entry_ids)
            })
            
            return shared_count > 0
            
        except Exception as e:
            print(f"Error sharing knowledge: {e}")
            return False


class PrivateMemoryManager:
    """Manager for multiple private memory systems."""
    
    def __init__(self, system_id: str, storage_path: str = "./memory_data"):
        self.system_id = system_id
        self.storage_path = storage_path
        self.agent_memories: Dict[str, PrivateMemorySystem] = {}
    
    def get_agent_memory(self, agent_id: str) -> PrivateMemorySystem:
        """Get or create private memory for an agent."""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = PrivateMemorySystem(
                self.system_id, agent_id, self.storage_path
            )
        return self.agent_memories[agent_id]
    
    def get_all_memories(self) -> Dict[str, PrivateMemorySystem]:
        """Get all agent memories."""
        return self.agent_memories.copy()
    
    def export_all_memories(self, output_dir: str) -> bool:
        """Export all agent memories for analysis."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for agent_id, memory in self.agent_memories.items():
                filepath = os.path.join(output_dir, f"private_memory_{agent_id}.json")
                memory.export_memory(filepath)
            
            # Create summary file
            summary = {
                'system_id': self.system_id,
                'total_agents': len(self.agent_memories),
                'agent_summaries': {
                    agent_id: memory.get_memory_summary()
                    for agent_id, memory in self.agent_memories.items()
                },
                'export_timestamp': datetime.now().isoformat()
            }
            
            summary_path = os.path.join(output_dir, "private_memories_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting all memories: {e}")
            return False

"""
Shared memory system implementation using JSON storage and ChromaDB for semantic search.
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings

from .base_memory import BaseMemorySystem, MemoryEntry


class SharedMemorySystem(BaseMemorySystem):
    """Shared memory system accessible by all agents."""
    
    def __init__(self, system_id: str, storage_path: str = "./memory_data", 
                 chroma_host: str = "localhost", chroma_port: int = 8000):
        super().__init__(system_id)
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, f"shared_memory_{system_id}.json")
        
        # Initialize ChromaDB for semantic search
        try:
            self.chroma_client = chromadb.HttpClient(
                host=chroma_host, 
                port=chroma_port,
                settings=Settings(allow_reset=True)
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name=f"shared_memory_{system_id}"
            )
        except Exception as e:
            print(f"Warning: ChromaDB not available, using basic search: {e}")
            self.chroma_client = None
            self.collection = None
        
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
        """Store a memory entry in both JSON and vector database."""
        try:
            # Store in JSON
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
            
            # Store in ChromaDB for semantic search
            if self.collection is not None:
                self.collection.add(
                    documents=[entry.content],
                    metadatas=[{
                        'agent_id': entry.agent_id,
                        'timestamp': entry.timestamp.isoformat(),
                        'tags': ','.join(entry.tags),
                        'importance_score': entry.importance_score,
                        **entry.metadata
                    }],
                    ids=[entry.id]
                )
            
            self.log_access('store', entry.agent_id, {
                'entry_id': entry.id,
                'content_length': len(entry.content),
                'tags': entry.tags
            })
            
            return True
            
        except Exception as e:
            print(f"Error storing memory entry: {e}")
            return False
    
    def retrieve(self, query: str, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve relevant memory entries using semantic search."""
        try:
            results = []
            
            if self.collection is not None:
                # Use ChromaDB for semantic search
                search_results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                if search_results['ids'] and search_results['ids'][0]:
                    data = self._load_json()
                    
                    for entry_id in search_results['ids'][0]:
                        if entry_id in data:
                            entry_data = data[entry_id]
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
            else:
                # Fallback to basic keyword search
                data = self._load_json()
                query_lower = query.lower()
                
                for entry_id, entry_data in data.items():
                    content_lower = entry_data['content'].lower()
                    if (query_lower in content_lower or 
                        any(tag.lower() in query_lower for tag in entry_data['tags'])):
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
                
                # Sort by importance score and limit
                results.sort(key=lambda x: x.importance_score, reverse=True)
                results = results[:limit]
            
            # Check for cross-agent access
            cross_agent_access = any(entry.agent_id != agent_id for entry in results)
            
            self.log_access('retrieve', agent_id, {
                'query': query,
                'results_found': len(results),
                'cross_agent_access': cross_agent_access,
                'limit': limit
            })
            
            return results
            
        except Exception as e:
            print(f"Error retrieving memory entries: {e}")
            self.log_access('retrieve_error', agent_id, {'query': query, 'error': str(e)})
            return []
    
    def update(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        try:
            data = self._load_json()
            
            if entry_id not in data:
                return False
            
            # Update JSON data
            for key, value in updates.items():
                if key in data[entry_id]:
                    data[entry_id][key] = value
            
            data[entry_id]['timestamp'] = datetime.now().isoformat()
            self._save_json(data)
            
            # Update ChromaDB if available
            if self.collection is not None:
                try:
                    self.collection.update(
                        ids=[entry_id],
                        documents=[data[entry_id]['content']],
                        metadatas=[{
                            'agent_id': data[entry_id]['agent_id'],
                            'timestamp': data[entry_id]['timestamp'],
                            'tags': ','.join(data[entry_id]['tags']),
                            'importance_score': data[entry_id]['importance_score'],
                            **data[entry_id]['metadata']
                        }]
                    )
                except Exception as e:
                    print(f"Warning: ChromaDB update failed: {e}")
            
            self.log_access('update', data[entry_id]['agent_id'], {
                'entry_id': entry_id,
                'updates': list(updates.keys())
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating memory entry: {e}")
            return False
    
    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        try:
            data = self._load_json()
            
            if entry_id not in data:
                return False
            
            agent_id = data[entry_id]['agent_id']
            del data[entry_id]
            self._save_json(data)
            
            # Delete from ChromaDB if available
            if self.collection is not None:
                try:
                    self.collection.delete(ids=[entry_id])
                except Exception as e:
                    print(f"Warning: ChromaDB delete failed: {e}")
            
            self.log_access('delete', agent_id, {'entry_id': entry_id})
            return True
            
        except Exception as e:
            print(f"Error deleting memory entry: {e}")
            return False
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the shared memory contents."""
        data = self._load_json()
        
        if not data:
            return {'total_entries': 0, 'agents': [], 'tags': []}
        
        agents = set()
        all_tags = set()
        
        for entry_data in data.values():
            agents.add(entry_data['agent_id'])
            all_tags.update(entry_data['tags'])
        
        return {
            'total_entries': len(data),
            'agents': list(agents),
            'tags': list(all_tags),
            'latest_update': max(
                datetime.fromisoformat(entry['timestamp']) 
                for entry in data.values()
            ).isoformat() if data else None
        }
    
    def export_memory(self, filepath: str) -> bool:
        """Export memory data to a file for analysis."""
        try:
            data = self._load_json()
            stats = self.get_access_stats()
            summary = self.get_memory_summary()
            
            export_data = {
                'memory_data': data,
                'access_stats': stats,
                'summary': summary,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting memory: {e}")
            return False

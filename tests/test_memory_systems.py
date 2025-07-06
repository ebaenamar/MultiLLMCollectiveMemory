#!/usr/bin/env python3
"""
Unit tests for memory systems in the Multi-LLM Collective Memory benchmark.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_systems.base_memory import BaseMemorySystem, MemoryEntry, NoMemorySystem, MemoryMetrics
from memory_systems.shared_memory import SharedMemorySystem
from memory_systems.private_memory import PrivateMemorySystem, PrivateMemoryManager


class TestMemoryEntry(unittest.TestCase):
    """Test MemoryEntry dataclass functionality."""
    
    def test_memory_entry_creation(self):
        """Test basic memory entry creation."""
        entry = MemoryEntry(
            key="test_key",
            content="Test content",
            agent_id="test_agent",
            metadata={"type": "test", "priority": 1}
        )
        
        self.assertEqual(entry.key, "test_key")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.agent_id, "test_agent")
        self.assertEqual(entry.metadata["type"], "test")
        self.assertIsNotNone(entry.timestamp)
    
    def test_memory_entry_to_dict(self):
        """Test memory entry serialization."""
        entry = MemoryEntry("key", "content", "agent", {"test": True})
        entry_dict = entry.to_dict()
        
        self.assertIn("key", entry_dict)
        self.assertIn("content", entry_dict)
        self.assertIn("agent_id", entry_dict)
        self.assertIn("metadata", entry_dict)
        self.assertIn("timestamp", entry_dict)


class TestNoMemorySystem(unittest.TestCase):
    """Test NoMemorySystem (baseline) functionality."""
    
    def setUp(self):
        self.memory = NoMemorySystem()
    
    def test_store_does_nothing(self):
        """Test that store operation does nothing."""
        entry = MemoryEntry("key", "content", "agent", {})
        result = self.memory.store(entry)
        self.assertTrue(result)  # Should return True but do nothing
    
    def test_retrieve_returns_empty(self):
        """Test that retrieve always returns empty list."""
        result = self.memory.retrieve("any_key")
        self.assertEqual(result, [])
    
    def test_update_does_nothing(self):
        """Test that update operation does nothing."""
        result = self.memory.update("key", {"new": "content"})
        self.assertTrue(result)
    
    def test_delete_does_nothing(self):
        """Test that delete operation does nothing."""
        result = self.memory.delete("key")
        self.assertTrue(result)
    
    def test_get_summary(self):
        """Test summary returns zero stats."""
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_entries"], 0)
        self.assertEqual(summary["total_agents"], 0)


class TestSharedMemorySystem(unittest.TestCase):
    """Test SharedMemorySystem functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = os.path.join(self.temp_dir, "test_memory.json")
        self.memory = SharedMemorySystem(self.memory_file)
    
    def tearDown(self):
        # Clean up temp files
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
        os.rmdir(self.temp_dir)
    
    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations."""
        entry = MemoryEntry("test_key", "test content", "agent1", {"type": "test"})
        
        # Store entry
        result = self.memory.store(entry)
        self.assertTrue(result)
        
        # Retrieve entry
        retrieved = self.memory.retrieve("test_key")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]["content"], "test content")
        self.assertEqual(retrieved[0]["agent_id"], "agent1")
    
    def test_update_entry(self):
        """Test updating existing entry."""
        entry = MemoryEntry("update_key", "original content", "agent1", {})
        self.memory.store(entry)
        
        # Update entry
        result = self.memory.update("update_key", {"content": "updated content"})
        self.assertTrue(result)
        
        # Verify update
        retrieved = self.memory.retrieve("update_key")
        self.assertEqual(retrieved[0]["content"], "updated content")
    
    def test_delete_entry(self):
        """Test deleting entry."""
        entry = MemoryEntry("delete_key", "content to delete", "agent1", {})
        self.memory.store(entry)
        
        # Verify entry exists
        retrieved = self.memory.retrieve("delete_key")
        self.assertEqual(len(retrieved), 1)
        
        # Delete entry
        result = self.memory.delete("delete_key")
        self.assertTrue(result)
        
        # Verify entry is gone
        retrieved = self.memory.retrieve("delete_key")
        self.assertEqual(len(retrieved), 0)
    
    def test_search_by_content(self):
        """Test content-based search."""
        entries = [
            MemoryEntry("key1", "machine learning algorithms", "agent1", {}),
            MemoryEntry("key2", "traffic sensor deployment", "agent2", {}),
            MemoryEntry("key3", "neural network architecture", "agent1", {})
        ]
        
        for entry in entries:
            self.memory.store(entry)
        
        # Search for machine learning related content
        results = self.memory.search_by_content("machine learning")
        self.assertGreater(len(results), 0)
        
        # Should find entries with related terms
        found_keys = [r["key"] for r in results]
        self.assertIn("key1", found_keys)  # Direct match
    
    def test_get_summary(self):
        """Test memory summary statistics."""
        entries = [
            MemoryEntry("key1", "content1", "agent1", {}),
            MemoryEntry("key2", "content2", "agent2", {}),
            MemoryEntry("key3", "content3", "agent1", {})
        ]
        
        for entry in entries:
            self.memory.store(entry)
        
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_entries"], 3)
        self.assertEqual(summary["total_agents"], 2)
        self.assertIn("agent1", summary["entries_by_agent"])
        self.assertEqual(summary["entries_by_agent"]["agent1"], 2)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        entry = MemoryEntry("persist_key", "persistent content", "agent1", {})
        self.memory.store(entry)
        
        # Create new instance with same file
        new_memory = SharedMemorySystem(self.memory_file)
        retrieved = new_memory.retrieve("persist_key")
        
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]["content"], "persistent content")


class TestPrivateMemorySystem(unittest.TestCase):
    """Test PrivateMemorySystem functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = os.path.join(self.temp_dir, "private_memory.json")
        self.memory = PrivateMemorySystem("agent1", self.memory_file)
    
    def tearDown(self):
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
        os.rmdir(self.temp_dir)
    
    def test_agent_isolation(self):
        """Test that agents can only access their own memories."""
        entry1 = MemoryEntry("key1", "agent1 content", "agent1", {})
        entry2 = MemoryEntry("key2", "agent2 content", "agent2", {})
        
        self.memory.store(entry1)
        self.memory.store(entry2)  # Should be rejected
        
        # Should only retrieve agent1's entry
        retrieved = self.memory.retrieve("key1")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]["agent_id"], "agent1")
        
        # Should not retrieve agent2's entry
        retrieved = self.memory.retrieve("key2")
        self.assertEqual(len(retrieved), 0)
    
    def test_knowledge_sharing(self):
        """Test controlled knowledge sharing between agents."""
        # Create another agent's memory
        agent2_file = os.path.join(self.temp_dir, "agent2_memory.json")
        agent2_memory = PrivateMemorySystem("agent2", agent2_file)
        
        # Store knowledge in agent2's memory
        shared_entry = MemoryEntry("shared_key", "shared knowledge", "agent2", 
                                 {"shareable": True, "domain": "sensors"})
        agent2_memory.store(shared_entry)
        
        # Agent1 should be able to access shared knowledge
        shared_knowledge = self.memory.get_shared_knowledge([agent2_memory], "sensors")
        self.assertGreater(len(shared_knowledge), 0)
        
        # Clean up
        os.remove(agent2_file)


class TestPrivateMemoryManager(unittest.TestCase):
    """Test PrivateMemoryManager functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PrivateMemoryManager(self.temp_dir)
    
    def tearDown(self):
        # Clean up all created files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_create_agent_memory(self):
        """Test creating memory for new agent."""
        memory = self.manager.get_agent_memory("test_agent")
        self.assertIsInstance(memory, PrivateMemorySystem)
        self.assertEqual(memory.agent_id, "test_agent")
    
    def test_agent_memory_persistence(self):
        """Test that agent memories persist."""
        memory1 = self.manager.get_agent_memory("agent1")
        memory2 = self.manager.get_agent_memory("agent1")  # Same agent
        
        # Should return the same instance
        self.assertIs(memory1, memory2)
    
    def test_multiple_agents(self):
        """Test managing multiple agent memories."""
        agents = ["agent1", "agent2", "agent3"]
        memories = {}
        
        for agent in agents:
            memories[agent] = self.manager.get_agent_memory(agent)
        
        # All should be different instances
        self.assertEqual(len(set(memories.values())), 3)
        
        # Each should have correct agent_id
        for agent, memory in memories.items():
            self.assertEqual(memory.agent_id, agent)


class TestMemoryMetrics(unittest.TestCase):
    """Test memory metrics calculations."""
    
    def test_calculate_redundancy(self):
        """Test redundancy calculation."""
        entries = [
            {"content": "machine learning algorithms for traffic prediction"},
            {"content": "traffic prediction using machine learning"},
            {"content": "sensor deployment strategy"},
            {"content": "ML algorithms for traffic optimization"}
        ]
        
        redundancy = MemoryMetrics.calculate_redundancy(entries)
        self.assertGreater(redundancy, 0)  # Should detect some redundancy
        self.assertLessEqual(redundancy, 100)  # Should be percentage
    
    def test_calculate_reuse_rate(self):
        """Test knowledge reuse rate calculation."""
        access_log = [
            {"key": "key1", "timestamp": "2024-01-01T10:00:00"},
            {"key": "key2", "timestamp": "2024-01-01T10:01:00"},
            {"key": "key1", "timestamp": "2024-01-01T10:02:00"},  # Reuse
            {"key": "key3", "timestamp": "2024-01-01T10:03:00"},
            {"key": "key2", "timestamp": "2024-01-01T10:04:00"}   # Reuse
        ]
        
        reuse_rate = MemoryMetrics.calculate_reuse_rate(access_log)
        self.assertEqual(reuse_rate, 40.0)  # 2 reuses out of 5 accesses


def run_tests():
    """Run all tests."""
    # Create test suite
    test_classes = [
        TestMemoryEntry,
        TestNoMemorySystem,
        TestSharedMemorySystem,
        TestPrivateMemorySystem,
        TestPrivateMemoryManager,
        TestMemoryMetrics
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

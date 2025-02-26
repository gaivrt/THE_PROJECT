"""
Tests for the memory module.
"""

import pytest
import time
import time as tm
from core.modules.memory_module import MemoryModule, Memory

@pytest.fixture
def memory_module():
    """Create a memory module instance for testing."""
    return MemoryModule()

def test_store_thoughts(memory_module):
    """Test storing thoughts in memory."""
    thought = {
        "content": "Test thought",
        "confidence": 0.8,
        "emotional_influence": {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.2
        }
    }
    
    # Store thought
    memory_module.store_thoughts(thought)
    
    # Verify storage
    assert len(memory_module.short_term_memory) == 1
    assert len(memory_module.context_window) == 1
    
    stored_memory = memory_module.short_term_memory[0]
    assert stored_memory.content == thought
    assert stored_memory.memory_type == "short_term"

def test_context_window(memory_module):
    """Test context window behavior."""
    # Add more thoughts than context window size
    for i in range(15):
        thought = {
            "content": f"Thought {i}",
            "confidence": 0.8
        }
        memory_module.store_thoughts(thought)
    
    # Verify context window size
    assert len(memory_module.context_window) == memory_module.context_window.maxlen
    
    # Verify order (most recent first)
    contexts = list(memory_module.context_window)
    for i in range(len(contexts) - 1):
        assert int(contexts[i]["content"].split()[-1]) > int(contexts[i+1]["content"].split()[-1])

def test_memory_consolidation(memory_module):
    """Test memory consolidation to long-term storage."""
    # Create thought with high importance
    important_thought = {
        "content": "Very important thought",
        "confidence": 1.0,
        "emotional_influence": {
            "valence": 0.9,
            "arousal": 0.9,
            "dominance": 0.9
        }
    }
    
    # Store thought
    memory_module.store_thoughts(important_thought)
    
    # Verify long-term storage
    assert len(memory_module.long_term_memory) > 0
    assert any(
        mem.content == important_thought 
        for mem in memory_module.long_term_memory
    )

def test_memory_access(memory_module):
    """Test memory access tracking."""
    # Create and store memory
    memory = Memory({"content": "Test memory"}, "long_term")
    initial_access_count = memory.access_count
    initial_access_time = memory.last_access_time
    
    # Add a small delay
    time.sleep(0.1)
    
    # Access memory
    memory.access()
    
    # Verify access tracking
    assert memory.access_count == initial_access_count + 1
    assert memory.last_access_time > initial_access_time

def test_memory_cleanup(memory_module):
    """Test memory cleanup functionality."""
    # Add old memories
    old_memory = Memory({"content": "Old memory"}, "long_term")
    old_memory.creation_time = time.time() - 100000  # Very old
    old_memory.last_access_time = old_memory.creation_time
    old_memory.importance_score = 0.3
    
    # Add important memory
    important_memory = Memory({"content": "Important memory"}, "long_term")
    important_memory.creation_time = time.time() - 100000
    important_memory.importance_score = 0.9
    
    memory_module.long_term_memory.extend([old_memory, important_memory])
    
    # Perform cleanup
    memory_module.cleanup_memory()
    
    # Verify cleanup
    assert old_memory not in memory_module.long_term_memory  # Should be removed
    assert important_memory in memory_module.long_term_memory  # Should be kept

def test_get_relevant_memories(memory_module):
    """Test retrieval of relevant memories."""
    # Add some memories
    contexts = [
        {"content": f"Memory {i}", "topic": "test"}
        for i in range(10)
    ]
    
    for context in contexts:
        memory_module.store_thoughts(context)
    
    # Get relevant memories
    current_context = {"content": "Memory 5", "topic": "test"}
    memory_module.context_window.append(current_context)
    
    relevant_memories = memory_module._get_relevant_memories()
    
    # Verify relevance retrieval
    assert len(relevant_memories) <= 5  # Should return at most 5 memories
    assert all(isinstance(mem, dict) for mem in relevant_memories)

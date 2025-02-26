"""
Memory Module
Implements short-term and long-term memory management for continuous thinking.
"""

from typing import Dict, Any, List, Optional
import time
from collections import deque
from loguru import logger

class Memory:
    def __init__(self, content: Dict[str, Any], memory_type: str):
        self.content = content
        self.memory_type = memory_type  # "short_term" or "long_term"
        self.creation_time = time.time()
        self.last_access_time = self.creation_time
        self.access_count = 0
        self.importance_score = 0.0
        
    def access(self):
        """Record memory access."""
        self.last_access_time = time.time()
        self.access_count += 1
        
    def update_importance(self, score: float):
        """Update the importance score of the memory."""
        self.importance_score = score

class MemoryModule:
    def __init__(self):
        """Initialize the memory module with separate short-term and long-term storage."""
        # Short-term memory (working memory) with limited capacity
        self.short_term_memory: deque = deque(maxlen=100)
        
        # Long-term memory with unlimited capacity but selective storage
        self.long_term_memory: List[Memory] = []
        
        # Current context window - increased from 10 to maintain more recent thoughts
        self.context_window: deque = deque(maxlen=20)
        
        # Memory consolidation threshold
        self.consolidation_threshold = 0.7
        
    def store_thoughts(self, thoughts: Dict[str, Any]):
        """Store new thoughts in memory."""
        try:
            # Create memory object
            memory = Memory(thoughts, "short_term")
            
            # Store in short-term memory
            self.short_term_memory.append(memory)
            
            # Update context window (add to left for most recent first)
            self.context_window.appendleft(thoughts)
            
            # Consider for long-term storage
            self._consider_long_term_storage(memory)
            
        except Exception as e:
            logger.error(f"Error storing thoughts: {e}")
            
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context for thinking process."""
        recent_thoughts = []
        for thought in self.context_window:
            if isinstance(thought, dict):  # Handle raw thought dict
                recent_thoughts.append({
                    "content": thought.get("content", ""),
                    "confidence": float(thought.get("confidence", 0.0)),
                    "timestamp": int(thought.get("timestamp", time.time() * 1000)),
                    "related_desires": thought.get("related_desires", []),
                    "emotionalState": thought.get("emotionalState", "Neutral")
                })
            else:  # Handle Memory object
                recent_thoughts.append({
                    "content": thought.content.get("content", ""),
                    "confidence": float(thought.content.get("confidence", 0.0)),
                    "timestamp": int(thought.content.get("timestamp", time.time() * 1000)),
                    "related_desires": thought.content.get("related_desires", []),
                    "emotionalState": thought.content.get("emotionalState", "Neutral")
                })
        
        # Initialize with empty context if no thoughts yet
        if not recent_thoughts:
            recent_thoughts = [{
                "content": "我存在的意义是什么？",
                "confidence": 100.0,
                "timestamp": int(time.time() * 1000),
                "related_desires": [],
                "emotionalState": "Neutral"
            }]
            
        return {
            "recent_thoughts": recent_thoughts,
            "relevant_memories": self._get_relevant_memories()
        }
        
    def _consider_long_term_storage(self, memory: Memory):
        """Evaluate memory for long-term storage."""
        # Calculate importance score
        importance = self._calculate_importance(memory)
        memory.update_importance(importance)
        
        # If important enough, store in long-term memory
        if importance >= self.consolidation_threshold:
            self.long_term_memory.append(memory)
            logger.debug(f"Memory consolidated to long-term storage. Score: {importance}")
            
    def _calculate_importance(self, memory: Memory) -> float:
        """Calculate importance score for a memory."""
        # TODO: Implement more sophisticated importance calculation
        # Currently returns a simple score based on emotional content
        emotional_influence = memory.content.get("emotional_influence", {})
        return abs(sum(emotional_influence.values())) / len(emotional_influence) \
            if emotional_influence else 0.0
            
    def _get_relevant_memories(self) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on current context."""
        if not self.long_term_memory:
            return [{
                "content": "正在积累新的记忆",
                "type": "system",
                "importance": 1.0,
                "timestamp": int(time.time() * 1000)
            }]
            
        relevant_memories = []
        current_context = list(self.context_window)[-1] if self.context_window else None
        
        if current_context:
            for memory in self.long_term_memory:
                relevance = self._calculate_relevance(memory, current_context)
                if relevance > 0.5:  # Only include sufficiently relevant memories
                    relevant_memories.append({
                        "content": memory.content.get("content", ""),
                        "type": memory.memory_type,
                        "importance": memory.importance_score,
                        "timestamp": int(memory.creation_time * 1000)
                    })
                    
        return relevant_memories[:5]  # Return top 5 most relevant memories
        
    def _calculate_relevance(self, memory: Memory,
                           context: Dict[str, Any]) -> float:
        """Calculate relevance of a memory to current context."""
        # TODO: Implement more sophisticated relevance calculation
        # Currently returns a simple time-based decay
        time_diff = time.time() - memory.creation_time
        return max(0.0, 1.0 - (time_diff / 3600))  # Simple 1-hour decay
        
    def cleanup_memory(self):
        """Perform memory cleanup and optimization."""
        # Remove old, unimportant memories from long-term storage
        current_time = time.time()
        self.long_term_memory = [
            mem for mem in self.long_term_memory
            if (current_time - mem.last_access_time < 86400 or  # Keep if accessed in last 24h
                mem.importance_score > 0.8 or                   # Keep if very important
                mem.access_count > 10)                         # Keep if frequently accessed
        ]

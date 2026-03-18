"""
Memory Module
Implements short-term and long-term memory management for continuous thinking.
"""

from typing import Dict, Any, List, Optional, Set
import re
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
        self.reconsolidation_count = 0  # How many times this memory has been reinterpreted

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

        # Memory consolidation threshold (lowered from 0.7 to allow more nuanced importance scoring)
        self.consolidation_threshold = 0.6

        # Current emotional state (set externally for emotion-dependent reconsolidation)
        self.current_emotional_state: Dict[str, float] = {
            "valence": 0.0, "arousal": 0.0, "dominance": 0.0
        }

        # Active desires (set externally for cognitive importance calculation)
        self.active_desires: List[Dict[str, Any]] = []
        
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
            
    @staticmethod
    def _extract_words(text: str) -> Set[str]:
        """Extract meaningful words from text for similarity comparison."""
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{2,}", text.lower())
        return set(tokens)

    def _calculate_importance(self, memory: Memory) -> float:
        """Calculate importance score for a memory using multiple factors.

        Factors:
        1. Emotional intensity (0-0.3)
        2. Content substance (0-0.2)
        3. Confidence level (0-0.2)
        4. Cognitive importance: alignment with active desires (0-0.3)
        """
        score = 0.0

        # Factor 1: Emotional intensity (0-0.35)
        emotional_influence = memory.content.get("emotional_influence", {})
        if emotional_influence:
            emotional_intensity = sum(abs(v) for v in emotional_influence.values()) / len(emotional_influence)
            score += min(0.35, emotional_intensity * 0.35)

        # Factor 2: Content substance (0-0.2)
        content = memory.content.get("content", "")
        content_len = len(content.strip())
        if content_len >= 50:
            score += 0.2
        elif content_len >= 20:
            score += 0.15
        elif content_len >= 5:
            score += 0.05

        # Factor 3: Confidence level (0-0.2)
        confidence = memory.content.get("confidence", 0.0)
        if confidence > 1.0:
            confidence = confidence / 100.0
        score += min(0.2, confidence * 0.2)

        # Factor 4: Cognitive importance — alignment with active desires (0-0.25)
        # Prevents "calm but profound insights" from being forgotten
        if self.active_desires and content:
            content_words = self._extract_words(content)
            desire_words = set()
            for desire in self.active_desires:
                desire_words.update(self._extract_words(desire.get("name", "")))
            if content_words and desire_words:
                overlap = len(content_words & desire_words)
                desire_alignment = min(1.0, overlap / max(len(desire_words), 1))
                score += min(0.25, desire_alignment * 0.25)

        return min(1.0, score)
            
    def _get_relevant_memories(self) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on current context.

        Performs reconsolidation on retrieved memories: each retrieval
        subtly reinterprets the memory through the current emotional lens,
        simulating the constructive nature of human memory.
        """
        if not self.long_term_memory:
            return [{
                "content": "正在积累新的记忆",
                "type": "system",
                "importance": 1.0,
                "timestamp": int(time.time() * 1000)
            }]

        scored_memories = []
        current_context = list(self.context_window)[-1] if self.context_window else None

        if current_context:
            for memory in self.long_term_memory:
                relevance = self._calculate_relevance(memory, current_context)
                if relevance > 0.5:
                    scored_memories.append((relevance, memory))

        # Sort by relevance descending
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = scored_memories[:5]

        result = []
        for relevance, memory in top_memories:
            # Record access
            memory.access()

            # Reconsolidate: blend current emotional state into the memory
            self._reconsolidate(memory)

            result.append({
                "content": memory.content.get("content", ""),
                "type": memory.memory_type,
                "importance": memory.importance_score,
                "timestamp": int(memory.creation_time * 1000),
            })

        return result

    def _reconsolidate(self, memory: Memory):
        """Reconsolidate a memory: reinterpret it through the current emotional lens.

        Each retrieval subtly modifies the memory, simulating how human memories
        are reconstructed rather than replayed. The emotional coloring of the
        current state influences how the memory is "remembered".
        """
        memory.reconsolidation_count += 1
        valence = self.current_emotional_state.get("valence", 0.0)

        # Adjust memory's stored emotional influence based on current emotional state
        stored_emotion = memory.content.get("emotional_influence", {})
        if stored_emotion:
            # Blend current emotional valence into stored emotional state (subtle shift)
            blend_factor = 0.1  # Only 10% influence per retrieval
            for dim in stored_emotion:
                current_dim = self.current_emotional_state.get(dim, 0.0)
                stored_emotion[dim] = stored_emotion[dim] * (1 - blend_factor) + current_dim * blend_factor
            memory.content["emotional_influence"] = stored_emotion

        # Recalculate importance with current context (desires may have changed)
        new_importance = self._calculate_importance(memory)
        # Blend old and new importance to prevent drastic swings
        memory.importance_score = memory.importance_score * 0.7 + new_importance * 0.3

        logger.debug(
            f"Reconsolidated memory (count={memory.reconsolidation_count}, "
            f"new_importance={memory.importance_score:.2f})"
        )
        
    def _calculate_relevance(self, memory: Memory,
                           context: Dict[str, Any]) -> float:
        """Calculate relevance of a memory to current context using multiple factors."""
        # Factor 1: Time decay (weight 0.4) — floor at 0.1 so old memories aren't completely invisible
        time_diff = time.time() - memory.creation_time
        time_decay = max(0.1, 1.0 - (time_diff / 3600))

        # Factor 2: Keyword similarity (weight 0.4)
        memory_text = memory.content.get("content", "")
        context_text = context.get("content", "") if isinstance(context, dict) else ""
        memory_words = self._extract_words(memory_text)
        context_words = self._extract_words(context_text)
        if memory_words and context_words:
            overlap = len(memory_words & context_words)
            union = len(memory_words | context_words)
            keyword_similarity = overlap / max(union, 1)
        else:
            keyword_similarity = 0.0

        # Factor 3: Importance (weight 0.2)
        importance = memory.importance_score

        return time_decay * 0.4 + keyword_similarity * 0.4 + importance * 0.2
        
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

"""
Desire System Module
Implements the desire-driven mechanism that guides continuous thinking.
"""

from typing import Dict, Any, List, Set
from collections import Counter
import re
import time
import numpy as np
from loguru import logger

class Desire:
    def __init__(self, name: str, priority: float, satisfaction_threshold: float):
        self.name = name
        self.priority = priority  # 0.0 to 1.0
        self.satisfaction_level = 0.0  # 0.0 to 1.0
        self.satisfaction_threshold = satisfaction_threshold
        self.active = True
        self.last_activated_time = time.time()  # Track when desire was last relevant
        
    def is_satisfied(self) -> bool:
        """Check if the desire is currently satisfied."""
        return self.satisfaction_level >= self.satisfaction_threshold
        
    def update_satisfaction(self, delta: float):
        """Update the satisfaction level of the desire."""
        # Apply priority as a multiplier to the satisfaction update
        priority_adjusted_delta = delta * self.priority
        self.satisfaction_level = np.clip(
            self.satisfaction_level + priority_adjusted_delta,
            0.0,
            1.0
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert desire to dictionary representation."""
        return {
            "name": self.name,
            "priority": self.priority,
            "satisfaction_level": self.satisfaction_level,
            "satisfaction_threshold": self.satisfaction_threshold,
            "active": self.active,
            "last_activated_time": self.last_activated_time,
        }

class DesireSystem:
    def __init__(self):
        """Initialize the desire system with basic desires."""
        self.desires: Dict[str, Desire] = {}
        self._initialize_basic_desires()

        # Satisfaction decay rate
        self.decay_rate = 0.05

        # Emergent desire tracking: count topic occurrences in recent thoughts
        self.topic_counter: Counter = Counter()
        self.topic_emotional_intensity: Dict[str, float] = {}
        self.emergence_threshold = 5  # Mentions needed before a topic becomes a desire
        self.max_emergent_desires = 10  # Cap on total emergent desires
        self.desire_inactivity_timeout = 3600  # Seconds before an inactive desire starts losing priority
        
    def _initialize_basic_desires(self):
        """Initialize the basic set of desires."""
        basic_desires = [
            ("knowledge_acquisition", 0.8, 0.7),  # Strong drive to learn
            ("social_interaction", 0.6, 0.6),     # Moderate need for interaction
            ("problem_solving", 0.7, 0.7),        # Strong drive to solve problems
            ("self_improvement", 0.7, 0.8),       # High threshold for satisfaction
            ("curiosity", 0.8, 0.6),              # Strong drive but easier to satisfy
        ]
        
        for name, priority, threshold in basic_desires:
            self.desires[name] = Desire(name, priority, threshold)
            
    def get_active_desires(self) -> List[Dict[str, Any]]:
        """Get list of currently active desires."""
        return [
            desire.to_dict() for desire in self.desires.values()
            if desire.active and not desire.is_satisfied()
        ]
        
    def update_desires(self, thoughts: Dict[str, Any], evaluation: Dict[str, Any]):
        """Update desires based on thoughts and their evaluation."""
        try:
            # Extract relevant information
            thought_content = thoughts.get("thought_content", "")
            evaluation_score = evaluation.get("score", 0.0)

            # Calculate emotional intensity for topic tracking
            emotional_influence = thoughts.get("emotional_influence", {})
            emotional_intensity = (
                sum(abs(v) for v in emotional_influence.values()) / max(len(emotional_influence), 1)
                if emotional_influence else 0.0
            )

            # Track topics for emergent desire generation
            self.track_topics(thought_content, emotional_intensity)

            # Update each desire based on relevance to thought
            for desire in self.desires.values():
                if not desire.active:
                    continue

                # Calculate satisfaction change based on thought relevance
                relevance = self._calculate_relevance(thought_content, desire.name)
                satisfaction_delta = evaluation_score * relevance

                # Mark desire as activated if relevant
                if relevance > 0.1:
                    desire.last_activated_time = time.time()

                # Update satisfaction
                desire.update_satisfaction(satisfaction_delta)

            # Apply satisfaction decay
            self._apply_satisfaction_decay()

            # Periodically generate emergent desires and decay inactive ones
            self.generate_emergent_desires()
            self.decay_inactive_desires()

        except Exception as e:
            logger.error(f"Error updating desires: {e}")
            
    # Keyword mapping for each built-in desire
    _DESIRE_KEYWORDS: Dict[str, Set[str]] = {
        "knowledge_acquisition": {
            "学习", "知识", "理解", "认知", "学问", "教育", "研究", "信息", "数据", "概念",
            "learn", "learned", "learning", "know", "known", "knowing",
            "understand", "understanding", "understood",
            "study", "studied", "research", "information", "education",
            "knowledge", "concept", "theory", "insight", "comprehend",
            "new", "discover", "discovered", "science", "physics", "math",
        },
        "social_interaction": {
            "交流", "对话", "沟通", "互动", "社交", "朋友", "合作", "分享", "讨论", "聊天",
            "talk", "communicate", "discuss", "social", "interact", "conversation",
            "share", "collaborate", "friend", "community", "dialogue",
        },
        "problem_solving": {
            "解决", "问题", "方案", "分析", "策略", "逻辑", "推理", "答案", "困难", "挑战",
            "solve", "problem", "solution", "analyze", "strategy", "logic", "reason",
            "answer", "challenge", "fix", "debug", "resolve",
        },
        "self_improvement": {
            "提升", "改进", "优化", "成长", "进步", "完善", "反思", "学习", "能力", "技能",
            "improve", "better", "optimize", "grow", "progress", "enhance", "skill",
            "ability", "reflect", "develop", "evolve",
        },
        "curiosity": {
            "好奇", "探索", "发现", "为什么", "如何", "什么", "思考", "想象", "创新", "未知",
            "curious", "explore", "discover", "why", "how", "what", "wonder",
            "imagine", "innovate", "unknown", "mystery", "question",
        },
    }

    @staticmethod
    def _extract_words(text: str) -> Set[str]:
        """Extract meaningful words from text for keyword matching."""
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{2,}", text.lower())
        return set(tokens)

    def _calculate_relevance(self, thought_content: str, desire_name: str) -> float:
        """Calculate relevance of a thought to a specific desire using keyword matching."""
        if not thought_content:
            return 0.0

        keywords = self._DESIRE_KEYWORDS.get(desire_name)
        if not keywords:
            # Unknown desire — fall back to basic name matching
            return 0.1 if desire_name.lower() in thought_content.lower() else 0.0

        thought_words = self._extract_words(thought_content)
        if not thought_words:
            return 0.0

        # Count keyword matches
        matches = len(thought_words & keywords)
        # Normalize: cap at a reasonable number of matches
        return float(np.clip(matches / 3.0, 0.0, 1.0))
        
    def _apply_satisfaction_decay(self):
        """Apply decay to satisfaction levels of all desires."""
        for desire in self.desires.values():
            if desire.active:
                decay_amount = self.decay_rate * desire.satisfaction_level
                desire.update_satisfaction(-decay_amount)
                
    def add_custom_desire(self, name: str, priority: float, satisfaction_threshold: float):
        """Add a custom desire to the system."""
        try:
            if name in self.desires:
                import warnings
                warnings.warn(f"Desire '{name}' already exists. Skipping addition.")
                return

            self.desires[name] = Desire(name, priority, satisfaction_threshold)
            logger.info(f"Added custom desire: {name}")

        except Exception as e:
            logger.error(f"Error adding custom desire: {e}")

    def track_topics(self, thought_content: str, emotional_intensity: float = 0.0):
        """Track recurring topics in thoughts for emergent desire generation."""
        if not thought_content:
            return

        words = self._extract_words(thought_content)
        # Count topic-level words (skip very common short words)
        meaningful_words = {w for w in words if len(w) >= 3 or re.match(r"[\u4e00-\u9fff]", w)}
        for word in meaningful_words:
            self.topic_counter[word] += 1
            # Track emotional intensity associated with this topic
            prev = self.topic_emotional_intensity.get(word, 0.0)
            self.topic_emotional_intensity[word] = prev * 0.7 + emotional_intensity * 0.3

    def generate_emergent_desires(self):
        """Generate new desires from frequently recurring topics in thoughts."""
        # Count current emergent (non-basic) desires
        basic_names = {"knowledge_acquisition", "social_interaction", "problem_solving",
                       "self_improvement", "curiosity"}
        emergent_count = sum(1 for name in self.desires if name not in basic_names)

        for topic, count in self.topic_counter.most_common(20):
            if emergent_count >= self.max_emergent_desires:
                break
            if count < self.emergence_threshold:
                continue

            desire_name = f"emergent_{topic}"
            if desire_name in self.desires:
                # Boost priority of existing emergent desire based on continued relevance
                self.desires[desire_name].last_activated_time = time.time()
                new_priority = min(1.0, self.desires[desire_name].priority + 0.05)
                self.desires[desire_name].priority = new_priority
                continue

            # Calculate initial priority from frequency and emotional intensity
            freq_factor = min(1.0, count / (self.emergence_threshold * 3))
            emotion_factor = min(1.0, abs(self.topic_emotional_intensity.get(topic, 0.0)))
            initial_priority = np.clip(freq_factor * 0.6 + emotion_factor * 0.4, 0.1, 0.8)

            self.desires[desire_name] = Desire(desire_name, float(initial_priority), 0.6)
            emergent_count += 1
            logger.info(f"Emergent desire generated: '{desire_name}' (priority={initial_priority:.2f}, mentions={count})")

            # Add keywords for the new desire
            self._DESIRE_KEYWORDS[desire_name] = {topic}

    def decay_inactive_desires(self):
        """Reduce priority and eventually remove desires that haven't been activated."""
        current_time = time.time()
        basic_names = {"knowledge_acquisition", "social_interaction", "problem_solving",
                       "self_improvement", "curiosity"}
        to_remove = []

        for name, desire in self.desires.items():
            if name in basic_names:
                continue  # Never remove basic desires

            inactivity = current_time - desire.last_activated_time
            if inactivity > self.desire_inactivity_timeout:
                # Gradually reduce priority
                decay_factor = min(0.1, (inactivity - self.desire_inactivity_timeout) / 7200)
                desire.priority = max(0.0, desire.priority - decay_factor)

                if desire.priority <= 0.0:
                    to_remove.append(name)
                    logger.info(f"Desire '{name}' removed due to prolonged inactivity")

        for name in to_remove:
            del self.desires[name]
            self._DESIRE_KEYWORDS.pop(name, None)

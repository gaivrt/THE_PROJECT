"""
Desire System Module
Implements the desire-driven mechanism that guides continuous thinking.
"""

from typing import Dict, Any, List, Set
import re
import numpy as np
from loguru import logger

class Desire:
    def __init__(self, name: str, priority: float, satisfaction_threshold: float):
        self.name = name
        self.priority = priority  # 0.0 to 1.0
        self.satisfaction_level = 0.0  # 0.0 to 1.0
        self.satisfaction_threshold = satisfaction_threshold
        self.active = True
        
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
            "active": self.active
        }

class DesireSystem:
    def __init__(self):
        """Initialize the desire system with basic desires."""
        self.desires: Dict[str, Desire] = {}
        self._initialize_basic_desires()
        
        # Satisfaction decay rate
        self.decay_rate = 0.05
        
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
            
            # Update each desire based on relevance to thought
            for desire in self.desires.values():
                if not desire.active:
                    continue
                    
                # Calculate satisfaction change based on thought relevance
                relevance = self._calculate_relevance(thought_content, desire.name)
                satisfaction_delta = evaluation_score * relevance
                
                # Update satisfaction
                desire.update_satisfaction(satisfaction_delta)
                
            # Apply satisfaction decay
            self._apply_satisfaction_decay()
            
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

"""
Evaluation System Module
Implements evaluation mechanisms for thoughts and determines expression criteria.
"""

from typing import Dict, Any, List
import re
import difflib
import numpy as np
from loguru import logger

class EvaluationSystem:
    def __init__(self):
        """Initialize the evaluation system with evaluation criteria."""
        # Evaluation criteria weights
        self.criteria_weights = {
            "coherence": 0.3,
            "relevance": 0.2,
            "novelty": 0.15,
            "emotional_impact": 0.15,
            "desire_alignment": 0.2
        }
        
        # Expression threshold
        self.expression_threshold = 0.7
        
        # Recent evaluations for novelty calculation
        self.recent_evaluations = []
        self.max_recent_evaluations = 50
        
    def evaluate_thoughts(self, thoughts: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate thoughts based on multiple criteria."""
        try:
            # Calculate individual scores
            coherence_score = self._evaluate_coherence(thoughts)
            relevance_score = self._evaluate_relevance(thoughts)
            novelty_score = self._evaluate_novelty(thoughts)
            emotional_score = self._evaluate_emotional_impact(thoughts)
            desire_score = self._evaluate_desire_alignment(thoughts)
            
            # Calculate weighted total score
            total_score = (
                coherence_score * self.criteria_weights["coherence"] +
                relevance_score * self.criteria_weights["relevance"] +
                novelty_score * self.criteria_weights["novelty"] +
                emotional_score * self.criteria_weights["emotional_impact"] +
                desire_score * self.criteria_weights["desire_alignment"]
            )
            
            # Create evaluation result
            evaluation = {
                "score": total_score,
                "components": {
                    "coherence": coherence_score,
                    "relevance": relevance_score,
                    "novelty": novelty_score,
                    "emotional_impact": emotional_score,
                    "desire_alignment": desire_score
                }
            }
            
            # Store evaluation with thought content for novelty calculation
            self._store_evaluation(evaluation, thoughts.get("content", ""))
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in thought evaluation: {e}")
            return {"score": 0.0, "error": str(e)}
            
    def should_express(self, thoughts: Dict[str, Any],
                      evaluation: Dict[str, Any]) -> bool:
        """Determine whether thoughts should be expressed."""
        try:
            # Get evaluation score
            score = evaluation.get("score", 0.0)
            
            # Get emotional impact
            emotional_impact = evaluation.get("components", {}).get("emotional_impact", 0.0)
            
            # Consider expression criteria
            should_express = (
                score >= self.expression_threshold or  # High quality thoughts
                emotional_impact > 0.8 or             # Strong emotional content
                self._is_urgent(thoughts)             # Urgent thoughts
            )
            
            return should_express
            
        except Exception as e:
            logger.error(f"Error in expression evaluation: {e}")
            return False
            
    # Logical connectors used for coherence scoring (Chinese + English)
    _CONNECTORS = re.compile(
        r"因此|所以|但是|然而|因为|由于|不过|虽然|尽管|而且|并且|另外|此外|"
        r"总之|综上|换言之|也就是说|"
        r"\btherefore\b|\bthus\b|\bhowever\b|\bbecause\b|\bmoreover\b|"
        r"\bfurthermore\b|\balthough\b|\bnevertheless\b|\bconsequently\b|\bin\s+conclusion\b",
        re.IGNORECASE,
    )

    # Urgency keywords
    _URGENCY_KEYWORDS = re.compile(
        r"紧急|立即|马上|危险|警告|注意|立刻|迫切|刻不容缓|"
        r"\burgent\b|\bimmediately\b|\bcritical\b|\bdanger\b|\bwarning\b|\balert\b|\basap\b",
        re.IGNORECASE,
    )

    @staticmethod
    def _extract_words(text: str) -> List[str]:
        """Extract meaningful words from text for similarity comparison."""
        # Split on whitespace and Chinese characters, filter short tokens
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{2,}", text.lower())
        return tokens

    def _evaluate_coherence(self, thoughts: Dict[str, Any]) -> float:
        """Evaluate the coherence of thoughts using heuristic analysis."""
        content = thoughts.get("content", "")
        if not content or len(content.strip()) < 5:
            return 0.1

        score = 0.5  # Baseline

        # Reward logical connectors (max +0.3)
        connector_count = len(self._CONNECTORS.findall(content))
        score += min(0.3, connector_count * 0.1)

        # Reward adequate length (not too short, not excessively long)
        length = len(content)
        if length >= 20:
            score += 0.1
        if length >= 50:
            score += 0.1

        # Penalize very short content
        if length < 10:
            score -= 0.2

        return float(np.clip(score, 0.0, 1.0))

    def _evaluate_relevance(self, thoughts: Dict[str, Any]) -> float:
        """Evaluate the relevance of thoughts to current context using keyword overlap."""
        content = thoughts.get("content", "")
        if not content:
            return 0.0

        # Gather context words from related desires and emotional state
        context_parts: List[str] = []
        for desire in thoughts.get("related_desires", []):
            context_parts.append(desire.get("name", ""))
        emotional_state = thoughts.get("emotionalState", "")
        if emotional_state:
            context_parts.append(str(emotional_state))

        if not context_parts:
            return 0.5  # No context available, default to moderate

        content_words = set(self._extract_words(content))
        context_words = set(self._extract_words(" ".join(context_parts)))

        if not content_words or not context_words:
            return 0.5

        # Jaccard-like overlap
        overlap = len(content_words & context_words)
        union = len(content_words | context_words)
        return float(np.clip(overlap / max(union, 1) + 0.3, 0.0, 1.0))

    def _evaluate_novelty(self, thoughts: Dict[str, Any]) -> float:
        """Evaluate the novelty of thoughts compared to recent thoughts using text similarity."""
        content = thoughts.get("content", "")
        if not content:
            return 0.0

        if not self.recent_evaluations:
            return 0.8  # First thought is novel

        # Compare against recent thought contents
        max_similarity = 0.0
        for past_eval in self.recent_evaluations:
            past_content = past_eval.get("thought_content", "")
            if not past_content:
                continue
            similarity = difflib.SequenceMatcher(None, content, past_content).ratio()
            max_similarity = max(max_similarity, similarity)

        # Novelty is inverse of similarity
        return float(np.clip(1.0 - max_similarity, 0.0, 1.0))
        
    def _evaluate_emotional_impact(self, thoughts: Dict[str, Any]) -> float:
        """Evaluate the emotional impact of thoughts."""
        emotional_influence = thoughts.get("emotional_influence", {})
        if not emotional_influence:
            return 0.0
            
        # Calculate magnitude of emotional impact
        return min(1.0, sum(abs(v) for v in emotional_influence.values()) / len(emotional_influence))
        
    def _evaluate_desire_alignment(self, thoughts: Dict[str, Any]) -> float:
        """Evaluate how well thoughts align with current desires."""
        related_desires = thoughts.get("related_desires", [])
        if not related_desires:
            return 0.0
            
        # Calculate average alignment with related desires
        return sum(desire.get("priority", 0.0) for desire in related_desires) / len(related_desires)
        
    def _store_evaluation(self, evaluation: Dict[str, Any], thought_content: str = ""):
        """Store evaluation along with thought content for novelty calculation."""
        evaluation["thought_content"] = thought_content
        self.recent_evaluations.append(evaluation)
        if len(self.recent_evaluations) > self.max_recent_evaluations:
            self.recent_evaluations.pop(0)

    def _is_urgent(self, thoughts: Dict[str, Any]) -> bool:
        """Determine if thoughts are urgent based on keyword detection."""
        content = thoughts.get("content", "")
        if not content:
            return False

        # Check for urgency keywords
        if self._URGENCY_KEYWORDS.search(content):
            return True

        # Check for direct questions (possible user-triggered interaction)
        if "?" in content or "？" in content:
            return True

        return False

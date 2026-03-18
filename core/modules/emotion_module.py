"""
Emotion Module
Implements emotional state management and emotional influence on thinking processes.
"""

from typing import Dict, Any, List
from collections import deque
import numpy as np
from loguru import logger

class EmotionModule:
    def __init__(self):
        """Initialize the emotion module with base emotional dimensions."""
        # Initialize basic emotional dimensions (valence-arousal-dominance model)
        self.emotional_state = {
            "valence": 0.0,  # -1 (negative) to 1 (positive)
            "arousal": 0.0,  # -1 (calm) to 1 (excited)
            "dominance": 0.0  # -1 (submissive) to 1 (dominant)
        }

        # Per-dimension decay rates (dynamic, adapt based on history)
        self.decay_rates = {
            "valence": 0.1,
            "arousal": 0.1,
            "dominance": 0.1,
        }

        # Base decay rate (used as reference point)
        self.base_decay_rate = 0.1

        # Backward-compatible scalar property
        @property
        def decay_rate(self):
            return self.base_decay_rate

        # Emotion event history for adaptive decay (recent events per dimension)
        self._event_history: Dict[str, deque] = {
            "valence": deque(maxlen=50),
            "arousal": deque(maxlen=50),
            "dominance": deque(maxlen=50),
        }

        # Emotion intensity limits
        self.intensity_limits = (-1.0, 1.0)

    @property
    def decay_rate(self) -> float:
        """Backward-compatible scalar decay rate."""
        return self.base_decay_rate

    @decay_rate.setter
    def decay_rate(self, value: float):
        """Setting decay_rate updates all dimensions uniformly."""
        self.base_decay_rate = value
        for dim in self.decay_rates:
            self.decay_rates[dim] = value
        
    def get_current_state(self) -> Dict[str, float]:
        """Return the current emotional state."""
        return self.emotional_state.copy()
        
    def update_state(self, thoughts: Dict[str, Any], evaluation: Dict[str, Any]):
        """Update emotional state based on thoughts and their evaluation."""
        try:
            # Extract emotional influence from thoughts
            emotional_influence = thoughts.get("emotional_influence", {})

            # Extract evaluation metrics
            evaluation_score = evaluation.get("score", 0.0)

            # Record event history for adaptive decay
            for dimension in self.emotional_state:
                influence = emotional_influence.get(dimension, 0.0)
                self._event_history[dimension].append(influence)

            # Calculate new emotional state
            self._calculate_new_state(emotional_influence, evaluation_score)

            # Adapt decay rates based on event history
            self._adapt_decay_rates()

            # Apply emotional decay
            self._apply_decay()

            logger.debug(f"Updated emotional state: {self.emotional_state}")

        except Exception as e:
            logger.error(f"Error updating emotional state: {e}")
            
    def _calculate_new_state(self, emotional_influence: Dict[str, float],
                           evaluation_score: float):
        """Calculate new emotional state based on influences and evaluation."""
        for dimension in self.emotional_state:
            # Get influence for this dimension
            influence = emotional_influence.get(dimension, 0.0)
            
            # Combine with evaluation score
            combined_influence = (influence + evaluation_score) / 2
            
            # Update state with bounds checking
            new_value = self.emotional_state[dimension] + combined_influence
            self.emotional_state[dimension] = np.clip(
                new_value,
                self.intensity_limits[0],
                self.intensity_limits[1]
            )
            
    def _apply_decay(self):
        """Apply per-dimension emotional decay to move emotions gradually toward neutral."""
        for dimension in self.emotional_state:
            current_value = self.emotional_state[dimension]
            rate = self.decay_rates.get(dimension, self.base_decay_rate)
            # Decay toward neutral (0.0)
            decay_amount = current_value * rate
            self.emotional_state[dimension] -= decay_amount

    def _adapt_decay_rates(self):
        """Adapt decay rates based on emotional event history.

        - Repeated positive experiences → slower positive decay (emotional resilience)
        - Repeated negative experiences → faster negative decay (desensitization)
        """
        for dimension in self.decay_rates:
            history = self._event_history[dimension]
            if len(history) < 5:
                continue  # Not enough history to adapt

            recent = list(history)[-10:]  # Last 10 events
            avg = sum(recent) / len(recent)

            if avg > 0.1:
                # Repeated positive → slow down decay (resilience), min 0.03
                self.decay_rates[dimension] = max(0.03, self.base_decay_rate * 0.7)
            elif avg < -0.1:
                # Repeated negative → speed up decay (desensitization), max 0.2
                self.decay_rates[dimension] = min(0.2, self.base_decay_rate * 1.5)
            else:
                # Neutral → drift back toward base rate
                self.decay_rates[dimension] += (self.base_decay_rate - self.decay_rates[dimension]) * 0.1
            
    def get_emotion_label(self) -> str:
        """Convert dimensional emotions to categorical label for easier interpretation."""
        # Simple mapping of dimensional space to basic emotions
        v, a, d = (self.emotional_state["valence"],
                   self.emotional_state["arousal"],
                   self.emotional_state["dominance"])
                   
        if v > 0.3:
            if a > 0.3: return "excited" if d > 0 else "happy"
            else: return "content" if d > 0 else "relaxed"
        elif v < -0.3:
            if a > 0.3: return "angry" if d > 0 else "afraid"
            else: return "sad" if d > 0 else "depressed"
        else:
            return "neutral"

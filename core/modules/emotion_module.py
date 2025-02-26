"""
Emotion Module
Implements emotional state management and emotional influence on thinking processes.
"""

from typing import Dict, Any
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
        
        # Emotional decay rate (how quickly emotions return to neutral)
        self.decay_rate = 0.1
        
        # Emotion intensity limits
        self.intensity_limits = (-1.0, 1.0)
        
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
            
            # Calculate new emotional state
            self._calculate_new_state(emotional_influence, evaluation_score)
            
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
        """Apply emotional decay to move emotions gradually toward neutral."""
        for dimension in self.emotional_state:
            current_value = self.emotional_state[dimension]
            # Decay toward neutral (0.0)
            decay_amount = current_value * self.decay_rate
            self.emotional_state[dimension] -= decay_amount
            
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

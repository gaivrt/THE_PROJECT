"""
Tests for the emotion module.
"""

import pytest
from core.modules.emotion_module import EmotionModule

@pytest.fixture
def emotion_module():
    """Create an emotion module instance for testing."""
    return EmotionModule()

def test_initial_state(emotion_module):
    """Test initial emotional state."""
    state = emotion_module.get_current_state()
    
    # Verify initial state
    assert "valence" in state
    assert "arousal" in state
    assert "dominance" in state
    assert all(v == 0.0 for v in state.values())

def test_update_state(emotion_module):
    """Test emotional state updates."""
    thoughts = {
        "emotional_influence": {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.2
        }
    }
    
    evaluation = {
        "score": 0.8
    }
    
    # Update state
    emotion_module.update_state(thoughts, evaluation)
    state = emotion_module.get_current_state()
    
    # Verify state changes
    assert all(isinstance(v, float) for v in state.values())
    assert all(-1 <= v <= 1 for v in state.values())
    assert state["valence"] > 0
    assert state["arousal"] > 0
    assert state["dominance"] > 0

def test_emotional_decay(emotion_module):
    """Test emotional state decay."""
    # Set initial state
    thoughts = {
        "emotional_influence": {
            "valence": 1.0,
            "arousal": 1.0,
            "dominance": 1.0
        }
    }
    evaluation = {"score": 1.0}
    emotion_module.update_state(thoughts, evaluation)
    
    # Apply decay
    emotion_module._apply_decay()
    state = emotion_module.get_current_state()
    
    # Verify decay
    assert all(v < 1.0 for v in state.values())

def test_emotion_label(emotion_module):
    """Test emotion label generation."""
    test_cases = [
        # (valence, arousal, dominance, expected_label)
        (0.5, 0.5, 0.5, "excited"),
        (-0.5, 0.5, 0.5, "angry"),
        (-0.5, -0.5, 0.5, "sad"),
        (0.5, -0.5, 0.5, "content"),
        (0.0, 0.0, 0.0, "neutral")
    ]
    
    for valence, arousal, dominance, expected in test_cases:
        # Set emotional state
        emotion_module.emotional_state = {
            "valence": valence,
            "arousal": arousal,
            "dominance": dominance
        }
        
        # Get label
        label = emotion_module.get_emotion_label()
        
        # Verify label
        assert label == expected

def test_intensity_limits(emotion_module):
    """Test emotional intensity limits."""
    # Try to set extreme values
    thoughts = {
        "emotional_influence": {
            "valence": 2.0,
            "arousal": -2.0,
            "dominance": 2.0
        }
    }
    evaluation = {"score": 1.0}
    
    # Update state
    emotion_module.update_state(thoughts, evaluation)
    state = emotion_module.get_current_state()
    
    # Verify limits
    assert all(-1 <= v <= 1 for v in state.values())

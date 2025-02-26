"""
Tests for the desire system.
"""

import pytest
from core.modules.desire_system import DesireSystem, Desire

@pytest.fixture
def desire_system():
    """Create a desire system instance for testing."""
    return DesireSystem()

def test_basic_desires_initialization(desire_system):
    """Test initialization of basic desires."""
    # Get active desires
    active_desires = desire_system.get_active_desires()
    
    # Verify basic desires
    desire_names = {d["name"] for d in active_desires}
    expected_names = {
        "knowledge_acquisition",
        "social_interaction",
        "problem_solving",
        "self_improvement",
        "curiosity"
    }
    
    assert desire_names == expected_names
    assert all(0 <= d["priority"] <= 1 for d in active_desires)
    assert all(0 <= d["satisfaction_level"] <= 1 for d in active_desires)

def test_desire_satisfaction_update(desire_system):
    """Test updating desire satisfaction levels."""
    thoughts = {
        "thought_content": "I've learned something new about quantum physics.",
        "confidence": 0.8
    }
    
    evaluation = {
        "score": 0.9
    }
    
    # Initial state
    initial_desires = desire_system.get_active_desires()
    initial_satisfaction = {
        d["name"]: d["satisfaction_level"] for d in initial_desires
    }
    
    # Update desires
    desire_system.update_desires(thoughts, evaluation)
    
    # Get updated state
    updated_desires = desire_system.get_active_desires()
    updated_satisfaction = {
        d["name"]: d["satisfaction_level"] for d in updated_desires
    }
    
    # Verify changes
    assert any(
        updated_satisfaction[name] != initial_satisfaction[name]
        for name in initial_satisfaction
    )

def test_desire_satisfaction_decay(desire_system):
    """Test decay of desire satisfaction levels."""
    # Set initial high satisfaction
    for desire in desire_system.desires.values():
        desire.satisfaction_level = 1.0
    
    # Apply decay
    desire_system._apply_satisfaction_decay()
    
    # Verify decay
    for desire in desire_system.desires.values():
        assert desire.satisfaction_level < 1.0

def test_custom_desire_addition(desire_system):
    """Test adding custom desires."""
    # Add custom desire
    desire_system.add_custom_desire(
        name="test_desire",
        priority=0.8,
        satisfaction_threshold=0.7
    )
    
    # Verify addition
    active_desires = desire_system.get_active_desires()
    assert any(d["name"] == "test_desire" for d in active_desires)
    
    # Try adding duplicate
    with pytest.warns(UserWarning):
        desire_system.add_custom_desire(
            name="test_desire",
            priority=0.9,
            satisfaction_threshold=0.8
        )

def test_desire_satisfaction_threshold(desire_system):
    """Test desire satisfaction threshold behavior."""
    # Create test desire
    test_desire = Desire("test", 0.8, 0.7)
    
    # Test below threshold
    test_desire.satisfaction_level = 0.6
    assert not test_desire.is_satisfied()
    
    # Test at threshold
    test_desire.satisfaction_level = 0.7
    assert test_desire.is_satisfied()
    
    # Test above threshold
    test_desire.satisfaction_level = 0.8
    assert test_desire.is_satisfied()

def test_desire_priority_influence(desire_system):
    """Test influence of desire priority on satisfaction updates."""
    # Create two desires with different priorities
    high_priority = Desire("high_priority", 0.9, 0.7)
    low_priority = Desire("low_priority", 0.3, 0.7)
    
    # Apply same satisfaction update
    delta = 0.2
    high_priority.update_satisfaction(delta)
    low_priority.update_satisfaction(delta)
    
    # Verify priority influence
    assert high_priority.satisfaction_level > low_priority.satisfaction_level

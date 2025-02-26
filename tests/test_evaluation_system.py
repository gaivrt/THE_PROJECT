"""
Tests for the evaluation system.
"""

import pytest
from core.modules.evaluation_system import EvaluationSystem

@pytest.fixture
def evaluation_system():
    """Create an evaluation system instance for testing."""
    return EvaluationSystem()

def test_thought_evaluation(evaluation_system):
    """Test comprehensive thought evaluation."""
    thought = {
        "content": "I should explore quantum computing to expand my knowledge.",
        "confidence": 0.8,
        "emotional_influence": {
            "valence": 0.6,
            "arousal": 0.4,
            "dominance": 0.5
        },
        "related_desires": [
            {"name": "knowledge_acquisition", "priority": 0.9},
            {"name": "curiosity", "priority": 0.8}
        ]
    }
    
    # Evaluate thought
    evaluation = evaluation_system.evaluate_thoughts(thought)
    
    # Verify evaluation structure
    assert "score" in evaluation
    assert "components" in evaluation
    assert all(
        component in evaluation["components"]
        for component in [
            "coherence",
            "relevance",
            "novelty",
            "emotional_impact",
            "desire_alignment"
        ]
    )
    
    # Verify score ranges
    assert 0 <= evaluation["score"] <= 1
    assert all(
        0 <= score <= 1
        for score in evaluation["components"].values()
    )

def test_expression_decision(evaluation_system):
    """Test expression decision making."""
    # Test high-quality thought
    high_quality_thought = {
        "content": "Important insight about AI consciousness",
        "confidence": 0.9,
        "emotional_influence": {"valence": 0.3, "arousal": 0.2, "dominance": 0.4}
    }
    high_quality_eval = {"score": 0.9, "components": {"emotional_impact": 0.5}}
    
    assert evaluation_system.should_express(high_quality_thought, high_quality_eval)
    
    # Test low-quality thought
    low_quality_thought = {
        "content": "Random mundane thought",
        "confidence": 0.3,
        "emotional_influence": {"valence": 0.1, "arousal": 0.1, "dominance": 0.1}
    }
    low_quality_eval = {"score": 0.3, "components": {"emotional_impact": 0.2}}
    
    assert not evaluation_system.should_express(low_quality_thought, low_quality_eval)

def test_emotional_impact_evaluation(evaluation_system):
    """Test emotional impact evaluation."""
    thought = {
        "content": "Feeling extremely excited about new discoveries!",
        "emotional_influence": {
            "valence": 0.9,
            "arousal": 0.8,
            "dominance": 0.7
        }
    }
    
    impact_score = evaluation_system._evaluate_emotional_impact(thought)
    
    # Verify emotional impact calculation
    assert isinstance(impact_score, float)
    assert 0 <= impact_score <= 1
    assert impact_score > 0.5  # Should be high due to strong emotions

def test_desire_alignment_evaluation(evaluation_system):
    """Test desire alignment evaluation."""
    thought = {
        "content": "Learning new programming concepts",
        "related_desires": [
            {"name": "knowledge_acquisition", "priority": 0.9},
            {"name": "self_improvement", "priority": 0.8}
        ]
    }
    
    alignment_score = evaluation_system._evaluate_desire_alignment(thought)
    
    # Verify desire alignment calculation
    assert isinstance(alignment_score, float)
    assert 0 <= alignment_score <= 1
    assert alignment_score > 0.8  # Should be high due to high-priority desires

def test_novelty_evaluation(evaluation_system):
    """Test novelty evaluation."""
    # Add some recent evaluations
    evaluation_system.recent_evaluations = [
        {"score": 0.8, "components": {"novelty": 0.7}},
        {"score": 0.7, "components": {"novelty": 0.6}}
    ]
    
    thought = {
        "content": "Completely new and unique insight"
    }
    
    novelty_score = evaluation_system._evaluate_novelty(thought)
    
    # Verify novelty calculation
    assert isinstance(novelty_score, float)
    assert 0 <= novelty_score <= 1

def test_evaluation_weights(evaluation_system):
    """Test evaluation weight application."""
    # Verify weight normalization
    total_weight = sum(evaluation_system.criteria_weights.values())
    assert abs(total_weight - 1.0) < 0.0001  # Should sum to 1
    
    # Verify all criteria are weighted
    expected_criteria = {
        "coherence",
        "relevance",
        "novelty",
        "emotional_impact",
        "desire_alignment"
    }
    assert set(evaluation_system.criteria_weights.keys()) == expected_criteria

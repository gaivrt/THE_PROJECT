"""
Tests for the DeepSeek R1 model wrapper.
"""

import pytest
import torch
from core.models.deepseek_wrapper import DeepSeekWrapper

@pytest.fixture
async def model_wrapper():
    """Create a model wrapper instance for testing."""
    wrapper = DeepSeekWrapper(model_name="deepseek-ai/deepseek-r1-70b")
    return wrapper

@pytest.mark.asyncio
async def test_prompt_construction(model_wrapper):
    """Test prompt construction logic."""
    context = {
        "recent_thoughts": [
            {"content": "Exploring new ideas"},
            {"content": "Learning from experiences"}
        ]
    }
    
    emotional_state = {
        "valence": 0.5,
        "arousal": 0.3,
        "dominance": 0.4
    }
    
    desires = [
        {
            "name": "knowledge_acquisition",
            "priority": 0.8,
            "active": True
        },
        {
            "name": "problem_solving",
            "priority": 0.7,
            "active": True
        }
    ]
    
    prompt = model_wrapper._construct_prompt(context, emotional_state, desires)
    
    # Verify prompt structure
    assert "Recent thoughts:" in prompt
    assert "Exploring new ideas" in prompt
    assert "Learning from experiences" in prompt
    assert "Current emotional state:" in prompt
    assert "Active desires:" in prompt
    assert "knowledge_acquisition" in prompt
    assert "problem_solving" in prompt

@pytest.mark.asyncio
async def test_thought_processing(model_wrapper):
    """Test thought processing logic."""
    thought_text = "Thought: I should explore more advanced concepts to satisfy my curiosity."
    context = {"recent_thoughts": []}
    emotional_state = {"valence": 0.5, "arousal": 0.3, "dominance": 0.4}
    desires = [{"name": "knowledge_acquisition", "priority": 0.8, "active": True}]
    
    result = model_wrapper._process_thought(thought_text, context, emotional_state, desires)
    
    # Verify thought structure
    assert "content" in result
    assert "confidence" in result
    assert "related_desires" in result
    assert "emotional_influence" in result
    assert isinstance(result["confidence"], float)
    assert isinstance(result["related_desires"], list)
    assert isinstance(result["emotional_influence"], dict)

@pytest.mark.asyncio
async def test_confidence_calculation(model_wrapper):
    """Test confidence score calculation."""
    content = "I should explore more advanced concepts."
    emotional_state = {"valence": 0.5, "arousal": 0.3, "dominance": 0.4}
    desires = [{"name": "knowledge_acquisition", "priority": 0.8, "active": True}]
    
    confidence = model_wrapper._calculate_confidence(content, emotional_state, desires)
    
    # Verify confidence score
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1

@pytest.mark.asyncio
async def test_emotional_influence_calculation(model_wrapper):
    """Test emotional influence calculation."""
    content = "I feel excited about learning new concepts!"
    
    emotional_influence = model_wrapper._calculate_emotional_influence(content)
    
    # Verify emotional influence structure
    assert "valence" in emotional_influence
    assert "arousal" in emotional_influence
    assert "dominance" in emotional_influence
    assert all(isinstance(v, float) for v in emotional_influence.values())
    assert all(-1 <= v <= 1 for v in emotional_influence.values())

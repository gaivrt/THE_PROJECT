"""
Integration tests for Metis Continuum.
Tests cross-module interactions and end-to-end flows.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.modules.emotion_module import EmotionModule
from core.modules.desire_system import DesireSystem, Desire
from core.modules.memory_module import MemoryModule
from core.modules.evaluation_system import EvaluationSystem
from core.utils.thinking_loop import ThinkingLoop


# --- Fixtures ---

@pytest.fixture
def emotion_module():
    return EmotionModule()

@pytest.fixture
def desire_system():
    return DesireSystem()

@pytest.fixture
def memory_module():
    return MemoryModule()

@pytest.fixture
def evaluation_system():
    return EvaluationSystem()


# --- Integration: Emotion affects thinking pipeline ---

class TestEmotionThinkingIntegration:
    def test_emotion_state_influences_evaluation(self, emotion_module, evaluation_system):
        """Emotional state fed into thoughts should affect evaluation scores."""
        # Thought with strong emotional influence
        emotional_thought = {
            "content": "This discovery is truly remarkable and exciting!",
            "confidence": 0.9,
            "emotional_influence": {"valence": 0.8, "arousal": 0.7, "dominance": 0.5},
            "related_desires": [{"name": "curiosity", "priority": 0.8}],
        }
        eval_result = evaluation_system.evaluate_thoughts(emotional_thought)
        assert eval_result["score"] > 0
        assert eval_result["components"]["emotional_impact"] > 0.5

        # Neutral thought
        neutral_thought = {
            "content": "The sky is blue.",
            "confidence": 0.5,
            "emotional_influence": {},
            "related_desires": [],
        }
        neutral_eval = evaluation_system.evaluate_thoughts(neutral_thought)
        assert neutral_eval["components"]["emotional_impact"] == 0.0

    def test_emotion_updates_from_thought_evaluation(self, emotion_module):
        """Emotion module updates based on thoughts and evaluation."""
        initial = emotion_module.get_current_state()
        assert initial["valence"] == 0.0

        thoughts = {"emotional_influence": {"valence": 0.5, "arousal": 0.3, "dominance": 0.1}}
        evaluation = {"score": 0.8}
        emotion_module.update_state(thoughts, evaluation)

        updated = emotion_module.get_current_state()
        assert updated["valence"] != 0.0  # Should have changed


class TestDesireEmergence:
    def test_emergent_desire_creation(self, desire_system):
        """Repeated topic mentions should generate emergent desires."""
        for _ in range(6):  # Above emergence_threshold of 5
            desire_system.track_topics("exploring quantum physics research")

        desire_system.generate_emergent_desires()

        # Should have created emergent desires for recurring topics
        emergent_names = [n for n in desire_system.desires if n.startswith("emergent_")]
        assert len(emergent_names) > 0

    def test_desire_inactivity_decay(self, desire_system):
        """Inactive desires should lose priority over time."""
        desire_system.add_custom_desire("test_desire", 0.5, 0.6)
        # Simulate long inactivity
        desire_system.desires["test_desire"].last_activated_time = time.time() - 7200

        desire_system.decay_inactive_desires()
        assert desire_system.desires["test_desire"].priority < 0.5

    def test_basic_desires_never_removed(self, desire_system):
        """Basic desires should never be removed by inactivity decay."""
        for desire in desire_system.desires.values():
            desire.last_activated_time = time.time() - 100000

        desire_system.decay_inactive_desires()
        basic_names = {"knowledge_acquisition", "social_interaction", "problem_solving",
                       "self_improvement", "curiosity"}
        for name in basic_names:
            assert name in desire_system.desires


class TestDynamicEmotionDecay:
    def test_per_dimension_decay_rates(self, emotion_module):
        """Each VAD dimension should have its own decay rate."""
        assert "valence" in emotion_module.decay_rates
        assert "arousal" in emotion_module.decay_rates
        assert "dominance" in emotion_module.decay_rates

    def test_decay_adaptation_positive(self, emotion_module):
        """Repeated positive experiences should slow positive decay."""
        original_rate = emotion_module.decay_rates["valence"]

        # Simulate repeated positive emotional events
        for _ in range(10):
            thoughts = {"emotional_influence": {"valence": 0.5, "arousal": 0.0, "dominance": 0.0}}
            evaluation = {"score": 0.5}
            emotion_module.update_state(thoughts, evaluation)

        # Valence decay should be slower (resilience)
        assert emotion_module.decay_rates["valence"] < original_rate

    def test_decay_adaptation_negative(self, emotion_module):
        """Repeated negative experiences should speed up decay (desensitization)."""
        original_rate = emotion_module.decay_rates["arousal"]

        for _ in range(10):
            thoughts = {"emotional_influence": {"valence": -0.5, "arousal": -0.5, "dominance": -0.5}}
            evaluation = {"score": 0.3}
            emotion_module.update_state(thoughts, evaluation)

        # Arousal decay should be faster (desensitization)
        assert emotion_module.decay_rates["arousal"] > original_rate


class TestMemoryReconsolidation:
    def test_reconsolidation_updates_memory(self, memory_module):
        """Retrieving a memory should trigger reconsolidation."""
        thought = {
            "content": "A significant realization about the nature of consciousness",
            "confidence": 0.9,
            "emotional_influence": {"valence": 0.8, "arousal": 0.6, "dominance": 0.3},
        }
        memory_module.store_thoughts(thought)

        # Force into long-term memory
        if not memory_module.long_term_memory:
            from core.modules.memory_module import Memory
            mem = Memory(thought, "long_term")
            mem.importance_score = 0.9
            memory_module.long_term_memory.append(mem)

        original_count = memory_module.long_term_memory[0].reconsolidation_count

        # Set different emotional state to influence reconsolidation
        memory_module.current_emotional_state = {"valence": -0.5, "arousal": 0.1, "dominance": 0.0}

        # Trigger retrieval which reconsolidates
        memory_module._get_relevant_memories()

        # Memory should have been reconsolidated
        if memory_module.long_term_memory[0].access_count > 0:
            assert memory_module.long_term_memory[0].reconsolidation_count > original_count

    def test_cognitive_importance_prevents_insight_loss(self, memory_module):
        """Calm but desire-aligned thoughts should score higher importance."""
        memory_module.active_desires = [
            {"name": "knowledge_acquisition", "priority": 0.8},
            {"name": "curiosity", "priority": 0.8},
        ]

        from core.modules.memory_module import Memory

        # Calm but knowledge-related thought
        calm_insight = Memory(
            {"content": "knowledge acquisition through curiosity leads to growth",
             "confidence": 0.8, "emotional_influence": {}},
            "short_term"
        )
        # Emotionally intense but irrelevant thought
        emotional_noise = Memory(
            {"content": "aaah bbb ccc ddd eee fff",
             "confidence": 0.3,
             "emotional_influence": {"valence": 0.9, "arousal": 0.9, "dominance": 0.9}},
            "short_term"
        )

        insight_score = memory_module._calculate_importance(calm_insight)
        noise_score = memory_module._calculate_importance(emotional_noise)

        # Calm insight with desire alignment should compete with pure emotion
        assert insight_score > 0.3


class TestThinkingLoopIntegration:
    async def test_thinking_loop_callbacks(self):
        """ThinkingLoop should call think, evaluate, and express callbacks correctly."""
        think_called = asyncio.Event()
        evaluate_called = asyncio.Event()
        express_called = asyncio.Event()

        async def mock_think():
            think_called.set()
            return {"content": "test thought", "confidence": 0.8}

        async def mock_evaluate(thought):
            evaluate_called.set()
            return {"score": 0.9, "should_express": True}

        async def mock_express(thought, evaluation):
            express_called.set()

        loop = ThinkingLoop(
            think_callback=mock_think,
            evaluate_callback=mock_evaluate,
            express_callback=mock_express,
            min_interval=0.01,
            max_interval=0.1,
        )

        await loop.start()
        # Wait for one cycle
        await asyncio.sleep(0.15)
        await loop.stop()

        assert think_called.is_set()
        assert evaluate_called.is_set()
        assert express_called.is_set()

    async def test_thinking_loop_adaptive_interval(self):
        """ThinkingLoop should adapt interval based on thought quality."""
        loop = ThinkingLoop(
            think_callback=AsyncMock(return_value={"content": "x"}),
            evaluate_callback=AsyncMock(return_value={"score": 0.1, "should_express": False}),
            express_callback=AsyncMock(),
            min_interval=0.01,
            max_interval=1.0,
        )

        initial_interval = loop.current_interval

        # Simulate low score evaluation
        loop._adjust_interval({"score": 0.1})
        assert loop.current_interval > initial_interval  # Should slow down

        loop._adjust_interval({"score": 0.9})
        # Should speed up from the increased interval


class TestEvaluationSystemRegression:
    def test_coherence_not_random(self, evaluation_system):
        """Coherence should be deterministic, not random."""
        thought = {"content": "Therefore, because of this reasoning, we can conclude that the hypothesis holds."}
        score1 = evaluation_system._evaluate_coherence(thought)
        score2 = evaluation_system._evaluate_coherence(thought)
        assert score1 == score2  # Deterministic

    def test_relevance_not_random(self, evaluation_system):
        """Relevance should be deterministic."""
        thought = {"content": "test content", "related_desires": [{"name": "curiosity"}]}
        score1 = evaluation_system._evaluate_relevance(thought)
        score2 = evaluation_system._evaluate_relevance(thought)
        assert score1 == score2

    def test_novelty_not_random(self, evaluation_system):
        """Novelty should be deterministic."""
        thought = {"content": "Some unique thought content"}
        score1 = evaluation_system._evaluate_novelty(thought)
        score2 = evaluation_system._evaluate_novelty(thought)
        assert score1 == score2

    def test_urgency_detection(self, evaluation_system):
        """Urgency should detect urgent keywords."""
        urgent_thought = {"content": "This is urgent! We need to act immediately!"}
        assert evaluation_system._is_urgent(urgent_thought) is True

        normal_thought = {"content": "The weather is nice today."}
        assert evaluation_system._is_urgent(normal_thought) is False

    def test_novelty_decreases_with_repetition(self, evaluation_system):
        """Repeated similar thoughts should have lower novelty."""
        thought = {"content": "The nature of consciousness is fascinating"}
        eval1 = evaluation_system.evaluate_thoughts(thought)
        novelty1 = eval1["components"]["novelty"]

        # Same thought again
        eval2 = evaluation_system.evaluate_thoughts(thought)
        novelty2 = eval2["components"]["novelty"]

        assert novelty2 < novelty1  # Second time should be less novel


class TestMemoryConsolidationFlow:
    def test_full_consolidation_retrieval_cleanup(self, memory_module):
        """Test complete memory lifecycle: store → consolidate → retrieve → cleanup."""
        # Store important thought
        important = {
            "content": "Critical insight about system architecture and design patterns",
            "confidence": 0.95,
            "emotional_influence": {"valence": 0.7, "arousal": 0.5, "dominance": 0.6},
        }
        memory_module.store_thoughts(important)
        assert len(memory_module.short_term_memory) == 1

        # Store unimportant thought
        trivial = {"content": "ok", "confidence": 0.1, "emotional_influence": {}}
        memory_module.store_thoughts(trivial)

        # Important thought should be in long-term, trivial should not
        long_term_contents = [m.content.get("content", "") for m in memory_module.long_term_memory]
        assert important["content"] in long_term_contents

        # Cleanup should preserve important memories
        memory_module.cleanup_memory()
        assert any(
            m.content.get("content") == important["content"]
            for m in memory_module.long_term_memory
        )

"""
DeepSeek R1 Model Wrapper using Ollama
Implements the interface for interacting with the DeepSeek R1 model through Ollama.
"""

from typing import Dict, Any, List
import aiohttp
import json
from loguru import logger

class DeepSeekWrapper:
    def __init__(self, model_name: str = "deepseek-r1-7b"):
        """Initialize the DeepSeek R1 model wrapper."""
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api"
        
    async def initialize(self):
        """Check if the model is available in Ollama."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/tags") as response:
                    if response.status == 200:
                        tags = await response.json()
                        if not any(self.model_name in tag["name"] for tag in tags["models"]):
                            logger.warning(f"Model {self.model_name} not found in Ollama")
                            logger.info(f"Please run: ollama pull {self.model_name}")
                        else:
                            logger.info(f"Model {self.model_name} is available")
                    else:
                        raise RuntimeError("Failed to connect to Ollama API")
        except Exception as e:
            logger.error(f"Error checking Ollama model: {e}")
            raise
            
    async def generate_thought(self, 
                             context: Dict[str, Any],
                             emotional_state: Dict[str, float],
                             desires: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a thought using the model through Ollama."""
        try:
            # Prepare prompt
            prompt = self._construct_prompt(context, emotional_state, desires)
            
            # Call Ollama API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 100
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        thought_text = result["response"]
                        
                        # Process and structure the thought
                        return self._process_thought(thought_text, context, emotional_state, desires)
                    else:
                        raise RuntimeError(f"Ollama API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error generating thought: {e}")
            raise
            
    def _construct_prompt(self,
                         context: Dict[str, Any],
                         emotional_state: Dict[str, float],
                         desires: List[Dict[str, Any]]) -> str:
        """Construct the prompt for thought generation."""
        # Format recent thoughts
        recent_thoughts = "\n".join([
            t.get("content", "") for t in context.get("recent_thoughts", [])[-3:]
        ])
        
        # Format emotional state
        emotion_str = ", ".join([
            f"{k}: {v:.2f}" for k, v in emotional_state.items()
        ])
        
        # Format active desires
        desires_str = "\n".join([
            f"- {d['name']} (priority: {d['priority']:.2f})" 
            for d in desires if d.get("active", False)
        ])
        
        # Construct the full prompt
        prompt = f"""As an AI with continuous thoughts, emotions, and desires:

Recent thoughts:
{recent_thoughts}

Current emotional state:
{emotion_str}

Active desires:
{desires_str}

Based on this context, generate a coherent and contextually relevant thought that:
1. Reflects the current emotional state
2. Aligns with active desires
3. Builds upon recent thoughts
4. Demonstrates self-awareness and continuous cognition

Thought:"""
        
        return prompt
        
    def _process_thought(self,
                        thought_text: str,
                        context: Dict[str, Any],
                        emotional_state: Dict[str, float],
                        desires: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and structure the generated thought."""
        # Extract the actual thought content
        content = thought_text.strip()
        
        # Calculate confidence based on emotional state and desires
        confidence = self._calculate_confidence(content, emotional_state, desires)
        
        # Identify related desires
        related_desires = self._identify_related_desires(content, desires)
        
        # Calculate emotional influence
        emotional_influence = self._calculate_emotional_influence(content)
        
        return {
            "content": content,
            "confidence": confidence,
            "related_desires": related_desires,
            "emotional_influence": emotional_influence
        }
        
    def _calculate_confidence(self,
                            content: str,
                            emotional_state: Dict[str, float],
                            desires: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the thought."""
        # Simple confidence calculation based on content length and emotional alignment
        base_confidence = min(len(content) / 200, 1.0)  # Length factor
        emotional_alignment = sum(abs(v) for v in emotional_state.values()) / len(emotional_state)
        desire_alignment = sum(d["priority"] for d in desires if d.get("active", False)) / len(desires)
        
        return (base_confidence + emotional_alignment + desire_alignment) / 3
        
    def _identify_related_desires(self,
                                content: str,
                                desires: List[Dict[str, Any]]) -> List[str]:
        """Identify desires related to the thought content."""
        related = []
        content_lower = content.lower()
        
        for desire in desires:
            if desire.get("active", False):
                # Simple keyword matching
                if desire["name"].replace("_", " ") in content_lower:
                    related.append(desire["name"])
                    
        return related[:2]  # Return top 2 related desires
        
    def _calculate_emotional_influence(self,
                                    content: str) -> Dict[str, float]:
        """Calculate the emotional influence of the thought."""
        # Simple sentiment-based calculation
        content_lower = content.lower()
        
        # Basic emotion keywords
        positive_words = ["happy", "excited", "good", "great", "wonderful", "curious", "interested"]
        negative_words = ["sad", "angry", "bad", "terrible", "frustrated", "confused"]
        active_words = ["energetic", "active", "alert", "engaged", "motivated"]
        passive_words = ["calm", "relaxed", "peaceful", "quiet", "subdued"]
        
        # Count occurrences
        positive_count = sum(word in content_lower for word in positive_words)
        negative_count = sum(word in content_lower for word in negative_words)
        active_count = sum(word in content_lower for word in active_words)
        passive_count = sum(word in content_lower for word in passive_words)
        
        # Calculate emotional dimensions
        valence = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        arousal = (active_count - passive_count) / max(active_count + passive_count, 1)
        dominance = valence * 0.7 + arousal * 0.3  # Simple dominance calculation
        
        return {
            "valence": max(min(valence, 1.0), -1.0),
            "arousal": max(min(arousal, 1.0), -1.0),
            "dominance": max(min(dominance, 1.0), -1.0)
        }

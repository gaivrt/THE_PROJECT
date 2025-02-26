"""
Thinking Engine Module
Manages the continuous thinking process of the AI system.
"""

from typing import Dict, Any, List, Optional
import asyncio
import time
import os
from loguru import logger
from ..llm_base import LLMRequest
from ..llm_factory import LLMFactory

class ThinkingEngine:
    """Manages the continuous thinking process."""
    
    def __init__(self, llm_type: str = "ollama", llm_config: Optional[Dict[str, Any]] = None):
        """Initialize the thinking engine."""
        self.llm_factory = LLMFactory()
        self.llm_type = llm_type.lower().strip()
        self.llm_config = llm_config or {}
        
        # Get proxy configuration from environment
        proxy = self.llm_factory.get_proxy_from_env()
        
        # Initialize LLM based on type
        if self.llm_type == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1")
            self.llm = self.llm_factory.create_ollama(
                base_url=base_url,
                proxy=proxy
            )
        elif self.llm_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required for Gemini API")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            self.llm = self.llm_factory.create_gemini(
                api_key=api_key,
                model_name=model_name,
                proxy=proxy
            )
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")
        
        logger.info(f"Initialized ThinkingEngine with {self.llm_type} LLM")
        
        self.thinking_chain = []
        self.last_thought = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    async def initialize_model(self) -> bool:
        """Check if LLM is available and ready."""
        for attempt in range(self.max_retries):
            try:
                is_healthy = await self.llm.health_check()
                if not is_healthy:
                    raise Exception(f"{self.llm_type} API is not available")
                logger.info(f"Successfully connected to {self.llm_type} API")
                return True
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Failed to initialize {self.llm_type} API (attempt {attempt + 1}/{self.max_retries}): {e}")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to initialize {self.llm_type} API after {self.max_retries} attempts: {e}")
                    return False
                    
    async def think(self, context: Dict[str, Any], emotional_state: Dict[str, float],
                   desires: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate thoughts based on current context, emotional state, and desires."""
        try:
            # Combine context with emotional state and desires
            thinking_input = self._prepare_thinking_input(context, emotional_state, desires)
            
            # Generate thoughts using LLM with retry logic
            for attempt in range(self.max_retries):
                try:
                    thoughts = await self._generate_thoughts(thinking_input)
                    self._update_thinking_chain(thoughts)
                    return thoughts
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Thought generation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Error in thinking process: {e}")
            return {
                "error": str(e),
                "thought": "I am having difficulty processing my thoughts at the moment.",
                "metadata": {
                    "error_type": type(e).__name__,
                    "attempt": self.max_retries
                }
            }
            
    async def _generate_thoughts(self, thinking_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate thoughts using the configured LLM."""
        prompt = self._format_thinking_prompt(thinking_input)
        
        request = LLMRequest(
            prompt=prompt,
            system="""你是一个AI代理的思维引擎。生成详细的、内省的想法，要求：
1. 展示深入的分析和反思
2. 考虑多个角度和影响
3. 与先前的上下文和情感状态建立联系
4. 展示清晰的推理和逻辑流程
5. 表达完整的想法，不要中途截断
6. 只输出<think>与<\think>之间的内容，不要任何输出""",
            stream=False,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 500
            }
        )
        
        try:
            response = await self.llm.generate(request)
            
            # Extract the response text
            thought_text = response.get("response", "")
            
            # Create thought structure
            current_time = time.time()
            
            # Format emotional state as a string description
            emotional_state = thinking_input["emotional_state"]
            emotional_desc = self._format_emotional_state(emotional_state)
            
            # Calculate confidence based on response metadata
            confidence = min(100, max(1, int(
                (response.get("eval_count", 0) / max(1, response.get("prompt_eval_count", 1))) * 100
            )))
            
            return {
                "content": thought_text,
                "confidence": confidence,
                "timestamp": int(current_time * 1000),  # Convert to milliseconds
                "related_desires": [
                    {
                        "name": d["name"],
                        "priority": float(d["priority"]),
                        "satisfaction_level": float(d["satisfaction_level"]),
                        "satisfaction_threshold": float(d["satisfaction_threshold"]),
                        "active": bool(d["active"])
                    }
                    for d in thinking_input["desires"]
                ],
                "emotionalState": emotional_desc,
                "metadata": {
                    "model": response.get("model", self.llm_type),
                    "created_at": response.get("created_at", ""),
                    "done": response.get("done", True),
                    "total_duration": response.get("total_duration", 0),
                    "load_duration": response.get("load_duration", 0),
                    "prompt_eval_count": response.get("prompt_eval_count", 0),
                    "eval_count": response.get("eval_count", 0),
                    "eval_duration": response.get("eval_duration", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error generating thoughts: {e}")
            raise
            
    def _format_emotional_state(self, emotional_state: Dict[str, float]) -> str:
        """Convert emotional state values into a descriptive string."""
        valence = emotional_state.get("valence", 0)
        arousal = emotional_state.get("arousal", 0)
        dominance = emotional_state.get("dominance", 0)
        
        # Generate descriptions based on values
        valence_desc = "Positive" if valence > 0 else "Negative" if valence < 0 else "Neutral"
        arousal_desc = "Energetic" if arousal > 0 else "Calm" if arousal < 0 else "Balanced"
        dominance_desc = "Dominant" if dominance > 0 else "Submissive" if dominance < 0 else "Neutral"
        
        # Combine descriptions
        return f"{valence_desc}, {arousal_desc}, {dominance_desc}"
        
    def _prepare_thinking_input(self, context: Dict[str, Any],
                              emotional_state: Dict[str, float],
                              desires: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare input for the thinking process by combining all relevant factors."""
        return {
            "context": context,
            "emotional_state": emotional_state,
            "desires": desires,
            "last_thought": self.last_thought,
            "thinking_chain": self.thinking_chain[-5:]  # Keep last 5 thoughts for context
        }
        
    def _format_thinking_prompt(self, thinking_input: Dict[str, Any]) -> str:
        """Format the thinking input into a prompt for the LLM."""
        return f"""作为一个持续思考的AI代理，请分析以下上下文并生成一个完整、连贯的想法：

当前上下文：
{thinking_input['context']}

情感状态：
{thinking_input['emotional_state']}

当前欲望：
{thinking_input['desires']}

上一个想法：
{thinking_input['last_thought']}

最近的思维链：
{thinking_input['thinking_chain']}

请生成一个完整的想法，要求：
1. 展示清晰的推理和逻辑进展
2. 表现情感意识和自我反思
3. 与先前的想法和上下文建立联系
4. 考虑当前的欲望和动机
5. 达到自然的结论，不要中途截断
"""
        
    def _update_thinking_chain(self, thought: Dict[str, Any]) -> None:
        """Update the thinking chain with the new thought."""
        if "error" not in thought:
            self.thinking_chain.append(thought)
            self.last_thought = thought
            
            # Keep thinking chain at a reasonable size
            if len(self.thinking_chain) > 100:
                self.thinking_chain = self.thinking_chain[-100:]

"""
Configuration Utility
Manages configuration settings for the Metis Continuum system.
"""

from typing import Dict, Any
import os
from pydantic import BaseSettings
from loguru import logger

class MetisConfig(BaseSettings):
    """Configuration settings for Metis Continuum."""
    
    # Model settings
    model_name: str = "deepseek-ai/deepseek-r1-70b"
    model_device: str = "cuda"  # or "cpu"
    
    # Thinking loop settings
    min_thinking_interval: float = 0.1
    max_thinking_interval: float = 5.0
    initial_thinking_interval: float = 1.0
    
    # Memory settings
    short_term_memory_size: int = 100
    long_term_memory_size: int = 1000
    context_window_size: int = 10
    memory_consolidation_threshold: float = 0.7
    
    # Emotion settings
    emotion_decay_rate: float = 0.1
    emotion_intensity_limits: tuple = (-1.0, 1.0)
    
    # Desire settings
    desire_decay_rate: float = 0.05
    min_desire_priority: float = 0.1
    max_desire_priority: float = 1.0
    
    # Evaluation settings
    expression_threshold: float = 0.7
    evaluation_weights: Dict[str, float] = {
        "coherence": 0.3,
        "relevance": 0.2,
        "novelty": 0.15,
        "emotional_impact": 0.15,
        "desire_alignment": 0.2
    }
    
    # Server settings
    host: str = "localhost"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        
def load_config() -> MetisConfig:
    """Load configuration from environment variables and .env file."""
    try:
        config = MetisConfig()
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise
        
def create_default_env():
    """Create default .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# Metis Continuum Configuration

# Model settings
MODEL_NAME=deepseek-ai/deepseek-r1-70b
MODEL_DEVICE=cuda

# Server settings
HOST=localhost
PORT=8000

# Add your custom settings below
""")

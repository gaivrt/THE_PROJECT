"""
Base LLM Module
Defines the base interface for LLM implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class LLMRequest:
    """Base request structure for LLM APIs."""
    prompt: str
    system: str = None
    stream: bool = False
    options: Dict[str, Any] = None

class BaseLLM(ABC):
    """Base class for LLM implementations."""
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate response from the LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is available."""
        pass

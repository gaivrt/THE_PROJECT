"""
LLM Factory Module
Manages different LLM implementations.
"""

from typing import Dict, Optional, Union
from .llm_base import BaseLLM
from .ollama_api import OllamaAPI
from .gemini_api import GeminiAPI
import os
from loguru import logger

class LLMFactory:
    """Factory class for creating LLM instances."""
    
    def __init__(self):
        self._llms: Dict[str, BaseLLM] = {}
        
    def register_llm(self, name: str, llm: BaseLLM):
        """Register a new LLM implementation."""
        self._llms[name] = llm
        
    def get_llm(self, name: str) -> Optional[BaseLLM]:
        """Get a registered LLM by name."""
        return self._llms.get(name)
        
    @staticmethod
    def create_ollama(base_url: str = "http://localhost:11434", proxy: Optional[str] = None) -> OllamaAPI:
        """Create an Ollama API instance."""
        proxy_config = proxy or LLMFactory.get_proxy_from_env()
        logger.debug(f"Creating Ollama API with proxy: {proxy_config}")
        return OllamaAPI(base_url=base_url, proxy=proxy_config)
        
    @staticmethod
    def create_gemini(api_key: str, model_name: str = "gemini-2.0-flash", proxy: Optional[str] = None) -> GeminiAPI:
        """Create a Gemini API instance."""
        proxy_config = proxy or LLMFactory.get_proxy_from_env()
        logger.debug(f"Creating Gemini API with proxy: {proxy_config}")
        return GeminiAPI(api_key=api_key, model_name=model_name, proxy=proxy_config)
        
    @staticmethod
    def get_proxy_from_env() -> Optional[str]:
        """Get proxy configuration from environment variables."""
        if os.getenv("USE_PROXY", "false").lower() == "true":
            # Try HTTPS proxy first, then HTTP proxy, then SOCKS proxy
            proxy = (
                os.getenv("HTTPS_PROXY") or 
                os.getenv("HTTP_PROXY") or 
                os.getenv("SOCKS_PROXY")
            )
            if proxy:
                logger.info(f"Using proxy from environment: {proxy}")
                return proxy
            else:
                logger.warning("USE_PROXY is true but no proxy URL found in environment variables")
        return None

"""
Gemini API Module
Implements integration with Google's Gemini API.
"""

from typing import Dict, Any, Optional
import google.generativeai as genai
import aiohttp
from loguru import logger
from dataclasses import dataclass
import os

@dataclass
class GeminiRequest:
    """Request structure for Gemini API."""
    prompt: str
    system: Optional[str] = None
    stream: bool = False
    options: Dict[str, Any] = None

class GeminiAPI:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", proxy: Optional[str] = None):
        """Initialize Gemini API with API key and model name."""
        self.api_key = api_key
        self.model_name = model_name
        self.proxy = proxy
        
        # Configure proxy for requests if specified
        if proxy:
            logger.info(f"Configuring Gemini API with proxy: {proxy}")
            # Set environment variables for requests
            os.environ['HTTPS_PROXY'] = proxy
            os.environ['HTTP_PROXY'] = proxy
            os.environ['GOOGLE_API_USE_CLIENT_CERTIFICATE'] = 'false'
            
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    async def generate(self, request: GeminiRequest) -> Dict[str, Any]:
        """Generate response using Gemini API."""
        try:
            # Configure model settings
            if request.options:
                if "temperature" in request.options:
                    self.model.temperature = request.options["temperature"]
                if "top_p" in request.options:
                    self.model.top_p = request.options["top_p"]
                if "top_k" in request.options:
                    self.model.top_k = request.options["top_k"]
                if "max_output_tokens" in request.options:
                    self.model.max_output_tokens = request.options["max_output_tokens"]

            # Set system instruction if provided
            if request.system:
                self.model.system_instruction = request.system

            # Generate content
            if request.stream:
                response = await self._stream_generate(request.prompt)
            else:
                response = await self._generate(request.prompt)

            return response

        except Exception as e:
            logger.error(f"Error in Gemini API generation: {e}")
            return {
                "error": str(e),
                "response": "Error generating response from Gemini API"
            }

    async def _generate(self, prompt: str) -> Dict[str, Any]:
        """Generate non-streaming response."""
        try:
            response = self.model.generate_content(prompt)
            return {
                "response": response.text,
                "model": self.model_name,
                "done": True
            }
        except Exception as e:
            logger.error(f"Error in Gemini generation: {e}")
            return {
                "error": str(e),
                "response": "Error generating response",
                "done": True
            }

    async def _stream_generate(self, prompt: str) -> Dict[str, Any]:
        """Generate streaming response."""
        try:
            response = self.model.generate_content(prompt, stream=True)
            chunks = []
            async for chunk in response:
                chunks.append(chunk.text)
            
            return {
                "response": "".join(chunks),
                "model": self.model_name,
                "done": True
            }
        except Exception as e:
            logger.error(f"Error in Gemini streaming: {e}")
            return {
                "error": str(e),
                "response": "Error generating streaming response",
                "done": True
            }

    async def health_check(self) -> bool:
        """Check if Gemini API is available and working."""
        try:
            response = await self._generate("Hi")
            return "error" not in response
        except Exception as e:
            logger.error(f"Gemini API health check failed: {e}")
            return False

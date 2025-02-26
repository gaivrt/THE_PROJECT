"""
Ollama API integration module for the Metis Continuum project.
Handles communication with the Ollama API for AI model interactions.
"""

import aiohttp
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
import traceback
import asyncio
from .llm_base import BaseLLM, LLMRequest
from dataclasses import dataclass, asdict

@dataclass
class OllamaRequest(LLMRequest):
    """Request structure for Ollama API."""
    model: str = "deepseek-r1"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        base_dict = asdict(self)
        # Remove None values
        return {k: v for k, v in base_dict.items() if v is not None}

class OllamaAPI(BaseLLM):
    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 60.0, model_name: str = "deepseek-r1", proxy: Optional[str] = None):
        """Initialize Ollama API with base URL."""
        self.base_url = base_url
        self.timeout = timeout
        self.model_name = model_name
        self.generate_endpoint = f"{base_url}/api/generate"
        self.chat_endpoint = f"{base_url}/api/chat"
        self.proxy = proxy

    async def generate(self, request: LLMRequest) -> Dict[str, Any]:
        """Generate a response from the Ollama API."""
        if not isinstance(request, OllamaRequest):
            # Convert base request to Ollama request
            request = OllamaRequest(
                prompt=request.prompt,
                system=request.system,
                stream=request.stream,
                options=request.options,
                model="deepseek-r1"
            )
            
        try:
            data = request.to_dict()
            logger.debug(f"Sending generate request with data: {data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60),  # 60 second timeout for generation
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Generate request failed with status {response.status}: {error_text}")
                    
                    if request.stream:
                        return await self._handle_stream_response(response)
                    else:
                        try:
                            response_text = await response.text()
                            if not response_text:
                                raise Exception("Empty response received from Ollama API")
                            
                            response_data = json.loads(response_text)
                            if not response_data:
                                raise Exception("No valid response data received")
                                
                            logger.debug(f"Received response: {response_data}")
                            return response_data
                            
                        except json.JSONDecodeError as e:
                            raise Exception(f"Failed to parse response as JSON: {e}")
                        
        except asyncio.TimeoutError:
            raise Exception("Generate request timed out")
        except aiohttp.ClientError as e:
            raise Exception(f"Generate request failed with client error: {e}")
        except Exception as e:
            if isinstance(e, Exception):
                raise
            raise Exception(f"Generate request failed with unexpected error: {e}")

    async def _handle_stream_response(self, response) -> Dict[str, Any]:
        """Handle streaming response from Ollama API."""
        try:
            final_response = None
            async for line in response.content:
                if line:
                    try:
                        line_data = json.loads(line)
                        if line_data:
                            final_response = line_data
                    except json.JSONDecodeError:
                        continue
                        
            if final_response is None:
                raise Exception("No valid response data received from stream")
                
            return final_response
            
        except Exception as e:
            raise Exception(f"Error handling stream response: {e}")

    async def chat(self, request: LLMRequest) -> Dict[str, Any]:
        """
        Send a chat request to the Ollama API.
        
        Args:
            request (LLMRequest): The request parameters for chat
            
        Returns:
            Dict[str, Any]: The response from the Ollama API
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout, connect=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {"Content-Type": "application/json"}
                request_data = request.to_dict()
                logger.debug(f"Sending chat request to Ollama API: {request_data}")
                
                async with session.post(
                    self.chat_endpoint,
                    json=request_data,
                    headers=headers,
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error (status {response.status}): {error_text}")
                        raise Exception(f"Ollama API returned status {response.status}: {error_text}")

                    # Read and process the ndjson response
                    response_data = None
                    try:
                        async for line in response.content:
                            if line:
                                try:
                                    line_data = json.loads(line.decode('utf-8'))
                                    if not line_data.get("done", False):
                                        response_data = line_data
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to decode JSON line: {e}")
                                    continue
                    except Exception as e:
                        logger.error(f"Error reading response stream: {e}")
                        raise

                    if response_data is None:
                        logger.error("No valid response data received")
                        raise Exception("No valid response received from Ollama API")

                    logger.debug(f"Received chat response: {response_data}")
                    return response_data

        except asyncio.TimeoutError as e:
            logger.error(f"Chat request timed out after {self.timeout} seconds")
            raise Exception(f"Chat request timed out after {self.timeout} seconds") from e
        except aiohttp.ClientError as e:
            logger.error(f"Ollama API client error in chat: {str(e)}\n{traceback.format_exc()}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat request: {str(e)}\n{traceback.format_exc()}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama API is available and responsive."""
        try:
            data = {
                "model": self.model_name,
                "prompt": "test",
                "stream": False,
                "options": {
                    "num_predict": 1  # Minimal prediction for health check
                }
            }
            
            logger.debug(f"Performing health check with data: {data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10),  # Shorter timeout for health check
                    proxy=self.proxy
                ) as response:
                    if response.status == 200:
                        logger.debug("Successfully connected to Ollama API")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Health check failed with status {response.status}: {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Health check timed out")
            return False
        except aiohttp.ClientError as e:
            logger.error(f"Health check failed with client error: {e}")
            return False
        except Exception as e:
            logger.error(f"Health check failed with unexpected error: {e}")
            return False

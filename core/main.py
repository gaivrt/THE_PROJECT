"""
Metis Continuum - Main Entry Point
This module initializes and coordinates all core components of the Metis Continuum system.
"""

import asyncio
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typing import Dict, Any
import httpx
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import time
import os
import json
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import core modules
from core.modules.thinking_engine import ThinkingEngine
from core.modules.emotion_module import EmotionModule
from core.modules.desire_system import DesireSystem
from core.modules.memory_module import MemoryModule
from core.modules.evaluation_system import EvaluationSystem
from core.ollama_api import OllamaAPI, OllamaRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application."""
    # Startup: Initialize the continuous thinking process
    logger.info("Starting Metis Continuum system...")
    metis.thinking_task = asyncio.create_task(metis.start_continuous_thinking())
    yield
    # Shutdown: Clean up resources
    if metis.thinking_task:
        metis.thinking_task.cancel()
        try:
            await metis.thinking_task
        except asyncio.CancelledError:
            pass
    logger.info("Metis Continuum system shutdown complete")

app = FastAPI(title="Metis Continuum API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only - configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetisContinuum:
    def __init__(self):
        """Initialize the Metis Continuum system with all core components."""
        # Load environment variables
        load_dotenv()
        
        # Debug: Print environment variables
        logger.debug(f"Environment variables:")
        logger.debug(f"LLM_TYPE: {os.getenv('LLM_TYPE')}")
        logger.debug(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")
        logger.debug(f"GEMINI_MODEL: {os.getenv('GEMINI_MODEL')}")
        logger.debug(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
        logger.debug(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")
        
        # Get LLM configuration from environment
        llm_type = os.getenv("LLM_TYPE", "ollama")
        if llm_type:
            llm_type = llm_type.lower().strip().split("#")[0].strip()  # Remove comments and whitespace
        logger.info(f"Using LLM type: {llm_type}")
        llm_config = self._get_llm_config(llm_type)
        
        # Initialize thinking engine with specified LLM
        self.thinking_engine = ThinkingEngine(llm_type=llm_type, llm_config=llm_config)
        self.emotion_module = EmotionModule()
        self.desire_system = DesireSystem()
        self.memory_module = MemoryModule()
        self.evaluation_system = EvaluationSystem()
        
        # Background thinking task
        self.thinking_task = None
        
    def _get_llm_config(self, llm_type: str) -> Dict[str, Any]:
        """Get LLM configuration based on type."""
        config = {}
        
        if llm_type == "ollama":
            config["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            config["model_name"] = os.getenv("OLLAMA_MODEL", "deepseek-r1")
        elif llm_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required for Gemini API")
            config["api_key"] = api_key
            config["model_name"] = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        return config

    async def start_continuous_thinking(self):
        """Start the continuous background thinking process."""
        while True:
            try:
                # Get current context from memory
                context = self.memory_module.get_current_context()
                
                # Generate thoughts based on context, emotions, and desires
                thoughts = await self.thinking_engine.think(
                    context=context,
                    emotional_state=self.emotion_module.get_current_state(),
                    desires=self.desire_system.get_active_desires()
                )
                
                # Evaluate thoughts
                evaluation = self.evaluation_system.evaluate_thoughts(thoughts)
                
                # Update memory and emotional state based on thoughts
                self.memory_module.store_thoughts(thoughts)
                self.emotion_module.update_state(thoughts, evaluation)
                
                # Decide whether to express thoughts
                if self.evaluation_system.should_express(thoughts, evaluation):
                    # Queue thoughts for expression
                    await self.queue_expression(thoughts)
                
                # Longer pause between thoughts to allow for more natural thinking rhythm
                # and to prevent overwhelming the system
                await asyncio.sleep(5.0)  # 5 seconds between thoughts
                
            except Exception as e:
                logger.error(f"Error in continuous thinking process: {e}")
                # Brief pause before retrying after an error
                await asyncio.sleep(1.0)

    async def queue_expression(self, thoughts: Dict[str, Any]):
        """Queue thoughts for expression through the frontend."""
        # Implementation for expression queuing
        pass

    async def test_ollama_connection(self) -> bool:
        """Test the connection to Ollama API."""
        try:
            # First check if Ollama API is healthy
            is_healthy = await self.ollama_api.health_check()
            if not is_healthy:
                logger.error("Ollama API health check failed")
                return False

            # Then initialize the thinking engine which uses Ollama
            engine_initialized = await self.thinking_engine.initialize_model()
            if not engine_initialized:
                logger.error("Failed to initialize thinking engine with Ollama")
                return False

            logger.info("Successfully connected to Ollama and initialized thinking engine")
            return True
        except Exception as e:
            logger.error(f"Error testing Ollama connection: {e}")
            return False

# Initialize the system
metis = MetisContinuum()

@app.post("/api/generate")
async def generate(request: OllamaRequest):
    """
    Generate a response using the Ollama API.
    """
    try:
        response = await metis.ollama_api.generate(request)
        return response
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: OllamaRequest):
    """
    Send a chat request to the Ollama API.
    """
    try:
        response = await metis.ollama_api.chat(request)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Check the health of the Ollama API.
    """
    try:
        is_healthy = await metis.ollama_api.health_check()
        return {"status": "healthy" if is_healthy else "unhealthy"}
    except Exception as e:
        logger.error(f"Error in health check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection opened")
    
    try:
        # Send initial state
        initial_state = await process_websocket_message({})
        await websocket.send_json(initial_state)
        
        # Start periodic state updates
        while True:
            try:
                # Process any incoming messages
                data = await websocket.receive_json()
                response = await process_websocket_message(data)
                await websocket.send_json(response)
                
                # Send periodic state updates
                state_update = await process_websocket_message({})
                await websocket.send_json(state_update)
                
                # Brief pause to prevent overwhelming the connection
                await asyncio.sleep(1)
                
            except WebSocketDisconnect as e:
                if e.code == 1000:
                    logger.info("WebSocket closed normally")
                elif e.code == 1001:
                    logger.info("WebSocket client disconnected")
                else:
                    logger.warning(f"WebSocket disconnected with code {e.code}: {e.reason}")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({"type": "error", "data": str(e)})
    finally:
        logger.info("WebSocket connection closed")

async def process_websocket_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process messages from the frontend and generate appropriate responses."""
    try:
        # Get current system state
        context = metis.memory_module.get_current_context()
        emotional_state = metis.emotion_module.get_current_state()
        desires = metis.desire_system.get_active_desires()
        
        # Create state update message
        state_update = {
            "type": "state_update",
            "data": {
                "thoughts": [
                    {
                        "content": thought.get("content", ""),
                        "confidence": float(thought.get("confidence", 0.0)),
                        "timestamp": int(thought.get("timestamp", time.time() * 1000)),  # Convert to milliseconds
                        "related_desires": [
                            {
                                "name": d["name"],
                                "priority": float(d["priority"]),
                                "satisfaction_level": float(d["satisfaction_level"]),
                                "satisfaction_threshold": float(d["satisfaction_threshold"]),
                                "active": bool(d["active"])
                            }
                            for d in thought.get("related_desires", [])
                        ],
                        "emotionalState": thought.get("emotional_state", "neutral")
                    }
                    for thought in context.get("recent_thoughts", [])
                ],
                "emotions": {
                    "valence": float(emotional_state["valence"]),
                    "arousal": float(emotional_state["arousal"]),
                    "dominance": float(emotional_state["dominance"])
                },
                "desires": [
                    {
                        "name": d["name"],
                        "priority": float(d["priority"]),
                        "satisfaction_level": float(d["satisfaction_level"]),
                        "satisfaction_threshold": float(d["satisfaction_threshold"]),
                        "active": bool(d["active"])
                    }
                    for d in desires
                ]
            }
        }
        
        return state_update
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {
            "type": "error",
            "data": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Metis Continuum server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["core"],
        workers=1
    )

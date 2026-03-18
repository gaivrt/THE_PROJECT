# CLAUDE.md - Metis Continuum

## Project Overview

Metis Continuum is an AI system that simulates continuous human-like thinking. It integrates emotion, desire, memory, and evaluation modules to produce context-aware, emotionally influenced thought processes. The system runs as a FastAPI backend with WebSocket support for real-time state updates.

## Tech Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI + Uvicorn
- **ML/AI**: PyTorch, DeepSeek R1 (via Ollama or direct), Google Gemini (cloud fallback)
- **Validation**: Pydantic (BaseSettings for config)
- **Logging**: loguru
- **Testing**: pytest + pytest-asyncio
- **Async**: asyncio, aiohttp, websockets, httpx

## Directory Structure

```
├── core/                        # Main application code
│   ├── main.py                  # FastAPI app, MetisContinuum orchestrator, endpoints
│   ├── llm_base.py              # Abstract base class for LLM implementations
│   ├── llm_factory.py           # Factory for creating LLM instances (Ollama/Gemini)
│   ├── ollama_api.py            # Ollama API integration
│   ├── gemini_api.py            # Google Gemini API integration
│   ├── modules/
│   │   ├── thinking_engine.py   # Core continuous thinking logic
│   │   ├── emotion_module.py    # VAD (Valence-Arousal-Dominance) emotion model
│   │   ├── desire_system.py     # Desire-driven behavior with priority/satisfaction
│   │   ├── memory_module.py     # Short-term and long-term memory management
│   │   └── evaluation_system.py # Thought evaluation and expression filtering
│   ├── models/
│   │   └── deepseek_wrapper.py  # DeepSeek R1 model wrapper
│   ├── api/                     # API endpoint definitions
│   └── utils/
│       ├── config.py            # MetisConfig (Pydantic BaseSettings)
│       └── thinking_loop.py     # Continuous thinking loop mechanism
├── tests/                       # pytest test suite
│   ├── conftest.py              # Shared fixtures (event_loop)
│   ├── test_emotion_module.py
│   ├── test_desire_system.py
│   ├── test_memory_module.py
│   ├── test_evaluation_system.py
│   └── test_deepseek_wrapper.py
├── .env                         # Environment configuration (not committed)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── test_ollama.py               # Standalone Ollama connection test
```

## Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy or create a `.env` file at the project root with required settings (see Configuration below).

## Common Commands

```bash
# Run the server
python -m uvicorn core.main:app --reload

# Run all tests
pytest

# Run a specific test file
pytest tests/test_emotion_module.py

# Test Ollama connection
python test_ollama.py
```

## Configuration

Configuration is managed via `.env` file and loaded through Pydantic `BaseSettings` in `core/utils/config.py`.

Key environment variables:
- `LLM_TYPE` - LLM backend: `ollama` (default) or `gemini`
- `OLLAMA_BASE_URL` - Ollama API URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Ollama model name (default: `deepseek-r1`)
- `GEMINI_API_KEY` - Required when using Gemini backend
- `GEMINI_MODEL` - Gemini model (default: `gemini-2.0-flash`)
- `MODEL_NAME`, `MODEL_DEVICE` - Base model settings
- `HOST`, `PORT` - Server bind settings (default: `localhost:8000`)
- `SHORT_TERM_MEMORY_SIZE`, `LONG_TERM_MEMORY_SIZE` - Memory limits
- `EMOTION_DECAY_RATE`, `DESIRE_DECAY_RATE` - Module decay rates
- `EXPRESSION_THRESHOLD` - Minimum score for thought expression
- `USE_PROXY`, `HTTP_PROXY`, `HTTPS_PROXY`, `SOCKS_PROXY` - Network proxy settings

## API Endpoints

- `POST /api/generate` - Generate a response via Ollama
- `POST /api/chat` - Chat endpoint via Ollama
- `GET /api/health` - Health check
- `WS /ws` - WebSocket for real-time state updates (thoughts, emotions, desires)

## Architecture and Patterns

- **Async-first**: All core operations use `async/await`. The thinking engine runs as a background `asyncio.Task`.
- **Factory pattern**: `LLMFactory` in `core/llm_factory.py` creates the appropriate LLM backend (Ollama or Gemini) based on config.
- **Abstract base class**: `BaseLLM` in `core/llm_base.py` defines the LLM interface; all backends implement it.
- **Class-based modules**: Each cognitive module (emotion, desire, memory, evaluation, thinking) is a standalone class in `core/modules/`.
- **Orchestrator**: `MetisContinuum` class in `core/main.py` wires all modules together and runs the continuous thinking loop.
- **Pydantic config**: `MetisConfig(BaseSettings)` auto-loads from `.env` with typed defaults.

## Coding Conventions

- Full type hints on all function signatures (use `typing` module)
- Docstrings on classes and public methods
- `loguru.logger` for all logging (debug, info, error levels)
- Pydantic models for data validation and request/response schemas
- Error handling with try/except and logger.error in critical paths
- Async test support via `pytest-asyncio` with `asyncio_mode = auto`

## Testing

Tests live in `tests/` and follow these conventions:
- File naming: `test_*.py`
- Class naming: `Test*`
- Function naming: `test_*`
- Fixtures defined in `tests/conftest.py`
- Async tests are auto-detected (no `@pytest.mark.asyncio` needed due to `asyncio_mode = auto` in `pytest.ini`)
- Tests cover initialization, state transitions, decay mechanisms, and multi-component workflows

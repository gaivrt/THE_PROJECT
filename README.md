# Metis Continuum

A groundbreaking AI system that simulates continuous human-like thinking through desire-driven chains, powered by DeepSeek R1.

## Project Overview

Metis Continuum is an innovative AI system that aims to create a truly "living" artificial intelligence that thinks continuously in the background, similar to the human brain. It leverages the powerful DeepSeek R1 language model, enhanced with emotion and desire-driven mechanisms, to create a more human-like AI experience.

## Core Features

- **Continuous Background Thinking**: System runs perpetually, simulating never-ending brain activity
- **Emotion & Desire Integration**: Enhanced with emotional awareness and desire-driven decision making
- **Memory Management**: Sophisticated memory system for context retention and knowledge accumulation
- **Autonomous Expression**: AI independently decides when and what to express based on internal states
- **Frontend Interface**: Modern React-based UI for monitoring and interacting with the AI

## Architecture

The project follows a modular architecture with these key components:

- `core/models/`: Contains the distilled DeepSeek R1 model implementations
- `core/modules/`: Houses the core system modules (emotion, desire, memory, evaluation)
- `core/utils/`: Utility functions and helper classes
- `frontend/`: React-based user interface
- `tests/`: Test suite
- `docs/`: Project documentation

## Getting Started

### Prerequisites

- Install [Ollama](https://ollama.ai/)
- Pull the DeepSeek R1 7B model:
```bash
ollama pull deepseek-r1-7b
```
- Python 3.9 or higher
- Node.js 16+
- GPU with CUDA support (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/metis-continuum.git
cd metis-continuum
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

### Configuration

Create a `.env` file in the project root with the following settings:

```env
# Model Settings
MODEL_NAME=deepseek-r1-7b
OLLAMA_API_URL=http://localhost:11434/api

# Server Settings
HOST=localhost
PORT=8000

# Thinking Loop Settings
THOUGHT_INTERVAL=5.0
MEMORY_CLEANUP_INTERVAL=300.0

# Memory Settings
SHORT_TERM_MEMORY_SIZE=100
CONTEXT_WINDOW_SIZE=10
LONG_TERM_MEMORY_THRESHOLD=0.7

# Emotion Settings
EMOTION_DECAY_RATE=0.1
EMOTION_UPDATE_WEIGHT=0.3

# Desire Settings
DESIRE_DECAY_RATE=0.05
SATISFACTION_THRESHOLD=0.7

# Evaluation Settings
MIN_CONFIDENCE_THRESHOLD=0.6
MIN_EMOTIONAL_IMPACT=0.3
```

### Running the System

1. Start the backend server:
```bash
python -m uvicorn core.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

## Contributing

We welcome contributions! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- DeepSeek AI for their groundbreaking R1 model
- The open-source AI community for inspiration and support

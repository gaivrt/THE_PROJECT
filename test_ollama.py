import asyncio
from core.main import metis

async def test():
    result = await metis.test_ollama_connection()
    if result:
        print("✅ Successfully connected to Ollama!")
    else:
        print("❌ Failed to connect to Ollama. Please make sure Ollama is running.")

if __name__ == "__main__":
    asyncio.run(test())

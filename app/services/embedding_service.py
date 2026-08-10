import httpx
from app.config import settings

async def embedding(text: str) -> list[float]:
    """
    Take a text and convert it into a semantic vector
    """
    
    async with httpx.AsyncClient(timeout=120) as client:

        
        response = await client.post(
            f"{settings.OLLAMA_URL}/api/embeddings",
            json={
                "model": settings.EMBEDDING_MODEL,
                "prompt": text
            }
        )

        response.raise_for_status()

        return response.json()["embedding"]


import httpx
from app.config import settings

async def query_llm(payload: dict):
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        
        response = await client.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json=payload
        )
        
        response.raise_for_status() 
        return response.json()
        


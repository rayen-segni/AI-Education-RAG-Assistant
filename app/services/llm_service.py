from ollama import AsyncClient
from app.config import settings

async def query_llm(payload: dict) -> str:
    
    client = AsyncClient()

    
    temp = payload.pop("temperature", None)
    
    response = await client.chat(
        options={
            "temperature": temp
        },
        **payload
    )
    
    # The output content string
    return response["message"]["content"]
        


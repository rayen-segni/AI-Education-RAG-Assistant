from ollama import AsyncClient
from app.config import settings


"""
response = await client.embed(
    model="nomic-embed-text", input=["Chunk 1 text", "Chunk 2 text"]
)

# response.embeddings has length 2
# response.embeddings[0] -> Vector for "Chunk 1 text"
# response.embeddings[1] -> Vector for "Chunk 2 text"

that's why we take [0] because embed can accept multiple text at once
"""


async def embedding(text: str) -> list[float]:
    """
    Take a text and convert it into a semantic vector
    """

    client = AsyncClient()
    
    response = await client.embed(
        model=settings.EMBEDDING_MODEL,
        input=text
    )


    return list(response.embeddings[0])


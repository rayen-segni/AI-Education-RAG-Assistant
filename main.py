import asyncio
from config import settings
from pathlib import Path
from repository.documents import DocumentsRepository
from ingestion.pipeline import DocumentIngestionPipeline
from services.embedding_service import embedding
from services.llm_service import query_llm
from psycopg.errors import UniqueViolation

from pathlib import Path
from rich.console import Console
from rich.progress import track
from psycopg.errors import UniqueViolation

# Initialize rich console instance
console = Console()

async def insert_file(
    file: Path, 
    chunk_size: int = 500, 
    overlap_ratio: float = 0.1, 
    subject: str = "", 
    metadata: dict = None
) -> None:
    """
    Take a file pass it in the chunking pipeline and insert it in the database
    """

    pipeline = DocumentIngestionPipeline(chunk_size, overlap_ratio)

    console.print("[cyan][Status]:[/] Start processing document...")
    # Pass the file in the pipline: Loading -> Cleaning -> Chunking
    chunks: list[dict] = pipeline.process_file(file)
    console.print("[green][Success]:[/] Document processing complete with success !")
    
    #Prepare the document dict
    document = {
        "filename": file.name,
        "file_path": str(file),
        "file_type": file.suffix.lower(),
        "total_chunks": len(chunks)
    }

    console.print("[cyan][Status]:[/] Adding the document in the database...")
    try:
        document_id = await DocumentsRepository.add_document(document)
        
    except UniqueViolation as e: # If the document already exists
        console.print(f"[red][Error]:[/] {e}")
        return
    except Exception as e:
        console.print(f"[red][Error]:[/] Failed to insert document: {e}")
        return
    console.print("[green][Success]:[/] Document added with success !")

    # Base metadata passed from caller or extracted from file context
    base_metadata = metadata or {
        "title": file.stem.replace("_", " ").title(),
        "subject": subject,
        "source": file.name
    }

    console.print("[cyan][Status]:[/] Vectorizing chunks and add them in the database...")
    # Vectorize each chunk and insert it in the database with their metadata using the track bar
    for chunk in track(chunks, description="[cyan][Status]: Embedding & inserting chunks...[/]"):
        chunk["document_id"] = document_id
        chunk["embedding"] = str(await embedding(chunk["content"]))
        
        # Inject metadata into chunk (including chunk page/index)
        chunk["metadata"] = {
            **base_metadata,
            "chunk_index": chunk["chunk_index"],
            "chunk_count": chunk["token_count"]
        }
        
        await DocumentsRepository.add_chunk(chunk)
        
    console.print("[green][Success]:[/] Chunks added with success !")
    console.print(f"[green][Success]:[/] {file.name} was inserted with sucesss !")

    

async def semantic_search(query: str, top_k: int):
    """
    Take a query and search the top nearest chunks to it
    """

    embeded_vector = await embedding(query)
    return await DocumentsRepository.search_chunks(embeded_vector, top_k)


async def chat(msg: str):
    
    """
    RAG Pipeline 
        Prompt -> Retriever -> Context -> LLM -> Answer
    """
    
    
    top_k = 5
    
    # Retrieve relevant chunks
    infos = await semantic_search(msg, top_k)
    
    #Extract content in an array
    context_arr = [chunk[2] for chunk in infos]
    
    with open("output.json", "w", encoding="utf-8") as f:
        f.write(str(context_arr))
    
    #Prepare text
    context = "\n".join(context_arr)
    
    #Prepare Prompt
    prompt = f"""
    Context:
        {context}
    
    These are informations in the context about the user prompt 
    you can use them as trusted source to help you reply on the prompt bellow.
    
    User prompt:
        {msg}
    """
    
    #Prepare payload to Ollama API
    payload = {
        "model": settings.LARGE_LANGUAGE_MODEL,
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "stream": False
    }
    
    try:
        #Send prompt to the LLM
        response = await query_llm(payload)
        
    except Exception as e:
        print("Error: ", e)
        
    else:
        
        return response["message"]["content"]

FILE = Path("documents") / "retriever_augmented_generation.md"

async def main():

    await insert_file(FILE, chunk_size=500, overlap_ratio=0.1, subject="RAG")


if __name__ == "__main__":
    asyncio.run(main())

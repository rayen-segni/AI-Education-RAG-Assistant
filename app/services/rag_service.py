from pathlib import Path
from psycopg.errors import UniqueViolation
from rich.console import Console
from rich.progress import track

from app.config import settings
from app.repository.documents import DocumentsRepository
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.services.embedding_service import embedding
from app.services.llm_service import query_llm


# Initialize rich console instance
console = Console()

async def insert_file(
    file: Path, 
    chunk_size: int = 500, 
    overlap_ratio: float = 0.1, 
    subject: str = "", 
    metadata: dict = {}
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
        raise
    except Exception as e:
        console.print_exception()
        raise
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


async def chat(msg: str) -> dict[str, list[str]] | None:
    
    """
    RAG Pipeline 
        Prompt -> Retriever -> Context -> LLM -> Answer
    """
    
    
    top_k = 5
    
    # Retrieve relevant chunks
    infos = await semantic_search(msg, top_k)
    
    #Extract content in an array
    context_arr = [chunk[2] for chunk in infos]

    sources: list[str] = []
    subjects: list[str] = []
    for chunk in infos:
        sources.append(
            chunk[4]["source"]
        )

        subjects.append(
            chunk[4]["subject"]
        )
    
    #Prepare text
    context = "\n".join(context_arr)
    
    #Prepare Prompt
    system_instruction = (
            "You are a precise technical AI assistant. "
            "Answer the user's question using ONLY the provided context below. "
            "If the information is not present or cannot be directly inferred from the context, "
            "explicitly state: 'The provided context does not contain sufficient information to answer this question.' "
            "Do NOT use external knowledge or fabricate details."
        )
    user_content = f"Context:\n{context}\n\nUser Question:\n{msg}"
    messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]
    
    #Prepare payload to Ollama API
    payload = {
        "model": settings.LARGE_LANGUAGE_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        #Send prompt to the LLM
        answer = await query_llm(payload)
        
    except Exception as e:
        print("Error: ", e)
        
    else:
        output = {
            "response": answer,
            "sources": list(dict.fromkeys(sources)),
            "subjects": list(dict.fromkeys(subjects))
        }
        
        return output


BASE_DIR = Path(__file__).resolve().parent.parent.parent
async def main():
    print("Hello")
    files = [
        f"{BASE_DIR}/documents/async.md",
        f"{BASE_DIR}/documents/cloud.md",
        f"{BASE_DIR}/documents/docker.md",
        f"{BASE_DIR}/documents/fastapi-cli.md",
        f"{BASE_DIR}/documents/fastapi.md",
        f"{BASE_DIR}/documents/fastapicloud.md",
        f"{BASE_DIR}/documents/https.md",
        f"{BASE_DIR}/documents/server-workers.md",
        f"{BASE_DIR}/documents/websockets.md",
    ]

    for file in files:
        await insert_file(Path(file))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
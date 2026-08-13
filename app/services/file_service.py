"""
Process File
"""
from pathlib import Path
from psycopg.errors import UniqueViolation

from app.config import settings
from app.repository.documents import DocumentsRepository
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.services.embedding_service import embedding
from app.services.llm_service import query_llm
from app.retrieval import retrieval


# Initialize rich console instance

class FileProcessor:
    """Class allow you to process the file (chnk and save in the database) with option parameters 
    """
    def __init__(
        self,
        file: Path,
        metadata: dict,
        chunk_size: int = 500,
        overlap_ratio: float = 0.1
    ):
        self.file = file
        self.metadata = metadata
        self.chunk_size = chunk_size
        self.overlap_ratio = overlap_ratio


    def chunking_file(self) -> list[dict]:
        #Prepare Chunking
        pipeline = DocumentIngestionPipeline(self.chunk_size, self.overlap_ratio)

        # Pass the file in the pipline: Loading -> Cleaning -> Chunking
        chunks: list[dict] = pipeline.process_file(self.file)

        return chunks

    async def insert_chunks(
        self,
        document_id: int,
        chunks: list[dict]
    ) -> None:

        # Vectorize each chunk
        input_content = [chunk["content"] for chunk in chunks]
        vectors = await embedding(input_content)

        for idx, chunk in enumerate(chunks):
            chunk["document_id"] = document_id
            chunk["embedding"] = str(vectors[idx])


        await DocumentsRepository.add_chunks(chunks)

    async def insert_file(self, chunks: list[dict]) -> int | None:
        """
        Take a file pass it in the chunking pipeline and insert it in the database
        """

        #Prepare the document dict
        document = {
            "filename": self.file.name,
            "total_chunks": len(chunks),
            "metadata": self.metadata
        }

        try:
            document_id = await DocumentsRepository.add_document(document)

        except UniqueViolation as e: # If the document already exists
            print(f"[red][Error]:[/] {e}")
        else:
            return document_id



async def chat(msg: str) -> dict[str, list[str]] | None:

    """
    RAG Pipeline 
        Prompt -> Retriever -> Context -> LLM -> Answer
    """

    # Retrieve relevant chunks
    infos = await retrieval.retrieval(msg)

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
            "explicitly state:"
            "'The provided context doesn't contain sufficient information to answer this question.'"
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


async def hard_file_insertion():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
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
        processor = FileProcessor(Path(file), {})
        chunks = processor.chunking_file()
        await processor.insert_file(chunks)

async def main():
    pass

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

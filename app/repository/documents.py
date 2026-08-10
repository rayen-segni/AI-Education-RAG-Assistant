import json
from app.database.vector_db import get_conn


class DocumentsRepository:
    
    @staticmethod
    async def add_document(document: dict) -> int | None:
        """
        Add given document in table 'documents' the database
        """
        
        
        async with get_conn() as conn:
            async with conn.cursor() as curr:
                
                await curr.execute("""
                    INSERT INTO documents
                    (filename, file_path, file_type, total_chunks)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (document["filename"],
                    document["file_path"],
                    document["file_type"],
                    document["total_chunks"])
                )
                
                document_id = await curr.fetchone()

                assert document_id is not None, "Failed to insert document and retrieve ID"
                
                return document_id[0]

    @staticmethod
    async def add_chunk(chunk: dict) -> None:
        """
        Add given chunk in table 'chunks' in the database
        """

        async with get_conn() as conn:
            async with conn.cursor() as curr:
                
                await curr.execute("""
                    INSERT INTO chunks
                    (document_id, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    """, 
                    (
                        chunk["document_id"],
                        chunk["chunk_index"],
                        chunk["content"],
                        chunk["embedding"],
                        json.dumps(chunk["metadata"])
                    )
                )
    
    @staticmethod
    async def search_chunks(
            query_embedding: list[float],
            top_k: int
        ) -> list[tuple[int, int, str, float]]:
        """
        Search the top-k nearest vectors to the given vector using cosine similarity ordred by distance
        
        Returns:
            A list of tuples each tuple contains the chunk and the document ID and the content of the chunk (text) 
            and its cosine distance
        """
        
        async with get_conn() as conn:
            async with conn.cursor() as curr:
                
                await curr.execute("""
                    SELECT id, document_id, content, embedding <=> %s::vector AS distance
                    FROM chunks
                    ORDER BY distance
                    LIMIT %s;
                    """,
                    (query_embedding, top_k)
                    )
                
                
                return await curr.fetchall()
        
        

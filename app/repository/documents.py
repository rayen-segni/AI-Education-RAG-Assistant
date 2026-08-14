"""
CRUD Documents
"""

import json
from psycopg.sql import SQL
from app.database.vector_db import get_conn


class DocumentsRepository:
    """
    Interface That interact directly with the database to CRUD documents and chunks
    """

    @staticmethod
    async def add_document(document: dict) -> int:
        """
        Add given document in table 'documents' the database
        """

        async with get_conn() as conn:
            async with conn.cursor() as curr:

                await curr.execute("""
                    INSERT INTO documents
                    (filename, total_chunks, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (
                    document["filename"],
                    document["total_chunks"],
                    json.dumps(document["metadata"])
                    )
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

                await curr.execute(f"""
                    INSERT INTO chunks
                    (document_id, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        chunk["document_id"],
                        chunk["chunk_index"],
                        chunk["content"],
                        chunk["embedding"]
                    )
                )

    @staticmethod
    async def add_chunks(chunks: list[dict]) -> None:
        """
        Add given chunk in table 'chunks' in the database
        """

        values, params = build_chunks_clause(chunks)

        async with get_conn() as conn:
            async with conn.cursor() as curr:

                await curr.execute(SQL(
                    """
                    INSERT INTO chunks
                    (document_id, chunk_index, content, embedding)
                    VALUES {}
                    """).format(SQL(values)), # type: ignore
                    params
                    )

    @staticmethod
    async def search_chunks(
            vector: list[float],
            filters: dict | None,
            top_k: int,
            threshold: float
        ) -> list[tuple[int, int, str, float, dict]]:
        """
        Search the top-k nearest vectors to the given vector using cosine similarity
        ordred by distance
        
        Returns:
            A list of tuples each tuple contains 
            (filenmae, chunk_index, content, cos_distance, metadata)
        """

        filter_payload = json.dumps(filters or {}) # The case where the filters are null
        
        async with get_conn() as conn:
            async with conn.cursor() as curr:

                await curr.execute("""
                    SELECT 
                        d.filename, 
                        c.chunk_index, 
                        c.content, 
                        (1 - (c.embedding <=> %s::vector)) AS similarity, 
                        d.metadata
                        
                    FROM chunks c
                    JOIN documents d
                        ON c.document_id = d.id
                        
                    WHERE d.metadata @> %s::jsonb
                    AND (1 - (c.embedding <=> %s::vector)) > %s
                    
                    ORDER BY similarity DESC
                    LIMIT %s;
                """,
                    (
                    vector,
                    filter_payload,
                    vector,
                    threshold,
                    top_k
                    )
                    )

                return await curr.fetchall()



def build_chunks_clause(chunks: list[dict]):
    """Take the chunks list and build the clauses of the query
    Build the fields of the quey

    Args:
        chunks (list[dict]): _description_
    """
    
    values = ", ".join(["(%s, %s, %s, %s)"] * len(chunks))
    params = []
    for chunk in chunks:
        param = [
                chunk["document_id"],
                chunk["chunk_index"],
                chunk["content"],
                chunk["embedding"],
                ]
        params.extend(param)


    return values, params

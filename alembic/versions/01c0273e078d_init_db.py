"""init_db

Revision ID: 01c0273e078d
Revises: 
Create Date: 2026-08-12 18:09:00.683495

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '01c0273e078d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema using raw SQL."""
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create 'documents' table
    op.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR NOT NULL UNIQUE,
            total_chunks INTEGER,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


    # 3. Create 'chunks' table
    op.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Create HNSW index on embedding column
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding
        ON chunks USING hnsw (embedding vector_cosine_ops);
    """)


def downgrade() -> None:
    """Downgrade schema using raw SQL."""
    # 1. Drop HNSW index
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding;")

    # 2. Drop chunks table
    op.execute("DROP TABLE IF EXISTS chunks;")

    # 3. Drop documents table
    op.execute("DROP TABLE IF EXISTS documents;")

    # 4. Drop vector extension
    op.execute("DROP EXTENSION IF EXISTS vector CASCADE;")


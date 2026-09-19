CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,

    -- Original file ka naam.
    filename TEXT NOT NULL,

    -- Original document ka complete extracted text.
    content TEXT NOT NULL,

    -- Document database mein kab create hua.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,

    -- Ye chunk kis document se belong karta hai.
    document_id BIGINT NOT NULL
        REFERENCES documents(id)
        ON DELETE CASCADE,

    -- Actual text chunk.
    chunk_text TEXT NOT NULL,

    -- 384-dimensional hain.
    embedding VECTOR(384) NOT NULL,

    -- Additional information/filtering ke liye.
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb

  
    CREATE TABLE IF NOT EXISTS document_chunks (
        id BIGSERIAL PRIMARY KEY,
        document_id BIGINT NOT NULL
            REFERENCES documents(id)
            ON DELETE CASCADE,
        chunk_text TEXT NOT NULL,
        embedding VECTOR(384) NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

        -- PostgreSQL full-text-search representation of the chunk.
        search_vector TSVECTOR
            GENERATED ALWAYS AS (
                to_tsvector('english', chunk_text)
            ) STORED
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
ON document_chunks(document_id);

-- Index for fast keyword/full-text search.
CREATE INDEX IF NOT EXISTS idx_document_chunks_search_vector
ON document_chunks
USING GIN(search_vector);

-- Existing vector index.
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw
ON document_chunks
USING hnsw (embedding vector_cosine_ops);


);


CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
ON document_chunks(document_id);



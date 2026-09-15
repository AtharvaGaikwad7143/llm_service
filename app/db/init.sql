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
);


CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
ON document_chunks(document_id);
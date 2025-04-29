CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    original_name VARCHAR(255),
    processed_content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
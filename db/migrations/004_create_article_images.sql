-- Create table for storing diagram images associated with articles
CREATE TABLE IF NOT EXISTS article_images (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    diagram_type TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

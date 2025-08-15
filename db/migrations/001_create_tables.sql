-- Create initial tables for auto_blog
CREATE TABLE series (
    id SERIAL PRIMARY KEY,
    topic VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    topic VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    markdown TEXT,
    markdown_raw TEXT,
    series_id INTEGER REFERENCES series(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ
);

-- //@UNDO

DROP TABLE articles;
DROP TABLE series;

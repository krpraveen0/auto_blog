-- Add markdown_raw column to articles
ALTER TABLE articles ADD COLUMN markdown_raw TEXT;

-- //@UNDO

ALTER TABLE articles DROP COLUMN markdown_raw;

-- Add summary column to articles
ALTER TABLE articles ADD COLUMN summary TEXT;

-- //@UNDO

ALTER TABLE articles DROP COLUMN summary;

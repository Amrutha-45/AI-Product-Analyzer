-- Add category_data column for non-food polymorphic fields
ALTER TABLE scans ADD COLUMN IF NOT EXISTS category_data JSONB;

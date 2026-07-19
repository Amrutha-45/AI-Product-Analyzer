-- AI Product Analyzer: Supabase Initialization Script
-- Run this in the Supabase SQL Editor to set up the database schema.

-- Products: deduplicated cache of anything we've ever resolved,
-- keyed by barcode when available.
CREATE TABLE IF NOT EXISTS products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode         TEXT UNIQUE,
    product_name    TEXT,
    brand           TEXT,
    category        TEXT,
    off_data        JSONB,              -- raw OpenFoodFacts payload, cached
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Scans: one row per user-submitted scan.
CREATE TABLE IF NOT EXISTS scans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id           TEXT,                     -- anonymous grouping key
    product_id          UUID REFERENCES products(id),
    content_hash        TEXT UNIQUE,               -- for cache lookups
    front_image_url     TEXT,
    back_image_url      TEXT,
    health_score         NUMERIC(3,1),
    ingredient_safety_score NUMERIC(3,1),
    health_score_breakdown JSONB,
    trust_score          NUMERIC(5,2),
    expiry_status        TEXT CHECK (expiry_status IN ('valid','expired','unclear')),
    manufacturing_date   TEXT,
    expiry_date          TEXT,
    batch_number         TEXT,
    packaging_signals    JSONB,
    nutrition            JSONB,
    nova_class           INTEGER,
    ingredients          JSONB,           -- array of {name, risk_level, explanation, flags}
    warnings             TEXT[],
    alternatives         JSONB,
    category_data        JSONB,           -- For polymorphic non-food category data
    ai_provider          TEXT,          -- e.g. 'gemini-2.5-flash', for later comparison
    prompt_version       TEXT,
    source               TEXT CHECK (source IN ('ai_extracted','openfoodfacts_merged')),
    created_at           TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_scans_device_id ON scans (device_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_content_hash ON scans (content_hash);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products (barcode);

-- Set up Row Level Security (RLS)
-- Since we are using the service_role key in the backend, these policies 
-- ensure the DB is secure against direct anonymous access.
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

-- Allow read access for everyone (if needed for a public API later), 
-- but writes are restricted to the service_role (backend).
CREATE POLICY "Enable read access for all users" ON products FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON scans FOR SELECT USING (true);

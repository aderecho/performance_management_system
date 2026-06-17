-- Get all objectives under a Strategic Result Area
SELECT i.*
FROM item_closure ic
JOIN items i ON i.id = ic.descendant_id
WHERE ic.ancestor_id = 'uuid-sra-1'
  AND ic.depth = 1; -- direct children only

-- Get all performance measures under an Objective
SELECT i.*
FROM item_closure ic
JOIN items i ON i.id = ic.descendant_id
WHERE ic.ancestor_id = 'uuid-objective-1';

-- Get entire hierarchy of a Program
WITH RECURSIVE hierarchy AS (
    SELECT id, name, type, 0 AS depth
    FROM items WHERE id = 'uuid-prog-1'
    UNION ALL
    SELECT i.id, i.name, i.type, h.depth + 1
    FROM items i
    JOIN item_closure ic ON i.id = ic.descendant_id
    JOIN hierarchy h ON ic.ancestor_id = h.id
    WHERE ic.depth = 1
)
SELECT * FROM hierarchy;

-- Compare target vs actual values
SELECT i.name, i.target, v.year, v.actual
FROM items i
LEFT JOIN item_values v ON v.item_id = i.id
WHERE i.id = 'uuid-perf-measure-1';

-- NUMBER 1

-- =========================
-- USERS (basic reference)
-- =========================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- UNIT OF MEASURE
-- =========================
CREATE TABLE unit_of_measures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(50),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- TEMPLATES (frameworks)
-- e.g., Strategic Planning, PBB, Performance Indicators
-- =========================
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- NODE TYPES (per template)
-- e.g., SRA, Objective, Performance Measure
-- =========================
CREATE TABLE node_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE, 
    name VARCHAR(255) NOT NULL,
    short_code VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(template_id, name)
);

-- =========================
-- ITEMS (the actual nodes)
-- =========================
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    node_type_id UUID NOT NULL REFERENCES node_types(id) ON DELETE CASCADE,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target NUMERIC(15,2),
    unit_of_measure_id UUID REFERENCES unit_of_measures(id),
    start_date DATE,
    end_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- CLOSURE TABLE
-- Stores ancestor-descendant relationships
-- =========================
CREATE TABLE item_closure (
    ancestor_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    descendant_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    depth INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- =========================
-- REPORTING PERIODS
-- Dictated by admin (e.g., FY2024-Q1, 2024, Q1-2025, etc.)
-- =========================
CREATE TABLE reporting_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL, -- e.g., "FY2024-Q1"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- ITEM VALUES (actual reports per period)
-- =========================
CREATE TABLE item_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    reporting_period_id UUID NOT NULL REFERENCES reporting_periods(id) ON DELETE CASCADE,
    actual_value NUMERIC(15,2) NOT NULL,
    remarks TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(item_id, reporting_period_id)
);

-- NUMBER 2
-- First, create a function that validates the closure insert
CREATE OR REPLACE FUNCTION enforce_template_rules()
RETURNS TRIGGER AS $$
DECLARE
    ancestor_type UUID;
    descendant_type UUID;
    valid_rule BOOLEAN;
BEGIN
    -- Only check direct parent-child (depth = 1)
    IF NEW.depth = 1 THEN
        -- Get ancestor's node type
        SELECT node_type_id INTO ancestor_type
        FROM items WHERE id = NEW.ancestor_id;

        -- Get descendant's node type
        SELECT node_type_id INTO descendant_type
        FROM items WHERE id = NEW.descendant_id;

        -- Check if a valid rule exists
        SELECT EXISTS (
            SELECT 1
            FROM template_rules
            WHERE parent_type_id = ancestor_type
              AND child_type_id = descendant_type
        ) INTO valid_rule;

        IF NOT valid_rule THEN
            RAISE EXCEPTION 'Invalid relationship: % -> % is not allowed',
                ancestor_type, descendant_type;
        END IF;
    ELSE
        -- Prevent manual insert for depth > 1
        RAISE EXCEPTION 'Manual insertion not allowed for depth > 1';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to item_closures table
DROP TRIGGER IF EXISTS trg_enforce_template_rules ON item_closures;

CREATE TRIGGER trg_enforce_template_rules
BEFORE INSERT OR UPDATE ON item_closures
FOR EACH ROW
EXECUTE FUNCTION enforce_template_rules();
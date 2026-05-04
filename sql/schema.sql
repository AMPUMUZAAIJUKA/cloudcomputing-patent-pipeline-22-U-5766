--  Drop tables if they exist (so we can re-run cleanly) 
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS patents;

--  1. PATENTS 
CREATE TABLE patents (
    patent_id    TEXT PRIMARY KEY,
    title        TEXT,
    filing_date  TEXT,
    patent_type  TEXT,
    year         INTEGER
);

-- 2. INVENTORS 
CREATE TABLE inventors (
    inventor_id  TEXT PRIMARY KEY,
    name         TEXT,
    country      TEXT
);

--  3. COMPANIES 
CREATE TABLE companies (
    company_id   TEXT PRIMARY KEY,
    name         TEXT
);

--  4. RELATIONSHIPS 
CREATE TABLE relationships (
    patent_id    TEXT,
    inventor_id  TEXT,
    company_id   TEXT,
    FOREIGN KEY (patent_id)   REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id)  REFERENCES companies(company_id)
);
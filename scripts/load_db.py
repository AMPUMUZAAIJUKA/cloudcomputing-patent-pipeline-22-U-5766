import sqlite3
import pandas as pd
import os

CLEAN  = "data/clean"
DB     = "database/patents.db"
SCHEMA = "sql/schema.sql"

os.makedirs("database", exist_ok=True)

CHUNK_SIZE = 500_000

print("\nConnecting to database...")
conn   = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.executescript("""
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous  = NORMAL;
    PRAGMA cache_size   = -64000;
    PRAGMA temp_store   = MEMORY;
""")

print("Creating tables from schema...")
with open(SCHEMA, 'r') as f:
    cursor.executescript(f.read())
conn.commit()
print("  Tables created")


# ── PATENTS ─────────────────────────────────────────────
print("\nInserting patents...")
total = 0
for chunk in pd.read_csv(f"{CLEAN}/clean_patents.csv",
                          chunksize=CHUNK_SIZE, low_memory=False):
    chunk[['patent_id','title','filing_date','patent_type','year']]\
        .to_sql('patents', conn, if_exists='append', index=False)
    total += len(chunk)
    print(f"  {total:,} patents inserted so far...")
print(f"  Done: {total:,} patents")


# ── INVENTORS ───────────────────────────────────────────
print("\nInserting inventors...")
total     = 0
seen_inv  = set()
chunk_num = 0

for chunk in pd.read_csv(f"{CLEAN}/clean_inventors.csv",
                          chunksize=CHUNK_SIZE, low_memory=False):
    chunk_num += 1

    unique = chunk.drop_duplicates(subset='inventor_id')
    unique = unique[~unique['inventor_id'].isin(seen_inv)]
    seen_inv.update(unique['inventor_id'].tolist())

    if not unique.empty:
        unique[['inventor_id','name','country']]\
            .to_sql('inventors', conn, if_exists='append', index=False)

    chunk[['patent_id','inventor_id']].assign(company_id=None)\
        .to_sql('relationships', conn, if_exists='append', index=False)

    total += len(chunk)
    print(f"  chunk {chunk_num} -> {len(seen_inv):,} unique inventors | {total:,} relationships")

print(f"  Done: {len(seen_inv):,} unique inventors")


# ── COMPANIES ───────────────────────────────────────────
print("\nInserting companies...")
total     = 0
seen_comp = set()
chunk_num = 0

for chunk in pd.read_csv(f"{CLEAN}/clean_companies.csv",
                          chunksize=CHUNK_SIZE, low_memory=False):
    chunk_num += 1

    unique = chunk.drop_duplicates(subset='company_id')
    unique = unique[~unique['company_id'].isin(seen_comp)]
    seen_comp.update(unique['company_id'].tolist())

    if not unique.empty:
        unique[['company_id','name']]\
            .to_sql('companies', conn, if_exists='append', index=False)

    chunk[['patent_id','company_id']].assign(inventor_id=None)\
        .to_sql('relationships', conn, if_exists='append', index=False)

    total += len(chunk)
    print(f"  chunk {chunk_num} -> {len(seen_comp):,} unique companies | {total:,} relationships")

print(f"  Done: {len(seen_comp):,} unique companies")


# ── VERIFY ──────────────────────────────────────────────
print("\n" + "="*55)
print("  DATABASE LOADED SUCCESSFULLY")
print("="*55)
for table in ['patents','inventors','companies','relationships']:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<15} -> {count:>12,} rows")

conn.close()
print(f"\n  Database saved to: {DB}")
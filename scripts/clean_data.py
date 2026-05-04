import zipfile
import pandas as pd
import os

RAW   = "data/raw"
CLEAN = "data/clean"
os.makedirs(CLEAN, exist_ok=True)

CHUNK_SIZE  = 500_000
NROWS_LIMIT = float('inf')

# ══════════════════════════════════════════════════════
# 1. PATENTS
# ══════════════════════════════════════════════════════
print("\nLoading patents in chunks...")

patent_out = f"{CLEAN}/clean_patents.csv"
if os.path.exists(patent_out):
    os.remove(patent_out)

total_patents = 0
chunk_num     = 0

with zipfile.ZipFile(f"{RAW}/g_patent.tsv.zip") as z:
    with z.open(z.namelist()[0]) as f:
        reader = pd.read_csv(
            f, sep='\t', low_memory=False, chunksize=CHUNK_SIZE,
            usecols=['patent_id','patent_title','patent_date','patent_type']
        )
        for chunk in reader:
            if total_patents >= NROWS_LIMIT:
                break
            chunk_num += 1
            chunk.columns = ['patent_id','patent_type','filing_date','title']
            chunk['patent_id']   = chunk['patent_id'].astype(str).str.strip()
            chunk['title']       = chunk['title'].astype(str).str.strip()
            chunk['filing_date'] = pd.to_datetime(chunk['filing_date'], errors='coerce')
            chunk['year']        = chunk['filing_date'].dt.year
            chunk.dropna(subset=['patent_id','title'], inplace=True)
            chunk.drop_duplicates(subset='patent_id', inplace=True)
            chunk.to_csv(patent_out, mode='a', header=(chunk_num == 1), index=False)
            total_patents += len(chunk)
            print(f"  chunk {chunk_num} -> {total_patents:,} patents so far")

print(f"  Done: {total_patents:,} patents saved")


# ══════════════════════════════════════════════════════
# 2. LOCATION FILE
# ══════════════════════════════════════════════════════
print("\nLoading location data...")
with zipfile.ZipFile(f"{RAW}/g_location_disambiguated.tsv.zip") as z:
    with z.open(z.namelist()[0]) as f:
        locations = pd.read_csv(
            f, sep='\t', low_memory=False,
            usecols=['location_id','disambig_country']
        )
locations.columns = ['location_id','country']
locations['country'] = locations['country'].fillna('Unknown').str.strip()
print(f"  Done: {len(locations):,} locations loaded")


# ══════════════════════════════════════════════════════
# 3. INVENTORS
# ══════════════════════════════════════════════════════
print("\nLoading inventors in chunks...")

inventor_out = f"{CLEAN}/clean_inventors.csv"
if os.path.exists(inventor_out):
    os.remove(inventor_out)

total_inventors = 0
chunk_num       = 0

with zipfile.ZipFile(f"{RAW}/g_inventor_disambiguated.tsv.zip") as z:
    with z.open(z.namelist()[0]) as f:
        reader = pd.read_csv(
            f, sep='\t', low_memory=False, chunksize=CHUNK_SIZE,
            usecols=['patent_id','inventor_id',
                     'disambig_inventor_name_first',
                     'disambig_inventor_name_last',
                     'location_id']
        )
        for chunk in reader:
            if total_inventors >= NROWS_LIMIT:
                break
            chunk_num += 1
            chunk = chunk.merge(locations, on='location_id', how='left')
            chunk['country']     = chunk['country'].fillna('Unknown')
            chunk['patent_id']   = chunk['patent_id'].astype(str).str.strip()
            chunk['inventor_id'] = chunk['inventor_id'].astype(str).str.strip()
            chunk['first_name']  = chunk['disambig_inventor_name_first'].fillna('').astype(str).str.strip()
            chunk['last_name']   = chunk['disambig_inventor_name_last'].fillna('').astype(str).str.strip()
            chunk['name']        = (chunk['first_name'] + ' ' + chunk['last_name']).str.strip()
            out = chunk[['patent_id','inventor_id','name','country']].copy()
            out.dropna(subset=['inventor_id'], inplace=True)
            out.drop_duplicates(inplace=True)
            out.to_csv(inventor_out, mode='a', header=(chunk_num == 1), index=False)
            total_inventors += len(out)
            print(f"  chunk {chunk_num} -> {total_inventors:,} inventors so far")

print(f"  Done: {total_inventors:,} inventors saved")


# ══════════════════════════════════════════════════════
# 4. COMPANIES
# ══════════════════════════════════════════════════════
print("\nLoading companies in chunks...")

company_out = f"{CLEAN}/clean_companies.csv"
if os.path.exists(company_out):
    os.remove(company_out)

total_companies = 0
chunk_num       = 0

with zipfile.ZipFile(f"{RAW}/g_assignee_disambiguated.tsv.zip") as z:
    with z.open(z.namelist()[0]) as f:
        reader = pd.read_csv(
            f, sep='\t', low_memory=False, chunksize=CHUNK_SIZE,
            usecols=['patent_id','assignee_id','disambig_assignee_organization']
        )
        for chunk in reader:
            if total_companies >= NROWS_LIMIT:
                break
            chunk_num += 1
            chunk.columns = ['patent_id','company_id','name']
            chunk['patent_id']  = chunk['patent_id'].astype(str).str.strip()
            chunk['company_id'] = chunk['company_id'].astype(str).str.strip()
            chunk['name']       = chunk['name'].astype(str).str.strip()
            chunk = chunk[chunk['name'].notna()]
            chunk = chunk[chunk['name'] != 'nan']
            chunk.drop_duplicates(inplace=True)
            chunk.to_csv(company_out, mode='a', header=(chunk_num == 1), index=False)
            total_companies += len(chunk)
            print(f"  chunk {chunk_num} -> {total_companies:,} companies so far")

print(f"  Done: {total_companies:,} companies saved")


# ══════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════
print("\n" + "="*55)
print("  ALL FILES CLEANED AND SAVED to data/clean/")
print("="*55)
print(f"  clean_patents.csv   -> {total_patents:>12,} rows")
print(f"  clean_inventors.csv -> {total_inventors:>12,} rows")
print(f"  clean_companies.csv -> {total_companies:>12,} rows")
print(f"  Total               -> {total_patents + total_inventors + total_companies:>12,} rows")
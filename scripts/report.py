import sqlite3
import pandas as pd
import json
import os

DB      = "database/patents.db"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

conn = sqlite3.connect(DB)

#  ALL QUERIES

top_inventors = pd.read_sql_query("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name ORDER BY patent_count DESC LIMIT 10
""", conn)

top_companies = pd.read_sql_query("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r JOIN companies c ON r.company_id = c.company_id
    WHERE r.company_id IS NOT NULL
    GROUP BY c.company_id, c.name ORDER BY patent_count DESC LIMIT 10
""", conn)

top_countries = pd.read_sql_query("""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL AND i.country != 'Unknown'
    GROUP BY i.country ORDER BY patent_count DESC LIMIT 10
""", conn)

yearly_trends = pd.read_sql_query("""
    SELECT year, COUNT(*) AS patent_count
    FROM patents WHERE year IS NOT NULL
    GROUP BY year ORDER BY year ASC
""", conn)

total_patents = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM patents", conn
).iloc[0]['total']

cte_inventors = pd.read_sql_query("""
    WITH inventor_stats AS (
        SELECT i.inventor_id, i.name,
               COUNT(DISTINCT r.patent_id) AS total_patents,
               MAX(p.year) AS latest_year
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        JOIN patents p ON r.patent_id = p.patent_id
        WHERE r.inventor_id IS NOT NULL
        GROUP BY i.inventor_id, i.name
    ),
    top_inventors AS (SELECT * FROM inventor_stats WHERE total_patents >= 3)
    SELECT name, total_patents, latest_year FROM top_inventors
    ORDER BY total_patents DESC LIMIT 15
""", conn)

ranked_inventors = pd.read_sql_query("""
    SELECT name, patent_count,
           RANK() OVER (ORDER BY patent_count DESC) AS rank,
           NTILE(4) OVER (ORDER BY patent_count DESC) AS quartile
    FROM (
        SELECT i.name, COUNT(DISTINCT r.patent_id) AS patent_count
        FROM inventors i JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE r.inventor_id IS NOT NULL
        GROUP BY i.inventor_id, i.name HAVING patent_count >= 2
    ) ranked ORDER BY patent_count DESC LIMIT 15
""", conn)

join_sample = pd.read_sql_query("""
    SELECT p.patent_id, p.title, p.year,
           i.name AS inventor, i.country,
           c.name AS company
    FROM inventors i
    JOIN relationships r_i ON i.inventor_id = r_i.inventor_id
    JOIN patents p ON r_i.patent_id = p.patent_id
    LEFT JOIN relationships r_c ON p.patent_id = r_c.patent_id
        AND r_c.company_id IS NOT NULL
    LEFT JOIN companies c ON r_c.company_id = c.company_id
    LIMIT 15
""", conn)

conn.close()

# REPORT A 

print("\n" + "="*55)
print("          PATENT INTELLIGENCE REPORT")
print("\n" + "─"*55)
print(f"\n  ********** Total Patents in Database******** : {int(total_patents):>10,}")
print(f"  +++++Unique Inventors +++         : {pd.read_sql_query('SELECT COUNT(*) c FROM inventors', sqlite3.connect(DB)).iloc[0]['c']:>10,}")
print(f"  ++++Unique Companies+++          : {pd.read_sql_query('SELECT COUNT(*) c FROM companies', sqlite3.connect(DB)).iloc[0]['c']:>10,}")

print("\n" + "─"*55)
print("  ____ TOP 10 INVENTORS BY PATENT COUNT____")
print("\n" + "─"*55)
for i, row in top_inventors.iterrows():
    print(f"  {i+1:>2}. {row['name']:<35} {row['patent_count']:>5} patents")

print("\n" + "─"*55)
print("  _____TOP 10 COMPANIES BY PATENT COUNT_____")
print("─"*55)
for i, row in top_companies.iterrows():
    print(f"  {i+1:>2}. {row['name']:<45} {row['patent_count']:>5} patents")

print("\n" + "─"*55)
print("  ____ TOP 10 COUNTRIES BY PATENT COUNT____")
print("─"*55)
for i, row in top_countries.iterrows():
    print(f"  {i+1:>2}. {row['country']:<10} {row['patent_count']:>8,} patents")

print("\n" + "─"*55)
print("  *** PATENTS PER YEAR***")
print("\n" + "─"*55)
for _, row in yearly_trends.iterrows():
    bar = "█" * (int(row['patent_count']) // 5000)
    print(f"  {int(row['year'])} │{bar} {int(row['patent_count']):,}")

print("\n" + "─"*55)
print("   SAMPLE JOIN (Patents + Inventors + Companies)")
print("\n" + "─"*55)
print(join_sample[['patent_id','title','inventor','country','company']]\
    .head(10).to_string(index=False))

print("\n" + "─"*55)
print("   CTE — TOP INVENTORS (3+ patents)")
print("\n" + "─"*55)
print(cte_inventors.to_string(index=False))

print("\n" + "─"*55)
print("   RANKED INVENTORS (Window Functions)")
print("\n" + "─"*55)
print(ranked_inventors.to_string(index=False))

print("\n" + "─"*55)
print("   END OF CONSOLE REPORT")
print("\n" + "─"*55)


# REPORT B — CSV EXPORTS

top_inventors.to_csv(f"{REPORTS}/top_inventors.csv",  index=False)
top_companies.to_csv(f"{REPORTS}/top_companies.csv",  index=False)
top_countries.to_csv(f"{REPORTS}/country_trends.csv", index=False)
yearly_trends.to_csv(f"{REPORTS}/yearly_trends.csv",  index=False)
print(f"\n CSV reports saved to /{REPORTS}/")


# REPORT C — JSON EXPORT

report_json = {
    "total_patents": int(total_patents),
    "top_inventors": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patent_count"])}
        for i, row in top_inventors.iterrows()
    ],
    "top_companies": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patent_count"])}
        for i, row in top_companies.iterrows()
    ],
    "top_countries": [
        {"country": row["country"], "patents": int(row["patent_count"])}
        for i, row in top_countries.iterrows()
    ],
    "yearly_trends": [
        {"year": int(row["year"]), "patents": int(row["patent_count"])}
        for _, row in yearly_trends.iterrows()
    ]
}

with open(f"{REPORTS}/report.json", "w") as f:
    json.dump(report_json, f, indent=2)

print(f" JSON report saved to /{REPORTS}/report.json")
print("\n ALL REPORTS GENERATED SUCCESSFULLY!")
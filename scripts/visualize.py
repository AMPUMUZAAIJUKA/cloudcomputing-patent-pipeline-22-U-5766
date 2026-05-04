import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

DB      = "database/patents.db"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

# ── Style ───────────────────────────────────────────────
sns.set_theme(style="darkgrid")
PALETTE = "viridis"

conn = sqlite3.connect(DB)

# ── Load data ───────────────────────────────────────────
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

patent_types = pd.read_sql_query("""
    SELECT patent_type, COUNT(*) AS count
    FROM patents GROUP BY patent_type ORDER BY count DESC
""", conn)

conn.close()


# CHART 1 — Top 10 Inventors (horizontal bar)

fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette(PALETTE, len(top_inventors))
bars = ax.barh(
    top_inventors['name'][::-1],
    top_inventors['patent_count'][::-1],
    color=colors
)
ax.bar_label(bars, padding=3, fontsize=9)
ax.set_xlabel("Number of Patents", fontsize=11)
ax.set_title(" Top 10 Inventors by Patent Count", fontsize=14, fontweight='bold', pad=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{REPORTS}/chart_top_inventors.png", dpi=150, bbox_inches='tight')
plt.close()
print(" Saved chart_top_inventors.png")

# CHART 2 — Top 10 Companies (horizontal bar)


name_map = {
    "International Business Machines Corporation": "IBM",
    "SAMSUNG DISPLAY CO., LTD.": "Samsung Display",
    "CANON KABUSHIKI KAISHA": "Canon",
    "SONY GROUP CORPORATION": "Sony",
    "Kabushiki Kaisha Toshiba": "Toshiba",
    "MITSUBISHI ELECTRIC CORPORATION": "Mitsubishi Electric",
    "General Electric Company": "General Electric",
    "HITACHI, LTD.": "Hitachi",
    "LG ELECTRONICS INC.": "LG Electronics",
    "Fujitsu Limited": "Fujitsu"
}
top_companies['short_name'] = top_companies['name'].replace(name_map)

fig, ax = plt.subplots(figsize=(11, 6))
colors = sns.color_palette("magma", len(top_companies))
bars = ax.barh(
    top_companies['short_name'][::-1],
    top_companies['patent_count'][::-1],
    color=colors
)
ax.bar_label(bars, padding=3, fontsize=9,
             labels=[f"{v:,}" for v in top_companies['patent_count'][::-1]])
ax.set_xlabel("Number of Patents", fontsize=11)
ax.set_title(" Top 10 Companies by Patent Count", fontsize=14, fontweight='bold', pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{REPORTS}/chart_top_companies.png", dpi=150, bbox_inches='tight')
plt.close()
print(" Saved chart_top_companies.png")


# CHART 3 — Top Countries (pie chart)

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(
    top_countries['patent_count'],
    labels=top_countries['country'],
    autopct='%1.1f%%',
    colors=sns.color_palette("tab10", len(top_countries)),
    startangle=140,
    pctdistance=0.82
)
for text in autotexts:
    text.set_fontsize(8)
ax.set_title(" Top 10 Countries by Patent Count", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f"{REPORTS}/chart_top_countries.png", dpi=150, bbox_inches='tight')
plt.close()
print(" Saved chart_top_countries.png")


# CHART 4 — Patents Per Year (line chart)

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(
    yearly_trends['year'],
    yearly_trends['patent_count'],
    marker='o', linewidth=2.5,
    color='steelblue', markersize=8
)
for _, row in yearly_trends.iterrows():
    ax.annotate(
        f"{int(row['patent_count']):,}",
        (row['year'], row['patent_count']),
        textcoords="offset points", xytext=(0, 10),
        ha='center', fontsize=9
    )
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Number of Patents", fontsize=11)
ax.set_title(" Patent Grants Per Year", fontsize=14, fontweight='bold', pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{REPORTS}/chart_yearly_trends.png", dpi=150, bbox_inches='tight')
plt.close()
print(" Saved chart_yearly_trends.png")


# CHART 5 — Patent Types (donut chart)

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    patent_types['count'],
    labels=patent_types['patent_type'],
    autopct='%1.1f%%',
    colors=sns.color_palette("Set2", len(patent_types)),
    startangle=90,
    wedgeprops=dict(width=0.5)   # donut style
)
ax.set_title(" Patent Types Distribution", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f"{REPORTS}/chart_patent_types.png", dpi=150, bbox_inches='tight')
plt.close()
print(" Saved chart_patent_types.png")

print("\n" + "="*50)
print(" ALL 5 CHARTS SAVED to /reports/")
print("="*50)
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

DB = "database/patents.db"

st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    layout="wide"
)

@st.cache_data
def query(sql):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# ── Header ───────────────────────────────────────────
st.title("Global Patent Intelligence Dashboard")
st.markdown("Analyzing USPTO patent data across inventors, companies and countries")
st.divider()

# ── Metrics ──────────────────────────────────────────
total     = int(query("SELECT COUNT(*) AS c FROM patents").iloc[0]['c'])
inventors = int(query("SELECT COUNT(*) AS c FROM inventors").iloc[0]['c'])
companies = int(query("SELECT COUNT(*) AS c FROM companies").iloc[0]['c'])

col1, col2, col3 = st.columns(3)
col1.metric("Total Patents",    f"{total:,}")
col2.metric("Unique Inventors", f"{inventors:,}")
col3.metric("Unique Companies", f"{companies:,}")

st.divider()

# ── Top Inventors ─────────────────────────────────────
st.subheader("Top 15 Inventors by Patent Count")
inv = query("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS patents
    FROM relationships r JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name ORDER BY patents DESC LIMIT 15
""")
fig = px.bar(inv, x='patents', y='name', orientation='h',
             color='patents', color_continuous_scale='viridis',
             labels={'patents':'Patent Count','name':'Inventor'})
fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Top Companies ─────────────────────────────────────
st.subheader("Top 15 Companies by Patent Count")
comp = query("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents
    FROM relationships r JOIN companies c ON r.company_id = c.company_id
    WHERE r.company_id IS NOT NULL
    GROUP BY c.company_id, c.name ORDER BY patents DESC LIMIT 15
""")
fig2 = px.bar(comp, x='patents', y='name', orientation='h',
              color='patents', color_continuous_scale='magma',
              labels={'patents':'Patent Count','name':'Company'})
fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Countries ─────────────────────────────────────────
st.subheader("Top Countries by Patent Count")
countries = query("""
    SELECT i.country, COUNT(DISTINCT r.patent_id) AS patents
    FROM relationships r JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL AND i.country != 'Unknown'
    GROUP BY i.country ORDER BY patents DESC LIMIT 15
""")

col1, col2 = st.columns(2)
with col1:
    fig3 = px.pie(countries, values='patents', names='country',
                  title='Share by Country',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig3, use_container_width=True)
with col2:
    fig4 = px.bar(countries, x='country', y='patents',
                  color='patents', color_continuous_scale='blues',
                  labels={'patents':'Patent Count','country':'Country'})
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Yearly Trends ─────────────────────────────────────
st.subheader("Patent Grants Per Year")
yearly = query("""
    SELECT year, COUNT(*) AS patents FROM patents
    WHERE year IS NOT NULL GROUP BY year ORDER BY year
""")
fig5 = px.line(yearly, x='year', y='patents', markers=True,
               labels={'patents':'Patent Count','year':'Year'},
               color_discrete_sequence=['steelblue'])
fig5.update_traces(line_width=2.5, marker_size=8)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Patent Types ──────────────────────────────────────
st.subheader("Patent Types Distribution")
types = query("""
    SELECT patent_type, COUNT(*) AS count
    FROM patents GROUP BY patent_type ORDER BY count DESC
""")
fig6 = px.pie(types, values='count', names='patent_type',
              title='Patent Types',
              color_discrete_sequence=px.colors.qualitative.Set2,
              hole=0.4)
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# ── Search ────────────────────────────────────────────
st.subheader("Search Patents by Keyword")
keyword = st.text_input("Enter a keyword to search patent titles:")
if keyword:
    results = query(f"""
        SELECT patent_id, title, year, patent_type
        FROM patents WHERE title LIKE '%{keyword}%'
        LIMIT 50
    """)
    st.write(f"Found {len(results)} results for '{keyword}'")
    st.dataframe(results, use_container_width=True)

st.caption("Data source: USPTO PatentsView | Global Patent Intelligence Pipeline")
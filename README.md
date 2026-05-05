# Global Patent Intelligence Data Pipeline
A data engineering project that builds an end-to-end pipeline for collecting,
cleaning, storing, and analyzing real-world patent data from the USPTO PatentsView
database. The project covers over 200,000 patent records spanning multiple years
and countries.

## Project Overview
Patents are official records of inventions filed with government agencies. By
analyzing patent data at scale, we can identify leading inventors, dominant
companies, and innovation trends across countries and time periods.
This project simulates what a real data engineer would build to answer business
intelligence questions using patent data. The pipeline moves data through six
stages: raw file ingestion, cleaning with pandas, storage in a relational
database, analysis with SQL, and output as structured reports and charts.

## Project Structure

    patent_pipeline/
        data/
            raw/              - downloaded USPTO zip files (not tracked in git)
            clean/            - cleaned CSV files ready for database loading
                clean_patents.csv
                clean_inventors.csv
                clean_companies.csv
        scripts/
            clean_data.py     - reads raw zip files and cleans data using pandas
            load_db.py        - loads cleaned data into a SQLite database
            report.py         - runs all SQL queries and generates reports
            visualize.py      - generates five charts from the database
        sql/
            schema.sql        - defines the four database tables
            queries.sql       - seven analytical SQL queries
        reports/
            top_inventors.csv
            top_companies.csv
            country_trends.csv
            yearly_trends.csv
            report.json
            chart_top_inventors.png
            chart_top_companies.png
            chart_top_countries.png
            chart_yearly_trends.png
            chart_patent_types.png
        database/
            patents.db        - SQLite database file (not tracked in git)
        requirements.txt
        README.md

## Database Schema

The database contains four tables:
patents stores patent_id, title, filing date, patent type, and year.
inventors stores inventor_id, full name, and country code derived from the
USPTO location disambiguation file.
companies stores company_id and the organization name from the assignee
disambiguation file.
relationships links each patent to its inventors and companies, serving as
the central join table for all analytical queries.
## SQL Queries
Seven analytical queries are included in sql/queries.sql:

1. Top inventors by total patent count
2. Top companies by total patent count
3. Top countries by total patent count
4. Patent grants grouped by year to show trends over time
5. JOIN query combining patents, inventors, and companies in one result
6. CTE query that breaks down inventor statistics into readable steps
7. Ranking query using window functions to rank inventors and assign quartiles

## Key Findings
Based on all patent records from 1976-2025:

## How to Reproduce This Project

### Requirements

- Python 3.8 or higher
- Git

### Step 1 - Clone the repository

    git clone https://github.com/AMPUMUZAAIJUKA/cloudcomputing-patent-pipeline-22-U-5766.git
    cd patent_pipeline

### Step 2 - Create and activate a virtual environment

    python -m venv venv

    Windows:
    venv\Scripts\activate

    Mac or Linux:
    source venv/bin/activate

### Step 3 - Install dependencies

    pip install -r requirements.txt

### Step 4 - Download the raw data

Go to the USPTO Open Data Portal at the link below and download these four
files, then place them inside the data/raw/ folder:

    https://data.uspto.gov/bulkdata/datasets/pvgpatdis

Files needed:

    g_patent.tsv.zip
    g_inventor_disambiguated.tsv.zip
    g_assignee_disambiguated.tsv.zip
    g_location_disambiguated.tsv.zip

### Step 5 - Run the pipeline in order

    python scripts/clean_data.py
    python scripts/load_db.py
    python scripts/report.py
    python scripts/visualize.py

## Reports Generated
Running the full pipeline produces the following outputs:

- A console report printed to the terminal showing totals, top rankings,
  and year-by-year trends with a simple bar visualization
- Four CSV files covering top inventors, top companies, top countries,
  and yearly patent trends
- A JSON report summarizing all key statistics in a structured format
- Five PNG charts saved to the reports folder covering inventors,
  companies, countries, yearly trends, and patent type distribution
## Technologies Used
- Python 3.14
- pandas for data cleaning and transformation
- SQLite3 for relational database storage and querying
- matplotlib and seaborn for data visualization
- Git for version control
## Data Source
PatentsView Granted Patent Disambiguated Data
United States Patent and Trademark Office
https://data.uspto.gov/bulkdata/datasets/pvgpatdis

## Author
Name: AMPUMUZA AIJUKA
RegNo:22/U/5766
StudentNo:2200705766
github link:https://github.com/AMPUMUZAAIJUKA/cloudcomputing-patent-pipeline-22-U-5766.git
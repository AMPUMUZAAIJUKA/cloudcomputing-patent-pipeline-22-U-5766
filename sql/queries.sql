
-- Q1: TOP INVENTORS — Who has the most patents?

SELECT 
    i.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
WHERE r.inventor_id IS NOT NULL
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 10;



-- Q2: TOP COMPANIES — Which companies own the most patents?

SELECT 
    c.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN companies c ON r.company_id = c.company_id
WHERE r.company_id IS NOT NULL
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 10;



-- Q3: COUNTRIES — Which countries produce the most patents?

SELECT 
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
WHERE r.inventor_id IS NOT NULL
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 10;



-- Q4: TRENDS OVER TIME — Patents per year
SELECT 
    year,
    COUNT(*) AS patent_count
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year ASC;



-- Q5: JOIN QUERY — Patents with their inventors and companies

SELECT 
    p.patent_id,
    p.title,
    p.year,
    i.name   AS inventor_name,
    c.name   AS company_name
FROM patents p
LEFT JOIN relationships r_i ON p.patent_id = r_i.patent_id 
    AND r_i.inventor_id IS NOT NULL
LEFT JOIN inventors i ON r_i.inventor_id = i.inventor_id
LEFT JOIN relationships r_c ON p.patent_id = r_c.patent_id 
    AND r_c.company_id IS NOT NULL
LEFT JOIN companies c ON r_c.company_id = c.company_id
LIMIT 20;



-- Q6: CTE QUERY — Top inventors with their most recent patent

WITH inventor_stats AS (
    SELECT 
        i.inventor_id,
        i.name,
        COUNT(DISTINCT r.patent_id)  AS total_patents,
        MAX(p.year)                  AS latest_year
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    JOIN patents p       ON r.patent_id   = p.patent_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
),
top_inventors AS (
    SELECT * FROM inventor_stats
    WHERE total_patents >= 3
)
SELECT 
    name,
    total_patents,
    latest_year
FROM top_inventors
ORDER BY total_patents DESC
LIMIT 15;



-- Q7: RANKING QUERY — Rank inventors using window functions

SELECT 
    name,
    patent_count,
    RANK()        OVER (ORDER BY patent_count DESC) AS rank,
    DENSE_RANK()  OVER (ORDER BY patent_count DESC) AS dense_rank,
    NTILE(4)      OVER (ORDER BY patent_count DESC) AS quartile
FROM (
    SELECT 
        i.name,
        COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
    HAVING patent_count >= 2
) ranked
ORDER BY patent_count DESC
LIMIT 20;
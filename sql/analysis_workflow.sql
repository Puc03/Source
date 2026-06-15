-- Analysis workflow for the UEH-Tiki Big Data project.
-- Run after ai_recommendation_workflow.sql.
-- The outputs are CSV files for report tables and charts.

CREATE SCHEMA IF NOT EXISTS analysis;

CREATE OR REPLACE VIEW analysis.overview_kpis AS
SELECT
    COUNT(*) AS total_match_rows,
    COUNT(DISTINCT student_token) AS total_students,
    COUNT(DISTINCT major) AS total_majors,
    COUNT(DISTINCT course) AS total_courses,
    COUNT(DISTINCT tiki_book_id) AS total_tiki_books,
    COUNT(DISTINCT repo_doc_id) AS total_repo_documents,
    ROUND(AVG(TRY_CAST(tiki_score AS DOUBLE)), 2) AS avg_tiki_match_score,
    ROUND(AVG(TRY_CAST(repo_score AS DOUBLE)), 2) AS avg_repo_match_score
FROM fact_student_resource_matches;

CREATE OR REPLACE VIEW analysis.major_match_summary AS
SELECT
    major,
    COUNT(*) AS match_rows,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT course) AS courses,
    COUNT(DISTINCT tiki_book_id) AS tiki_books,
    COUNT(DISTINCT repo_doc_id) AS repo_documents,
    ROUND(AVG(TRY_CAST(tiki_score AS DOUBLE)), 2) AS avg_tiki_score,
    ROUND(AVG(TRY_CAST(repo_score AS DOUBLE)), 2) AS avg_repo_score
FROM fact_student_resource_matches
GROUP BY major
ORDER BY match_rows DESC;

CREATE OR REPLACE VIEW analysis.course_match_summary AS
SELECT
    major,
    course,
    COUNT(*) AS match_rows,
    COUNT(DISTINCT student_token) AS students,
    ROUND(AVG(TRY_CAST(tiki_score AS DOUBLE)), 2) AS avg_tiki_score,
    ROUND(AVG(TRY_CAST(repo_score AS DOUBLE)), 2) AS avg_repo_score
FROM fact_student_resource_matches
GROUP BY major, course
ORDER BY match_rows DESC, avg_tiki_score DESC;

CREATE OR REPLACE VIEW analysis.tiki_confidence_summary AS
SELECT
    tiki_confidence AS confidence,
    COUNT(*) AS match_rows,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(TRY_CAST(tiki_score AS DOUBLE)), 2) AS avg_tiki_score,
    ROUND(AVG(TRY_CAST(tiki_rating_average AS DOUBLE)), 2) AS avg_rating,
    ROUND(AVG(TRY_CAST(tiki_review_count AS DOUBLE)), 2) AS avg_review_count,
    ROUND(AVG(TRY_CAST(tiki_quantity_sold AS DOUBLE)), 2) AS avg_quantity_sold
FROM fact_student_resource_matches
GROUP BY tiki_confidence
ORDER BY match_rows DESC;

CREATE OR REPLACE VIEW analysis.repo_confidence_summary AS
SELECT
    repo_confidence AS confidence,
    COUNT(*) AS match_rows,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(TRY_CAST(repo_score AS DOUBLE)), 2) AS avg_repo_score,
    ROUND(AVG(TRY_CAST(repo_views AS DOUBLE)), 2) AS avg_views
FROM fact_student_resource_matches
GROUP BY repo_confidence
ORDER BY match_rows DESC;

CREATE OR REPLACE VIEW analysis.tiki_commerce_summary AS
SELECT
    COUNT(*) AS tiki_match_rows,
    COUNT(DISTINCT tiki_book_id) AS tiki_books,
    ROUND(AVG(TRY_CAST(tiki_rating_average AS DOUBLE)), 2) AS avg_rating,
    ROUND(AVG(TRY_CAST(tiki_review_count AS DOUBLE)), 2) AS avg_review_count,
    ROUND(AVG(TRY_CAST(tiki_quantity_sold AS DOUBLE)), 2) AS avg_quantity_sold,
    ROUND(AVG(TRY_CAST(tiki_price AS DOUBLE)), 2) AS avg_price,
    COUNT_IF(COALESCE(tiki_source_keys, '') <> '') AS rows_with_search_keywords
FROM fact_student_resource_matches;

CREATE OR REPLACE VIEW analysis.top_tiki_books_by_match AS
SELECT
    tiki_book_id,
    tiki_title,
    COUNT(*) AS matched_times,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT course) AS courses,
    ROUND(AVG(TRY_CAST(tiki_score AS DOUBLE)), 2) AS avg_tiki_score,
    ROUND(AVG(TRY_CAST(tiki_rating_average AS DOUBLE)), 2) AS avg_rating,
    ROUND(AVG(TRY_CAST(tiki_review_count AS DOUBLE)), 2) AS avg_review_count,
    ROUND(AVG(TRY_CAST(tiki_quantity_sold AS DOUBLE)), 2) AS avg_quantity_sold
FROM fact_student_resource_matches
GROUP BY tiki_book_id, tiki_title
ORDER BY matched_times DESC, avg_tiki_score DESC;

CREATE OR REPLACE VIEW analysis.top_repo_documents_by_match AS
SELECT
    repo_doc_id,
    repo_title,
    repo_year,
    repo_collection,
    COUNT(*) AS matched_times,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT course) AS courses,
    ROUND(AVG(TRY_CAST(repo_score AS DOUBLE)), 2) AS avg_repo_score,
    ROUND(AVG(TRY_CAST(repo_views AS DOUBLE)), 2) AS avg_views
FROM fact_student_resource_matches
GROUP BY repo_doc_id, repo_title, repo_year, repo_collection
ORDER BY matched_times DESC, avg_repo_score DESC;

CREATE OR REPLACE VIEW analysis.data_lake_partition_summary AS
SELECT
    major,
    COUNT(*) AS rows_in_partition
FROM read_parquet(
    'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/data_lake/student_matches/**/*.parquet'
)
GROUP BY major
ORDER BY rows_in_partition DESC;

CREATE OR REPLACE VIEW analysis.recommendation_kpis AS
SELECT
    COUNT(*) AS top5_recommendation_rows,
    COUNT(DISTINCT student_token) AS students_with_recommendations,
    COUNT(DISTINCT resource_id) AS recommended_resources,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score,
    ROUND(MIN(recommendation_score), 2) AS min_recommendation_score,
    ROUND(MAX(recommendation_score), 2) AS max_recommendation_score
FROM ai.student_recommendations_top5;

CREATE OR REPLACE VIEW analysis.recommendation_by_resource_type AS
SELECT
    resource_type,
    COUNT(*) AS recommendation_rows,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT resource_id) AS resources,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score,
    ROUND(AVG(match_score), 2) AS avg_match_score,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(popularity_score), 2) AS avg_popularity_score
FROM ai.student_recommendations_top5
GROUP BY resource_type
ORDER BY recommendation_rows DESC;

CREATE OR REPLACE VIEW analysis.top_recommended_resources AS
SELECT
    resource_type,
    resource_title,
    COUNT(*) AS recommended_times,
    COUNT(DISTINCT student_token) AS students,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score,
    ROUND(AVG(match_score), 2) AS avg_match_score,
    ROUND(AVG(quality_score), 2) AS avg_quality_score,
    ROUND(AVG(popularity_score), 2) AS avg_popularity_score
FROM ai.student_recommendations_top5
GROUP BY resource_type, resource_title
ORDER BY recommended_times DESC, avg_recommendation_score DESC;

CREATE OR REPLACE VIEW analysis.major_recommendation_summary AS
SELECT
    major,
    COUNT(*) AS recommendation_rows,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT resource_id) AS resources,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score
FROM ai.student_recommendations_top5
GROUP BY major
ORDER BY recommendation_rows DESC;

CREATE OR REPLACE VIEW analysis.low_confidence_improvement_candidates AS
SELECT
    student_token,
    major,
    course,
    tiki_title,
    tiki_score,
    tiki_confidence,
    repo_title,
    repo_score,
    repo_confidence
FROM fact_student_resource_matches
WHERE tiki_confidence = 'low'
   OR repo_confidence = 'low'
ORDER BY TRY_CAST(tiki_score AS DOUBLE), TRY_CAST(repo_score AS DOUBLE)
LIMIT 100;

COPY analysis.overview_kpis
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/overview_kpis.csv'
(FORMAT CSV, HEADER true);

COPY (SELECT * FROM analysis.major_match_summary LIMIT 50)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/major_match_summary.csv'
(FORMAT CSV, HEADER true);

COPY (SELECT * FROM analysis.course_match_summary LIMIT 100)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/course_match_summary.csv'
(FORMAT CSV, HEADER true);

COPY analysis.tiki_confidence_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/tiki_confidence_summary.csv'
(FORMAT CSV, HEADER true);

COPY analysis.repo_confidence_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/repo_confidence_summary.csv'
(FORMAT CSV, HEADER true);

COPY analysis.tiki_commerce_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/tiki_commerce_summary.csv'
(FORMAT CSV, HEADER true);

COPY (SELECT * FROM analysis.top_tiki_books_by_match LIMIT 50)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/top_tiki_books_by_match.csv'
(FORMAT CSV, HEADER true);

COPY (SELECT * FROM analysis.top_repo_documents_by_match LIMIT 50)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/top_repo_documents_by_match.csv'
(FORMAT CSV, HEADER true);

COPY analysis.data_lake_partition_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/data_lake_partition_summary.csv'
(FORMAT CSV, HEADER true);

COPY analysis.recommendation_kpis
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/recommendation_kpis.csv'
(FORMAT CSV, HEADER true);

COPY analysis.recommendation_by_resource_type
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/recommendation_by_resource_type.csv'
(FORMAT CSV, HEADER true);

COPY (SELECT * FROM analysis.top_recommended_resources LIMIT 50)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/top_recommended_resources.csv'
(FORMAT CSV, HEADER true);

COPY analysis.major_recommendation_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/major_recommendation_summary.csv'
(FORMAT CSV, HEADER true);

COPY analysis.low_confidence_improvement_candidates
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/analysis/low_confidence_improvement_candidates.csv'
(FORMAT CSV, HEADER true);


-- AI recommendation workflow for the UEH-Tiki Big Data project.
-- Model: content-based recommendation with popularity-aware ranking.
-- Run inside DuckDB after opening outputs/warehouse/ueh_bigdata.duckdb.

CREATE SCHEMA IF NOT EXISTS ai;

CREATE OR REPLACE TABLE ai.resource_recommendation_candidates AS
WITH base AS (
    SELECT *
    FROM fact_student_resource_matches
),
tiki_features AS (
    SELECT
        student_token,
        major,
        major_norm,
        cohort,
        course_order,
        course,
        course_norm,
        'tiki_book' AS resource_type,
        CAST(tiki_book_id AS VARCHAR) AS resource_id,
        tiki_title AS resource_title,
        tiki_url AS resource_url,
        tiki_source_keys AS search_keywords,
        tiki_match_reason AS match_reason,
        TRY_CAST(tiki_score AS DOUBLE) AS match_score,
        tiki_confidence AS confidence,
        TRY_CAST(tiki_rating_average AS DOUBLE) AS rating_average,
        TRY_CAST(tiki_review_count AS DOUBLE) AS review_count,
        TRY_CAST(tiki_quantity_sold AS DOUBLE) AS quantity_sold,
        TRY_CAST(tiki_price AS DOUBLE) AS price,
        CASE tiki_confidence
            WHEN 'high' THEN 100.0
            WHEN 'medium' THEN 60.0
            WHEN 'low' THEN 30.0
            ELSE 40.0
        END AS confidence_score,
        CASE
            WHEN COALESCE(TRY_CAST(tiki_rating_average AS DOUBLE), 0.0) > 0
                THEN LEAST(100.0, TRY_CAST(tiki_rating_average AS DOUBLE) * 20.0)
            ELSE 50.0
        END AS rating_score,
        CASE
            WHEN COALESCE(TRY_CAST(tiki_review_count AS DOUBLE), 0.0) > 0
                THEN LEAST(100.0, LN(1.0 + TRY_CAST(tiki_review_count AS DOUBLE)) * 22.0)
            ELSE 50.0
        END AS review_score,
        CASE
            WHEN COALESCE(TRY_CAST(tiki_quantity_sold AS DOUBLE), 0.0) > 0
                THEN LEAST(100.0, LN(1.0 + TRY_CAST(tiki_quantity_sold AS DOUBLE)) * 11.0)
            ELSE 50.0
        END AS sales_score,
        CASE
            WHEN tiki_match_reason LIKE '%exact_course_in_title%' THEN 100.0
            WHEN tiki_match_reason LIKE '%exact_major_in_title%' THEN 90.0
            WHEN tiki_match_reason LIKE '%exact_course_in_secondary_text%' THEN 80.0
            WHEN COALESCE(tiki_source_keys, '') <> '' THEN 70.0
            WHEN tiki_match_reason LIKE '%partial_course_tokens%' THEN 60.0
            ELSE 40.0
        END AS search_signal_score
    FROM base
    WHERE tiki_book_id IS NOT NULL
      AND tiki_title IS NOT NULL
      AND tiki_title <> ''
),
tiki_candidates AS (
    SELECT
        student_token,
        major,
        major_norm,
        cohort,
        course_order,
        course,
        course_norm,
        resource_type,
        resource_id,
        resource_title,
        resource_url,
        search_keywords,
        match_reason,
        match_score,
        confidence,
        rating_average,
        review_count,
        quantity_sold,
        price,
        confidence_score,
        rating_score,
        review_score,
        sales_score,
        search_signal_score,
        ROUND(0.70 * rating_score + 0.30 * review_score, 2) AS quality_score,
        ROUND(0.65 * sales_score + 0.35 * review_score, 2) AS popularity_score,
        ROUND(
            0.45 * COALESCE(match_score, 0.0) +
            0.20 * confidence_score +
            0.15 * (0.70 * rating_score + 0.30 * review_score) +
            0.15 * (0.65 * sales_score + 0.35 * review_score) +
            0.05 * search_signal_score,
            2
        ) AS recommendation_score,
        'Tiki: content match + confidence + rating + review_count + quantity_sold + search keywords' AS model_explanation
    FROM tiki_features
),
repo_features AS (
    SELECT
        student_token,
        major,
        major_norm,
        cohort,
        course_order,
        course,
        course_norm,
        'ueh_repository' AS resource_type,
        CAST(repo_doc_id AS VARCHAR) AS resource_id,
        repo_title AS resource_title,
        repo_url AS resource_url,
        CAST(NULL AS VARCHAR) AS search_keywords,
        repo_match_reason AS match_reason,
        TRY_CAST(repo_score AS DOUBLE) AS match_score,
        repo_confidence AS confidence,
        CAST(NULL AS DOUBLE) AS rating_average,
        CAST(NULL AS DOUBLE) AS review_count,
        CAST(NULL AS DOUBLE) AS quantity_sold,
        CAST(NULL AS DOUBLE) AS price,
        CASE repo_confidence
            WHEN 'high' THEN 100.0
            WHEN 'medium' THEN 60.0
            WHEN 'low' THEN 30.0
            ELSE 40.0
        END AS confidence_score,
        CASE
            WHEN TRY_CAST(repo_year AS INTEGER) >= 2023 THEN 100.0
            WHEN TRY_CAST(repo_year AS INTEGER) >= 2020 THEN 80.0
            WHEN TRY_CAST(repo_year AS INTEGER) >= 2017 THEN 60.0
            WHEN TRY_CAST(repo_year AS INTEGER) IS NULL THEN 50.0
            ELSE 40.0
        END AS freshness_score,
        CASE
            WHEN COALESCE(TRY_CAST(repo_views AS DOUBLE), 0.0) > 0
                THEN LEAST(100.0, LN(1.0 + TRY_CAST(repo_views AS DOUBLE)) * 12.0)
            ELSE 50.0
        END AS views_score
    FROM base
    WHERE repo_doc_id IS NOT NULL
      AND repo_title IS NOT NULL
      AND repo_title <> ''
),
repo_candidates AS (
    SELECT
        student_token,
        major,
        major_norm,
        cohort,
        course_order,
        course,
        course_norm,
        resource_type,
        resource_id,
        resource_title,
        resource_url,
        search_keywords,
        match_reason,
        match_score,
        confidence,
        rating_average,
        review_count,
        quantity_sold,
        price,
        confidence_score,
        freshness_score AS rating_score,
        50.0 AS review_score,
        views_score AS sales_score,
        50.0 AS search_signal_score,
        freshness_score AS quality_score,
        views_score AS popularity_score,
        ROUND(
            0.60 * COALESCE(match_score, 0.0) +
            0.25 * confidence_score +
            0.10 * freshness_score +
            0.05 * views_score,
            2
        ) AS recommendation_score,
        'UEH Repository: content match + confidence + publication year + views' AS model_explanation
    FROM repo_features
)
SELECT *
FROM tiki_candidates
UNION ALL
SELECT *
FROM repo_candidates;

CREATE OR REPLACE TABLE ai.student_recommendations AS
WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY student_token, resource_type, resource_id
            ORDER BY recommendation_score DESC, match_score DESC
        ) AS duplicate_rank
    FROM ai.resource_recommendation_candidates
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY student_token, course
            ORDER BY recommendation_score DESC, match_score DESC
        ) AS course_rank,
        ROW_NUMBER() OVER (
            PARTITION BY student_token
            ORDER BY recommendation_score DESC, match_score DESC
        ) AS student_rank
    FROM deduplicated
    WHERE duplicate_rank = 1
)
SELECT *
FROM ranked;

CREATE OR REPLACE VIEW ai.student_recommendations_top3 AS
SELECT *
FROM ai.student_recommendations
WHERE student_rank <= 3;

CREATE OR REPLACE VIEW ai.student_recommendations_top5 AS
SELECT *
FROM ai.student_recommendations
WHERE student_rank <= 5;

CREATE OR REPLACE VIEW ai.resource_popularity_summary AS
SELECT
    resource_type,
    resource_id,
    resource_title,
    COUNT(*) AS recommended_times,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score,
    ROUND(AVG(match_score), 2) AS avg_match_score,
    ROUND(AVG(rating_score), 2) AS avg_quality_component,
    ROUND(AVG(sales_score), 2) AS avg_popularity_component
FROM ai.student_recommendations
WHERE student_rank <= 5
GROUP BY resource_type, resource_id, resource_title
ORDER BY recommended_times DESC, avg_recommendation_score DESC;

CREATE OR REPLACE VIEW ai.major_recommendation_summary AS
SELECT
    major,
    COUNT(*) AS recommendation_rows,
    COUNT(DISTINCT student_token) AS students,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score,
    ROUND(AVG(match_score), 2) AS avg_match_score
FROM ai.student_recommendations
WHERE student_rank <= 5
GROUP BY major
ORDER BY recommendation_rows DESC;

CREATE OR REPLACE VIEW ai.model_feature_summary AS
SELECT
    resource_type,
    COUNT(*) AS candidates,
    ROUND(AVG(match_score), 2) AS avg_match_score,
    ROUND(AVG(confidence_score), 2) AS avg_confidence_score,
    ROUND(AVG(rating_score), 2) AS avg_rating_or_freshness_score,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(sales_score), 2) AS avg_sales_or_views_score,
    ROUND(AVG(search_signal_score), 2) AS avg_search_signal_score,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score
FROM ai.resource_recommendation_candidates
GROUP BY resource_type
ORDER BY resource_type;

COPY (
    SELECT *
    FROM ai.student_recommendations_top5
    ORDER BY student_token, student_rank
)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/recommendations/student_recommendations_top5.csv'
(
    FORMAT CSV,
    HEADER true
);

COPY (
    SELECT *
    FROM ai.resource_popularity_summary
    LIMIT 50
)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/recommendations/top_recommended_resources.csv'
(
    FORMAT CSV,
    HEADER true
);

COPY (
    SELECT *
    FROM ai.model_feature_summary
)
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/recommendations/model_feature_summary.csv'
(
    FORMAT CSV,
    HEADER true
);


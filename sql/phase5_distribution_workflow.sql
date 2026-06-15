-- Phase 5: Recommendation distribution workflow.
-- Purpose: prepare recommendation results for Web Portal, Mobile App,
-- Email Digest, and OPAC/Repository widgets.
-- Run after ai_recommendation_workflow.sql and analysis_workflow.sql.

CREATE SCHEMA IF NOT EXISTS phase5;

CREATE OR REPLACE TABLE phase5.distribution_ready_recommendations AS
SELECT
    student_token,
    major,
    course,
    course_order,
    resource_type,
    resource_id,
    resource_title,
    resource_url,
    recommendation_score,
    student_rank,
    confidence,
    match_score,
    quality_score,
    popularity_score,
    model_explanation,
    CURRENT_TIMESTAMP AS availability_checked_at,
    CASE
        WHEN resource_type = 'tiki_book' THEN 'print_collection_or_marketplace'
        WHEN resource_type = 'ueh_repository' THEN 'digital_repository'
        ELSE 'unknown'
    END AS delivery_type,
    CASE
        WHEN resource_type = 'tiki_book' AND COALESCE(resource_url, '') <> ''
            THEN 'available_via_tiki_link'
        WHEN resource_type = 'ueh_repository' AND COALESCE(resource_url, '') <> ''
            THEN 'digital_access_granted'
        ELSE 'manual_check_required'
    END AS availability_status,
    CASE
        WHEN resource_type = 'tiki_book'
            THEN 'OPAC-SIM-' || COALESCE(resource_id, 'UNKNOWN')
        ELSE NULL
    END AS simulated_opac_code,
    CASE
        WHEN resource_type = 'tiki_book'
            THEN 'UEH Library - Suggested Shelf - Floor '
                 || CAST(((HASH(COALESCE(resource_id, resource_title)) % 4) + 1) AS VARCHAR)
        ELSE NULL
    END AS simulated_shelf_location,
    CASE
        WHEN resource_type = 'tiki_book' THEN 'place_hold_or_open_tiki_link'
        WHEN resource_type = 'ueh_repository' THEN 'open_repository_link'
        ELSE 'manual_review'
    END AS primary_action,
    CASE
        WHEN resource_type = 'ueh_repository' AND COALESCE(resource_url, '') <> ''
            THEN 'student_access_allowed'
        WHEN resource_type = 'ueh_repository'
            THEN 'access_check_required'
        ELSE NULL
    END AS digital_access_right,
    CASE
        WHEN recommendation_score >= 80 THEN 'high_priority'
        WHEN recommendation_score >= 60 THEN 'recommended'
        ELSE 'optional'
    END AS priority_badge,
    'mobile_app; web_portal; email_digest; opac_terminal_widget' AS distribution_channels
FROM ai.student_recommendations_top5;

CREATE OR REPLACE VIEW phase5.distribution_kpis AS
SELECT
    COUNT(*) AS delivery_rows,
    COUNT(DISTINCT student_token) AS students,
    COUNT(DISTINCT resource_id) AS resources,
    COUNT_IF(delivery_type = 'print_collection_or_marketplace') AS print_or_marketplace_items,
    COUNT_IF(delivery_type = 'digital_repository') AS digital_repository_items,
    COUNT_IF(availability_status IN ('available_via_tiki_link', 'digital_access_granted')) AS available_items,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score
FROM phase5.distribution_ready_recommendations;

CREATE OR REPLACE VIEW phase5.availability_status_summary AS
SELECT
    delivery_type,
    availability_status,
    COUNT(*) AS items,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score
FROM phase5.distribution_ready_recommendations
GROUP BY delivery_type, availability_status
ORDER BY items DESC;

CREATE OR REPLACE VIEW phase5.web_portal_payload AS
SELECT
    student_token,
    student_rank AS card_order,
    priority_badge,
    resource_type,
    LEFT(resource_title, 100) AS display_title,
    course AS related_course,
    major,
    recommendation_score,
    availability_status,
    primary_action,
    resource_url AS action_url
FROM phase5.distribution_ready_recommendations
WHERE student_rank <= 5
ORDER BY student_token, card_order;

CREATE OR REPLACE VIEW phase5.email_digest_payload AS
SELECT
    student_token,
    student_rank AS email_order,
    '[' || priority_badge || '] '
        || LEFT(resource_title, 90)
        || ' - '
        || course AS email_line,
    recommendation_score,
    resource_url
FROM phase5.distribution_ready_recommendations
WHERE student_rank <= 3
ORDER BY student_token, email_order;

CREATE OR REPLACE VIEW phase5.opac_terminal_widget_payload AS
SELECT
    student_token,
    student_rank AS widget_order,
    resource_type,
    LEFT(resource_title, 90) AS resource_title,
    simulated_opac_code,
    simulated_shelf_location,
    digital_access_right,
    availability_status,
    primary_action,
    resource_url
FROM phase5.distribution_ready_recommendations
WHERE student_rank <= 5
ORDER BY student_token, widget_order;

CREATE OR REPLACE VIEW phase5.demo_student_distribution AS
SELECT
    student_token,
    student_rank,
    resource_type,
    LEFT(resource_title, 100) AS resource_title,
    recommendation_score,
    delivery_type,
    availability_status,
    primary_action,
    COALESCE(simulated_opac_code, digital_access_right) AS access_reference
FROM phase5.distribution_ready_recommendations
WHERE student_token = (
    SELECT student_token
    FROM phase5.distribution_ready_recommendations
    GROUP BY student_token
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
ORDER BY student_rank;

COPY phase5.distribution_ready_recommendations
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/distribution_ready_recommendations.csv'
(FORMAT CSV, HEADER true);

COPY phase5.distribution_kpis
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/distribution_kpis.csv'
(FORMAT CSV, HEADER true);

COPY phase5.availability_status_summary
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/availability_status_summary.csv'
(FORMAT CSV, HEADER true);

COPY phase5.web_portal_payload
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/web_portal_payload.csv'
(FORMAT CSV, HEADER true);

COPY phase5.email_digest_payload
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/email_digest_payload.csv'
(FORMAT CSV, HEADER true);

COPY phase5.opac_terminal_widget_payload
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/opac_terminal_widget_payload.csv'
(FORMAT CSV, HEADER true);

COPY phase5.demo_student_distribution
TO 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/phase5_distribution/demo_student_distribution.csv'
(FORMAT CSV, HEADER true);


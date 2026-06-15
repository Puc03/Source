# Privacy Layer Outputs

These files are generated from the cleaned and matched datasets.

## Key Rules

- `student_hash` is generated with HMAC-SHA256 from `student_code`.
- `student_token` is a stable short pseudonymous ID for API, dashboard, and downstream analytics use.
- The private raw token mapping is stored in `.secrets/student_token_mapping_private.csv`, not in this output folder.
- Analytics files do not contain raw student IDs, student codes, names, masked codes, or initials.
- Protected files keep initials and `student_code_masked`, where the final 5 digits are hidden.
- Kafka, dashboards, and APIs should use analytics files by default.

## Files

- `student_token_map_protected.csv`: 2000 rows
- `students_protected.csv`: 2000 rows
- `student_courses_protected.csv`: 12000 rows
- `student_resource_matches_analytics.csv`: 12000 rows
- `course_resource_matches_analytics.csv`: 1296 rows
- `tiki_books_public.csv`: 6399 rows
- `ueh_repository_public.csv`: 2000 rows
- `privacy_validation.csv`: 18 rows

## Validation

- PASS: students_protected_row_count_matches_source - {'source': 2000, 'protected': 2000}
- PASS: student_hash_unique_per_student - {'unique_hashes': 2000, 'students': 2000}
- PASS: student_hash_is_hmac_sha256_length - all hashes are 64 lowercase hex characters
- PASS: student_hash_reproducible - protected hashes match deterministic HMAC output
- PASS: student_token_unique_per_student - {'unique_tokens': 2000, 'students': 2000}
- PASS: student_token_format - all tokens match stu_ plus 16 lowercase hex characters
- PASS: student_token_reproducible - protected tokens match deterministic HMAC token output
- PASS: student_token_map_protected_row_count - {'source': 2000, 'token_map': 2000}
- PASS: student_token_map_protected_has_no_raw_pii_columns - no raw PII columns
- PASS: student_token_map_protected_sample_has_no_raw_student_codes - first 1000 rows do not contain sampled raw student codes
- PASS: students_protected_sample_has_no_raw_student_codes - first 1000 rows do not contain sampled raw student codes
- PASS: student_courses_protected_sample_has_no_raw_student_codes - first 1000 rows do not contain sampled raw student codes
- PASS: student_resource_matches_analytics_has_no_forbidden_pii_columns - no forbidden columns
- PASS: student_resource_matches_analytics_sample_has_no_raw_student_codes - first 1000 rows do not contain sampled raw student codes
- PASS: course_resource_matches_analytics_has_no_forbidden_pii_columns - no forbidden columns
- PASS: student_courses_protected_row_count - 12000
- PASS: student_matches_analytics_row_count - 12000
- PASS: student_matches_analytics_has_all_matches - {'missing_tiki': 0, 'missing_repo': 0}

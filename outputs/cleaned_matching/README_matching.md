# Cleaned and Matched Dataset Outputs

Pipeline output for the three CSV files supplied by the user.

## Files

- `tiki_books_clean.csv`: unique cleaned Tiki book records.
- `ueh_students_clean.csv`: cleaned student table, one row per student.
- `ueh_student_courses_clean.csv`: exploded student-course table.
- `ueh_repository_clean.csv`: cleaned UEH repository metadata.
- `course_resource_matches.csv`: top 3 Tiki books and top 3 UEH repository documents for each major-course pair.
- `student_resource_matches.csv`: final joined table, one row per student-course with the best Tiki and UEH repository match.
- `match_quality_summary.csv`: row counts and confidence distribution.
- `data_cleaning_report.json`: machine-readable audit notes.

## Matching Method

Text was normalized accent-insensitively, tokenized into words and n-grams, expanded with Vietnamese/English domain synonyms, then scored against resource titles and secondary text. Each match includes a numeric score, confidence label, and reason string.

## Summary

- raw_tiki_rows: 9473.0
- clean_tiki_unique_books: 6399.0
- raw_student_rows: 2000.0
- clean_student_rows: 2000.0
- student_course_rows: 12000.0
- unique_major_course_pairs: 216.0
- raw_repo_rows: 2000.0
- clean_repo_unique_docs: 2000.0
- course_resource_match_rows_top3_each_type: 1296.0
- student_resource_match_rows: 12000.0
- student_rows_with_tiki_match: 12000.0
- student_rows_with_repo_match: 12000.0
- student_rows_with_both_matches: 12000.0
- top1_tiki_book_confidence_high: 73.0
- top1_tiki_book_confidence_low: 72.0
- top1_tiki_book_confidence_medium: 71.0
- top1_tiki_book_avg_score: 51.51
- top1_ueh_repository_confidence_medium: 88.0
- top1_ueh_repository_confidence_low: 80.0
- top1_ueh_repository_confidence_high: 48.0
- top1_ueh_repository_avg_score: 40.65

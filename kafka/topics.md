# Kafka Topics

Bootstrap server from host:

```text
localhost:9092
```

Bootstrap server from containers:

```text
kafka:29092
```

## Topics

| Topic | Partitions | Purpose | Producer |
|---|---:|---|---|
| `privacy.validation.v1` | 1 | Privacy-layer validation/audit events | privacy layer |
| `dataset.analytics.student_matches.v1` | 3 | One event per protected student-course match | `producer_student_matches.py` |
| `dataset.analytics.course_matches.v1` | 3 | Course-level top resource matches | future producer |
| `dataset.public.tiki_books.v1` | 3 | Public Tiki book metadata | future producer |
| `dataset.public.ueh_repository.v1` | 3 | Public UEH repository metadata | future producer |
| `data_quality.report.v1` | 1 | Row counts, schema validation, and quality reports | quality jobs |
| `audit.privacy_access.v1` | 1 | Access/audit trail for protected datasets | services |
| `dead_letter.dataset_pipeline.v1` | 1 | Invalid records and publish failures | all producers |

## Privacy Rule

Default downstream services should consume from:

```text
dataset.analytics.student_matches.v1
dataset.analytics.course_matches.v1
dataset.public.tiki_books.v1
dataset.public.ueh_repository.v1
```

Do not publish raw `student_code`, `student_name`, `student_id`, masked code, or initials into analytics topics.

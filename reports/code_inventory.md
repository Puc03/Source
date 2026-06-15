# Tong Hop File Code Trong Du An

Thu muc goc:

```text
C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki
```

Luu y bao mat:

- Khong dua noi dung thu muc `.secrets` vao report.
- File `.secrets/student_token_mapping_private.csv` la mapping rieng tu, chi dung noi bo.
- Cac file trong `outputs` la ket qua sinh ra, khong phai code chinh.

## 1. Nhom Code Chinh Nen Dua Vao Report

| Phase | File | Vai tro |
|---|---|---|
| Cleaning & Matching | `scripts/clean_and_match_datasets.py` | Lam sach 3 dataset goc, chuan hoa text, matching sinh vien - mon hoc - Tiki - UEH Repository |
| Workbook output | `scripts/build_matched_workbook.mjs` | Tao file Excel tong hop cleaned/matched |
| Privacy Layer | `scripts/create_privacy_layer.py` | Tao student_token, student_hash, che student_code, xoa PII, xuat analytics/protected files |
| Privacy Workbook | `scripts/build_privacy_workbook.mjs` | Tao workbook Excel cho privacy layer |
| AI Recommendation | `sql/ai_recommendation_workflow.sql` | Tao bang/VIEW de xep hang goi y Top-N tai nguyen |
| Analysis | `sql/analysis_workflow.sql` | Tao cac bang phan tich KPI, confidence, Tiki commerce, top resources |
| Phase 5 Distribution | `sql/phase5_distribution_workflow.sql` | Chuan bi ket qua de phan phoi qua web, mobile, email, OPAC widget |

## 2. Nhom Code Kafka Cu

Nhom da quyet dinh bo Kafka trong report chinh, nhung cac file nay van ton tai trong project.

| File | Vai tro |
|---|---|
| `kafka/docker-compose.yml` | Dung Docker Compose de chay Kafka local |
| `kafka/create-topics.sh` | Tao cac Kafka topics cho pipeline |
| `scripts/kafka_smoke_test.ps1` | Script PowerShell chay smoke test Kafka |
| `scripts/producer_student_matches.py` | Doc analytics CSV, validate theo schema, publish event len Kafka |
| `scripts/consumer_debug_student_matches.py` | Consume event tu Kafka de debug |
| `scripts/consumer_sink_sqlite.py` | Consume Kafka event va luu vao SQLite |
| `scripts/query_student_matches_db.py` | Query SQLite sink va in report kiem tra |

Khuyen nghi khi bao cao:

> Cac file Kafka duoc xem la huong mo rong, khong trinh bay trong demo chinh de giu pipeline gon va on dinh.

## 3. Nhom JSON Schema

| File | Vai tro |
|---|---|
| `schemas/student_resource_match.schema.json` | Dinh nghia cau truc event student-resource-match |
| `schemas/course_resource_match.schema.json` | Dinh nghia cau truc event course-resource-match |

Schema chu yeu phuc vu Kafka/event bus. Neu bo Kafka trong report, chi can nhac ngan rang schema la phan mo rong cho event validation.

## 4. Chi Tiet Tung File Code

### `scripts/clean_and_match_datasets.py`

Dong code: 762.

Vai tro:

- Doc 3 file raw CSV:
  - `tiki_books (2).csv`
  - `mock_ueh_students_2000.csv`
  - `ueh_repository_raw.csv`
- Lam sach text tieng Viet.
- Chuan hoa major/course/title.
- Tach danh sach mon hoc cua sinh vien.
- Chuan hoa metadata Tiki va UEH Repository.
- Tao token/ngram de so khop noi dung.
- Tinh diem matching va confidence.
- Xuat ket qua vao `outputs/cleaned_matching`.

Output chinh:

```text
outputs/cleaned_matching/tiki_books_clean.csv
outputs/cleaned_matching/ueh_students_clean.csv
outputs/cleaned_matching/ueh_student_courses_clean.csv
outputs/cleaned_matching/ueh_repository_clean.csv
outputs/cleaned_matching/course_resource_matches.csv
outputs/cleaned_matching/student_resource_matches.csv
outputs/cleaned_matching/match_quality_summary.csv
outputs/cleaned_matching/data_cleaning_report.json
```

Lenh chay:

```powershell
python scripts/clean_and_match_datasets.py
```

### `scripts/build_matched_workbook.mjs`

Dong code: 70.

Vai tro:

- Gom cac CSV cleaned/matched thanh mot file Excel.
- Tao sheet README.
- Tao preview anh workbook.

Output:

```text
outputs/cleaned_matching/ueh_tiki_cleaned_matched_dataset.xlsx
outputs/cleaned_matching/workbook_readme_preview.png
```

Lenh chay:

```powershell
node scripts/build_matched_workbook.mjs
```

### `scripts/create_privacy_layer.py`

Dong code: 473.

Vai tro:

- Tao secret rieng trong `.secrets`.
- Tao `student_hash`.
- Tao `student_token`.
- Che `student_code` bang cach giu phan dau va che 5 so cuoi.
- Tao initials cho ten sinh vien.
- Xoa cac cot PII khoi file analytics.
- Tao audit report va validation.

Output chinh:

```text
outputs/privacy_layer/student_resource_matches_analytics.csv
outputs/privacy_layer/course_resource_matches_analytics.csv
outputs/privacy_layer/students_protected.csv
outputs/privacy_layer/student_courses_protected.csv
outputs/privacy_layer/student_token_map_protected.csv
outputs/privacy_layer/privacy_validation.csv
outputs/privacy_layer/privacy_audit_report.json
```

Output rieng tu, khong dua vao report:

```text
.secrets/student_hash_secret
.secrets/student_token_mapping_private.csv
```

Lenh chay:

```powershell
python scripts/create_privacy_layer.py
```

### `scripts/build_privacy_workbook.mjs`

Dong code: 82.

Vai tro:

- Gom cac file privacy/protected CSV thanh Excel workbook.
- Tao README sheet.
- Tao preview anh workbook.

Output:

```text
outputs/privacy_layer/ueh_tiki_privacy_layer.xlsx
outputs/privacy_layer/ueh_tiki_privacy_layer_mask_last5.xlsx
outputs/privacy_layer/privacy_workbook_readme_preview.png
```

Lenh chay:

```powershell
node scripts/build_privacy_workbook.mjs
```

### `sql/ai_recommendation_workflow.sql`

Dong code: 292.

Vai tro:

- Tao schema `ai`.
- Tao bang ung vien goi y:
  - `ai.resource_recommendation_candidates`
- Tao bang ket qua recommendation:
  - `ai.student_recommendations`
- Tao view Top-N:
  - `ai.student_recommendations_top3`
  - `ai.student_recommendations_top5`
- Tao summary:
  - `ai.resource_popularity_summary`
  - `ai.major_recommendation_summary`
  - `ai.model_feature_summary`

Mo hinh:

```text
Content-based Recommendation with Popularity-aware Ranking
```

Tin hieu su dung:

- Match score.
- Confidence score.
- Tiki rating.
- Tiki review count.
- Tiki quantity sold.
- Tiki search keywords.
- UEH Repository year.
- UEH Repository views.

Output:

```text
outputs/recommendations/student_recommendations_top5.csv
outputs/recommendations/top_recommended_resources.csv
outputs/recommendations/model_feature_summary.csv
```

Lenh chay trong DuckDB:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/ai_recommendation_workflow.sql'
```

### `sql/analysis_workflow.sql`

Dong code: 211.

Vai tro:

- Tao schema `analysis`.
- Tao cac view phan tich:
  - `analysis.overview_kpis`
  - `analysis.major_match_summary`
  - `analysis.course_match_summary`
  - `analysis.tiki_confidence_summary`
  - `analysis.repo_confidence_summary`
  - `analysis.tiki_commerce_summary`
  - `analysis.top_tiki_books_by_match`
  - `analysis.top_repo_documents_by_match`
  - `analysis.data_lake_partition_summary`
  - `analysis.recommendation_kpis`
  - `analysis.recommendation_by_resource_type`
  - `analysis.top_recommended_resources`
  - `analysis.major_recommendation_summary`

Output:

```text
outputs/analysis/overview_kpis.csv
outputs/analysis/major_match_summary.csv
outputs/analysis/course_match_summary.csv
outputs/analysis/tiki_confidence_summary.csv
outputs/analysis/repo_confidence_summary.csv
outputs/analysis/tiki_commerce_summary.csv
outputs/analysis/top_tiki_books_by_match.csv
outputs/analysis/top_repo_documents_by_match.csv
outputs/analysis/data_lake_partition_summary.csv
outputs/analysis/recommendation_kpis.csv
outputs/analysis/recommendation_by_resource_type.csv
outputs/analysis/top_recommended_resources.csv
outputs/analysis/major_recommendation_summary.csv
outputs/analysis/low_confidence_improvement_candidates.csv
```

Lenh chay trong DuckDB:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/analysis_workflow.sql'
```

### `sql/phase5_distribution_workflow.sql`

Dong code: 170.

Vai tro:

- Tao schema `phase5`.
- Lay ket qua tu `ai.student_recommendations_top5`.
- Mo phong check availability:
  - Tiki link.
  - Repository access.
  - OPAC code mo phong.
  - Shelf location mo phong.
- Tao payload cho cac kenh:
  - Web portal.
  - Mobile app.
  - Email digest.
  - OPAC terminal widget.

Output:

```text
outputs/phase5_distribution/distribution_ready_recommendations.csv
outputs/phase5_distribution/distribution_kpis.csv
outputs/phase5_distribution/availability_status_summary.csv
outputs/phase5_distribution/web_portal_payload.csv
outputs/phase5_distribution/email_digest_payload.csv
outputs/phase5_distribution/opac_terminal_widget_payload.csv
outputs/phase5_distribution/demo_student_distribution.csv
```

Lenh chay trong DuckDB:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/phase5_distribution_workflow.sql'
```

### `scripts/producer_student_matches.py`

Dong code: 259.

Vai tro:

- Doc `student_resource_matches_analytics.csv`.
- Dong goi moi dong thanh event JSON.
- Validate event theo `schemas/student_resource_match.schema.json`.
- Publish len Kafka topic `dataset.analytics.student_matches.v1`.
- Ghi dead-letter file neu record loi.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `scripts/consumer_debug_student_matches.py`

Dong code: 152.

Vai tro:

- Consume event Kafka de kiem tra.
- Validate xem event co lo PII hay khong.
- In sample event khi debug.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `scripts/consumer_sink_sqlite.py`

Dong code: 548.

Vai tro:

- Consume event Kafka.
- Validate record.
- Luu event vao SQLite.
- Ghi invalid event vao dead-letter file.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `scripts/query_student_matches_db.py`

Dong code: 271.

Vai tro:

- Query SQLite sink.
- In thong ke ve event, student, major, course, resource.
- Kiem tra privacy tren SQLite.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `scripts/kafka_smoke_test.ps1`

Dong code: 29.

Vai tro:

- Start Kafka bang Docker Compose.
- Tao topics.
- Publish sample event.
- Consume va validate event.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `kafka/docker-compose.yml`

Dong code: 43.

Vai tro:

- Cau hinh Kafka local bang Docker Compose.
- Dung image `apache/kafka:3.7.2`.
- Mo port `9092`.
- Chay service `kafka-init` de tao topics.

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `kafka/create-topics.sh`

Dong code: 28.

Vai tro:

- Tao cac Kafka topics:
  - `privacy.validation.v1`
  - `dataset.analytics.student_matches.v1`
  - `dataset.analytics.course_matches.v1`
  - `dataset.public.tiki_books.v1`
  - `dataset.public.ueh_repository.v1`
  - `data_quality.report.v1`
  - `audit.privacy_access.v1`
  - `dead_letter.dataset_pipeline.v1`

Trang thai trong report:

```text
Huong mo rong / khong demo chinh
```

### `schemas/student_resource_match.schema.json`

Dong code: 182.

Vai tro:

- JSON Schema cho event student-resource-match.
- Dam bao event co dung field bat buoc.
- Chan field ngoai schema.

### `schemas/course_resource_match.schema.json`

Dong code: 91.

Vai tro:

- JSON Schema cho event course-resource-match.
- Phuc vu event validation neu dung Kafka.

## 5. Thu Tu Chay Code Cho Demo Chinh

### Buoc 1: Cleaning & Matching

```powershell
python scripts/clean_and_match_datasets.py
```

```powershell
node scripts/build_matched_workbook.mjs
```

### Buoc 2: Privacy Layer

```powershell
python scripts/create_privacy_layer.py
```

```powershell
node scripts/build_privacy_workbook.mjs
```

### Buoc 3: Warehouse / DuckDB

Mo DuckDB database:

```powershell
& "C:/duckdb/duckdb.exe" "C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/warehouse/ueh_bigdata.duckdb"
```

### Buoc 4: AI Recommendation

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/ai_recommendation_workflow.sql'
```

### Buoc 5: Analysis

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/analysis_workflow.sql'
```

### Buoc 6: Phase 5 Distribution

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/phase5_distribution_workflow.sql'
```

## 6. Thu Tu Code Theo Pipeline

```text
Raw CSV
  |
  v
scripts/clean_and_match_datasets.py
  |
  v
outputs/cleaned_matching/*.csv
  |
  v
scripts/create_privacy_layer.py
  |
  v
outputs/privacy_layer/*_analytics.csv
  |
  v
DuckDB warehouse: outputs/warehouse/ueh_bigdata.duckdb
  |
  v
sql/ai_recommendation_workflow.sql
  |
  v
sql/analysis_workflow.sql
  |
  v
sql/phase5_distribution_workflow.sql
  |
  v
outputs/recommendations + outputs/analysis + outputs/phase5_distribution
```

## 7. File Nen Dua Vao Phu Luc Code

Neu report khong the dua tat ca code, nen dua cac file nay:

1. `scripts/clean_and_match_datasets.py`
2. `scripts/create_privacy_layer.py`
3. `sql/ai_recommendation_workflow.sql`
4. `sql/analysis_workflow.sql`
5. `sql/phase5_distribution_workflow.sql`

Neu co them phu luc mo rong:

6. `scripts/build_matched_workbook.mjs`
7. `scripts/build_privacy_workbook.mjs`
8. `schemas/student_resource_match.schema.json`


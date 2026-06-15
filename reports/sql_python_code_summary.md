# Tong Hop Code SQL Va Python Cho Bao Cao

Thu muc du an:

```text
C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki
```

## 1. Ket Luan Nhanh

Nhom khong can viet them code moi cho Phase 5 neu chi lam demo va report. Cac phan code chinh da co du de trinh bay pipeline:

```text
Cleaning & Matching
-> Privacy Layer
-> Data Warehouse / Analysis
-> AI Recommendation
-> Phase 5 Distribution
-> Spark ALS Extension
```

Khi bao cao, chi nen dua cac file code chinh vao noi dung. Cac file Kafka nen de o muc "huong mo rong" vi nhom da quyet dinh bo Kafka trong demo chinh.

## 2. Python Code Chinh

| Phase | File | Vai tro |
|---|---|---|
| Phase 1 - Thu thap, lam sach, matching | `scripts/clean_and_match_datasets.py` | Doc 3 dataset raw, lam sach text, chuan hoa field, matching sinh vien - mon hoc - sach Tiki - tai lieu UEH Repository |
| Phase 2 - Privacy Layer | `scripts/create_privacy_layer.py` | Tao student_token, student_hash, che student_code, loai bo PII, tao protected/analytics files |
| Phase 4 mo rong - Spark ALS | `scripts/spark_als_library_recommendation.py` | Tao proxy implicit feedback va train mo hinh Apache Spark ALS de minh hoa collaborative filtering |

### 2.1 `scripts/clean_and_match_datasets.py`

Muc dich:

- Doc 3 file CSV goc:
  - `tiki_books (2).csv`
  - `mock_ueh_students_2000.csv`
  - `ueh_repository_raw.csv`
- Lam sach du lieu text tieng Viet.
- Chuan hoa ten nganh, mon hoc, tieu de sach, tieu de tai lieu.
- Tach mon hoc cua sinh vien thanh dang co the matching.
- Tinh diem matching giua:
  - sinh vien va sach Tiki
  - sinh vien va tai lieu UEH Repository
  - mon hoc va tai nguyen hoc tap
- Gan confidence:
  - `high`
  - `medium`
  - `low`
- Xuat cac file cleaned va matched.

Output quan trong:

```text
outputs/cleaned_matching/tiki_books_clean.csv
outputs/cleaned_matching/ueh_students_clean.csv
outputs/cleaned_matching/ueh_student_courses_clean.csv
outputs/cleaned_matching/ueh_repository_clean.csv
outputs/cleaned_matching/course_resource_matches.csv
outputs/cleaned_matching/student_resource_matches.csv
outputs/cleaned_matching/match_quality_summary.csv
```

Lenh chay:

```powershell
python scripts/clean_and_match_datasets.py
```

Doan giai thich dua vao bao cao:

> File `clean_and_match_datasets.py` dam nhan vai tro tien xu ly du lieu. Script doc ba nguon du lieu ban dau, lam sach va chuan hoa cac truong van ban, sau do tinh diem matching giua thong tin sinh vien, mon hoc, sach Tiki va tai lieu UEH Repository. Ket qua cua buoc nay la cac bang du lieu da sach va bang matching dung cho cac phase tiep theo.

## 3. Privacy Python Code

### 3.1 `scripts/create_privacy_layer.py`

Muc dich:

- Tao ma dinh danh an danh `student_token`.
- Tao `student_hash` bang secret rieng.
- Che `student_code`, giu phan dau va che 5 so cuoi.
- Loai bo thong tin dinh danh truc tiep nhu ho ten day du, ma sinh vien goc.
- Tao 2 nhom output:
  - protected files: dung de kiem tra noi bo
  - analytics files: dung cho phan tich va recommendation

Output quan trong:

```text
outputs/privacy_layer/student_resource_matches_analytics.csv
outputs/privacy_layer/course_resource_matches_analytics.csv
outputs/privacy_layer/students_protected.csv
outputs/privacy_layer/student_courses_protected.csv
outputs/privacy_layer/student_token_map_protected.csv
outputs/privacy_layer/privacy_validation.csv
outputs/privacy_layer/privacy_audit_report.json
```

Output khong dua vao report:

```text
.secrets/student_hash_secret
.secrets/student_token_mapping_private.csv
```

Lenh chay:

```powershell
python scripts/create_privacy_layer.py
```

Doan giai thich dua vao bao cao:

> File `create_privacy_layer.py` tao lop bao ve quyen rieng tu truoc khi du lieu duoc dua vao phan tich. Script thay the thong tin dinh danh cua sinh vien bang `student_token`, bam ma sinh vien thanh `student_hash`, dong thoi che 5 so cuoi cua `student_code`. Cac file analytics sau privacy layer khong con chua PII truc tiep, phu hop de su dung cho data warehouse, recommendation va analysis.

## 4. SQL Code Chinh

| Phase | File | Vai tro |
|---|---|---|
| Phase 3/4 - AI Recommendation | `sql/ai_recommendation_workflow.sql` | Tao bang ung vien de xuat, tinh diem recommendation, xuat Top-N recommendation |
| Phase Insight - Analysis | `sql/analysis_workflow.sql` | Tao KPI, phan tich confidence, top resource, insight theo nganh va tin hieu Tiki |
| Phase 5 - Distribution | `sql/phase5_distribution_workflow.sql` | Chuan bi ket qua phan phoi qua web, email, OPAC widget va file demo |

### 4.1 `sql/ai_recommendation_workflow.sql`

Muc dich:

- Tao schema `ai`.
- Doc du lieu analytics sau privacy layer.
- Tao bang ung vien de xuat.
- Tinh diem recommendation dua tren:
  - match score
  - confidence
  - rating Tiki
  - review count
  - quantity sold
  - repo year
  - repo views
- Xep hang tai nguyen cho tung sinh vien.
- Xuat Top-N recommendation.

Output:

```text
outputs/recommendations/student_recommendations_top5.csv
outputs/recommendations/top_recommended_resources.csv
outputs/recommendations/model_feature_summary.csv
```

Truy van demo:

```sql
SELECT
    student_token,
    major,
    course,
    resource_type,
    resource_title,
    recommendation_score,
    student_rank
FROM ai.student_recommendations_top5
ORDER BY student_token, student_rank
LIMIT 20;
```

Doan giai thich dua vao bao cao:

> File `ai_recommendation_workflow.sql` la phan xu ly recommendation chinh cua demo. Nhom su dung phuong phap content-based recommendation ket hop popularity-aware ranking. Mo hinh khai thac thong tin nganh hoc, mon hoc, diem matching, do tin cay matching va metadata tai nguyen de xep hang sach Tiki va tai lieu UEH Repository cho tung sinh vien.

### 4.2 `sql/analysis_workflow.sql`

Muc dich:

- Tao cac bang phan tich phuc vu insight.
- Thong ke so luong de xuat theo nganh.
- Phan tich do tin cay matching.
- Phan tich tin hieu Tiki:
  - rating
  - review count
  - quantity sold
- Tim top tai nguyen duoc de xuat nhieu nhat.

Truy van demo:

```sql
SELECT *
FROM analysis.major_recommendation_summary
ORDER BY total_recommendations DESC
LIMIT 10;
```

Doan giai thich dua vao bao cao:

> File `analysis_workflow.sql` dung de tao cac bang phan tich va KPI sau khi da co ket qua recommendation. Buoc nay giup nhom rut ra insight nhu nganh nao co nhieu tai nguyen phu hop, nhom tai nguyen nao co diem de xuat cao, va do tin cay matching phan bo nhu the nao.

### 4.3 `sql/phase5_distribution_workflow.sql`

Muc dich:

- Tao schema `phase5`.
- Lay Top-N recommendation tu schema `ai`.
- Kiem tra kha dung tai nguyen bang metadata hien co.
- Chia tai nguyen thanh:
  - `print_collection_or_marketplace`
  - `digital_repository`
- Tao payload cho cac kenh:
  - web portal
  - email digest
  - OPAC terminal widget
- Xuat CSV cho demo.

Output:

```text
outputs/phase5_distribution/distribution_kpis.csv
outputs/phase5_distribution/availability_status_summary.csv
outputs/phase5_distribution/distribution_ready_recommendations.csv
outputs/phase5_distribution/web_portal_payload.csv
outputs/phase5_distribution/email_digest_payload.csv
outputs/phase5_distribution/opac_terminal_widget_payload.csv
outputs/phase5_distribution/demo_student_distribution.csv
```

Ket qua Phase 5 hien tai:

```text
delivery_rows = 10000
students = 2000
resources = 151
print_or_marketplace_items = 5394
digital_repository_items = 4606
available_items = 10000
avg_recommendation_score = 70.5
```

Truy van demo:

```sql
SELECT *
FROM phase5.distribution_kpis;

SELECT *
FROM phase5.availability_status_summary;

SELECT *
FROM phase5.demo_student_distribution;
```

Doan giai thich dua vao bao cao:

> File `phase5_distribution_workflow.sql` mo phong buoc phan phoi ket qua de xuat den nguoi dung cuoi. Ket qua Top-N tu mo hinh AI duoc kiem tra kha dung dua tren metadata hien co, sau do chuan hoa thanh payload cho web portal, email digest va OPAC terminal widget. Trong demo, nhom xuat cac payload nay thanh CSV va dung DuckDB de truy van kiem tra.

## 5. Spark ALS Extension

### `scripts/spark_als_library_recommendation.py`

Muc dich:

- Minh hoa huong phat trien bang Apache Spark va Collaborative Filtering ALS.
- Tao proxy implicit feedback tu du lieu analytics hien co.
- Mapping user/item sang ID so.
- Train mo hinh ALS.
- Xuat top recommendation tu ALS.

Output:

```text
outputs/spark_als/als_input_summary
outputs/spark_als/als_model_metrics
outputs/spark_als/als_top_recommendations
outputs/spark_als/als_user_mapping
outputs/spark_als/als_item_mapping
outputs/spark_als/als_proxy_interactions
```

Lenh chay:

```powershell
python scripts/spark_als_library_recommendation.py --rank 20 --max-iter 10 --reg-param 0.1 --top-k 10
```

Ket qua da co:

```text
interaction_rows = 22115
users = 2000
items = 314
avg_proxy_rating = 4.8046
prediction_rows = 4287
rmse = 4.7891
```

Doan giai thich dua vao bao cao:

> Spark ALS duoc nhom dua vao nhu mot demo mo rong cho huong phat trien. Do chua co log hanh vi that cua sinh vien nhu click, muon/tra, download PDF hoac rating, nhom tao proxy implicit feedback tu du lieu analytics hien co. Trong he thong thuc te, proxy feedback nay se duoc thay bang log hanh vi that de huan luyen collaborative filtering chinh xac hon.

## 6. Code Khong Dua Vao Demo Chinh

Cac file Kafka ton tai trong du an nhung khong nen dua vao demo chinh:

```text
scripts/producer_student_matches.py
scripts/consumer_debug_student_matches.py
scripts/consumer_sink_sqlite.py
scripts/query_student_matches_db.py
scripts/kafka_smoke_test.ps1
kafka/docker-compose.yml
kafka/create-topics.sh
```

Cach ghi trong bao cao:

> Nhom co xay dung thu nghiem Event Bus voi Kafka o giai doan dau, tuy nhien de phu hop voi pham vi demo mon hoc, pipeline chinh tap trung vao batch analytics, DuckDB, Parquet, AI recommendation va Spark ALS extension. Kafka duoc xem la huong mo rong khi he thong can xu ly streaming event trong thuc te.

## 7. Thu Tu Demo De Giam Loi

Nen demo theo thu tu:

```text
1. Show raw/cleaned output
2. Show privacy layer output
3. Show DuckDB warehouse/data lake query
4. Show AI recommendation output
5. Show Phase 5 distribution output
6. Show Spark ALS extension output
```

Khong nen demo:

```text
Kafka local
Docker Compose Kafka
MongoDB
ClickHouse
```

Neu giang vien hoi ve quy mo lon:

> Trong demo, nhom dung DuckDB va Parquet de mo phong data warehouse/data lake tren may local. Trong huong phat trien, co the thay bang data lake phan tan nhu HDFS/S3/MinIO va xu ly bang Apache Spark.


# Demo Checklist - UEH Tiki Big Data Recommendation Project

## 1. Muc Tieu Demo

Demo can chung minh duoc pipeline Big Data hoan chinh:

1. Co nhieu nguon du lieu dau vao.
2. Da lam sach va matching du lieu.
3. Da tao privacy layer de bao ve thong tin sinh vien.
4. Da luu tru du lieu phan tich trong warehouse.
5. Da mo phong data lake / distributed storage bang Parquet partition.
6. Da xay dung AI recommendation workflow.
7. Da phan tich ket qua va rut insight.

## 2. Thu Tu Demo Nen Lam

### Buoc 1: Gioi thieu bai toan

Noi ngan gon:

> Nhom xay dung he thong goi y tai nguyen hoc tap cho sinh vien dua tren nganh hoc, mon hoc, sach Tiki va tai lieu UEH Repository.

Mo file / slide so do pipeline tong the.

### Buoc 2: Mo thu muc dataset dau vao

Can cho thay 3 file:

- mock_ueh_students_2000.csv
- tiki_books (2).csv
- ueh_repository_raw.csv

Noi:

> Du lieu den tu 3 nguon: ho so sinh vien mo phong, sach tren Tiki va tai lieu hoc thuat tu UEH Repository.

### Buoc 3: Mo ket qua clean va matching

Mo:

- outputs/cleaned_matching/student_resource_matches.csv
- outputs/cleaned_matching/ueh_tiki_cleaned_matched_dataset.xlsx

Noi:

> Sau khi chuan hoa ten nganh, mon hoc va tieu de tai nguyen, nhom matching sinh vien voi sach Tiki va tai lieu UEH Repository.

### Buoc 4: Mo privacy layer

Mo:

- outputs/privacy_layer/student_resource_matches_analytics.csv
- outputs/privacy_layer/student_token_map_protected.csv

Noi:

> Du lieu phan tich khong dung ma sinh vien that hay ten sinh vien that. Thay vao do, nhom dung student_token va student_hash.

Neu can, cho thay cot student_token.

### Buoc 5: Mo DuckDB warehouse

Trong DuckDB shell:

```sql
.tables
```

Sau do chay:

```sql
SELECT COUNT(*) AS total_rows
FROM fact_student_resource_matches;
```

Noi:

> Bang fact trong DuckDB dong vai tro analytical warehouse de truy van nhanh cho bao cao va mo hinh de xuat.

### Buoc 6: Demo data lake Parquet partition

Chay:

```sql
SELECT COUNT(DISTINCT major) AS total_partitions
FROM read_parquet(
  'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/data_lake/student_matches/**/*.parquet'
);
```

Noi:

> Nhom mo phong distributed storage bang Parquet, chia partition theo major. Cach nay tuong tu data lake tren HDFS/S3 trong he thong Big Data thuc te.

### Buoc 7: Demo AI recommendation

Chay:

```sql
SELECT
    student_token,
    major,
    course,
    resource_type,
    LEFT(resource_title, 80) AS resource_title,
    recommendation_score,
    student_rank
FROM ai.student_recommendations_top5
ORDER BY student_token, student_rank
LIMIT 20;
```

Noi:

> Mo hinh xep hang tai nguyen dua tren content matching, confidence, rating, review, luot mua va tin hieu tim kiem Tiki.

### Buoc 8: Demo analysis

Truoc analysis, demo Phase 5:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/phase5_distribution_workflow.sql'
```

```sql
SELECT * FROM phase5.distribution_kpis;
```

```sql
SELECT * FROM phase5.demo_student_distribution;
```

Noi:

> Phase 5 chuan bi ket qua recommendation de phan phoi qua web portal, mobile app, email digest va OPAC widget. Trong demo, buoc kiem tra tinh san co duoc mo phong bang DuckDB; he thong thuc te co the thay bang OPAC API va Repository access service.

### Buoc 9: Demo analysis

Chay cac bang quan trong:

```sql
SELECT * FROM analysis.overview_kpis;
```

```sql
SELECT * FROM analysis.tiki_confidence_summary;
```

```sql
SELECT
    resource_type,
    LEFT(resource_title, 90) AS resource_title,
    recommended_times,
    avg_recommendation_score
FROM analysis.top_recommended_resources
LIMIT 10;
```

Noi:

> Phan analysis giup nhom danh gia do phu du lieu, chat luong matching va tai nguyen duoc de xuat nhieu nhat.

## 3. Checklist Truoc Gio Demo

- [ ] Docker khong can mo neu nhom da bo Kafka.
- [ ] DuckDB shell mo duoc database ueh_bigdata.duckdb.
- [ ] Query .tables hien bang fact va schema ai, analysis.
- [ ] File outputs/privacy_layer/student_resource_matches_analytics.csv ton tai.
- [ ] Thu muc outputs/data_lake/student_matches co nhieu folder major=...
- [ ] File outputs/recommendations/student_recommendations_top5.csv ton tai.
- [ ] File outputs/phase5_distribution/distribution_ready_recommendations.csv ton tai.
- [ ] File outputs/analysis/overview_kpis.csv ton tai.
- [ ] Co san slide pipeline tong the.
- [ ] Co san 5-8 anh screenshot chinh.

## 4. Neu Bi Loi Khi Demo

### Loi DuckDB dang o memory

Neu prompt hien:

```text
memory D
```

Chay:

```sql
.open 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/outputs/warehouse/ueh_bigdata.duckdb'
```

### Loi file database bi khoa

Dong cac cua so DuckDB cu bang:

```sql
.exit
```

Hoac PowerShell:

```powershell
Get-Process duckdb | Stop-Process
```

### Loi khong thay bang ai / analysis

Chay lai:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/ai_recommendation_workflow.sql'
```

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/analysis_workflow.sql'
```

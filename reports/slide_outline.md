# Slide Outline - Demo And Report

## Slide 1: Title

Ten de tai:

> Big Data Pipeline for UEH Student Learning Resource Recommendation

Noi dung:

- Ten mon hoc
- Ten nhom
- Thanh vien
- Giang vien

## Slide 2: Problem Statement

Noi dung:

- Sinh vien co nhieu mon hoc va can tai nguyen phu hop.
- Tai nguyen nam o nhieu nguon: Tiki, UEH Repository.
- Can xu ly du lieu, bao mat va goi y tai nguyen.

## Slide 3: Dataset

Bang 3 nguon du lieu:

- Student profile
- Tiki books
- UEH Repository

Chen anh dataset goc.

## Slide 4: System Architecture

So do:

```text
Raw CSV
-> Cleaning & Matching
-> Privacy Layer
-> DuckDB Warehouse
-> Parquet Data Lake
-> AI Recommendation
-> Analysis
```

## Slide 5: Data Cleaning & Matching

Noi dung:

- Chuan hoa text.
- Chuan hoa major/course.
- Matching voi Tiki va UEH Repository.
- Tao match score va confidence.

Chen anh cleaned/matched data.

## Slide 6: Privacy Layer

Noi dung:

- Loai bo PII.
- Dung student_token.
- Bao ve student_code va student_name.

Chen anh analytics file va privacy PASS.

## Slide 7: Warehouse

Noi dung:

- DuckDB analytical warehouse.
- Bang fact_student_resource_matches.
- Ho tro SQL analysis.

Chen anh DuckDB query count.

## Slide 8: Data Lake Simulation

Noi dung:

- Parquet format.
- Partition by major.
- Mo phong HDFS/S3.

Chen anh folder major=... va query read_parquet.

## Slide 9: AI Recommendation Model

Noi dung:

- Content-based + popularity-aware ranking.
- Tiki score formula.
- UEH Repository score formula.

Chen so do recommendation workflow.

## Slide 10: Recommendation Result

Noi dung:

- Top 5 resources per student.
- Ranking theo recommendation_score.

Chen anh student_recommendations_top5.

## Slide 11: Phase 5 - Recommendation Distribution

Noi dung:

- Kiem tra tinh san co cua tai nguyen.
- Ban in / marketplace: OPAC code, shelf location, hold/open link.
- Ban so hoa: Repository link va access right.
- Kenh phan phoi: mobile app, web portal, email digest, OPAC widget.

Chen anh phase5.distribution_kpis va phase5.demo_student_distribution.

## Slide 12: Analysis Result

Noi dung:

- Dataset overview.
- Matching quality.
- Tiki commerce signal.
- Top recommended resources.

Chen 2-3 bang/charts.

## Slide 13: Insights

Noi dung:

- Nganh nao co nhieu match.
- Tai nguyen nao duoc de xuat nhieu.
- Tiki rating/luot mua giup uu tien sach pho bien.
- Privacy layer giup du lieu an toan hon.

## Slide 14: Limitations

Noi dung:

- Du lieu sinh vien mo phong.
- Chua co lich su click/muon-tra thuc te.
- Chua dung collaborative filtering.
- Data lake moi la mo phong local.

## Slide 15: Future Work

Noi dung:

- Bo sung log hanh vi nguoi dung.
- Su dung Spark cho xu ly lon.
- Trien khai data lake tren cloud/HDFS.
- Apache Spark + Collaborative Filtering ALS.
- Hybrid recommendation: ALS + content-based + NLP/embedding.
- Xay dashboard realtime.

## Slide 16: Conclusion

Noi dung:

- Pipeline hoan chinh.
- Co privacy, warehouse, data lake, recommendation, analysis.
- Phu hop voi muc tieu mon Big Data.

# Cau Truc Report Hoan Chinh

## 1. Gioi Thieu De Tai

Noi dung can co:

- Bai toan: goi y tai nguyen hoc tap cho sinh vien.
- Nguon du lieu: sinh vien mo phong, sach Tiki, UEH Repository.
- Ly do dung Big Data: du lieu nhieu nguon, can lam sach, matching, bao mat, luu tru, phan tich va goi y.

Doan viet mau:

> De tai huong den viec xay dung pipeline Big Data phuc vu bai toan goi y tai nguyen hoc tap cho sinh vien. He thong ket hop du lieu ho so hoc tap da an danh, sach tren san thuong mai dien tu Tiki va tai lieu hoc thuat tu UEH Repository. Muc tieu la xu ly, lam sach, matching va phan tich du lieu de tao ra danh sach tai nguyen phu hop voi tung sinh vien theo nganh hoc va mon hoc.

## 2. Mo Ta Dataset

Can co bang:

| Dataset | Vai tro | Noi dung chinh |
|---|---|---|
| mock_ueh_students_2000.csv | Ho so sinh vien | Ma sinh vien, ten, gioi tinh, nganh, khoa |
| tiki_books (2).csv | Tai nguyen sach | Tieu de sach, rating, review, luot ban, gia, tu khoa |
| ueh_repository_raw.csv | Tai lieu hoc thuat | Tieu de, tac gia, nam, bo suu tap, luot xem |

Can chen hinh:

- Anh 3 file dataset goc.
- Anh mot vai dong du lieu trong Excel/CSV.

## 3. Data Cleaning And Matching

Noi dung can co:

- Chuan hoa text tieng Viet.
- Chuan hoa nganh hoc va mon hoc.
- Loai bo / xu ly gia tri thieu.
- Matching sinh vien voi sach Tiki.
- Matching sinh vien voi tai lieu UEH Repository.
- Tao bang student_resource_matches.

Doan viet mau:

> O buoc lam sach du lieu, nhom chuan hoa cac truong van ban nhu nganh hoc, mon hoc va tieu de tai nguyen bang cach dua ve dang thong nhat, loai bo ky tu khong can thiet va xu ly gia tri thieu. Sau do, nhom thuc hien matching dua tren do khop giua mon hoc, nganh hoc va noi dung tai nguyen. Ket qua la bang student_resource_matches, dong vai tro du lieu trung gian cho cac buoc privacy, warehouse va recommendation.

Hinh can chen:

- File cleaned/matched.
- Mot bang co cac cot student, major, course, tiki_title, repo_title, score.

## 4. Privacy Layer

Noi dung can co:

- Ly do can privacy.
- An danh student_code, student_name.
- Dung student_token / student_hash.
- Tao analytics file khong chua PII.

Doan viet mau:

> Vi du lieu co lien quan den sinh vien, nhom xay dung privacy layer truoc khi dua du lieu vao phan tich. Cac truong nhay cam nhu ma sinh vien, ten sinh vien va cac dinh danh truc tiep duoc loai bo hoac thay the bang student_token va student_hash. File analytics chi giu lai cac truong can thiet cho phan tich va mo hinh de xuat, dam bao khong lam lo thong tin ca nhan.

Hinh can chen:

- student_resource_matches_analytics.csv.
- privacy validation PASS.
- student_token_map_protected.csv, khong chup raw private mapping.

## 5. Data Warehouse Bang DuckDB

Noi dung can co:

- Ly do dung DuckDB thay ClickHouse: nhe, de demo, phu hop bai bao cao sinh vien.
- Bang fact_student_resource_matches.
- Cac truy van OLAP co group by, count, avg.

Doan viet mau:

> Trong pham vi bao cao, nhom su dung DuckDB lam analytical warehouse thay cho cac he quan tri nang hon nhu ClickHouse. DuckDB phu hop cho demo cuc bo vi ho tro SQL, doc CSV/Parquet truc tiep va thuc hien truy van phan tich nhanh. Bang fact_student_resource_matches duoc su dung lam bang fact trung tam cho cac truy van theo sinh vien, nganh hoc, mon hoc va tai nguyen.

Hinh can chen:

- DuckDB shell hien ueh_bigdata.
- .tables.
- SELECT COUNT(*) FROM fact_student_resource_matches.

## 6. Data Lake / Distributed Storage Simulation

Noi dung can co:

- Xuat bang fact thanh Parquet.
- Partition theo major.
- Giai thich day la mo phong HDFS/S3.

Doan viet mau:

> De mo phong tang luu tru phan tan, nhom xuat du lieu tu warehouse sang dinh dang Parquet va chia partition theo nganh hoc major. Cach to chuc nay tuong tu mo hinh Data Lake tren HDFS hoac S3, trong do du lieu duoc luu theo thu muc partition de toi uu cac truy van phan tich theo nhom. Trong demo, DuckDB duoc dung de doc truc tiep cac file Parquet tu Data Lake cuc bo.

Hinh can chen:

- Thu muc outputs/data_lake/student_matches co major=...
- Query read_parquet.
- COUNT(DISTINCT major) = 36.

## 7. AI Recommendation Model

Noi dung can co:

- Ten mo hinh: Content-based Recommendation with Popularity-aware Ranking.
- Dau vao: student_token, major, course, Tiki metadata, UEH Repository metadata.
- Dau ra: Top-N recommended resources.

Cong thuc:

```text
Tiki Recommendation Score
= 45% Match Score
+ 20% Confidence Score
+ 15% Quality Score
+ 15% Popularity Score
+ 5% Search Signal Score
```

```text
Quality Score = 70% Rating Score + 30% Review Score
Popularity Score = 65% Sales Score + 35% Review Score
```

Doan viet mau:

> Nhom xay dung mo hinh de xuat tai nguyen hoc tap theo huong content-based recommendation ket hop popularity-aware ranking. Mo hinh su dung diem matching giua mon hoc/nganh hoc va tai nguyen, do tin cay matching, rating, so luot danh gia, so luong da ban va tu khoa tim kiem tren Tiki. Doi voi tai lieu UEH Repository, mo hinh su dung diem matching, do tin cay, nam xuat ban va luot xem. Ket qua la danh sach Top-N tai nguyen phu hop cho tung sinh vien da duoc an danh.

Hinh can chen:

- So do AI workflow.
- model_feature_summary.
- student_recommendations_top5.

## 8. Phase 5 - Phan Phoi De Xuat

Noi dung can co:

- Ket qua recommendation can duoc dua den sinh vien qua kenh nao.
- Kiem tra tinh san co cua tai nguyen.
- Phan biet ban in / marketplace va tai lieu so Repository.
- Mo phong payload cho web portal, email digest va OPAC widget.

Doan viet mau:

> Sau khi mo hinh AI tao danh sach Top-N tai nguyen cho tung sinh vien, nhom xay dung Phase 5 de mo phong buoc phan phoi ket qua de xuat den nguoi dung cuoi. He thong kiem tra tinh san co cua tai nguyen, phan loai tai nguyen thanh nhom print collection/marketplace va digital repository, sau do chuan bi payload cho cac kenh nhu mobile app, web portal, email digest va OPAC terminal widget. Trong pham vi demo, buoc kiem tra real-time duoc mo phong bang DuckDB dua tren link tai nguyen va loai tai nguyen; trong he thong thuc te co the thay the bang OPAC circulation API va Repository access service.

Hinh can chen:

- phase5.distribution_kpis.
- phase5.availability_status_summary.
- phase5.web_portal_payload.
- phase5.demo_student_distribution.

## 9. Analysis Results

Noi dung can co:

- Overview KPI.
- Matching quality.
- Tiki commerce signal.
- Top recommended resources.
- Insight.

Doan viet mau:

> Ket qua phan tich cho thay pipeline co the xu ly du lieu tu nhieu nguon, danh gia chat luong matching va tao de xuat tai nguyen hoc tap theo tung sinh vien. Cac chi so nhu match score, confidence, rating, review count va quantity sold giup mo hinh uu tien tai nguyen vua phu hop ve noi dung vua co tin hieu chat luong tot tu thi truong.

Hinh can chen:

- overview_kpis.
- tiki_confidence_summary.
- repo_confidence_summary.
- tiki_commerce_summary.
- top_recommended_resources.

## 10. Ket Luan

Noi dung can co:

- Nhom da hoan thanh pipeline.
- Diem manh.
- Gioi han.
- Huong phat trien.

Doan viet mau:

> Nhin chung, de tai da xay dung duoc pipeline Big Data hoan chinh gom lam sach du lieu, privacy layer, data warehouse, data lake mo phong, AI recommendation va analysis. He thong co kha nang goi y sach Tiki va tai lieu UEH Repository cho sinh vien dua tren nganh hoc, mon hoc va cac tin hieu chat luong cua tai nguyen. Han che hien tai la du lieu sinh vien va hanh vi nguoi dung con mang tinh mo phong, chua co lich su click, muon/tra hoac danh gia ca nhan. Trong tuong lai, he thong co the mo rong bang cach bo sung log hanh vi thuc te, su dung collaborative filtering va trien khai tren cac nen tang phan tan nhu Spark, HDFS hoac cloud storage.

Doan mo rong neu giang vien yeu cau phuong phap AI thuc te hon:

> Voi bai toan de xuat tai lieu thu vien trong moi truong thuc te, nhom de xuat su dung Apache Spark ket hop Collaborative Filtering bang thuat toan ALS. Khi co du lieu hanh vi that nhu lich su muon/tra, click OPAC, view/download tai lieu so, bookmark hoac rating, he thong co the xay dung ma tran user-item va dung Spark MLlib ALS de hoc moi quan he an giua sinh vien va tai nguyen. Do phan lon hanh vi thu vien la implicit feedback, mo hinh co the quy doi cac hanh vi thanh diem tuong tac va train voi cau hinh implicitPrefs=True. De xu ly cold-start cho sinh vien moi hoac tai nguyen moi, ALS nen duoc ket hop voi content-based matching va NLP/embedding thanh mo hinh hybrid recommendation.

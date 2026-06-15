# Demo Script - Loi Noi Khi Thuyet Trinh

## Mo Dau

Kinh thua thay/co va cac ban, nhom em thuc hien de tai xay dung he thong goi y tai nguyen hoc tap cho sinh vien dua tren du lieu Big Data. He thong ket hop 3 nguon du lieu gom ho so sinh vien mo phong, sach tren Tiki va tai lieu hoc thuat tu UEH Repository.

Muc tieu cua nhom la xay dung mot pipeline tu dau den cuoi: lam sach du lieu, bao ve thong tin sinh vien, luu tru phan tich, mo phong data lake, xay dung mo hinh goi y va phan tich ket qua.

## Demo Pipeline Tong The

Day la kien truc tong the cua he thong. Du lieu ban dau di qua cac buoc:

```text
Raw CSV
-> Data Cleaning & Matching
-> Privacy Layer
-> DuckDB Warehouse
-> Parquet Data Lake
-> AI Recommendation
-> Analysis & Report
```

Trong pham vi mon hoc, nhom tap trung vao xu ly du lieu va phan tich, nen su dung DuckDB va Parquet de demo nhanh, on dinh va de tai lap.

## Demo Dataset

Day la 3 file du lieu dau vao:

- mock_ueh_students_2000.csv
- tiki_books (2).csv
- ueh_repository_raw.csv

Du lieu sinh vien cung cap thong tin nganh hoc va khoa hoc. Du lieu Tiki cung cap thong tin sach, rating, review, luot ban, gia va tu khoa. Du lieu UEH Repository cung cap thong tin tai lieu hoc thuat, tac gia, nam xuat ban va luot xem.

## Demo Cleaning & Matching

Sau khi lam sach, nhom tao ra file student_resource_matches.csv. Bang nay ket noi sinh vien voi sach Tiki va tai lieu UEH Repository dua tren do khop giua nganh hoc, mon hoc va noi dung tai nguyen.

Moi dong trong bang the hien mot ket qua matching, bao gom diem tiki_score, repo_score va muc do tin cay high, medium hoac low.

## Demo Privacy Layer

Vi du lieu co lien quan den sinh vien, nhom tao privacy layer truoc khi dua vao phan tich. Cac truong nhu ten sinh vien va ma sinh vien that khong duoc dung truc tiep trong file analytics. Thay vao do, nhom su dung student_token va student_hash.

Day la file student_resource_matches_analytics.csv. File nay duoc dung cho warehouse, data lake va recommendation.

## Demo Warehouse

Tiep theo, nhom nap du lieu analytics vao DuckDB. Bang fact_student_resource_matches la bang fact trung tam cua he thong.

DuckDB cho phep nhom chay cac truy van phan tich nhu dem tong so dong, dem so sinh vien, thong ke theo nganh, thong ke theo confidence va tinh diem trung binh.

## Demo Data Lake

De mo phong luu tru phan tan, nhom xuat bang fact sang Parquet va chia partition theo major. Cach lam nay tuong tu cach du lieu duoc luu trong HDFS hoac S3 o cac he thong Big Data thuc te.

Khi truy van bang read_parquet, DuckDB doc du lieu truc tiep tu cac file Parquet trong thu muc data_lake.

## Demo AI Recommendation

Phan quan trong nhat la mo hinh AI recommendation. Nhom su dung mo hinh content-based recommendation ket hop popularity-aware ranking.

Voi sach Tiki, diem de xuat duoc tinh tu:

- Match score
- Confidence score
- Rating
- So luot danh gia
- So luong da ban
- Tin hieu tu khoa tim kiem Tiki

Voi tai lieu UEH Repository, diem de xuat duoc tinh tu:

- Match score
- Confidence score
- Nam xuat ban
- Luot xem

Ket qua la bang student_recommendations_top5, cho biet moi sinh vien duoc de xuat nhung sach hoac tai lieu nao.

## Demo Analysis

Cuoi cung, nhom phan tich ket qua. Cac bang quan trong gom:

- overview_kpis: tong quan dataset
- major_match_summary: thong ke theo nganh
- tiki_confidence_summary: chat luong matching Tiki
- repo_confidence_summary: chat luong matching UEH Repository
- top_recommended_resources: tai nguyen duoc de xuat nhieu nhat

Nhung ket qua nay giup danh gia pipeline va rut ra insight cho bao cao.

## Ket Thuc

Nhom da hoan thanh mot pipeline Big Data co day du cac thanh phan chinh: data cleaning, privacy, warehouse, data lake, recommendation va analysis. He thong hien tai phu hop voi muc tieu hoc tap va co the mo rong trong tuong lai bang cach bo sung log hanh vi thuc te cua sinh vien, su dung Spark hoac trien khai data lake tren cloud.


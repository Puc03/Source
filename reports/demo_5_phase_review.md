# Review Demo 5 Phase

## Ket Luan Nhanh

Demo hien tai da co nhieu bang chung tot, nhung can sap xep lai:

```text
Phase 1 = Thu thap va mo phong hanh vi nguoi dung
Phase 2 = Luu tru Data Lake
Phase 3 = Xu ly va phan tich du lieu
Phase 4 = Mo hinh de xuat AI
Phase 5 = Phan phoi ket qua de xuat
```

Van de lon nhat hien tai:

```text
1. Phase 1 van dang theo ban cu: Tiki + Repository + mock student.
2. Phase 2 va Phase 3 dang bi trung nhau.
3. Spark ALS dang bi de nham vao Phase 3.
4. Phase 4 chua noi ro mo hinh chinh va mo hinh mo rong.
5. Phase 5 kha on, chi can noi ro la mo phong, khong phai real-time/Kong that.
```

## 1. Ban Demo Dang Thieu Gi?

### 1.1 Thieu Phase 1 moi theo Smart Library

Ban demo hien tai van mo ta:

```text
UEH Repository
Tiki
mock student
```

Phan nay khong sai, nhung sau khi nhom chuyen sang y tuong "hanh vi nguoi dung tu UEH Smart Library", Phase 1 can cap nhat thanh:

```text
Sierra
DSpace / UEH Repository
EBSCO Discovery Service / OneSearch
OpenAthens
```

Nhom da co dataset mo phong moi:

```text
outputs/behavior_simulation/smart_library_behavior_events.csv
```

So lieu can dua vao demo:

```text
students = 2,000
events = 80,667
OpenAthens = 44,032 events
DSpace = 15,928 events
EBSCO OneSearch = 10,560 events
Sierra = 10,147 events
```

Can them vao slide:

```text
Screenshot folder outputs/behavior_simulation
Screenshot system_event_summary.csv
Screenshot smart_library_behavior_events.csv vai dong dau
```

### 1.2 Thieu Privacy Layer nhu mot buoc bat buoc

Trong demo co anh query kiem tra khong co PII, day la bang chung rat tot. Tuy nhien, ban nen noi ro:

```text
Privacy Layer nam giua Phase 1 va Phase 2
```

Vi trong 5 phase khong tach rieng privacy, hay trinh bay no nhu mot "cross-cutting layer":

```text
Raw / simulated behavior data
-> Privacy layer
-> analytics data khong chua PII
-> Data Lake / Warehouse
```

Can giu lai anh:

```text
Query information_schema.columns tra ve 0 rows
```

Y nghia:

```text
Bang fact khong co student_id, student_code, student_name, ma_sv, ho_ten, user_id.
```

### 1.3 Thieu cau noi ket noi giua 5 phase

Moi phase hien co anh minh chung, nhung can them 1 slide tong quan:

```text
Behavior logs + resource metadata
-> privacy
-> data lake
-> OLAP analysis
-> AI recommendation
-> distribution payload
```

Neu khong co slide nay, nguoi nghe se thay tung phan roi rac.

### 1.4 Thieu insight cuoi cung

Phan analysis hien co nhieu bang, nhung can rut ra insight thanh cau:

```text
Nganh nao co nhieu match nhat?
Tiki hay Repository co do tin cay cao hon?
Tiki rating/luot ban co giup uu tien tai nguyen khong?
Phan bo partition theo major co hop ly khong?
Recommendation co bao phu du 2,000 sinh vien khong?
```

Khong chi chup bang, can noi "bang nay cho thay dieu gi".

## 2. Ban Demo Dang Bi Thua Gi?

### 2.1 Thua cac screenshot ClickHouse, MongoDB, SQL Developer

Neu trong file demo con anh ClickHouse/MongoDB/SQL Developer, nen bo khoi demo chinh.

Ly do:

```text
Nhom da chot dung DuckDB + Parquet + Spark ALS extension.
ClickHouse/MongoDB lam nguoi nghe tuong nhom trien khai nhieu database khac nhau.
```

Co the de vao phu luc:

```text
Da thu nghiem ClickHouse nhung chuyen sang DuckDB vi phu hop demo local.
```

### 2.2 Thua Kafka trong demo chinh

Kafka da tung lam, nhung nhom da quyet dinh bo. Khong dua vao flow demo chinh.

Chi nen noi:

```text
Kafka la huong mo rong neu can streaming event thoi gian thuc.
```

### 2.3 Thua Spark ALS trong Phase 3

Trong anh demo, Spark ALS dang nam o:

```text
#Phase 3: Xu li phan tan
```

Can chuyen toan bo Spark ALS sang Phase 4.

Ly do:

```text
Spark ALS la mo hinh recommendation, khong phai buoc analysis chung.
```

### 2.4 Thua nhieu anh DuckDB trung lap

Ban dang co nhieu anh truy van:

```text
COUNT rows
COUNT distinct major
GROUP BY major
analysis.data_lake_partition_summary
```

Khong can dua het vao demo. Chon:

```text
Phase 2: COUNT rows + COUNT partitions
Phase 3: overview KPIs + major/confidence/resource analysis
```

### 2.5 Thua chu "real-time" neu chua ket noi API that

Phase 5 co noi "real-time availability check". Nen sua thanh:

```text
mo phong availability check dua tren metadata
```

Neu noi real-time, giang vien co the hoi:

```text
Da ket noi OPAC circulation API chua?
Da co Kong gateway that chua?
```

## 3. Ban Chinh Sua 5 Phase Nen Trinh Bay

### Phase 1 - Thu Thap Va Mo Phong Hanh Vi Nguoi Dung

Noi dung nen co:

```text
4 he thong thuc te cua UEH Smart Library:
- Sierra
- DSpace / UEH Repository
- EBSCO Discovery Service / OneSearch
- OpenAthens
```

Demo can show:

```text
scripts/simulate_smart_library_behavior.py
outputs/behavior_simulation/system_event_summary.csv
outputs/behavior_simulation/smart_library_behavior_events.csv
```

So lieu:

```text
2,000 students
80,667 behavior events
4 source systems
```

Tiki va UEH Repository nen de nhu:

```text
resource catalog / metadata bo sung
```

Khong nen de Tiki la nguon hanh vi sinh vien.

### Phase 2 - Luu Tru Phan Tan Data Lake

Noi dung nen co:

```text
Du lieu da qua privacy layer
-> export Parquet
-> partition theo major
-> doc lai bang read_parquet
```

Demo can show:

```text
COUNT(*) = 12,000 rows
COUNT(DISTINCT major) = 36 partitions
Folder outputs/data_lake/student_matches
```

Khong nen show:

```text
GROUP BY major insight
Spark ALS
recommendation metrics
```

May cai do de Phase 3/4.

### Phase 3 - Xu Ly Va Phan Tich Du Lieu

Noi dung nen co:

```text
DuckDB query engine
OLAP analysis
summary by major
confidence analysis
Tiki commerce signal
Repository signal
partition summary
```

Demo can show:

```text
analysis.overview_kpis
analysis.major_match_summary
analysis.tiki_confidence_summary
analysis.repo_confidence_summary
analysis.tiki_commerce_summary
analysis.resource_popularity_summary
```

Can noi insight:

```text
Du lieu co 12,000 match rows, 2,000 students, 36 majors, 201 courses.
Tiki co 162 sach, Repository co 152 tai lieu.
Confidence high/medium/low cho thay chat luong matching khac nhau.
```

### Phase 4 - Mo Hinh De Xuat AI

Nen chia Phase 4 thanh 2 lop:

```text
4A. Mo hinh chinh: Content-based + Popularity-aware Ranking
4B. Mo rong: Spark ALS Collaborative Filtering
```

Mo hinh chinh can show:

```text
sql/ai_recommendation_workflow.sql
analysis.recommendation_kpis
student_recommendations_top5.csv
top_recommended_resources.csv
```

So lieu:

```text
top5_recommendation_rows = 10,000
students_with_recommendations = 2,000
recommended_resources = 151
avg_recommendation_score = 70.5
```

Spark ALS can show nhu mo rong:

```text
scripts/spark_als_library_recommendation.py
outputs/spark_als/als_input_summary
outputs/spark_als/als_model_metrics
outputs/spark_als/als_top_recommendations
```

So lieu Spark ALS:

```text
interaction_rows = 22,115
users = 2,000
items = 314
prediction_rows = 4,287
RMSE = 4.7891
```

Can noi ro:

```text
Spark ALS dung proxy implicit rating, chua phai rating that cua sinh vien.
```

### Phase 5 - Phan Phoi Ket Qua De Xuat

Phase 5 cua ban hien kha dung. Nen giu:

```text
phase5.distribution_kpis
phase5.availability_status_summary
phase5.web_portal_payload
phase5.demo_student_distribution
```

So lieu:

```text
delivery_rows = 10,000
students = 2,000
resources = 151
print_or_marketplace_items = 5,394
digital_repository_items = 4,606
available_items = 10,000
avg_recommendation_score = 70.5
```

Can sua cach noi:

```text
Trong demo, availability check duoc mo phong bang DuckDB dua tren URL va resource_type.
Trong he thong that, co the thay bang OPAC API, Repository Access Service va API Gateway.
```

## 4. Thu Tu Demo De It Bi Roi

Nen demo theo thu tu:

```text
1. Architecture 5 phase
2. Phase 1: behavior simulation summary
3. Privacy proof: no PII columns
4. Phase 2: data lake rows + partitions
5. Phase 3: analysis KPIs + insights
6. Phase 4: recommendation KPIs + top recommendations
7. Phase 4 extension: Spark ALS output
8. Phase 5: distribution KPIs + web/demo payload
9. Limitations + future work
```

Khong nen demo theo thu tu:

```text
Phase 1 old crawl notebooks
-> DuckDB Data Lake
-> Spark ALS
-> AI workflow
-> Analysis
-> Phase 5
```

Viec nay lam nguoi nghe kho phan biet phase nao lam viec gi.

## 5. File Code Nen Dua Len GitHub

Nen co:

```text
scripts/clean_and_match_datasets.py
scripts/create_privacy_layer.py
scripts/simulate_smart_library_behavior.py
scripts/spark_als_library_recommendation.py
sql/ai_recommendation_workflow.sql
sql/analysis_workflow.sql
sql/phase5_distribution_workflow.sql
reports/
schemas/
requirements_spark_als.txt
README.md
```

Khong nen dua:

```text
.secrets/
__pycache__/
*.crc
node_modules/
.venv/
large output files neu GitHub qua nang
```

Neu can demo output, co the dua sample:

```text
outputs/sample/
```

## 6. Noi Dung Nen Sua Ngay Trong Slide/Doc Hien Tai

### Sua muc 1

Ban cu:

```text
Thu thap du lieu tu digital.lib.ueh.edu.vn, Tiki, mock student
```

Nen sua:

```text
Thu thap va mo phong du lieu hanh vi nguoi dung tu 4 he thong UEH Smart Library:
Sierra, DSpace, EBSCO OneSearch, OpenAthens.
Tiki va UEH Repository duoc dung nhu metadata/catalog tai nguyen bo sung cho demo.
```

### Sua muc 2

Ban cu:

```text
Luu tru phan tan + query major + analysis
```

Nen sua:

```text
Luu tru Data Lake: Parquet + partition theo major.
Chi show row count va partition count.
```

### Sua muc 3

Ban cu:

```text
Phase 3: Xu li phan tan + Spark ALS
```

Nen sua:

```text
Phase 3: OLAP analysis bang DuckDB.
Spark ALS chuyen sang Phase 4.
```

### Sua muc 4

Ban cu:

```text
Dang doi chinh sua phase4: AI recommendation workflow
```

Nen sua:

```text
Phase 4: AI Recommendation
- Content-based + popularity-aware ranking la mo hinh chinh
- Spark ALS la demo mo rong khi co log hanh vi that
```

### Sua muc 5

Ban cu:

```text
real-time, API Gateway Kong
```

Nen sua:

```text
Demo: availability check mo phong bang DuckDB
Future: OPAC API, Repository Access Service, API Gateway Kong
```


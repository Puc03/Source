# Apache Spark + Collaborative Filtering ALS Cho He Thong De Xuat Thu Vien

## 1. Ket Luan Nen Dung Phuong Phap Nao?

Voi bai toan de xuat tai lieu thu vien trong moi truong thuc te, nhom nen chon:

```text
Apache Spark + Collaborative Filtering ALS
```

Tuy nhien, can tach ro:

```text
Demo hien tai:
Content-based Recommendation + Popularity-aware Ranking

Huong phat trien thuc te:
Apache Spark + Collaborative Filtering ALS
```

Ly do:

- Demo hien tai chua co hanh vi that cua sinh vien.
- ALS can du lieu tuong tac user-item, vi du click, muon/tra, download PDF, bookmark, rating.
- Khi co du lieu hanh vi that, ALS phu hop hon content-based vi no hoc tu hanh vi cua nhieu nguoi dung.

## 2. ALS La Gi?

ALS la Alternating Least Squares, mot thuat toan collaborative filtering.

Noi de hieu:

```text
ALS hoc tu hanh vi cua nhieu nguoi dung de doan nguoi dung nao se thich tai nguyen nao.
```

Vi du:

```text
Sinh vien A va sinh vien B cung hay muon sach ve Co so du lieu.
Sinh vien B da muon them sach "Database Systems".
He thong co the goi y "Database Systems" cho sinh vien A.
```

Day la collaborative filtering vi he thong khong chi nhin noi dung sach, ma nhin vao hanh vi cua nhieu sinh vien.

## 3. Vi Sao Spark + ALS Phu Hop Voi Thu Vien?

Thu vien co nhieu loai interaction:

```text
borrow
return
renew
click OPAC
view repository
download PDF
bookmark
rating
search
hold request
```

Khi gom cac interaction nay lai, ta co bang:

```text
student_id / student_token
resource_id
interaction_score
timestamp
```

Bang nay co the rat lon neu thu vien co nhieu nam du lieu. Apache Spark phu hop vi:

- Xu ly du lieu lon theo co che phan tan.
- Doc du lieu tu Data Lake/HDFS/S3.
- Co MLlib ho tro ALS.
- Co the train model tren user-item interaction matrix lon.

Theo tai lieu Apache Spark, `spark.ml` ho tro collaborative filtering bang ALS, trong do user va item duoc bieu dien bang latent factors de du doan cac tuong tac con thieu.

## 4. Du Lieu Can Co De Chay ALS

ALS khong dung truc tiep `tiki_rating_average` lam rating cua sinh vien.

Vi sao?

```text
tiki_rating_average = rating cua nguoi mua tren Tiki
ALS can rating/interaction giua sinh vien va tai nguyen
```

Bang dau vao dung cho ALS nen co dang:

| user_id | item_id | rating |
|---:|---:|---:|
| 101 | 5001 | 4.0 |
| 101 | 5020 | 1.0 |
| 102 | 5001 | 3.0 |
| 103 | 6088 | 5.0 |

Trong thu vien, neu khong co rating that, co the tao implicit feedback score:

| Hanh vi | Diem goi y |
|---|---:|
| click tai lieu | 1 |
| view detail | 2 |
| download PDF | 4 |
| borrow book | 5 |
| renew book | 6 |
| bookmark/favorite | 4 |
| rating 5 sao | 5 |

Vi du:

```text
student_token = stu_abc
resource_id = UEH/63077
interaction_type = download_pdf
rating = 4
```

## 5. Flowchart Huong Phat Trien Voi Spark ALS

```text
Real Student Data
OPAC Borrow/Return Logs
Repository View/Download Logs
Search/Click Logs
Student Ratings
        |
        v
Batch/Streaming Ingestion
Kafka / Airflow
        |
        v
Privacy & Governance Layer
student_token, access control, audit
        |
        v
Distributed Data Lake
HDFS / S3 / MinIO, Parquet
        |
        v
Apache Spark Processing
clean logs, build user-item matrix
        |
        v
Collaborative Filtering ALS
train user factors + item factors
        |
        v
Top-N Recommendations
        |
        v
API Gateway
Web / Mobile / Email / OPAC Widget
        |
        v
Feedback Loop
new click, borrow, download, rating logs
```

## 6. Kien Truc Nen Ghi Trong Report

Nen ghi:

```text
Current Demo Pipeline:
Content-based recommendation vi chua co log hanh vi that.

Future Production Pipeline:
Apache Spark + ALS collaborative filtering khi co interaction logs that.
```

Khong nen ghi:

```text
Demo hien tai da dung ALS
```

Vi du lieu hien tai chua co user-item behavior that.

## 7. Code PySpark Minh Hoa

Day la code minh hoa cho huong phat trien, khong bat buoc chay trong demo hien tai.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

spark = (
    SparkSession.builder
    .appName("UEH-Library-ALS-Recommendation")
    .getOrCreate()
)

# Input example:
# user_id,item_id,rating,timestamp
interactions = spark.read.parquet("s3://ueh-data-lake/curated/user_item_interactions/")

ratings = interactions.select(
    col("user_id").cast("int"),
    col("item_id").cast("int"),
    col("rating").cast("float")
).dropna()

training, test = ratings.randomSplit([0.8, 0.2], seed=42)

als = ALS(
    maxIter=10,
    rank=50,
    regParam=0.1,
    userCol="user_id",
    itemCol="item_id",
    ratingCol="rating",
    implicitPrefs=True,
    coldStartStrategy="drop",
    nonnegative=True
)

model = als.fit(training)

predictions = model.transform(test)

evaluator = RegressionEvaluator(
    metricName="rmse",
    labelCol="rating",
    predictionCol="prediction"
)

rmse = evaluator.evaluate(predictions)
print(f"RMSE = {rmse}")

user_recommendations = model.recommendForAllUsers(10)
user_recommendations.write.mode("overwrite").parquet(
    "s3://ueh-data-lake/recommendations/als_top10/"
)
```

## 8. Neu Chi Co Implicit Feedback

Thu vien thuong khong co rating 1-5 sao. Thuong chi co hanh vi:

```text
click
view
download
borrow
renew
```

Vi vay nen dung:

```python
implicitPrefs=True
```

Trong Spark ALS, `implicitPrefs=True` phu hop khi rating duoc suy ra tu hanh vi, thay vi rating truc tiep do nguoi dung cham diem.

## 9. Hybrid Recommendation Moi La Tot Nhat

Trong thuc te, chi dung ALS van co han che:

- Sinh vien moi chua co log hanh vi.
- Tai lieu moi chua co ai doc/muon.
- ALS khong hieu noi dung tai lieu.

Vi vay kien truc tot nhat la:

```text
Hybrid Recommendation
= ALS Collaborative Filtering
+ Content-based Matching
+ NLP/Embedding Semantic Search
+ Popularity/Quality Signals
```

Vai tro tung phan:

| Thanh phan | Vai tro |
|---|---|
| ALS | Hoc tu hanh vi nguoi dung that |
| Content-based | Xu ly cold-start cho sinh vien/tai lieu moi |
| NLP/Embedding | Hieu ngu nghia title/abstract |
| Popularity signals | Uu tien tai nguyen co chat luong/pho bien |

## 10. Doan Bao Cao De Thay The Phan Huong Phat Trien

> Trong huong phat trien thuc te, nhom de xuat su dung Apache Spark ket hop Collaborative Filtering bang thuat toan ALS. Khac voi pipeline demo hien tai chu yeu dua tren content-based recommendation, ALS can du lieu tuong tac that giua sinh vien va tai nguyen, vi du lich su muon/tra sach, click OPAC, view/download tai lieu Repository, bookmark hoac rating. Khi co cac log hanh vi nay, he thong co the xay dung ma tran user-item va dung Spark MLlib ALS de hoc cac latent factors dai dien cho sinh vien va tai nguyen. Tu do, he thong co the du doan tai nguyen nao phu hop voi tung sinh vien dua tren hanh vi cua nhieu sinh vien co mau quan tam tuong tu.

> Apache Spark phu hop cho kien truc mo rong vi co kha nang xu ly du lieu lon tren moi truong phan tan va ho tro ALS trong MLlib. Voi du lieu thu vien, phan lon tin hieu la implicit feedback nhu click, download, borrow hoac renew, nen mo hinh co the su dung cau hinh implicitPrefs=True. Tuy nhien, ALS cung co han che voi sinh vien moi hoac tai nguyen moi chua co lich su tuong tac. Vi vay, huong phat trien tot nhat la hybrid recommendation, ket hop ALS voi content-based matching, NLP/embedding semantic search va cac tin hieu chat luong/pho bien cua tai nguyen.

## 11. Cau Noi Khi Thuyet Trinh

> Trong demo hien tai, nhom dung content-based recommendation vi chua co log hanh vi that cua sinh vien. Tuy nhien, neu trien khai trong thu vien that, nhom de xuat dung Apache Spark ket hop ALS collaborative filtering. Khi co log muon/tra, click, download va rating, Spark ALS co the hoc tu hanh vi cua nhieu sinh vien de tao de xuat ca nhan hoa tot hon.

## 12. Cau Tra Loi Neu Giang Vien Hoi

### Hoi: Vi sao khong dung ALS trong demo hien tai?

Tra loi:

> ALS can du lieu tuong tac user-item that, vi du sinh vien nao da muon, click, download hoac rating tai lieu nao. Dataset demo hien tai chua co log hanh vi that, nen nhom dung content-based recommendation. ALS duoc de xuat cho pipeline mo rong khi co du lieu thuc te.

### Hoi: Tiki rating co dung lam rating cho ALS duoc khong?

Tra loi:

> Khong nen dung truc tiep. Tiki rating la danh gia cua nguoi mua tren Tiki, khong phai danh gia cua sinh vien voi tai nguyen. Trong demo, Tiki rating duoc dung lam popularity/quality signal. De train ALS, can interaction giua sinh vien va item.

### Hoi: Neu co du lieu muon/tra nhung khong co rating thi sao?

Tra loi:

> Co the dung implicit feedback. Moi hanh vi duoc quy doi thanh diem, vi du click = 1, view = 2, download = 4, borrow = 5, renew = 6. Sau do train ALS voi implicitPrefs=True.


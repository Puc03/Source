# Huong Dan Lam Apache Spark + ALS Bang VSCode

## 1. Muc Tieu

Muc tieu cua phan nay la demo huong phat trien:

```text
Apache Spark + Collaborative Filtering ALS
```

Trong project hien tai, chua co log hanh vi that cua sinh vien. Vi vay script se tao `proxy implicit interactions` tu du lieu analytics da co.

Can ghi ro trong report:

```text
Demo Spark ALS nay dung proxy interaction de minh hoa cach train ALS.
Neu trien khai thuc te, proxy interaction se duoc thay bang log that nhu click, borrow, download, rating.
```

## 2. File Code Da Tao

File chinh:

```text
scripts/spark_als_library_recommendation.py
```

File requirements:

```text
requirements_spark_als.txt
```

Input:

```text
outputs/privacy_layer/student_resource_matches_analytics.csv
```

Output:

```text
outputs/spark_als/
```

## 3. Mo Project Bang VSCode

Mo VSCode.

Chon:

```text
File -> Open Folder
```

Chon thu muc:

```text
C:\Users\Minh Phuc\Documents\Codex\2026-05-27\files-mentioned-by-the-user-tiki
```

Sau khi mo dung, ban se thay cac thu muc:

```text
scripts
sql
outputs
reports
schemas
```

## 4. Mo Terminal Trong VSCode

Trong VSCode chon:

```text
Terminal -> New Terminal
```

Kiem tra terminal dang o dung thu muc:

```powershell
pwd
```

Can thay:

```text
C:\Users\Minh Phuc\Documents\Codex\2026-05-27\files-mentioned-by-the-user-tiki
```

Neu sai thu muc, chay:

```powershell
cd "C:\Users\Minh Phuc\Documents\Codex\2026-05-27\files-mentioned-by-the-user-tiki"
```

## 5. Kiem Tra Python

Chay:

```powershell
python --version
```

Neu may khong nhan `python`, thu:

```powershell
py --version
```

## 6. Tao Virtual Environment

Chay:

```powershell
python -m venv .venv
```

Kich hoat moi truong:

```powershell
.\.venv\Scripts\Activate.ps1
```

Neu PowerShell chan script, chay:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Sau do kich hoat lai:

```powershell
.\.venv\Scripts\Activate.ps1
```

Khi thanh cong, terminal se hien:

```text
(.venv)
```

## 7. Cai PySpark

Chay:

```powershell
python -m pip install -r requirements_spark_als.txt
```

Neu cai thanh cong, kiem tra:

```powershell
python -c "import pyspark; print(pyspark.__version__)"
```

## 8. Kiem Tra Java

Spark can Java.

Chay:

```powershell
java -version
```

Neu chua co Java, cai JDK 17 hoac JDK 11.

Sau khi cai, dong VSCode va mo lai de PATH duoc nhan.

## 9. Chay Spark ALS Script

Chay lenh:

```powershell
python scripts\spark_als_library_recommendation.py
```

Neu muon tuy chinh:

```powershell
python scripts\spark_als_library_recommendation.py --rank 20 --max-iter 10 --reg-param 0.1 --top-k 10
```

Sau khi chay xong, terminal se in:

```text
Spark ALS workflow finished.
Output folder: ...\outputs\spark_als
```

## 10. Kiem Tra Output

Mo thu muc:

```text
outputs/spark_als
```

Ban se thay cac folder CSV:

```text
als_proxy_interactions
als_user_mapping
als_item_mapping
als_input_summary
als_model_metrics
als_top_recommendations
```

Vi Spark xuat CSV thanh folder, moi folder co file `part-....csv`.

## 11. Cac File Can Chup Hinh

Nen mo cac folder sau:

```text
outputs/spark_als/als_input_summary
outputs/spark_als/als_model_metrics
outputs/spark_als/als_top_recommendations
```

Chup:

1. Terminal chay script thanh cong.
2. Thu muc output `outputs/spark_als`.
3. File `als_input_summary`.
4. File `als_model_metrics`.
5. File `als_top_recommendations`.

## 12. Giai Thich Output

### `als_proxy_interactions`

Bang user-item interaction mo phong.

Cac cot:

```text
student_token
resource_id
resource_type
resource_title
user_id
item_id
rating
```

Y nghia:

```text
Moi dong la mot sinh vien tuong tac voi mot tai nguyen.
Trong demo, rating duoc suy ra tu match score, confidence, rating Tiki, luot ban, nam tai lieu, luot xem.
```

### `als_user_mapping`

Map:

```text
student_token -> user_id
```

Spark ALS can user_id dang so nguyen.

### `als_item_mapping`

Map:

```text
resource_id -> item_id
```

Spark ALS can item_id dang so nguyen.

### `als_input_summary`

Tong quan input:

```text
so interaction
so user
so item
rating trung binh
rating nho nhat/lon nhat
```

### `als_model_metrics`

Ket qua danh gia model:

```text
prediction_rows
rmse
```

RMSE cang thap thi du doan cang gan rating.

### `als_top_recommendations`

Ket qua quan trong nhat:

```text
student_token
major
rank
resource_type
resource_id
resource_title
als_score
```

Day la Top-N tai nguyen ma ALS de xuat cho tung sinh vien.

## 13. Doan Bao Cao

> De minh hoa huong phat trien bang Collaborative Filtering, nhom xay dung mot workflow Apache Spark ALS trong VSCode. Do dataset hien tai chua co log hanh vi that cua sinh vien, nhom tao proxy implicit interactions tu bang analytics da duoc an danh. Moi interaction dai dien cho moi quan he giua student_token va tai nguyen, trong do rating duoc suy ra tu match score, confidence va cac tin hieu chat luong/pho bien nhu rating Tiki, luot ban, nam tai lieu va luot xem.

> Sau khi co bang user-item interaction, nhom dung PySpark de map student_token va resource_id thanh cac ID so nguyen, chia du lieu thanh train/test va train mo hinh ALS voi cau hinh implicitPrefs=True. Ket qua dau ra la bang Top-N recommendations cho tung sinh vien. Trong he thong thuc te, proxy interactions se duoc thay the bang log hanh vi that tu OPAC, Repository, LMS hoac Web Portal nhu click, view, download, borrow va rating.

## 14. Cau Noi Khi Demo

> Day la phan mo phong huong phat trien bang Spark ALS. Vi demo hien tai chua co log hanh vi that, nhom tao proxy interaction tu du lieu da match. Trong thuc te, bang nay se duoc thay bang log muon/tra, click, tai PDF hoac rating cua sinh vien. Spark ALS se hoc tu ma tran user-item va tao Top-N recommendation cho tung sinh vien.

## 15. Neu Bi Loi

### Loi khong co Java

Thong bao thuong gap:

```text
Java gateway process exited
```

Cach xu ly:

```text
Cai JDK 17 hoac JDK 11, sau do mo lai VSCode.
```

### Loi PowerShell khong cho activate venv

Chay:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Loi khong thay input CSV

Kiem tra file:

```text
outputs/privacy_layer/student_resource_matches_analytics.csv
```

Neu chua co, chay lai privacy layer.


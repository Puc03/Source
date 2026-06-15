# Huong Dan Dung NLP / Embedding De Cai Thien Matching

## 1. Van De Hien Tai

Trong project hien tai, matching giua mon hoc/nganh hoc va tai nguyen dang dua nhieu vao:

- Tu khoa trong ten mon hoc.
- Tu khoa trong nganh hoc.
- Tu khoa trong tieu de sach Tiki.
- Tu khoa trong tieu de/tom tat tai lieu UEH Repository.
- Diem matching dua tren do trung token.

Cach nay de hieu va phu hop voi demo, nhung co han che:

```text
Neu hai cau co cung y nghia nhung khac tu khoa, he thong co the khong match tot.
```

Vi du:

```text
Mon hoc: Co so du lieu
Tai lieu: Database systems for business applications
```

Neu chi khop tu tieng Viet, he thong co the cham diem thap. Nhung ve mat y nghia, hai noi dung nay rat gan nhau.

## 2. NLP / Embedding La Gi?

### NLP la gi?

NLP la Natural Language Processing, nghia la xu ly ngon ngu tu nhien.

Trong project nay, NLP dung de xu ly:

- Ten mon hoc.
- Nganh hoc.
- Tieu de sach.
- Tieu de tai lieu.
- Tom tat tai lieu.
- Tu khoa tim kiem.

### Embedding la gi?

Embedding la cach bien mot cau/van ban thanh mot day so.

Vi du:

```text
"Co so du lieu" -> [0.12, -0.45, 0.88, ...]
"Database system" -> [0.10, -0.41, 0.83, ...]
```

Neu hai van ban co y nghia gan nhau, vector cua chung se gan nhau.

Noi de hieu:

```text
Embedding = toa do y nghia cua cau trong khong gian so
```

## 3. Vi Sao Embedding Tot Hon Matching Tu Khoa?

Keyword matching chi hoi:

```text
Hai van ban co trung tu nao khong?
```

Embedding matching hoi:

```text
Hai van ban co gan nghia voi nhau khong?
```

Vi du:

| Mon hoc | Tai nguyen | Keyword matching | Embedding matching |
|---|---|---|---|
| Co so du lieu | Database systems | Co the thap | Cao |
| Tri tue nhan tao | Artificial Intelligence | Co the thap | Cao |
| Thuong mai dien tu | E-commerce | Co the thap | Cao |
| Quan tri chuoi cung ung | Supply chain management | Co the thap | Cao |

## 4. Embedding Matching Nam O Dau Trong Pipeline?

Trong pipeline cua nhom:

```text
Raw CSV
-> Cleaning
-> Matching hien tai
-> Privacy Layer
-> Warehouse
-> AI Recommendation
-> Analysis
```

Neu nang cap bang NLP/embedding, no nen nam o buoc:

```text
Cleaning & Matching
```

Pipeline moi:

```text
Raw CSV
-> Text Cleaning
-> NLP Embedding
-> Semantic Matching
-> Privacy Layer
-> Warehouse
-> AI Recommendation
-> Analysis
```

## 5. Y Tuong Thuat Toan

### Dau vao

Tu sinh vien:

```text
major
course
```

Tu Tiki:

```text
tiki_title
tiki_source_keys
author_name
```

Tu UEH Repository:

```text
repo_title
repo_subject
repo_abstract
repo_collection
```

### Tao cau query cho sinh vien

Vi du:

```text
course = "Co so du lieu"
major = "Cong nghe thong tin"
```

Tao text:

```text
"Cong nghe thong tin. Co so du lieu"
```

### Tao text cho tai nguyen

Voi Tiki:

```text
tiki_text = tiki_title + " " + tiki_source_keys
```

Voi UEH Repository:

```text
repo_text = repo_title + " " + repo_subject + " " + repo_abstract
```

### Bien text thanh vector

```text
student/course text -> vector A
resource text -> vector B
```

### Tinh cosine similarity

Cosine similarity cho biet 2 vector gan nhau den muc nao.

```text
gan 1.0  -> rat giong nhau
gan 0.0  -> khong lien quan
gan -1.0 -> trai nguoc
```

### Lay Top-K

Voi moi mon hoc/nganh hoc:

```text
Lay top 3 sach Tiki co semantic_score cao nhat
Lay top 3 tai lieu Repository co semantic_score cao nhat
```

## 6. Cong Thuc Matching Moi

Khong nen bo keyword matching cu. Nen ket hop:

```text
Final Match Score
= 60% Semantic Similarity Score
+ 25% Keyword Match Score
+ 15% Metadata Quality Score
```

Trong do:

```text
Semantic Similarity Score: diem embedding
Keyword Match Score: diem matching hien tai
Metadata Quality Score: rating/luot mua voi Tiki, nam/luot xem voi Repository
```

Vi du voi Tiki:

```text
Final Tiki Score
= 60% Embedding Score
+ 25% Current Tiki Score
+ 10% Rating Score
+ 5% Sales Score
```

Vi du voi Repository:

```text
Final Repo Score
= 65% Embedding Score
+ 25% Current Repo Score
+ 5% Freshness Score
+ 5% Views Score
```

## 7. Cach Lam Don Gian Nhat Cho Nhom Sinh Vien

Co 2 cach:

### Cach 1: TF-IDF + Cosine Similarity

Phu hop neu:

- May yeu.
- Khong muon cai model nang.
- Muon code don gian.
- Muon demo nhanh.

Uu diem:

- Nhe.
- De giai thich.
- Chay nhanh.

Nhuoc diem:

- Van dua nhieu vao tu khoa.
- Hieu ngu nghia chua sau.

### Cach 2: Sentence Embedding

Phu hop neu:

- Muon matching theo ngu nghia tot hon.
- Co the cai them thu vien.
- Co internet de tai model.

Uu diem:

- Hieu cau tot hon.
- Match duoc Viet-Anh gan nghia.
- Chat luong recommendation tot hon.

Nhuoc diem:

- Can tai model.
- Chay cham hon TF-IDF.
- Kho giai thich hon keyword matching.

## 8. Code Minh Hoa Cach 1 - TF-IDF

Code minh hoa:

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

matches = pd.read_csv("outputs/privacy_layer/student_resource_matches_analytics.csv")

course_texts = (
    matches["major"].fillna("") + " " +
    matches["course"].fillna("")
)

tiki_texts = (
    matches["tiki_title"].fillna("") + " " +
    matches["tiki_source_keys"].fillna("")
)

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1
)

all_texts = pd.concat([course_texts, tiki_texts], ignore_index=True)
vectors = vectorizer.fit_transform(all_texts)

course_vectors = vectors[:len(course_texts)]
tiki_vectors = vectors[len(course_texts):]

similarity = cosine_similarity(course_vectors, tiki_vectors)
```

Y nghia:

```text
TF-IDF bien text thanh vector theo tan suat tu.
Cosine similarity tinh do gan nhau giua mon hoc va sach.
```

## 9. Code Minh Hoa Cach 2 - Sentence Embedding

Vi du dung `sentence-transformers`:

```python
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

matches = pd.read_csv("outputs/privacy_layer/student_resource_matches_analytics.csv")

course_texts = (
    matches["major"].fillna("") + ". " +
    matches["course"].fillna("")
).tolist()

tiki_texts = (
    matches["tiki_title"].fillna("") + ". " +
    matches["tiki_source_keys"].fillna("")
).tolist()

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

course_embeddings = model.encode(course_texts, normalize_embeddings=True)
tiki_embeddings = model.encode(tiki_texts, normalize_embeddings=True)

similarity = cosine_similarity(course_embeddings, tiki_embeddings)
```

Y nghia:

```text
Model doc cau va bien moi cau thanh vector ngu nghia.
Hai cau gan nghia se co cosine similarity cao.
```

## 10. Ap Dung Vao Project Hien Tai

Neu nang cap project, nen tao them file:

```text
scripts/embedding_match_resources.py
```

File nay se:

```text
1. Doc outputs/privacy_layer/student_resource_matches_analytics.csv.
2. Tao text cho course/major.
3. Tao text cho Tiki resource.
4. Tao text cho Repository resource.
5. Tinh embedding similarity.
6. Ket hop voi score hien tai.
7. Xuat file semantic_student_resource_matches.csv.
```

Output de xuat:

```text
outputs/semantic_matching/semantic_student_resource_matches.csv
outputs/semantic_matching/semantic_match_summary.csv
```

Cac cot nen co:

```text
student_token
major
course
resource_type
resource_id
resource_title
keyword_score
semantic_score
metadata_score
final_match_score
rank
```

## 11. Cach Dua Vao Bao Cao

Neu nhom chua code that, dua vao muc "Huong phat trien":

> Trong tuong lai, nhom co the nang cap buoc matching bang NLP va embedding. Thay vi chi so khop tu khoa giua mon hoc va tieu de tai nguyen, he thong se bien mon hoc, nganh hoc va metadata tai nguyen thanh cac vector ngu nghia. Sau do, cosine similarity duoc su dung de do muc do gan nghia giua mon hoc va tai nguyen. Cach tiep can nay giup he thong phat hien cac tai nguyen lien quan ngay ca khi chung khong trung tu khoa truc tiep, vi du "Co so du lieu" va "Database systems" hoac "Tri tue nhan tao" va "Artificial Intelligence".

Neu nhom co code demo, dua vao muc "Model Improvement":

> Nhom de xuat mo rong cong thuc matching bang cach ket hop semantic similarity score voi keyword matching score va metadata quality score. Diem matching cuoi cung duoc tinh theo cong thuc: Final Match Score = 60% Semantic Similarity Score + 25% Keyword Match Score + 15% Metadata Quality Score. Cach ket hop nay giu duoc kha nang giai thich cua keyword matching, dong thoi cai thien kha nang hieu ngu nghia cua he thong.

## 12. Hinh Nen Dua Vao Report

Nen ve so do:

```text
Course + Major Text
        |
        v
Text Embedding Model
        |
        v
Course Vector

Resource Title + Metadata
        |
        v
Text Embedding Model
        |
        v
Resource Vector

Course Vector + Resource Vector
        |
        v
Cosine Similarity
        |
        v
Semantic Match Score
        |
        v
Final Recommendation Score
```

## 13. Cau Tra Loi Khi Giang Vien Hoi

### Hoi: Vi sao can embedding?

Tra loi:

> Vi keyword matching chi phat hien cac tu trung nhau, trong khi embedding co the do muc do gan nghia giua hai van ban. Nhờ đó hệ thống có thể match được các tài liệu liên quan dù tiêu đề không chứa đúng từ khóa của môn học.

### Hoi: Embedding co thay the matching hien tai khong?

Tra loi:

> Không nên thay thế hoàn toàn. Nhóm nên kết hợp embedding với keyword score và metadata score để vừa hiểu ngữ nghĩa tốt hơn, vừa giữ được khả năng giải thích kết quả.

### Hoi: Neu du lieu song ngu Viet-Anh thi sao?

Tra loi:

> Có thể dùng multilingual sentence embedding để đưa cả tiếng Việt và tiếng Anh vào cùng một không gian vector. Khi đó "Trí tuệ nhân tạo" và "Artificial Intelligence" vẫn có thể có độ tương đồng cao.


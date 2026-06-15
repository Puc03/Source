# Insight Guide - UEH Tiki Big Data Recommendation Project

## 1. Insight La Gi?

Insight khong phai la viec chi chup bang ket qua. Insight la viec nhin vao ket qua phan tich va tra loi:

- Du lieu cho thay dieu gi?
- Tai sao ket qua nay quan trong?
- No giup cai thien he thong recommendation nhu the nao?
- Neu trien khai that, nha truong/thu vien/sinh vien se dung ket qua nay de lam gi?

Vi du:

Ket qua query:

```text
Nganh Cong nghe thong tin co nhieu match.
```

Insight tot hon:

```text
Nganh Cong nghe thong tin co nhieu match vi nguon sach Tiki va tai lieu Repository co nhieu tieu de lien quan den lap trinh, co so du lieu, mang may tinh va AI. Dieu nay cho thay he thong co do phu tai nguyen tot hon voi cac nganh cong nghe, nhung can bo sung tai nguyen cho cac nganh co it match.
```

## 2. Thu Tu Lam Buoc Insight

Nen lam theo thu tu:

```text
1. Dataset overview insight
2. Major/course coverage insight
3. Matching quality insight
4. Tiki commerce signal insight
5. Repository insight
6. Recommendation result insight
7. Phase 5 distribution insight
8. Limitation and improvement insight
```

## 3. Insight 1 - Dataset Overview

### Query Can Chay

```sql
SELECT * FROM analysis.overview_kpis;
```

### Can Nhin Vao

- Tong so dong match.
- So sinh vien.
- So nganh.
- So mon hoc.
- So sach Tiki.
- So tai lieu UEH Repository.
- Diem match trung binh.

### Cau Hoi Can Tra Loi

- Dataset sau xu ly co du lon khong?
- Du lieu co den tu nhieu nguon khong?
- Bang fact co du de phan tich va recommendation khong?

### Mau Insight

> Ket qua tong quan cho thay pipeline da tao duoc bang fact co cau truc ro rang, ket hop du lieu sinh vien, mon hoc, sach Tiki va tai lieu UEH Repository. Viec co nhieu nganh, nhieu mon hoc va nhieu tai nguyen cho thay dataset co do phu tot de thuc hien phan tich va xay dung mo hinh de xuat. Bang fact nay la nen tang cho cac buoc recommendation va distribution o phia sau.

## 4. Insight 2 - Major / Course Coverage

### Query Can Chay

```sql
SELECT *
FROM analysis.major_match_summary
LIMIT 10;
```

```sql
SELECT *
FROM analysis.course_match_summary
LIMIT 10;
```

### Can Nhin Vao

- Nganh nao co nhieu match nhat.
- Nganh nao co nhieu sinh vien.
- Nganh nao co diem Tiki/Repository trung binh cao.
- Mon hoc nao co nhieu tai nguyen phu hop.

### Cau Hoi Can Tra Loi

- Nguon tai nguyen phu hop tot nhat voi nhom nganh nao?
- Nganh nao co the bi thieu tai nguyen?
- Co su lech giua cac nganh khong?

### Mau Insight

> Mot so nganh co so luong match cao hon cac nganh khac, cho thay nguon tai nguyen tren Tiki va UEH Repository phu hop hon voi cac nganh nay. Cac nganh lien quan den cong nghe, kinh doanh, tai chinh va logistics thuong co nhieu tai nguyen de matching. Nguoc lai, cac nganh co it match co the can duoc bo sung them sach, giao trinh hoac tai lieu Repository de tang do phu cua he thong de xuat.

## 5. Insight 3 - Matching Quality

### Query Can Chay

```sql
SELECT * FROM analysis.tiki_confidence_summary;
```

```sql
SELECT * FROM analysis.repo_confidence_summary;
```

### Can Nhin Vao

- Ty le high / medium / low.
- Diem trung binh cua tung muc confidence.
- Ben Tiki hay Repository co chat luong matching tot hon.

### Cau Hoi Can Tra Loi

- He thong matching co dang tin cay khong?
- Ty le low co cao khong?
- Neu co nhieu low thi can cai thien gi?

### Mau Insight

> Phan bo confidence giup danh gia chat luong matching cua he thong. Cac match co confidence high thuong co diem trung binh cao hon, cho thay cong thuc matching co kha nang phan biet tai nguyen phu hop va it phu hop. Tuy nhien, neu ty le low van con dang ke, day la dau hieu can bo sung them tu khoa, mo rong tap tai nguyen hoac cai thien thuat toan matching trong cac phien ban sau.

## 6. Insight 4 - Tiki Commerce Signal

### Query Can Chay

```sql
SELECT * FROM analysis.tiki_commerce_summary;
```

```sql
SELECT
    tiki_title,
    matched_times,
    avg_tiki_score,
    avg_rating,
    avg_review_count,
    avg_quantity_sold
FROM analysis.top_tiki_books_by_match
LIMIT 10;
```

### Can Nhin Vao

- Rating trung binh.
- Review count.
- Quantity sold.
- Nhung sach nao duoc match nhieu.
- Sach co match cao co rating/luot mua tot khong.

### Cau Hoi Can Tra Loi

- Tiki signal co giup de xuat tot hon khong?
- Sach pho bien co duoc uu tien khong?
- Co sach match cao nhung rating thap khong?

### Mau Insight

> Cac chi so thuong mai tu Tiki nhu rating trung binh, so luot danh gia va so luong da ban giup bo sung goc nhin ve chat luong va do pho bien cua tai nguyen. Neu chi dua tren noi dung, he thong co the de xuat tai nguyen phu hop ve tu khoa nhung chua chac co chat luong tot. Khi ket hop them rating va luot mua, mo hinh co the uu tien nhung sach vua lien quan den mon hoc vua duoc thi truong danh gia tich cuc.

## 7. Insight 5 - UEH Repository Signal

### Query Can Chay

```sql
SELECT
    repo_title,
    repo_year,
    repo_collection,
    matched_times,
    avg_repo_score,
    avg_views
FROM analysis.top_repo_documents_by_match
LIMIT 10;
```

### Can Nhin Vao

- Tai lieu nao duoc match nhieu.
- Nam xuat ban.
- Bo suu tap.
- Luot xem.
- Diem repo trung binh.

### Cau Hoi Can Tra Loi

- Repository co bo sung tai lieu hoc thuat tot khong?
- Tai lieu moi hay cu duoc de xuat nhieu?
- Cac bo suu tap nao co gia tri cho recommendation?

### Mau Insight

> UEH Repository bo sung nguon tai lieu hoc thuat cho he thong, dac biet phu hop voi cac mon can luan van, nghien cuu hoac tai lieu chuyen sau. Nam xuat ban va luot xem giup mo hinh danh gia them do moi va muc do quan tam cua tai lieu. Dieu nay giup can bang giua sach thuong mai tu Tiki va tai lieu hoc thuat noi bo cua nha truong.

## 8. Insight 6 - AI Recommendation Result

### Query Can Chay

```sql
SELECT * FROM analysis.recommendation_kpis;
```

```sql
SELECT * FROM analysis.recommendation_by_resource_type;
```

```sql
SELECT
    resource_type,
    LEFT(resource_title, 90) AS resource_title,
    recommended_times,
    students,
    avg_recommendation_score,
    avg_quality_score,
    avg_popularity_score
FROM analysis.top_recommended_resources
LIMIT 10;
```

### Can Nhin Vao

- Tong so recommendation.
- Bao nhieu sinh vien co recommendation.
- Tiki book hay Repository duoc de xuat nhieu hon.
- Tai nguyen nao nam trong top recommended.
- Diem recommendation trung binh.

### Cau Hoi Can Tra Loi

- Mo hinh co tao duoc de xuat cho phan lon sinh vien khong?
- Loai tai nguyen nao dong vai tro chinh?
- Top recommended resources co hop ly khong?

### Mau Insight

> Ket qua recommendation cho thay he thong co the tao danh sach Top-N tai nguyen cho sinh vien dua tren nganh hoc, mon hoc va cac tin hieu chat luong cua tai nguyen. Viec phan tich theo resource_type giup nhom so sanh vai tro cua sach Tiki va tai lieu UEH Repository. Cac tai nguyen duoc de xuat nhieu nhat thuong co diem matching tot, confidence cao va chi so chat luong/pho bien tich cuc.

## 9. Insight 7 - Phase 5 Distribution

### Query Can Chay

```sql
SELECT * FROM phase5.distribution_kpis;
```

```sql
SELECT * FROM phase5.availability_status_summary;
```

```sql
SELECT * FROM phase5.demo_student_distribution;
```

### Can Nhin Vao

- Bao nhieu recommendation san sang phan phoi.
- Bao nhieu tai nguyen co link Tiki hoac Repository.
- Hanh dong tiep theo la gi.
- Web/email/OPAC payload co du dung de demo khong.

### Cau Hoi Can Tra Loi

- Ket qua AI co the dua den nguoi dung nhu the nao?
- Tai nguyen digital va print/marketplace duoc xu ly khac nhau ra sao?
- Neu trien khai that can API nao?

### Mau Insight

> Phase 5 cho thay ket qua recommendation khong chi dung lai o bang diem, ma da duoc chuan bi de phan phoi den nguoi dung. He thong phan biet tai nguyen Tiki/ban in va tai lieu so Repository, gan trang thai kha dung, hanh dong tiep theo va kenh phan phoi. Trong he thong thuc te, phan check availability co the ket noi voi OPAC API va Repository Access Service de cap nhat trang thai theo thoi gian thuc.

## 10. Insight 8 - Limitation And Improvement

### Can Nhin Vao

- Du lieu sinh vien co phai mo phong khong.
- Co lich su click/muon-tra that khong.
- Data lake co phai local simulation khong.
- OPAC/API co phai mo phong khong.

### Mau Insight

> Han che lon nhat cua he thong hien tai la chua co du lieu hanh vi that cua sinh vien nhu click, muon/tra, thoi gian doc hoac danh gia ca nhan. Vi vay, mo hinh hien tai phu hop voi content-based recommendation hon la collaborative filtering. Ngoai ra, data lake va availability check dang duoc mo phong cuc bo, chua ket noi voi HDFS/S3, OPAC API hoac Repository Access Service that. Trong tuong lai, he thong co the mo rong bang cach bo sung log hanh vi nguoi dung, su dung Spark cho xu ly lon va trien khai API Gateway de phan phoi de xuat theo thoi gian thuc.

## 11. Bang Tong Hop Insight Nen Dua Vao Report

| Insight | Bang/Query | Nen hien thi bang/charts | Ket luan can viet |
|---|---|---|---|
| Dataset overview | `analysis.overview_kpis` | Bang KPI | Dataset du de phan tich va recommendation |
| Coverage theo nganh | `analysis.major_match_summary` | Bar chart top 10 | Nganh nao co nhieu tai nguyen phu hop |
| Matching quality | `analysis.tiki_confidence_summary`, `analysis.repo_confidence_summary` | Bar chart high/medium/low | Chat luong matching co the danh gia duoc |
| Tiki commerce | `analysis.tiki_commerce_summary` | Bang KPI | Rating/luot mua giup xep hang tot hon |
| Top resources | `analysis.top_recommended_resources` | Bang top 10 | Tai nguyen nao duoc de xuat nhieu nhat |
| Distribution | `phase5.demo_student_distribution` | Bang demo 1 sinh vien | Ket qua AI co the dua den nguoi dung |

## 12. Cau Chot Cho Phan Insight

> Cac insight thu duoc cho thay pipeline cua nhom khong chi xu ly du lieu va tao recommendation, ma con ho tro danh gia chat luong tai nguyen, do phu theo nganh hoc va kha nang phan phoi ket qua den sinh vien. He thong hien tai da dap ung muc tieu de xuat tai nguyen hoc tap dua tren noi dung va cac tin hieu chat luong/pho bien, dong thoi co kha nang mo rong sang kien truc Big Data thuc te trong tuong lai.


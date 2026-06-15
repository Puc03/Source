# 1. Thu Thap Du Lieu

## 1.1 Bo Du Lieu Lay Tu Dau?

Nhom su dung 3 nguon du lieu:

| Nguon | File trong du an | Vai tro trong bai toan |
|---|---|---|
| UEH Digital Repository | `ueh_repository_raw.csv` | Lay metadata tai lieu hoc thuat cua UEH nhu title, author, year, collection, views, URL |
| Tiki.vn | `tiki_books (2).csv` | Lay metadata sach nhu ten sach, gia, rating, review count, luot ban, keyword, URL |
| Mock student data | `mock_ueh_students_2000.csv` | Tao ho so sinh vien mo phong gom ma sinh vien, ten, gioi tinh, nganh, khoa, mon hoc |

Nguon tham khao:

- UEH Digital Repository: https://digital.lib.ueh.edu.vn/
- Tiki: https://tiki.vn/
- Tiki Open API docs: https://open.tiki.vn/docs/docs/current/getting-started/overview/

## 1.2 Tai Sao Chon 2 Nguon Digital Repository Va Tiki?

### UEH Digital Repository

UEH Digital Repository la kho tai lieu hoc thuat cua truong. Nguon nay phu hop voi bai toan goi y tai nguyen hoc tap vi co cac tai lieu nhu:

- Luan van.
- De tai nghien cuu.
- Giao trinh.
- Tai lieu hoc thuat.
- Bo suu tap theo chu de.

Metadata quan trong lay duoc:

```text
title
author
year
collection
subject
views
url
doc_id
```

Nhung truong nay giup he thong matching tai lieu voi nganh hoc va mon hoc cua sinh vien.

### Tiki.vn

Tiki la san thuong mai dien tu co nhieu sach giao trinh, sach chuyen nganh va sach tham khao. Nhom dung Tiki de bo sung nguon sach ngoai thu vien.

Metadata quan trong lay duoc:

```text
name
author_name
brand_name
price
original_price
rating_average
review_count
quantity_sold_value
inventory_status
source_key
url_path
```

Tiki dac biet huu ich vi co cac tin hieu thuong mai:

- Rating trung binh.
- So luot danh gia.
- So luong da ban.
- Gia ban.
- Tu khoa tim kiem.

Nhung tin hieu nay giup mo hinh recommendation khong chi dua tren noi dung, ma con dua tren chat luong va do pho bien cua sach.

## 1.3 Cach Crawl Du Lieu Tu Dau?

Trong pham vi project, nhom luu ket qua thu thap thanh 3 file CSV. Viec crawl co the mo ta theo 2 huong:

1. Crawl metadata cong khai tu website/API.
2. Luu ket qua crawl thanh file CSV de xu ly offline.

### 1.3.1 Crawl UEH Digital Repository

UEH Digital Repository chay tren nen tang DSpace/DSpace-CRIS. Day la he thong repository hoc thuat pho bien, co ho tro cac API va trang metadata cong khai.

Quy trinh thu thap:

```text
1. Gui request den trang search/browse cua Digital Repository.
2. Lay danh sach tai lieu theo tung trang.
3. Voi moi tai lieu, lay metadata nhu title, author, year, collection, subject, views, url.
4. Chuan hoa thanh bang CSV.
5. Luu vao ueh_repository_raw.csv.
```

Minh hoa code Python:

```python
import time
import requests
import pandas as pd

BASE_URL = "https://digital.lib.ueh.edu.vn"

def crawl_ueh_repository(keywords, max_pages=5):
    records = []

    for keyword in keywords:
        for page in range(max_pages):
            # Endpoint minh hoa. Khi crawl that, nhom co the lay endpoint
            # tu Network tab hoac REST API cong khai cua DSpace.
            url = f"{BASE_URL}/search"
            params = {
                "query": keyword,
                "page": page
            }

            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()

            # Trong project, buoc parse HTML/API JSON se trich ra cac truong can thiet.
            # Vi du:
            # title, author, year, collection, views, url, subject

            time.sleep(1)

    return pd.DataFrame(records)
```

Luu y khi viet report:

> Nhom chi thu thap metadata cong khai cua tai lieu, khong thu thap file PDF bi han che quyen truy cap va khong thu thap thong tin ca nhan nguoi dung.

### 1.3.2 Crawl Tiki

Tiki co cac trang san pham va API tra ve du lieu dang JSON cho thong tin san pham. Tai lieu Open API cua Tiki mo ta endpoint API theo dang `https://api.tiki.vn/integration/{version}/{resources}` cho cac ung dung tich hop. Voi muc tieu hoc tap, nhom thu thap metadata san pham cong khai phuc vu phan tich.

Quy trinh thu thap:

```text
1. Tao danh sach keyword theo nganh hoc/mon hoc.
2. Tim kiem sach tren Tiki theo tung keyword.
3. Lay metadata san pham: ten sach, tac gia, gia, rating, review count, luot ban, URL.
4. Ghi lai keyword da dung de tim kiem vao source_key.
5. Luu ket qua thanh tiki_books (2).csv.
```

Minh hoa code Python:

```python
import time
import requests
import pandas as pd

def crawl_tiki_books(keywords, max_pages=3):
    records = []

    for keyword in keywords:
        for page in range(1, max_pages + 1):
            # Endpoint minh hoa cho du lieu tim kiem cong khai dang JSON.
            # Khi chay that, can kiem tra endpoint hien tai bang Network tab
            # va tuan thu robots.txt / dieu khoan su dung cua website.
            url = "https://tiki.vn/api/v2/products"
            params = {
                "q": keyword,
                "page": page,
                "limit": 40
            }

            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": "student-research-demo/1.0"},
                timeout=20
            )
            response.raise_for_status()

            data = response.json()
            for item in data.get("data", []):
                records.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "original_price": item.get("original_price"),
                    "rating_average": item.get("rating_average"),
                    "review_count": item.get("review_count"),
                    "quantity_sold_value": (
                        item.get("quantity_sold") or {}
                    ).get("value"),
                    "url_path": item.get("url_path"),
                    "source_key": keyword
                })

            time.sleep(1)

    return pd.DataFrame(records)
```

Luu y:

> Khi thu thap du lieu tu san thuong mai dien tu, nhom chi dung metadata cong khai cua san pham, dat toc do request thap, khong thu thap thong tin nguoi mua va khong su dung du lieu dang nhap rieng tu.

## 1.4 Mock Du Lieu Sinh Vien Nhu The Nao?

Vi du lieu sinh vien that la du lieu nhay cam, nhom khong su dung thong tin sinh vien UEH that. Thay vao do, nhom tao dataset mo phong gom 2.000 sinh vien.

File:

```text
mock_ueh_students_2000.csv
```

Cac cot:

```text
user_id
ma_sv
ho_ten
gioi_tinh
nganh
khoa_nhap_hoc
mon_hoc
```

Nguyen tac mock:

```text
1. Tao user_id tang dan.
2. Tao ma_sv gia lap theo dinh dang gan giong ma sinh vien.
3. Tao ho_ten gia lap bang ten tieng Viet pho bien.
4. Gan gioi tinh ngau nhien.
5. Gan nganh hoc tu danh sach nganh UEH mo phong.
6. Gan khoa nhap hoc, vi du K23/K24.
7. Gan danh sach mon hoc phu hop voi tung nganh.
```

Muc dich cua mock data:

- Bao ve quyen rieng tu.
- Khong lam lo thong tin sinh vien that.
- Van giu duoc cau truc gan voi bai toan thuc te.
- Cho phep matching sinh vien voi mon hoc va tai nguyen.

Doan viet report:

> Do du lieu sinh vien that co tinh nhay cam, nhom su dung bo du lieu sinh vien mo phong gom 2.000 ban ghi. Dataset nay duoc thiet ke de co cau truc gan voi du lieu sinh vien thuc te, bao gom ma sinh vien gia lap, ten gia lap, gioi tinh, nganh hoc, khoa nhap hoc va danh sach mon hoc. Cach lam nay giup nhom xay dung va kiem thu pipeline recommendation ma khong lam lo thong tin ca nhan.

## 1.5 Dung Luong File Va So Ban Ghi

Thong ke file raw:

| File | So dong gom header | So ban ghi du lieu | Dung luong |
|---|---:|---:|---:|
| `tiki_books (2).csv` | 9,475 | 9,474 | 2,534,014 bytes, khoang 2.53 MB |
| `mock_ueh_students_2000.csv` | 2,001 | 2,000 | 535,984 bytes, khoang 0.54 MB |
| `ueh_repository_raw.csv` | 2,059 | 2,058 | 1,886,108 bytes, khoang 1.89 MB |

Tong raw data:

```text
13,532 ban ghi du lieu
khoang 4.96 MB CSV
```

Day la kich thuoc phu hop cho demo local bang DuckDB, nhung van du de minh hoa pipeline Big Data gom nhieu nguon, nhieu kieu metadata va nhieu buoc xu ly.

## 1.6 File Lay Tu San TMĐT De Lam Gi? Tai Sao Goi La Proxy Data?

Trong bai toan recommendation, ly tuong nhat la co du lieu hanh vi that cua sinh vien:

```text
sinh vien click tai lieu nao
sinh vien muon sach nao
sinh vien doc bao lau
sinh vien danh gia tai lieu may sao
```

Nhung nhom khong co log hanh vi that cua sinh vien. Vi vay, nhom dung du lieu tu Tiki lam proxy data.

Proxy data nghia la:

```text
Du lieu thay the, dai dien gan dung cho mot tin hieu ma minh chua co.
```

Trong project:

| Tin hieu that muon co | Nhom chua co | Proxy tu Tiki |
|---|---|---|
| Sinh vien danh gia sach | Khong co rating cua sinh vien | `rating_average` tren Tiki |
| Sinh vien quan tam sach | Khong co click/view cua sinh vien | `review_count`, `quantity_sold_value` |
| Sach co pho bien khong | Khong co lich su muon/tra | Luot ban va luot danh gia |
| Sach co lien quan den mon hoc khong | Can matching noi dung | `name`, `source_key`, `author_name` |

Doan viet report:

> Du lieu Tiki duoc su dung nhu proxy data cho cac tin hieu chat luong va do pho bien cua sach. Do nhom khong co du lieu hanh vi thuc te cua sinh vien nhu click, muon/tra hay rating ca nhan, cac chi so nhu rating trung binh, so luot danh gia va so luong da ban tren Tiki duoc dung de dai dien cho muc do tin cay, chat luong va do quan tam cua thi truong doi voi tung cuon sach. Nhung tin hieu nay giup mo hinh de xuat uu tien cac tai nguyen vua phu hop ve noi dung vua co muc do pho bien cao.

## 1.7 Code Xu Ly Sau Khi Thu Thap

Sau khi co 3 file raw CSV, code xu ly chinh cua nhom la:

```text
scripts/clean_and_match_datasets.py
```

Vai tro:

```text
1. Doc 3 file raw CSV.
2. Chuan hoa text tieng Viet.
3. Chuan hoa nganh hoc va mon hoc.
4. Lam sach metadata Tiki.
5. Lam sach metadata UEH Repository.
6. Matching mon hoc/nganh hoc voi sach Tiki.
7. Matching mon hoc/nganh hoc voi tai lieu UEH Repository.
8. Tao score va confidence.
9. Xuat cleaned/matched dataset.
```

Lenh chay:

```powershell
python scripts/clean_and_match_datasets.py
```

Output:

```text
outputs/cleaned_matching/tiki_books_clean.csv
outputs/cleaned_matching/ueh_students_clean.csv
outputs/cleaned_matching/ueh_student_courses_clean.csv
outputs/cleaned_matching/ueh_repository_clean.csv
outputs/cleaned_matching/course_resource_matches.csv
outputs/cleaned_matching/student_resource_matches.csv
```

## 1.8 Doan Bao Cao Hoan Chinh Cho Muc Thu Thap Du Lieu

> Du lieu dau vao cua de tai duoc tong hop tu ba nguon chinh: UEH Digital Repository, san thuong mai dien tu Tiki va bo du lieu sinh vien mo phong. UEH Digital Repository cung cap metadata tai lieu hoc thuat nhu tieu de, tac gia, nam xuat ban, bo suu tap, chu de, luot xem va URL. Tiki cung cap metadata sach nhu ten sach, tac gia, gia ban, rating trung binh, so luot danh gia, so luong da ban, tu khoa tim kiem va duong dan san pham. Do du lieu sinh vien that co tinh nhay cam, nhom tao bo du lieu mo phong gom 2.000 sinh vien voi cac truong nhu ma sinh vien gia lap, ho ten gia lap, gioi tinh, nganh hoc, khoa nhap hoc va danh sach mon hoc.

> Qua trinh thu thap du lieu duoc thuc hien theo huong crawl metadata cong khai va luu thanh file CSV de xu ly offline. Voi UEH Digital Repository, nhom thu thap metadata tai lieu tu cac trang search/browse cua he thong repository. Voi Tiki, nhom thu thap metadata sach tu ket qua tim kiem va thong tin san pham dang JSON, chi su dung cac thong tin cong khai va khong thu thap du lieu ca nhan nguoi dung. Sau khi thu thap, ba file raw duoc dua vao script lam sach va matching de tao ra bang du lieu phuc vu privacy layer, warehouse, recommendation va analysis.

> Du lieu Tiki dong vai tro proxy data cho cac tin hieu chat luong va do pho bien cua sach. Trong truong hop chua co du lieu hanh vi thuc te cua sinh vien nhu click, muon/tra hay danh gia ca nhan, cac chi so nhu rating trung binh, so luot danh gia va so luong da ban tren Tiki giup mo hinh uoc luong muc do huu ich va pho bien cua tung cuon sach. Nho do, he thong de xuat khong chi dua tren do khop noi dung voi mon hoc/nganh hoc, ma con co the uu tien cac tai nguyen co chat luong va do tin cay cao hon.


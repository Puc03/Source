# Phase 5 - Phan Phoi De Xuat

## 1. Muc Tieu

Phase 5 la buoc dua ket qua recommendation den nguoi dung cuoi. Sau khi mo hinh AI da tao Top-N tai nguyen cho moi sinh vien, he thong can kiem tra tai nguyen co san hay khong, sinh vien co quyen truy cap hay khong, sau do phan phoi qua cac kenh nhu web portal, mobile app, email digest hoac OPAC terminal widget.

## 2. Vi Tri Trong Pipeline

```text
Raw Data
-> Cleaning & Matching
-> Privacy Layer
-> Data Warehouse
-> Data Lake
-> AI Recommendation
-> Phase 5: Recommendation Distribution
```

## 3. Logic Phase 5

### 3.1 Kiem Tra Tinh San Co

Trong he thong thuc te, buoc nay se goi:

- OPAC circulation API de kiem tra ban in con/het.
- Repository access service de kiem tra quyen truy cap tai lieu so.

Trong demo cua nhom, buoc nay duoc mo phong bang DuckDB:

- Sach Tiki co link san pham duoc xem la co the truy cap qua marketplace link.
- Tai lieu UEH Repository co repo_url duoc xem la co quyen truy cap digital.
- Thoi diem kiem tra duoc ghi lai bang availability_checked_at.

### 3.2 Nhom Tai Nguyen

| Resource Type | Delivery Type | Action |
|---|---|---|
| tiki_book | print_collection_or_marketplace | place_hold_or_open_tiki_link |
| ueh_repository | digital_repository | open_repository_link |

### 3.3 Kenh Phan Phoi

Ket qua de xuat co the duoc dua den sinh vien qua:

- Mobile app
- Web portal
- Email digest
- OPAC terminal widget

## 4. SQL Workflow

Chay trong DuckDB:

```sql
.read 'C:/Users/Minh Phuc/Documents/Codex/2026-05-27/files-mentioned-by-the-user-tiki/sql/phase5_distribution_workflow.sql'
```

Workflow se tao schema:

```text
phase5
```

Va cac bang/view:

```text
phase5.distribution_ready_recommendations
phase5.distribution_kpis
phase5.availability_status_summary
phase5.web_portal_payload
phase5.email_digest_payload
phase5.opac_terminal_widget_payload
phase5.demo_student_distribution
```

## 5. Ket Qua Can Hien Thi

### 5.1 KPI Phan Phoi

```sql
SELECT * FROM phase5.distribution_kpis;
```

Dung de cho thay:

- So dong de xuat san sang phan phoi.
- So sinh vien nhan duoc de xuat.
- So tai nguyen duoc phan phoi.
- So tai nguyen digital.
- So tai nguyen print/marketplace.

### 5.2 Kiem Tra Tinh San Co

```sql
SELECT * FROM phase5.availability_status_summary;
```

Dung de cho thay tai nguyen nao:

- Co link Tiki.
- Co quyen truy cap Repository.
- Can kiem tra thu cong.

### 5.3 Payload Cho Web Portal

```sql
SELECT *
FROM phase5.web_portal_payload
LIMIT 20;
```

Bang nay mo phong du lieu tra ve cho giao dien web/mobile.

### 5.4 Payload Cho Email Digest

```sql
SELECT *
FROM phase5.email_digest_payload
LIMIT 20;
```

Bang nay mo phong noi dung email goi y hang ngay/hang tuan.

### 5.5 Demo Mot Sinh Vien Cu The

```sql
SELECT *
FROM phase5.demo_student_distribution;
```

Bang nay nen dung khi demo truoc lop vi de giai thich:

> Voi mot sinh vien cu the, he thong de xuat nhung tai nguyen nao, diem bao nhieu, co san hay khong va hanh dong tiep theo la gi.

## 6. Doan Bao Cao Mau

> O Phase 5, nhom mo phong buoc phan phoi ket qua de xuat den nguoi dung cuoi. Sau khi mo hinh AI tao danh sach Top-N tai nguyen cho tung sinh vien, he thong thuc hien kiem tra tinh san co cua tai nguyen. Doi voi ban in hoac sach tren Tiki, he thong chuan bi thong tin ma OPAC mo phong, vi tri ke va hanh dong dat muon/mo lien ket Tiki. Doi voi tai lieu so tu UEH Repository, he thong kiem tra duong dan truy cap va quyen truy cap cua sinh vien. Ket qua sau do duoc chuan bi thanh cac payload rieng cho web portal, mobile app, email digest va OPAC terminal widget.

> Trong pham vi demo, nhom chua ket noi truc tiep den OPAC circulation API hay he thong phan quyen digital thuc te. Thay vao do, nhom mo phong buoc real-time availability check bang DuckDB dua tren cac truong resource_url va loai tai nguyen. Cach thiet ke nay cho thay pipeline co the mo rong sang he thong thuc te bang cach thay the logic mo phong bang API call den OPAC va Repository access service.

## 7. Anh Can Chup Cho Report

Nen chup cac man hinh sau:

1. Query tao phase5 distribution workflow.
2. Ket qua phase5.distribution_kpis.
3. Ket qua phase5.availability_status_summary.
4. Ket qua phase5.web_portal_payload.
5. Ket qua phase5.demo_student_distribution.


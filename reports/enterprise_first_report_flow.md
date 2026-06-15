# Định Hướng Sửa Báo Cáo Theo Flow Mới

## 1. Tư Duy Trình Bày Mới

Nhóm sẽ không trình bày theo hướng “chúng em đã làm file CSV, DuckDB, Power BI” ngay từ đầu. Thay vào đó, báo cáo nên đi theo thứ tự:

1. Mô tả hệ thống đề xuất tài liệu thư viện ở phạm vi doanh nghiệp.
2. Trình bày kiến trúc Big Data đầy đủ nếu triển khai thật cho UEH Smart Library.
3. Sau đó mới giải thích bản demo của nhóm là phiên bản rút gọn, chạy local, dùng dữ liệu mô phỏng để chứng minh ý tưởng.

Cách trình bày này giúp báo cáo chuyên nghiệp hơn, vì nhóm thể hiện được cả tư duy hệ thống thật và năng lực hiện thực hóa bằng demo.

## 2. Mở Đầu Báo Cáo

Trong bối cảnh thư viện đại học ngày càng số hóa, sinh viên có thể truy cập nhiều loại tài nguyên khác nhau như sách in, tài liệu số, luận văn, bài báo khoa học, cơ sở dữ liệu học thuật và tài nguyên từ các nền tảng bên ngoài. Tuy nhiên, lượng tài nguyên lớn khiến người học khó tìm được tài liệu phù hợp với ngành học, môn học và nhu cầu nghiên cứu cá nhân.

Vì vậy, nhóm đề xuất hệ thống UEH Smart Library Recommendation System nhằm phân tích dữ liệu thư viện, dữ liệu học tập và dữ liệu tương tác người dùng để gợi ý tài nguyên phù hợp cho từng sinh viên. Hệ thống trong phạm vi doanh nghiệp có thể kết nối với các nền tảng thực tế như OPAC/Sierra, DSpace Repository, EBSCO OneSearch, OpenAthens, LMS và các nguồn dữ liệu bổ trợ khác.

Do giới hạn quyền truy cập dữ liệu thật, nhóm triển khai một bản demo đơn giản hơn bằng dữ liệu mô phỏng, dữ liệu metadata công khai và proxy data từ Tiki. Demo này không thay thế hệ thống production, mà đóng vai trò chứng minh pipeline Big Data và mô hình đề xuất có thể hoạt động.

## 3. Hệ Thống Đầy Đủ Trong Phạm Vi Doanh Nghiệp

### 3.1. Mục Tiêu Hệ Thống Doanh Nghiệp

Hệ thống production cần giải quyết ba mục tiêu chính:

- Thu thập và hợp nhất dữ liệu từ nhiều hệ thống thư viện và học tập.
- Phân tích hành vi người dùng để hiểu nhu cầu tài liệu của sinh viên.
- Đề xuất tài nguyên phù hợp theo thời gian gần thực hoặc theo chu kỳ.

Kết quả cuối cùng là mỗi sinh viên có thể nhận được danh sách tài nguyên cá nhân hóa, gồm sách in, tài liệu số UEH Repository, bài báo học thuật, cơ sở dữ liệu điện tử hoặc tài nguyên tham khảo ngoài thư viện.

### 3.2. Nguồn Dữ Liệu Trong Hệ Thống Thật

Trong hệ thống doanh nghiệp, dữ liệu có thể đến từ các nguồn sau:

| Nguồn dữ liệu | Vai trò trong hệ thống |
| --- | --- |
| OPAC/Sierra Circulation | Lịch sử mượn, trả, gia hạn, đặt giữ chỗ sách in |
| DSpace / UEH Repository | Metadata tài liệu số, lượt xem, lượt tải, collection, DOI, tác giả |
| EBSCO OneSearch | Hành vi tìm kiếm học thuật, từ khóa tìm kiếm, click kết quả |
| OpenAthens | Log xác thực và truy cập tài nguyên điện tử |
| LMS / hệ thống học tập | Ngành học, môn học, học phần, hành vi học tập |
| Feedback của sinh viên | Rating, lưu tài liệu, click đề xuất, bỏ qua đề xuất |
| Tiki hoặc nguồn ngoài | Dữ liệu bổ trợ về sách, giá, rating, review, lượt bán |

Trong báo cáo cần nhấn mạnh: Tiki chỉ là nguồn dữ liệu bổ trợ hoặc proxy data, không phải dữ liệu hành vi thật của sinh viên UEH.

### 3.3. Tầng Thu Thập Dữ Liệu

Ở quy mô doanh nghiệp, dữ liệu có thể được thu thập theo hai cách:

- Batch ingestion: nhập dữ liệu định kỳ từ OPAC, repository, LMS hoặc file CSV/API.
- Streaming ingestion: dùng Kafka để nhận log hành vi gần real-time từ web portal, mobile app, OPAC terminal hoặc hệ thống xác thực.

Các sự kiện có thể bao gồm:

- student_search
- item_view
- repository_download
- book_borrow
- book_return
- hold_request
- recommendation_click
- recommendation_ignore

Những sự kiện này là nền tảng để xây dựng mô hình đề xuất dựa trên hành vi thật.

### 3.4. Privacy Layer Và Data Governance

Vì dữ liệu sinh viên là dữ liệu nhạy cảm, hệ thống cần có lớp bảo vệ quyền riêng tư trước khi đưa dữ liệu vào phân tích.

Các thao tác cần có:

- Tách thông tin định danh như MSSV, họ tên, email khỏi dữ liệu phân tích.
- Sinh student_token để thay thế mã sinh viên thật.
- Hash hoặc mã hóa các định danh nhạy cảm.
- Phân quyền dữ liệu theo vai trò.
- Ghi nhận lineage để biết mỗi trường dữ liệu đến từ đâu và đã qua bước xử lý nào.

Trong hệ thống production, phần governance có thể dùng Apache Atlas hoặc DataHub. Trong demo, nhóm mô phỏng bằng privacy layer tạo student_token và loại bỏ các cột PII.

### 3.5. Data Lake Và Lưu Trữ Phân Tán

Ở phạm vi doanh nghiệp, dữ liệu nên được lưu trong Data Lake trên HDFS, S3 hoặc MinIO. Định dạng lưu trữ nên dùng Parquet vì tối ưu cho phân tích dữ liệu lớn.

Cấu trúc gợi ý:

```text
data_lake/
  bronze/
    raw_opac_logs/
    raw_repository_logs/
    raw_search_logs/
  silver/
    cleaned_events/
    protected_student_profiles/
  gold/
    recommendation_features/
    recommendation_results/
```

Dữ liệu nên được partition theo các khóa như ngày, ngành học hoặc loại tài nguyên để tối ưu truy vấn.

### 3.6. Processing Và Analytical Warehouse

Hệ thống production có thể dùng Spark để xử lý dữ liệu lớn, làm sạch log, tạo feature và huấn luyện mô hình. Sau đó dữ liệu tổng hợp có thể đưa vào Hive, ClickHouse hoặc warehouse phân tích để dashboard truy vấn nhanh.

Trong demo, nhóm dùng DuckDB thay cho warehouse lớn vì dữ liệu nhỏ và chạy local. DuckDB đóng vai trò analytical warehouse rút gọn.

### 3.7. AI Recommendation Engine

Hệ thống đề xuất doanh nghiệp nên có nhiều lớp mô hình:

1. Content-based recommendation: đề xuất dựa trên ngành học, môn học, tiêu đề tài liệu, chủ đề, tác giả và metadata.
2. Collaborative Filtering ALS: đề xuất dựa trên hành vi tương tác thật của nhiều sinh viên.
3. Semantic search / embedding: dùng vector để đo độ tương đồng ngữ nghĩa giữa nhu cầu học tập và nội dung tài liệu.
4. Hybrid ranking: kết hợp nhiều tín hiệu như match score, hành vi, rating, độ phổ biến, độ mới và quyền truy cập.

Trong hệ thống thật, Spark ALS sẽ phù hợp khi có nhiều log mượn/trả, click, tải PDF hoặc rating thật. Trong demo, nhóm có triển khai PySpark ALS bằng proxy implicit rating để minh họa hướng mở rộng.

### 3.8. Serving Và Phân Phối Đề Xuất

Sau khi có kết quả đề xuất, hệ thống cần kiểm tra tài nguyên có khả dụng không:

- Sách in: kiểm tra vị trí kệ, mã OPAC, trạng thái còn/hết.
- Tài liệu số: kiểm tra quyền truy cập, link PDF, DOI hoặc repository URL.
- Tài nguyên ngoài: kiểm tra link tham khảo hoặc marketplace URL.

Kết quả được phân phối qua:

- Web portal OPAC
- Mobile app
- Email digest
- OPAC terminal widget
- API cho các hệ thống khác

Trong production, API Gateway như Kong có thể đứng giữa recommendation service và các kênh phân phối.

## 4. Bản Demo Rút Gọn Của Nhóm

### 4.1. Lý Do Cần Demo Rút Gọn

Nhóm không có quyền truy cập trực tiếp vào log thật của OPAC, LMS, OpenAthens hoặc hệ thống phân quyền tài liệu số. Vì vậy, nhóm triển khai bản demo local nhằm chứng minh luồng xử lý chính:

```text
Thu thập dữ liệu
-> Làm sạch và matching
-> Privacy layer
-> Data Lake Parquet
-> DuckDB analysis
-> Recommendation
-> Distribution payload
-> Power BI dashboard
```

### 4.2. Dữ Liệu Demo

Demo sử dụng ba nhóm dữ liệu:

| Nhóm dữ liệu | Mục đích |
| --- | --- |
| UEH Repository metadata | Đại diện cho tài liệu số học thuật |
| Tiki books proxy data | Bổ sung tín hiệu rating, review, quantity_sold cho sách tham khảo |
| Mock students | Mô phỏng 2,000 sinh viên theo ngành học, khóa học và môn học |

Tiki được dùng như proxy data, không phải hành vi thật của sinh viên. Các trường như rating_average, review_count và quantity_sold_value được dùng để mô phỏng chất lượng và độ phổ biến của sách.

### 4.3. Privacy Layer Trong Demo

Nhóm tạo student_token để thay thế mã sinh viên thật. Các trường nhạy cảm như student_id, student_code, student_name và user_id không được đưa vào dữ liệu analytics.

Kết quả chính:

- student_token_map_protected.csv
- students_protected.csv
- student_resource_matches_analytics.csv

### 4.4. Data Lake Trong Demo

Nhóm mô phỏng Data Lake bằng local Parquet:

- Định dạng: Parquet
- Partition key: major
- Số dòng: 12,000
- Số partition: 36

Mục đích là minh họa cách dữ liệu có thể được tổ chức giống HDFS/S3/MinIO trong hệ thống thật.

### 4.5. DuckDB Warehouse Và Analysis

DuckDB được dùng để truy vấn dữ liệu Parquet và tạo các bảng phân tích:

- Tổng số match
- Số sinh viên
- Số ngành
- Số môn học
- Phân bố confidence
- Top ngành có nhiều match
- Top tài nguyên được đề xuất

Các KPI chính:

- 12,000 match rows
- 2,000 students
- 36 majors
- 201 courses
- 162 Tiki books
- 152 UEH repository documents

### 4.6. AI Recommendation Trong Demo

Mô hình chính trong demo là content-based recommendation kết hợp weighted scoring. Điểm đề xuất được tính từ:

- Match score
- Confidence
- Rating của Tiki
- Review count
- Quantity sold
- Metadata tài liệu UEH Repository
- Độ phù hợp theo ngành học và môn học

Kết quả:

- 10,000 recommendation rows
- 2,000 students có đề xuất
- 151 tài nguyên được đề xuất
- Điểm đề xuất trung bình: 70.5

### 4.7. PySpark ALS Demo Mở Rộng

Ngoài mô hình chính, nhóm triển khai thêm PySpark ALS để minh họa hướng phát triển collaborative filtering.

Kết quả demo ALS:

- 22,115 proxy interactions
- 2,000 users
- 314 items
- RMSE khoảng 4.7891

Lưu ý: ALS trong demo dùng proxy implicit rating, chưa phải rating thật. Trong production, rating này nên được thay bằng log mượn/trả, click, tải PDF, lưu tài liệu hoặc feedback thật của sinh viên.

### 4.8. Phase 5: Phân Phối Đề Xuất

Nhóm mô phỏng bước phân phối kết quả đề xuất cho người dùng cuối. Kết quả được chuẩn hóa thành payload để hiển thị trên web portal hoặc mobile app.

Kết quả chính:

- 10,000 delivery rows
- 2,000 students
- 151 resources
- 5,394 Tiki / print / marketplace items
- 4,606 digital repository items
- Average score: 70.5

Trong demo, bước kiểm tra khả dụng được mô phỏng bằng DuckDB. Trong hệ thống thật, bước này cần kết nối với OPAC circulation API và repository access service.

## 5. Dashboard Power BI

Dashboard Power BI được dùng để trình bày kết quả theo 5 nhóm:

1. Tổng quan hệ thống và KPI.
2. Hành vi người dùng mô phỏng.
3. Matching và confidence scoring.
4. Kết quả recommendation.
5. Distribution payload và trạng thái khả dụng.

Dashboard giúp người xem hiểu được dữ liệu đầu vào, quá trình xử lý và kết quả đề xuất cuối cùng.

## 6. Insight Chính

Một số insight từ demo:

- Hệ thống có thể tạo đề xuất cho toàn bộ 2,000 sinh viên.
- Các ngành có nhiều match nhất thường là nhóm tài chính, kinh doanh và công nghệ.
- Tiki books cung cấp tín hiệu bổ sung về mức độ phổ biến thông qua rating, review và quantity sold.
- UEH Repository giúp bổ sung tài nguyên học thuật chính thống.
- Content-based recommendation phù hợp trong giai đoạn chưa có dữ liệu hành vi thật.
- PySpark ALS là hướng phát triển phù hợp khi hệ thống có đủ log tương tác thật.

## 7. Hạn Chế

- Dữ liệu hành vi sinh viên là dữ liệu mô phỏng.
- Dữ liệu Tiki là proxy data, không phải hành vi thật của sinh viên UEH.
- Data Lake đang chạy local bằng Parquet, chưa phải HDFS/S3/MinIO thật.
- DuckDB là analytical warehouse local, chưa phải warehouse production.
- Phase 5 chưa kết nối OPAC API hoặc hệ thống phân quyền digital real-time.
- PySpark ALS dùng proxy implicit rating, chưa dùng rating thật.

## 8. Hướng Phát Triển

Trong tương lai, hệ thống có thể mở rộng theo các hướng:

- Thu thập log thật từ OPAC, Repository, LMS, OpenAthens và web portal.
- Lưu trữ dữ liệu trên HDFS, S3 hoặc MinIO.
- Dùng Spark để xử lý dữ liệu lớn và huấn luyện recommendation model.
- Triển khai Spark ALS trên dữ liệu hành vi thật.
- Bổ sung semantic search bằng embedding và vector database.
- Xây dựng API Gateway để phân phối đề xuất tới web portal, mobile app và email digest.
- Đánh giá chất lượng đề xuất bằng click-through rate, borrow rate, download rate và feedback thật.

## 9. Kết Luận

Đề tài đã xây dựng được một bản demo hoàn chỉnh cho hệ thống đề xuất tài nguyên thư viện thông minh. Dù chưa sử dụng dữ liệu hành vi thật và chưa triển khai trên hạ tầng doanh nghiệp, demo đã thể hiện đầy đủ các thành phần quan trọng của một pipeline Big Data: thu thập dữ liệu, bảo vệ quyền riêng tư, lưu trữ dạng Data Lake, phân tích bằng warehouse, xây dựng mô hình đề xuất và phân phối kết quả.

Hệ thống demo là nền tảng để phát triển lên phiên bản production trong tương lai, khi có thể kết nối trực tiếp với các hệ thống thật của UEH Smart Library và thu thập dữ liệu hành vi người dùng ở quy mô lớn.

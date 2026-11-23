# Hướng Dẫn Đóng Góp Mã Nguồn (Contributing Guide) - Yuu Cake

Chào mừng bạn tham gia phát triển dự án **Yuu Cake - Tiệm Bánh Trực Tuyến**. Tài liệu này quy định quy trình làm việc chuẩn cho các thành viên và cộng tác viên.

## 1. Quy trình phân nhánh (Git Branching Model)
Dự án áp dụng mô hình phân nhánh theo tính năng (Feature Branching):
- Nhánh `main`: Chứa mã nguồn ổn định nhất, sẵn sàng triển khai thực tế.
- Mọi thay đổi đều được thực hiện trên nhánh tính năng riêng biệt:
  - Cú pháp tên nhánh: `feature/<so_thu_tu>-<ten_ngan_gon>`
  - Ví dụ: `feature/15-ci-testing`, `feature/16-oss-docs-and-governance`.

## 2. Quy chuẩn thông điệp Commit (Conventional Commits)
Thông điệp commit cần ngắn gọn, rõ ràng theo cấu trúc:
`<loai>(<pham_vi>): <mo_ta_ngan_gon>`
- `feat`: Tính năng người dùng mới.
- `fix`: Sửa lỗi.
- `test`: Thêm hoặc cập nhật kịch bản kiểm thử tự động.
- `docs`: Cập nhật tài liệu hướng dẫn hoặc quy định.
- `chore`: Cấu hình hệ thống hoặc cập nhật phụ thuộc.

## 3. Tiêu chuẩn kiểm thử tự động (Quality Gates)
Trước khi mở Pull Request:
1. Chạy toàn bộ bộ kiểm thử tự động:
   ```bash
   pytest -v --cov=. --cov-report=term-missing
   ```
2. Độ bao phủ mã nguồn (Code Coverage) phải đạt tối thiểu từ **60%** trở lên (mục tiêu dự án duy trì trên 85%).
3. Toàn bộ kịch bản kiểm thử phải đạt trạng thái `PASSED`.

## 4. Quy trình xem xét mã nguồn (Pull Request & Code Review)
1. Đẩy nhánh lên repository từ xa: `git push -u origin feature/<ten_nhanh>`.
2. Tạo Pull Request trỏ vào nhánh `main`.
3. Điền đầy đủ mô tả PR (mục đích, danh sách thay đổi, kết quả tự kiểm thử).
4. Phân công tối thiểu một thành viên đồng đẳng (Peer Reviewer) xem xét mã nguồn.
5. Kiểm tra pipeline GitHub Actions CI phải vượt qua bài kiểm định (tích xanh).
6. Sau khi được Reviewer bấm **Approve**, thực hiện gộp nhánh bằng phương thức **Create a merge commit**.

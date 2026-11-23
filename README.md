# Yuu Cake – Website Tiệm Bánh Trực Tuyến (Flask)

[![CI Test & Code Coverage](https://github.com/nguyen-trong-vy/test-pnmnm/actions/workflows/ci.yml/badge.svg)](https://github.com/nguyen-trong-vy/test-pnmnm/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Dự án tổng hợp kiến thức **Chương 3, 4, 5, 6** học phần **Phần mềm Mã nguồn mở** (Trường ĐH Khoa học, ĐH Huế), thiết kế theo giao diện tiệm bánh **Yuu Cake**:
- **Phần A**: Cửa hàng bán lẻ trực tuyến (Trang chủ, Thực đơn bánh, Chi tiết, Giỏ hàng Session PRG, Đặt hàng & Xác nhận đơn hàng, Tìm kiếm chống XSS, Link rút gọn 301, Xuất CSV, RESTful API JSON).
- **Phần B**: Phân hệ Quản trị viên `/admin` (Bảo vệ route `@admin_required`, Dashboard thống kê tổng quan, Quản lý bánh & Upload ảnh, Quản lý danh mục & Bảo toàn toàn vẹn khoá ngoại, Quản lý đơn hàng & Cập nhật trạng thái).

---

## 1. Cài đặt & chạy dự án

```bash
# 1. Di chuyển vào thư mục dự án và tạo môi trường ảo Python
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Windows (CMD):        .venv\Scripts\activate.bat
# macOS / Linux:        source .venv/bin/activate

# 2. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 3. Khởi chạy máy chủ phát triển
flask --app app run --debug --port 8000
```

Mở trình duyệt tại: `http://127.0.0.1:8000`
*(Ứng dụng tự động khởi tạo CSDL `instance/yuucake.db` và nạp dữ liệu mẫu 5 danh mục, 20 sản phẩm, 3 bài viết blog khi chạy lần đầu).*

- **Tài khoản Quản trị mặc định**: `admin` / `admin123`
- **Đường dẫn phân hệ Admin**: `http://127.0.0.1:8000/admin/`

---

## 2. Kiểm tra danh sách route & kiểm thử nhanh bằng `curl`

Xem toàn bộ route Flask đã đăng ký trong ứng dụng:
```bash
flask --app app routes
```

Kiểm thử các chức năng Chương 3 bằng `curl`:
```bash
B=http://127.0.0.1:8000

# 1. Link rút gọn chuyển hướng 301 (Location sinh bằng url_for)
curl -i $B/sp/1

# 2. Xuất thông tin bánh CSV (Content-Type + Content-Disposition)
curl -i $B/san-pham/1/export

# 3. API đọc sản phẩm & lọc kết hợp (JSON tiếng Việt có dấu)
curl "$B/api/products?category=banh-donut&min_price=50000"

# 4. API kiểm tra sai kiểu tham số -> 400 JSON
curl -i "$B/api/products?min_price=abc"

# 5. API không tìm thấy -> 404 JSON
curl -i $B/api/products/999

# 6. API giỏ hàng (dùng -c/-b lưu cookie session): 201 + Location, 200, 400, 204, 405
C=$B/api/cart/items/1
curl -i -c cookies.txt -X PUT "$C?qty=2"      # 201 Created + Location
curl -i -b cookies.txt -c cookies.txt -X PUT "$C?qty=3"  # 200 OK
curl -i -b cookies.txt -X PUT "$C?qty=999"    # 400 Bad Request
curl -i -b cookies.txt -X DELETE $C           # 204 No Content
curl -i -X POST $C                            # 405 JSON
curl -i -X POST $B/san-pham                   # 405 HTML
```

---

## 3. Kiểm thử tự động & Độ bao phủ mã nguồn (Unit Tests & Coverage)

Dự án thiết lập bộ kiểm thử tự động toàn diện bằng `pytest` và `pytest-cov` với **26 kịch bản kiểm thử độc lập**, đạt độ bao phủ mã nguồn (Code Coverage) lên đến **90%** (vượt xa chỉ tiêu tối thiểu 60% của đề tài):

```bash
# Chạy toàn bộ 26 unit test kèm báo cáo độ bao phủ chi tiết từng file
pytest -v --cov=. --cov-report=term-missing
```

Cấu trúc bộ kiểm thử tại thư mục `tests/`:
- `tests/test_models.py`: Kiểm thử các thực thể ORM SQLAlchemy 2.0 (`Product`, `Category`, `Order`, `OrderItem`, `OrderStatusHistory`, `User`), quan hệ 1-N, hàm băm mật khẩu bảo mật `werkzeug.security`.
- `tests/test_store_routes.py`: Kiểm thử trang chủ, danh sách sản phẩm, lọc danh mục, chi tiết bánh, link rút gọn 301, xuất file CSV tải xuống, bài viết tin tức và cơ chế escape phòng chống lỗ hổng XSS tại form tìm kiếm.
- `tests/test_cart_and_checkout.py`: Kiểm thử Session giỏ hàng, cập nhật số lượng theo mô hình PRG (Post-Redirect-Get), xác thực form đặt hàng Flask-WTF, giao dịch nguyên tử (atomic transaction) và trừ kho tự động.
- `tests/test_api.py`: Kiểm thử các endpoint RESTful JSON API (`GET /api/products`, `GET /api/categories`, `PUT/GET/DELETE /api/cart/items/<id>`).
- `tests/test_admin.py`: Kiểm thử cơ chế bảo vệ truy cập `@admin_required`, đăng nhập/đăng xuất, CRUD sản phẩm & danh mục, ràng buộc toàn vẹn dữ liệu khi xoá, chuyển trạng thái đơn hàng và xuất hoá đơn CSV.
- `tests/test_errors.py`: Kiểm thử bộ xử lý lỗi tập trung HTTP 400, 404, 405 trả về HTML cho trình duyệt và JSON cho API client.

Pipeline **GitHub Actions CI** (`.github/workflows/ci.yml`) sẽ tự động kích hoạt mỗi khi có commit hoặc Pull Request vào nhánh `main` để kiểm định chất lượng mã nguồn.

---

## 4. Tài liệu học phần & Vấn đáp
- `docs/GIAI_THICH_KIEN_THUC.md`: Đối chiếu từng tính năng với chuẩn kiến thức Chương 3, 4, 5, 6 và hướng dẫn giải thích code khi thầy cô vấn đáp.
- `docs/LO_TRINH_COMMIT_VA_VAN_DAP.md`: Lộ trình chi tiết từng Pull Request và bộ câu hỏi vấn đáp trọng tâm.

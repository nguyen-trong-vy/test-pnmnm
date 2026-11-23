# Yuu Cake – Website Tiệm Bánh Trực Tuyến (Flask)

Dự án tổng hợp kiến thức **Chương 3, 4, 5, 6** học phần **Phần mềm Mã nguồn mở** (Trường ĐH Khoa học, ĐH Huế), thiết kế theo giao diện tiệm bánh **Yuu Cake** (Phần A – Trang bán hàng; kiến trúc CSDL đã chuẩn bị sẵn cho Phần B – `/admin` ở bước kế tiếp).

## 1. Cài đặt & chạy dự án

```bash
cd yuu_cake
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Windows (CMD):        .venv\Scripts\activate.bat
# macOS / Linux:        source .venv/bin/activate

pip install -r requirements.txt
flask --app app run --debug --port 8000
```

Mở trình duyệt tại: `http://127.0.0.1:8000`
*(Ứng dụng tự động tạo CSDL `instance/yuucake.db` và nạp dữ liệu mẫu lần đầu; cũng có thể gọi route `/them-mau` hoặc lệnh `flask --app app seed`.)*

## 2. Kiểm tra danh sách route & kiểm thử nhanh bằng `curl`

Xem toàn bộ route Flask đã đăng ký:
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

## 3. Tài liệu đọc thêm trước khi báo cáo / vấn đáp
- `docs/GIAI_THICH_KIEN_THUC.md`: Đối chiếu từng tính năng với Chương 3, 4, 5, 6 và giải thích phần giao diện mở rộng.
- `docs/LO_TRINH_COMMIT_VA_VAN_DAP.md`: Hướng dẫn chia **9 commit nhỏ có ý nghĩa** kèm lệnh `git` và bộ câu hỏi vấn đáp thầy hay hỏi.

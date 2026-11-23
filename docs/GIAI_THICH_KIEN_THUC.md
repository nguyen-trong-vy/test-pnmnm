# Giải thích Kiến thức Áp dụng (Chương 3 – 6 & Giao diện mở rộng)

## 1. Kiến thức từ các chương trong học phần

| Chương | Kiến thức áp dụng | File & vị trí trong dự án |
|---|---|---|
| **Chương 3: Routing, Request/Response & API** | Sinh 100% URL và header `Location` bằng `url_for()`, không viết cứng đường dẫn | Toàn bộ `templates/*.html`, `routes/*.py` |
| **Chương 3** | Converter `<int:product_id>`, `<int:order_id>`, `<slug>` | `routes/store.py`, `routes/cart.py`, `routes/checkout.py`, `routes/api.py` |
| **Chương 3** | Lọc dữ liệu qua `request.args` (phân biệt rõ **thiếu** và **sai kiểu** `min_price` -> 400) | `routes/store.py` (`/san-pham`, `/tim-kiem`), `routes/api.py` (`/api/products`) |
| **Chương 3** | Chuyển hướng vĩnh viễn `redirect(..., code=301)` cho link rút gọn `/sp/<id>` | `routes/store.py` (`product_short_redirect`) |
| **Chương 3** | Xuất tệp CSV tải xuống bằng `make_response` (`Content-Type`, `Content-Disposition`) | `routes/store.py` (`/san-pham/<id>/export`), `routes/checkout.py` (`/don-hang/<id>/export`) |
| **Chương 3** | Tìm kiếm an toàn chống XSS (`escape()`, auto-escape ở cả `value=""` và tiêu đề kết quả) | `routes/store.py` (`/tim-kiem`), `templates/search.html` |
| **Chương 3** | API JSON tiếng Việt có dấu (`app.json.ensure_ascii = False`), mã `200/201+Location/204/400/404/405` | `config.py`, `app.py`, `routes/api.py` |
| **Chương 3** | Xử lý lỗi tập trung `@app.errorhandler(400/404/405)` (trả JSON cho `/api/`, HTML cho web) | `routes/errors.py`, `templates/error.html` |
| **Chương 3** | Flask CLI (`flask --app app routes`, custom command `flask --app app seed`) | `app.py` |
| **Chương 4: Jinja2 & Bootstrap** | Kế thừa template `{% extends "base.html" %}`, `{% block %}` | `templates/base.html` và 12 template con |
| **Chương 4** | Custom filter `@app.template_filter("vnd")` định dạng `52.000 đ` và `date_vn` | `app.py` |
| **Chương 4** | `@app.context_processor` bơm `cart_count` và `nav_categories` cho navbar mọi trang | `app.py` |
| **Chương 5: Form, CSRF & Session** | Giỏ hàng lưu trong `session["cart"]` dạng `{product_id: qty}`, **không lưu giá** trong session | `routes/cart.py` |
| **Chương 5** | Bảo vệ CSRF toàn cục bằng `CSRFProtect` + `FlaskForm` (`Flask-WTF`) | `extensions.py`, `forms.py`, mọi form POST |
| **Chương 5** | Kiểm tra dữ liệu `CheckoutForm` (SĐT 10 số bắt đầu bằng `0`, Email đúng định dạng), hiện `is-invalid` / `invalid-feedback`, giữ dữ liệu khi lỗi | `forms.py`, `templates/checkout.html` |
| **Chương 5** | Mô hình **PRG (Post-Redirect-Get)** + `flash()` sau mọi thao tác thêm/sửa/xoá giỏ và đặt hàng | `routes/cart.py`, `routes/checkout.py` |
| **Chương 6: SQLite & SQLAlchemy 2.0** | Khai báo `DeclarativeBase`, `Mapped`, `mapped_column`, lưu tại `instance/yuucake.db` | `extensions.py`, `models.py`, `config.py` |
| **Chương 6** | Quan hệ khoá ngoại 1-Nhiều (`Category – Product`, `Order – OrderItem`, `Order – OrderStatusHistory`) | `models.py` |
| **Chương 6** | Lưu đơn giá lúc đặt (`OrderItem.unit_price`), trừ tồn kho nguyên tử trong 1 transaction | `routes/checkout.py` |
| **Chương 6** | Truy vấn thống kê `func.count`, `func.sum`, `func.avg`, `group_by`, phân trang `db.paginate` | `routes/store.py`, `routes/api.py` |
| **Chương 6** | Nạp dữ liệu mẫu bằng `/them-mau` và Flask-Migrate sẵn sàng cho mở rộng | `routes/store.py`, `seed.py`, `extensions.py` |

## 2. Giải thích phần Giao diện mở rộng (để đạt thẩm mỹ giống video Yuu Cake)

Ngoài Bootstrap 5 (Chương 4), dự án có bổ sung các kỹ thuật giao diện thuần HTML/CSS/JS để bám sát thiết kế tiệm bánh trong video mẫu:

1. **CSS Custom Properties (`:root` trong `static/css/style.css`)**:
   - Tập trung toàn bộ bảng màu thương hiệu (`--yuu-brown: #4a2016`, `--yuu-cream: #faf5f0`, `--yuu-accent: #e86f2c`) vào một chỗ giúp đổi màu toàn website dễ dàng và giữ cảm giác ấm áp của tiệm bánh.
2. **Google Fonts (`Playfair Display` + `Be Vietnam Pro`)**:
   - `Playfair Display` tạo logo chữ `Yuu Cake` sang trọng; `Be Vietnam Pro` được thiết kế riêng cho tiếng Việt nên hiển thị dấu sắc nét ở mọi cỡ chữ.
3. **Hero Slider & CSS Transition (`home.html`, `style.css`, `main.js`)**:
   - Xếp chồng các slide bằng `position: absolute; inset: 0` và chuyển mượt bằng thuộc tính `opacity` kết hợp 20 dòng JavaScript thuần (`setInterval` + click dot), không cần cài thư viện slider bên ngoài.
   - Phủ lớp `radial-gradient` màu nâu tối phía trên ảnh nền giúp tiêu đề chữ trắng luôn dễ đọc (đạt độ tương phản cao).
4. **Thanh thông báo chạy ngang Marquee (`@keyframes yuu-marquee`)**:
   - Dùng thuần CSS `transform: translateX(-50%)` chạy vòng lặp mượt, tự động tạm dừng (`animation-play-state: paused`) khi người dùng di chuột vào đọc.
5. **Nút tăng/giảm số lượng (`main.js`) & xác nhận xoá giỏ (`confirm`)**:
   - Chỉ đóng vai trò hỗ trợ trải nghiệm người dùng (UX). Mọi kiểm tra số lượng hợp lệ và tồn kho đều được thực thi lại hoàn toàn phía server trong `routes/cart.py` và `routes/checkout.py` theo nguyên tắc an toàn Chương 5.
6. **Chuẩn bị sẵn cho Phần B (`/admin`)**:
   - Bảng `OrderStatusHistory`, các hằng số trạng thái (`Chờ xác nhận`, `Đang giao`, `Hoàn tất`, `Đã huỷ`) và liên kết `Product.order_items` đã được định nghĩa sẵn trong `models.py` để khi thêm phần quản trị không phải sửa lại cấu trúc CSDL.

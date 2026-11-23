# Tài Liệu Hướng Dẫn Phát Triển (Developer Guide) - Yuu Cake

Tài liệu kỹ thuật dành cho lập trình viên tham gia bảo trì, phát triển mở rộng hoặc chấm điểm mã nguồn dự án **Yuu Cake**.

---

## 1. Công nghệ & Thư viện sử dụng (Tech Stack)
- **Ngôn ngữ:** Python 3.10+ (Đã kiểm thử hoàn hảo trên 3.11, 3.12, 3.14).
- **Web Framework:** Flask 3.0+.
- **ORM & CSDL:** SQLAlchemy 2.0+ (kết hợp Flask-SQLAlchemy 3.1+), cơ sở dữ liệu SQLite cục bộ (lưu tại `instance/yuucake.db`).
- **Biểu mẫu & Bảo mật:** Flask-WTF 1.2+ (CSRF protection tích hợp), WTForms 3.1+, Werkzeug Security (hashing PBKDF2/SHA256).
- **Giao diện (Frontend):** Jinja2 Template Engine, Bootstrap 5.3+, Bootstrap Icons 1.11, Google Fonts (Be Vietnam Pro, Playfair Display).
- **Kiểm thử tự động & CI:** `pytest` 8.0+, `pytest-cov` 5.0+, GitHub Actions.

---

## 2. Kiến trúc thư mục dự án
```text
yuu_cake/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline CI chạy tự động trên GitHub Actions
├── docs/                        # Toàn bộ tài liệu báo cáo, giải thích kiến thức, vấn đáp
│   ├── GIAI_THICH_KIEN_THUC.md
│   ├── LAP_LUAN_CHON_GIAY_PHEP.md
│   ├── LO_TRINH_COMMIT_VA_VAN_DAP.md
│   ├── TAI_LIEU_NGUOI_DUNG.md
│   └── TAI_LIEU_PHAT_TRIEN.md
├── instance/                    # Thư mục chứa CSDL SQLite cục bộ (bỏ qua khỏi git)
├── routes/                      # Các Blueprints chia nhỏ theo từng phân hệ chức năng
│   ├── __init__.py
│   ├── admin.py                 # Blueprint Quản trị (/admin): CRUD, auth, dashboard, export CSV
│   ├── api.py                   # Blueprint RESTful API JSON (/api): products, categories, cart
│   ├── cart.py                  # Blueprint Giỏ hàng Session PRG (/gio-hang)
│   ├── checkout.py              # Blueprint Đặt hàng, tính ship, trừ tồn kho (/dat-hang, /don-hang)
│   ├── errors.py                # Centralized error handler cho 400, 404, 405 (HTML & JSON)
│   └── store.py                 # Blueprint Cửa hàng bán lẻ (/san-pham, /tim-kiem, /sp/<id>, blog)
├── static/                      # Tài nguyên tĩnh
│   ├── css/style.css            # Tùy biến bảng màu pastel, animation card, sidebar admin
│   ├── images/                  # Toàn bộ ảnh sản phẩm, danh mục, blog định dạng AVIF tối ưu nhẹ
│   └── js/main.js               # Auto-dismiss flash alert, dynamic toast, quantity helpers
├── templates/                   # Giao diện Jinja2
│   ├── admin/                   # Khuôn mẫu phân hệ quản trị (kế thừa base_admin.html)
│   ├── base.html                # Khuôn mẫu dùng chung cho khách (kế thừa bởi mọi trang bán hàng)
│   └── ...                      # Các trang giao diện đơn lẻ
├── tests/                       # Bộ 26 kịch bản kiểm thử tự động pytest
│   ├── conftest.py              # Fixtures: In-memory SQLite DB, client, admin_client
│   ├── test_admin.py            # Kiểm thử phân quyền, login, CRUD, export CSV admin
│   ├── test_api.py              # Kiểm thử các endpoint RESTful JSON API
│   ├── test_cart_and_checkout.py# Kiểm thử giỏ hàng, form validation, trừ tồn kho
│   ├── test_errors.py           # Kiểm thử xử lý lỗi tập trung 400, 404, 405
│   ├── test_models.py           # Kiểm thử Model ORM, quan hệ 1-N, password hash
│   └── test_store_routes.py     # Kiểm thử cửa hàng, chống XSS, link 301, blog
├── app.py                       # Application Factory (create_app), nạp blueprints, CLI commands
├── config.py                    # Lớp cấu hình phát triển (DevelopmentConfig) và kiểm thử (TestConfig)
├── extensions.py                # Khởi tạo các phần mở rộng dùng chung (db, csrf, migrate)
├── forms.py                     # Định nghĩa biểu mẫu Flask-WTF và bộ kiểm tra (validators)
├── models.py                    # Định nghĩa các thực thể Model SQLAlchemy 2.0
├── pytest.ini                   # Cấu hình môi trường chạy pytest
├── requirements.txt             # Danh sách gói thư viện phụ thuộc
├── seed.py                      # Dữ liệu hạt giống ban đầu (5 danh mục, 20 bánh, 3 bài viết, 1 admin)
├── LICENSE                      # Giấy phép bản quyền mã nguồn mở MIT
├── CONTRIBUTING.md              # Quy chuẩn đóng góp mã nguồn
├── CODE_OF_CONDUCT.md           # Bộ quy tắc ứng xử cộng đồng
└── SECURITY.md                  # Chính sách bảo mật dự án
```

---

## 3. Kiến trúc thiết kế CSDL (ERD & Quan hệ bảng)
1. **`categories` (1) ─── (N) `products`:**
   - Một danh mục chứa nhiều sản phẩm.
   - Khoá ngoại: `products.category_id` $\rightarrow$ `categories.id`.
   - Ràng buộc: Chặn xoá danh mục khi còn sản phẩm thuộc danh mục để bảo vệ toàn vẹn tham chiếu.
2. **`orders` (1) ─── (N) `order_items`:**
   - Một đơn hàng có nhiều chi tiết dòng sản phẩm.
   - Khi lưu đơn hàng, `order_items.unit_price` lưu giá tại thời điểm khách chốt đơn, không bị ảnh hưởng nếu sau này giá trong bảng `products` thay đổi.
3. **`orders` (1) ─── (N) `order_status_history`:**
   - Lưu trữ các mốc thay đổi trạng thái (Chờ xác nhận $\rightarrow$ Đang giao $\rightarrow$ Hoàn tất) kèm thời gian `changed_at`.
4. **`users`:**
   - Lưu trữ tài khoản quản trị viên kèm chuỗi băm mật khẩu bảo mật `password_hash` sinh bởi `generate_password_hash`.
5. **`blog_posts`:**
   - Quản lý các bài viết tin tức và hướng dẫn làm bánh theo đường dẫn thân thiện SEO (slug).

---

## 4. Hướng dẫn phát triển & Mở rộng tính năng
### Thêm một tính năng mới:
1. Tạo nhánh mới: `git checkout -b feature/<so_thu_tu>-<ten_tinh_nang>`
2. Nếu cần tạo bảng mới: Thêm Model vào `models.py`.
3. Định nghĩa form nhập liệu (nếu có) trong `forms.py`.
4. Tạo route xử lý trong blueprint tương ứng hoặc tạo Blueprint mới trong thư mục `routes/`.
5. Tạo giao diện `.html` tương ứng trong thư mục `templates/`.
6. Viết thêm test case kiểm thử vào thư mục `tests/`.
7. Chạy kiểm tra: `pytest -v --cov=.` đảm bảo mọi test đều xanh.
8. Commit và mở Pull Request để Reviewer xem xét.

# Lộ trình Commit Chuẩn & Bộ Câu Hỏi Vấn Đáp (Phần A & Phần B)

> **Lưu ý quan trọng khi nộp bài:**
> - **TUYỆT ĐỐI KHÔNG** commit thư mục `.venv/` hoặc `instance/*.db` (đã có sẵn trong `.gitignore`).
> - Trước khi commit, hãy khai báo tên và email Git của chính bạn:
>   ```bash
>   git init
>   git config user.name "Ho Ten Cua Ban"
>   git config user.email "email_sinh_vien@husc.edu.vn"
>   ```
> - Lộ trình gồm 2 giai đoạn:
>   - **Phần A (Commit 1 – 9):** Toàn bộ giao diện bán hàng, giỏ hàng Session, đặt hàng Flask-WTF, API RESTful và CSDL SQLAlchemy 2.0.
>   - **Phần B (Commit 10 – 14):** Trọn bộ 6 màn hình Quản trị `/admin`, xử lý nghiệp vụ đơn hàng, upload ảnh bánh và bảo vệ route bằng Session.

---

## Danh sách 9 Commit tuần tự (chạy từng bước trong thư mục `yuu_cake/`)

### Commit 1: Khởi tạo cấu trúc dự án, cấu hình và tiện ích mở rộng
```bash
git add .gitignore requirements.txt config.py extensions.py
git commit -m "chore: khoi tao du an Flask, cau hinh SQLite, JSON tieng Viet va CSRF"
```
- **Ý nghĩa:** Thiết lập nền tảng dự án, bỏ qua `.venv/` và `instance/`, cấu hình `SECRET_KEY`, `JSON_AS_ASCII = False`, khởi tạo `db` (SQLAlchemy 2.0 `DeclarativeBase`), `csrf` (`CSRFProtect`) và `migrate` ở file riêng `extensions.py` để tránh vòng lặp import.
- **Thầy có thể hỏi:** *Vì sao phải tách `extensions.py` riêng thay vì khai báo `db = SQLAlchemy(app)` ngay trong `app.py`?*
  - **Trả lời:** Để tránh lỗi *circular import* khi `app.py` import `routes`, còn `routes` lại import `db` và `models`. Tách `extensions.py` rồi gọi `db.init_app(app)` theo mẫu Application Factory là chuẩn thực hành của Flask.

---

### Commit 2: Thiết kế CSDL quan hệ bằng SQLAlchemy 2.0
```bash
git add models.py
git commit -m "feat(db): thiet ke model SQLAlchemy 2.0 (Category, Product, Order, BlogPost)"
```
- **Ý nghĩa:** Xây dựng lược đồ CSDL chuẩn SQLAlchemy 2.0 (`Mapped`, `mapped_column`), thiết lập quan hệ khoá ngoại 1-Nhiều (`Category`–`Product`, `Order`–`OrderItem`, `Order`–`OrderStatusHistory`) và bảng `BlogPost`.
- **Thầy có thể hỏi:** *Vì sao bảng `OrderItem` lại lưu riêng cột `unit_price` và `product_name` thay vì chỉ lấy qua `product_id`?*
  - **Trả lời:** Vì giá bán của bánh có thể thay đổi trong tương lai. Nếu không lưu `unit_price` tại thời điểm khách đặt hàng, tổng tiền của các hoá đơn cũ sẽ bị thay đổi sai lệch theo giá mới.

---

### Commit 3: Chuẩn hoá bộ ảnh và viết hàm nạp dữ liệu mẫu
```bash
git add seed.py static/images/
git commit -m "feat(seed): bo sung bo anh tiem banh Yuu Cake va ham nap du lieu mau"
```
- **Ý nghĩa:** Tổ chức 31 ảnh theo từng thư mục sạch (`categories/`, `featured/`, `products/`, `blog/`) với tên không dấu tránh lỗi URL đa nền tảng; viết `seed_database()` chạy an toàn nhiều lần (chỉ nạp khi CSDL còn trống), cố ý tạo 1 sản phẩm `stock = 0` và 2 sản phẩm `stock <= 5` để kiểm thử các trạng thái kho.
- **Thầy có thể hỏi:** *Nếu gọi `/them-mau` hoặc `flask --app app seed` hai lần liên tiếp thì dữ liệu có bị nhân đôi không?*
  - **Trả lời:** Không, vì `seed_database()` kiểm tra `select(func.count(Category.id))` trước; nếu đã có dữ liệu thì bỏ qua và trả về trạng thái `seeded: False`.

---

### Commit 4: Xây dựng khuôn mẫu giao diện chung `base.html`, CSS và JS
```bash
git add templates/base.html static/css/style.css static/js/main.js
git commit -m "feat(ui): xay dung layout base.html, giao dien Yuu Cake va tuong tac JS"
```
- **Ý nghĩa:** Áp dụng kế thừa template Jinja2 (`{% block %}`), Bootstrap 5, thanh menu có badge giỏ hàng động, danh mục dropdown từ CSDL, vùng hiển thị flash message, CSS bảng màu nâu sô-cô-la & kem ấm giống video mẫu và JS thuần cho Hero Slider + nút `+/-`.
- **Thầy có thể hỏi:** *Làm sao thanh menu ở mọi trang đều biết số lượng bánh trong giỏ (`cart_count`) mà không cần truyền thủ công trong từng route?*
  - **Trả lời:** Nhờ `@app.context_processor` (`inject_global_context`) trong `app.py`, biến `cart_count` và `nav_categories` được tự động tiêm vào ngữ cảnh của mọi template.

---

### Commit 5: Hoàn thiện các trang bán hàng, tìm kiếm chống XSS, link 301 và xuất CSV
```bash
git add routes/__init__.py routes/store.py templates/home.html templates/products.html templates/product_detail.html templates/search.html templates/blog_list.html templates/blog_detail.html templates/faq.html templates/about.html
git commit -m "feat(store): hoan thien trang chu, san pham, tim kiem chong XSS, redirect 301 va CSV"
```
- **Ý nghĩa:** Triển khai toàn bộ giao diện bán hàng (Trang chủ giống video, Danh sách + lọc/phân trang, Chi tiết bánh, Blog, Hỏi đáp, Giới thiệu) cùng các kỹ thuật Chương 3: chuyển hướng 301 `/sp/<id>`, tải CSV bằng `make_response`, tìm kiếm an toàn chống XSS.
- **Thầy có thể hỏi:**
  1. *Vì sao nhập `"><script>alert(1)</script>` vào `/tim-kiem` không hiện hộp thoại cảnh báo?*
     - **Trả lời:** Jinja2 tự động escape (chuyển `"`, `<`, `>` thành `&quot;`, `&lt;`, `&gt;`) ở cả thuộc tính `value="{{ q }}"` lẫn phần tiêu đề kết quả, nên trình duyệt chỉ hiển thị như văn bản thường.
  2. *Vì sao `/sp/<id>` dùng mã `301` chứ không dùng `302`?*
     - **Trả lời:** `301 Moved Permanently` báo cho trình duyệt và công cụ tìm kiếm biết `/sp/<id>` là đường dẫn rút gọn chuyển vĩnh viễn sang địa chỉ chuẩn `/san-pham/<id>`.

---

### Commit 6: Xây dựng biểu mẫu Flask-WTF và giỏ hàng lưu bằng Session
```bash
git add forms.py routes/cart.py templates/cart.html
git commit -m "feat(cart): xay dung gio hang luu Session, CSRF, kiem tra ton kho va PRG"
```
- **Ý nghĩa:** Xây dựng `AddToCartForm`, `CheckoutForm` bằng Flask-WTF; lưu giỏ hàng dạng `session["cart"] = {"<id>": qty}`, luôn lấy giá mới nhất từ SQLite, toàn bộ nút thêm/tăng/giảm/xoá/xoá hết đều là POST + CSRF token + redirect (PRG).
- **Thầy có thể hỏi:**
  1. *Vì sao không lưu giá sản phẩm trong `session["cart"]`?*
     - **Trả lời:** Nếu lưu giá trong session, khi cửa hàng cập nhật giá mới thì giỏ hàng sẽ hiển thị giá cũ sai lệch. Chỉ lưu `product_id` và `quantity` rồi truy vấn giá mới nhất từ CSDL giúp dữ liệu luôn chính xác.
  2. *Mô hình PRG (Post-Redirect-Get) trong giỏ hàng có tác dụng gì?*
     - **Trả lời:** Sau khi xử lý POST (ví dụ thêm 1 bánh), server trả về `redirect()` sang GET. Nhờ vậy nếu người dùng bấm F5 tải lại trang sẽ không bị gửi lặp lại lệnh POST làm cộng dồn bánh ngoài ý muốn.

---

### Commit 7: Hoàn thiện luồng đặt hàng, trừ tồn kho và xuất hoá đơn CSV
```bash
git add routes/checkout.py templates/checkout.html templates/order_success.html
git commit -m "feat(checkout): them quy trinh dat hang Flask-WTF, tinh phi ship, tru ton kho"
```
- **Ý nghĩa:** Trang `/dat-hang` kiểm tra dữ liệu khách hàng (SĐT 10 số bắt đầu bằng `0`, email hợp lệ, hiện `is-invalid`), miễn phí vận chuyển từ `200.000 đ`, kiểm tra tồn kho lần cuối, lưu `Order` + `OrderItem` + `OrderStatusHistory`, trừ `stock`, xoá giỏ hàng và xuất hoá đơn CSV ở `/don-hang/<id>/export`.
- **Thầy có thể hỏi:** *Nếu khách mở trang thanh toán trước đó, nhưng trong lúc điền form thì bánh hết hàng trên kho, chuyện gì xảy ra khi bấm Xác nhận?*
  - **Trả lời:** Trong `routes/checkout.py`, trước khi tạo `Order`, hệ thống duyệt lại toàn bộ `product.stock < qty` từ CSDL. Nếu thiếu hàng, hệ thống không tạo đơn, không trừ kho, flash rõ tên bánh bị thiếu và đưa khách về `/gio-hang`.

---

### Commit 8: Bổ sung API JSON RESTful, xử lý lỗi tập trung và lắp ráp `app.py`
```bash
git add routes/api.py routes/errors.py templates/error.html app.py
git commit -m "feat(api): them API JSON, errorhandler 400/404/405 va lap rap ung dung app.py"
```
- **Ý nghĩa:** Hoàn thiện API JSON (`/api/products`, `/api/products/<id>`, `/api/categories`, `/api/cart/items/<id>` với đủ mã `200`, `201 + Location`, `204`, `400`, `404`, `405`), hàm xử lý lỗi tập trung phân biệt `/api/` (JSON) và trang web (HTML), cùng `app.py` đăng ký custom filter `|vnd`, context processor và lệnh CLI `seed`.
- **Thầy có thể hỏi:**
  1. *Vì sao trong `handle_http_error(error)` vẫn dùng được `request.path` dù nó không phải view function?*
     - **Trả lời:** Vì khi xảy ra lỗi 400/404/405 trong quá trình xử lý một HTTP request, Flask vẫn giữ nguyên **Request Context** đang hoạt động nên proxy `request` vẫn truy cập được bình thường.
  2. *Vì sao API `PUT /api/cart/items/<id>?qty=2` lần đầu trả `201` kèm header `Location`, còn lần sau trả `200`?*
     - **Trả lời:** `201 Created` biểu thị tài nguyên mới vừa được tạo (kèm `Location` chỉ tới URL tài nguyên đó, sinh bằng `url_for`), còn `200 OK` biểu thị cập nhật tài nguyên đã tồn tại.
  3. *Khác biệt giữa dữ liệu lưu trong `STUDENTS` (dict trên RAM ở Chương 3) và dữ liệu trong dự án này (SQLite Chương 6) khi khởi động lại server?*
     - **Trả lời:** Dict trên RAM sẽ mất sạch khi tắt server; còn dự án này lưu vào tệp CSDL `instance/yuucake.db` nên đơn hàng và tồn kho sau khi trừ vẫn được giữ nguyên sau khi khởi động lại server.

---

### Commit 9: Bổ sung tài liệu hướng dẫn, đối chiếu kiến thức và lộ trình vấn đáp
```bash
git add README.md docs/
git commit -m "docs: bo sung README, giai thich kien thuc Chuong 3-6 va huong dan van dap"
```
- **Ý nghĩa:** Ghi lại hướng dẫn chạy, các lệnh kiểm thử `curl`, bảng ánh xạ từng phần mã nguồn về Chương 3–6 và giải thích phần giao diện mở rộng.

---

## Phần B: Phân hệ Quản trị Viên (`/admin`) – Hoàn thành 6 Màn hình ⑥ đến ⑪

### Commit 10: Xây dựng khung giao diện Admin và Màn hình ⑥ Tổng quan (Dashboard)
```bash
git add routes/admin.py templates/admin/base_admin.html templates/admin/dashboard.html app.py
git commit -m "feat(admin): xay dung layout base_admin.html, route admin_bp va man hinh 6 dashboard"
```
- **Ý nghĩa:** Khởi tạo Blueprint `admin_bp` (tiền tố `/admin`), xây dựng khung sidebar quản trị `base_admin.html`, triển khai màn hình Tổng quan thống kê doanh thu (`func.sum`), đếm tổng đơn hàng, sản phẩm, danh mục và cảnh báo sản phẩm sắp hết hàng (`stock <= 5`).
- **Thầy có thể hỏi:** *Vì sao trang Dashboard tính doanh thu bằng `func.sum()` trên CSDL thay vì đọc hết Order về rồi dùng hàm `sum()` của Python?*
  - **Trả lời:** Dùng hàm tổng hợp của CSDL (`func.sum` của SQL) giúp tính toán trực tiếp trên database engine với hiệu năng tối ưu $O(1)$ truyền về, không làm tràn RAM của web server khi hệ thống có hàng chục ngàn đơn hàng.

---

### Commit 11: Triển khai Màn hình ⑦ & ⑧ Quản lý Sản phẩm (Danh sách, Thêm và Sửa bánh)
```bash
git add forms.py routes/admin.py templates/admin/products.html templates/admin/product_form.html
git commit -m "feat(admin): hoan thien man hinh 7 danh sach san pham va man hinh 8 them sua banh"
```
- **Ý nghĩa:** Bổ sung `ProductAdminForm` kiểm tra dữ liệu thêm/sửa bánh bằng Flask-WTF; xử lý upload ảnh sản phẩm an toàn hoặc chọn ảnh có sẵn; sinh `slug` tự động từ tên bánh; hỗ trợ tìm kiếm, lọc theo danh mục và phân trang sản phẩm trong trang quản trị.
- **Thầy có thể hỏi:**
  1. *Khi sửa một sản phẩm, làm thế nào để xử lý trường hợp người dùng không muốn đổi ảnh mới?*
     - **Trả lời:** Trong form sửa sản phẩm, trường ảnh được cấu hình không bắt buộc (`Optional()`). Nếu người dùng không upload file mới, server sẽ giữ nguyên đường dẫn `product.image` hiện tại trong CSDL.
  2. *Làm thế nào để xoá một sản phẩm an toàn mà không làm hỏng lịch sử hoá đơn cũ?*
     - **Trả lời:** Trong hàm xoá sản phẩm, hệ thống kiểm tra quan hệ `product.order_items`. Nếu sản phẩm đã từng được bán trong bất kỳ đơn hàng nào, hệ thống sẽ chặn thao tác xoá và flash cảnh báo để bảo đảm toàn vẹn dữ liệu kế toán.

---

### Commit 12: Triển khai Màn hình ⑨ Quản lý Danh mục bánh
```bash
git add forms.py routes/admin.py templates/admin/categories.html
git commit -m "feat(admin): trien khai man hinh 9 quan ly danh muc va kiem tra toan ven khoa ngoai"
```
- **Ý nghĩa:** Cho phép xem danh sách danh mục kèm số lượng bánh thuộc từng danh mục (`func.count(Product.id)`), thêm mới và chỉnh sửa danh mục bánh bằng `CategoryForm`; kiểm tra ràng buộc không cho phép xoá danh mục nếu vẫn còn bánh đang thuộc danh mục đó.
- **Thầy có thể hỏi:** *Vì sao không cho phép xoá một danh mục khi vẫn còn sản phẩm bên trong?*
  - **Trả lời:** Đây là nguyên tắc bảo toàn toàn vẹn tham chiếu (Referential Integrity) của CSDL quan hệ. Nếu xoá Category, các Product trỏ khoá ngoại `category_id` sẽ bị mồ côi hoặc gây lỗi vi phạm khoá ngoại (Foreign Key Constraint Error).

---

### Commit 13: Triển khai Màn hình ⑩ & ⑪ Quản lý Đơn hàng và Lịch sử chuyển trạng thái
```bash
git add forms.py routes/admin.py templates/admin/orders.html templates/admin/order_detail.html
git commit -m "feat(admin): hoan thien man hinh 10 danh sach don hang va man hinh 11 chi tiet don"
```
- **Ý nghĩa:** Bảng danh sách đơn hàng có lọc theo trạng thái (`Chờ xác nhận`, `Đang giao`, `Hoàn tất`, `Đã huỷ`); trang chi tiết đơn hàng hiển thị đầy đủ thông tin khách, chi tiết từng bánh (`OrderItem`), form cập nhật trạng thái đơn và tự động ghi nhận mốc thời gian vào bảng `OrderStatusHistory`.
- **Thầy có thể hỏi:** *Bảng `OrderStatusHistory` hoạt động như thế nào khi Admin chuyển trạng thái đơn hàng?*
  - **Trả lời:** Khi Admin chọn trạng thái mới trong `OrderStatusForm` và bấm lưu, server cập nhật `order.status`, đồng thời tạo một bản ghi mới `OrderStatusHistory(order_id=order.id, status=new_status, changed_at=datetime.now())` rồi `commit()`. Nhờ vậy trang chi tiết hiển thị được dòng thời gian (timeline) minh bạch của đơn hàng.

---

### Commit 14: Bổ sung xác thực Admin tối giản, tài khoản seed và bảo vệ toàn diện route
```bash
git add models.py forms.py seed.py routes/admin.py templates/admin/login.html templates/base.html
git commit -m "feat(admin): bao ve phan he admin bang decorator admin_required va session login"
```
- **Ý nghĩa:** Thêm model `AdminUser` (hoặc `User`), hàm seed tạo sẵn tài khoản `admin` / `admin123` (băm mật khẩu bằng `generate_password_hash`), trang đăng nhập `/admin/login`, và decorator `@admin_required` bảo vệ mọi route `/admin/*`. Bổ sung nút truy cập Quản trị trên thanh menu trang chủ khi admin đã đăng nhập.
- **Thầy có thể hỏi:** *Cơ chế hoạt động của decorator `@admin_required` là gì?*
  - **Trả lời:** Sử dụng `functools.wraps` để bọc view function. Decorator kiểm tra `session.get("admin_logged_in") == True`. Nếu chưa đăng nhập, nó lưu lại trang hiện tại bằng `request.full_path` và `redirect(url_for('admin.login', next=request.full_path))` kèm flash cảnh báo yêu cầu đăng nhập.

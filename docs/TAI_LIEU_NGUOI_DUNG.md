# Tài Liệu Hướng Dẫn Người Dùng (User Guide) - Yuu Cake

Tài liệu này hướng dẫn chi tiết các thao tác sử dụng hệ thống Tiệm bánh trực tuyến **Yuu Cake** dành cho hai đối tượng: **Khách hàng** và **Quản trị viên**.

---

## PHẦN 1: HƯỚNG DẪN DÀNH CHO KHÁCH HÀNG

### 1. Xem thực đơn và chi tiết bánh
- Truy cập trang chủ (`/`) để xem các sản phẩm nổi bật, banner sự kiện và danh mục bánh.
- Vào trang **Sản phẩm** (`/san-pham`) để xem danh sách toàn bộ các loại bánh.
- Sử dụng bộ lọc danh mục bên thanh bên trái (Bánh Donut, Bánh Sinh Nhật, Cupcake, Bánh Quy, Phụ Kiện).
- Bấm vào thẻ sản phẩm bất kỳ để vào trang **Chi tiết sản phẩm** (`/san-pham/<id>`) xem thành phần, mô tả chi tiết, số lượng tồn kho và các bánh gợi ý liên quan.
- Bấm nút **"Xuất CSV"** nếu muốn tải tệp bảng tính thông tin bánh về máy tính.

### 2. Tìm kiếm sản phẩm
- Bấm vào biểu tượng kính lúp hoặc truy cập `/tim-kiem`.
- Nhập từ khoá tên bánh hoặc nguyên liệu (ví dụ: `kem cốm`, `donut`, `dâu tây`).
- Hệ thống hỗ trợ tìm kiếm không phân biệt chữ hoa/thường và đã được trang bị cơ chế tự động lọc chuỗi an toàn phòng chống mã độc script (XSS).

### 3. Giỏ hàng & Cập nhật số lượng
- Tại trang chi tiết hoặc danh sách sản phẩm, chọn số lượng và bấm **"Thêm vào giỏ hàng"**.
- Bấm biểu tượng giỏ hàng trên thanh điều hướng để vào xem trang **Giỏ hàng** (`/gio-hang`).
- Tại đây, bạn có thể:
  - Bấm nút **`+`** để tăng số lượng (tối đa bằng tồn kho thực tế).
  - Bấm nút **`−`** để giảm số lượng (giảm về 0 sẽ tự động gỡ khỏi giỏ).
  - Bấm **"Xoá"** để bỏ hẳn một loại bánh ra khỏi giỏ.
  - Bấm **"Xoá toàn bộ"** để làm mới giỏ hàng.
- Hệ thống áp dụng chính sách: **Miễn phí vận chuyển cho đơn hàng từ 200.000 đ** (dưới 200.000 đ phí vận chuyển là 20.000 đ).

### 4. Đặt hàng và Xác nhận
1. Từ giỏ hàng, bấm **"Đặt hàng"** để chuyển sang trang thanh toán (`/dat-hang`).
2. Điền đầy đủ thông tin nhận hàng:
   - Họ và tên người nhận.
   - Số điện thoại (bắt buộc đúng định dạng 10 chữ số, bắt đầu bằng số `0`).
   - Địa chỉ giao hàng cụ thể.
   - Phương thức thanh toán: Tiền mặt khi nhận hàng (COD) hoặc Chuyển khoản ngân hàng.
   - Ghi chú giao hàng (tuỳ chọn).
3. Bấm **"Xác nhận đặt hàng"**. Hệ thống sẽ kiểm tra tồn kho một lần nữa và chuyển sang trang **Xác nhận đơn hàng** (`/don-hang/<id>`).
4. Khách hàng có thể bấm **"Tải hoá đơn CSV"** để lưu lại hoá đơn chi tiết.

---

## PHẦN 2: HƯỚNG DẪN DÀNH CHO QUẢN TRỊ VIÊN (ADMIN)

### 1. Đăng nhập phân hệ quản trị
- Truy cập đường dẫn: `http://localhost:8000/admin/login` (hoặc bấm nút "Khu vực Quản trị" ở đầu trang).
- Tài khoản quản trị mặc định:
  - **Tên đăng nhập:** `admin`
  - **Mật khẩu:** `admin123`
- Đăng nhập thành công sẽ được chuyển hướng tự động vào Bảng điều khiển (`/admin/`).

### 2. Bảng điều khiển kinh doanh (Dashboard)
- Quan sát nhanh 4 chỉ số kinh doanh quan trọng:
  - Tổng doanh thu bán hàng và số tiền thực thu.
  - Tổng số lượng đơn hàng (phân loại đơn chờ duyệt, đang giao, hoàn tất).
  - Tổng số sản phẩm đang kinh doanh.
  - Tổng số danh mục bánh.
- Bảng **Cảnh báo tồn kho**: Liệt kê các bánh có số lượng tồn kho thấp ($\le 5$) hoặc đã hết hàng để kịp thời nướng mới/nhập thêm nguyên liệu.
- Bảng **Đơn hàng mới nhất**: Xem nhanh 5 đơn hàng khách vừa đặt cần xử lý ngay.

### 3. Quản lý sản phẩm bánh (`/admin/san-pham`)
- Xem danh sách toàn bộ sản phẩm với hình ảnh, giá bán, danh mục, tồn kho và trạng thái nổi bật.
- **Thêm bánh mới (`/admin/san-pham/them`):**
  - Điền tên bánh, chọn danh mục, đơn giá, số lượng ban đầu, mô tả ngắn và mô tả chi tiết.
  - Tải lên file ảnh mới từ máy tính hoặc chọn ảnh có sẵn trong hệ thống.
  - Slug đường dẫn sẽ được hệ thống tự động sinh tối ưu SEO.
- **Chỉnh sửa bánh (`/admin/san-pham/sua/<id>`):** Cập nhật giá bán, thay đổi tồn kho hoặc đổi ảnh.
- **Xoá bánh:** Chỉ cho phép xoá các bánh chưa từng phát sinh đơn hàng trong quá khứ để đảm bảo tính toàn vẹn dữ liệu kế toán. Với bánh đã có đơn, quản trị viên cập nhật tồn kho về `0` (Hết hàng).

### 4. Quản lý danh mục (`/admin/danh-muc`)
- Xem thống kê số lượng bánh hiện có trong từng danh mục.
- Thêm mới danh mục hoặc cập nhật tên/mô tả danh mục.
- **Bảo vệ toàn vẹn khoá ngoại:** Hệ thống tự động chặn xoá các danh mục đang có sản phẩm bên trong để tránh lỗi dữ liệu mồ côi (Orphaned records).

### 5. Quản lý đơn hàng & Lịch sử trạng thái (`/admin/don-hang`)
- Lọc đơn hàng theo trạng thái: Tất cả, Chờ xác nhận, Đang giao, Hoàn tất, Đã huỷ.
- Tìm kiếm đơn hàng theo mã đơn, họ tên khách hàng hoặc số điện thoại.
- Bấm vào đơn hàng để xem chi tiết từng chiếc bánh khách đã mua và giá tiền tại thời điểm đặt.
- Cập nhật trạng thái đơn hàng (ví dụ chuyển từ "Chờ xác nhận" sang "Đang giao" hoặc "Hoàn tất"). Mỗi lần cập nhật đều được hệ thống ghi nhận mốc thời gian vào bảng lịch sử `order_status_history`.
- Bấm **"Xuất hoá đơn CSV"** để in hoặc lưu trữ kế toán.

### 6. Đăng xuất
- Bấm nút **"Đăng xuất"** trên thanh tiêu đề quản trị để huỷ phiên làm việc an toàn.

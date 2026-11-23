# Báo Cáo Lập Luận Lựa Chọn Giấy Phép Bản Quyền (License Rationale)

Dự án: **Yuu Cake - Website Tiệm Bánh Trực Tuyến**  
Học phần: **Phần mềm Mã nguồn mở - Trường ĐH Khoa học, ĐH Huế**

---

## 1. Bối cảnh và mục tiêu dự án
Dự án Yuu Cake được xây dựng với mục tiêu:
1. Phục vụ học tập, nghiên cứu và thực hành xây dựng phần mềm thương mại điện tử bằng mã nguồn mở (Python, Flask, SQLAlchemy, Bootstrap).
2. Tạo điều kiện để các sinh viên, cộng đồng và các cửa hàng bánh nhỏ có thể tự do tham khảo, tái sử dụng, tùy biến và tích hợp vào hệ thống của mình mà không gặp rào cản pháp lý phức tạp.
3. Dự án sử dụng các thư viện mã nguồn mở có giấy phép cấp quyền (Permissive Licenses):
   - **Flask:** Giấy phép BSD 3-Clause.
   - **SQLAlchemy:** Giấy phép MIT.
   - **Bootstrap 5:** Giấy phép MIT.
   - **Werkzeug, Jinja2, WTForms:** Giấy phép BSD 3-Clause.

---

## 2. So sánh các loại giấy phép mã nguồn mở phổ biến

| Tiêu chí | MIT License | Apache License 2.0 | GNU GPLv3 | BSD 3-Clause |
| :--- | :--- | :--- | :--- | :--- |
| **Phân loại** | Permissive (Cấp quyền rộng rãi) | Permissive | Copyleft (Ràng buộc lây truyền) | Permissive |
| **Quyền sửa đổi & phân phối** | Hoàn toàn tự do | Hoàn toàn tự do | Tự do nhưng bắt buộc mở mã | Hoàn toàn tự do |
| **Sử dụng cho thương mại** | Cho phép | Cho phép | Cho phép nhưng phải mở mã nguồn | Cho phép |
| **Tích hợp vào phần mềm đóng**| Cho phép | Cho phép | Không cho phép | Cho phép |
| **Điều khoản sáng chế (Patent)** | Ngắn gọn, không phức tạp | Quy định chặt chẽ về sáng chế | Bảo vệ mạnh chống lại bằng sáng chế | Không quy định sáng chế |
| **Độ dài và độ phức tạp văn bản**| Rất ngắn, dễ hiểu, minh bạch | Dài, mang tính pháp lý doanh nghiệp | Rất dài và khắt khe | Ngắn gọn |

---

## 3. Lý do lựa chọn Giấy phép MIT (MIT License)

Nhóm phát triển quyết định lựa chọn **Giấy phép MIT** cho dự án Yuu Cake vì các lý do cốt lõi sau:

1. **Khả năng tương thích giấy phép tối đa (License Compatibility):**
   - Dự án phụ thuộc trực tiếp vào Flask, Jinja2, Werkzeug (BSD) và Bootstrap (MIT). Giấy phép MIT hoàn toàn tương thích và hài hoà với các phụ thuộc hiện có mà không gây xung đột pháp lý.
2. **Khuyến khích lan toả và ứng dụng thực tế:**
   - Các cửa hàng nhỏ hoặc lập trình viên khác có thể tải mã nguồn về, điều chỉnh màu sắc, sản phẩm, thậm chí đóng gói vào giải pháp riêng mà không bắt buộc phải mở mã nguồn các phần mềm liên quan của họ (điều mà GNU GPLv3 bắt buộc).
3. **Đơn giản, trong sáng và minh bạch:**
   - Văn bản giấy phép MIT rất súc tích, bất kỳ lập trình viên nào cũng có thể đọc hiểu rõ quyền và trách nhiệm của mình trong vài phút.
4. **Giới hạn trách nhiệm pháp lý rõ ràng (Disclaimer of Warranty & Liability):**
   - Giấy phép khẳng định phần mềm cung cấp theo hình thức "nguyên trạng" (AS IS). Tác giả không chịu trách nhiệm pháp lý hay nghĩa vụ bảo hành nếu bên thứ ba sử dụng phần mềm gặp rủi ro kinh doanh, giúp bảo vệ quyền lợi an toàn cho sinh viên và nhóm phát triển.

---

## 4. Kết luận
Lựa chọn giấy phép **MIT** thể hiện đúng tinh thần tự do, cởi mở của văn hoá mã nguồn mở, tối ưu hoá cơ hội chia sẻ tri thức và hoàn toàn đáp ứng xuất sắc các tiêu chí đánh giá của học phần Phần mềm Mã nguồn mở.

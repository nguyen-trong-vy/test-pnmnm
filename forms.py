"""
forms.py - Định nghĩa các biểu mẫu Flask-WTF và kiểm tra dữ liệu đầu vào (Validation).

Kiến thức Chương 5:
- Kế thừa FlaskForm để tự động tích hợp bảo vệ CSRF token.
- Sử dụng các bộ kiểm tra (Validators): DataRequired, Length, Regexp, Email, Optional, NumberRange.
- Khi dữ liệu không hợp lệ, Flask-WTF giữ lại toàn bộ dữ liệu người dùng vừa nhập và trả danh sách lỗi
  để giao diện hiển thị class is-invalid / invalid-feedback ngay bên dưới từng ô nhập.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp

from models import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_SHIPPING,
)


class AddToCartForm(FlaskForm):
    """Form thêm sản phẩm vào giỏ hàng từ trang chi tiết bánh."""

    quantity = IntegerField(
        "Số lượng",
        default=1,
        validators=[
            DataRequired(message="Vui lòng nhập số lượng."),
            NumberRange(min=1, message="Số lượng phải lớn hơn hoặc bằng 1."),
        ],
    )
    submit = SubmitField("Thêm vào giỏ hàng")


class CheckoutForm(FlaskForm):
    """
    Form thông tin khách hàng khi đặt hàng (Màn hình ④).
    Kiểm tra đầy đủ ràng buộc theo bài tập tổng hợp Chương 5-6:
    - Họ tên: bắt buộc.
    - Số điện thoại: bắt buộc, đúng 10 chữ số và bắt đầu bằng số 0.
    - Email: không bắt buộc, nhưng nếu nhập phải đúng định dạng email.
    - Địa chỉ giao hàng: bắt buộc.
    - Phương thức thanh toán: bắt buộc chọn 1 trong 2 hình thức.
    """

    customer_name = StringField(
        "Họ tên",
        validators=[
            DataRequired(message="Vui lòng nhập họ tên người nhận."),
            Length(min=2, max=120, message="Họ tên phải từ 2 đến 120 ký tự."),
        ],
    )
    phone = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(
                r"^0\d{9}$",
                message="Số điện thoại gồm đúng 10 chữ số và bắt đầu bằng số 0.",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Địa chỉ email không đúng định dạng."),
            Length(max=120, message="Email tối đa 120 ký tự."),
        ],
    )
    address = TextAreaField(
        "Địa chỉ giao hàng",
        validators=[
            DataRequired(message="Vui lòng nhập địa chỉ giao hàng cụ thể."),
            Length(min=6, max=300, message="Địa chỉ cần chi tiết hơn (tối thiểu 6 ký tự)."),
        ],
    )
    note = TextAreaField(
        "Ghi chú",
        validators=[
            Optional(),
            Length(max=300, message="Ghi chú tối đa 300 ký tự."),
        ],
    )
    payment_method = RadioField(
        "Phương thức thanh toán",
        choices=[
            ("cod", "Tiền mặt khi nhận hàng (COD)"),
            ("bank", "Chuyển khoản ngân hàng"),
        ],
        default="cod",
        validators=[DataRequired(message="Vui lòng chọn phương thức thanh toán.")],
    )
    submit = SubmitField("Xác nhận đặt hàng")


class ProductAdminForm(FlaskForm):
    """
    Biểu mẫu Thêm và Sửa sản phẩm dành cho Quản trị viên (Màn hình ⑧).
    Kiến thức Chương 5:
    - Bắt lỗi dữ liệu bằng WTForms validators (DataRequired, NumberRange, Length).
    - Hỗ trợ tải tệp ảnh lên bằng FileField và kiểm tra đuôi mở rộng bằng FileAllowed.
    - SelectField nạp danh mục động từ CSDL.
    """

    name = StringField(
        "Tên sản phẩm bánh",
        validators=[
            DataRequired(message="Vui lòng nhập tên sản phẩm bánh."),
            Length(min=2, max=150, message="Tên bánh phải từ 2 đến 150 ký tự."),
        ],
    )
    category_id = SelectField(
        "Danh mục bánh",
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn danh mục cho bánh.")],
    )
    price = IntegerField(
        "Giá bán (VNĐ)",
        validators=[
            DataRequired(message="Vui lòng nhập giá bán."),
            NumberRange(min=1000, max=50_000_000, message="Giá bán phải từ 1.000 đ trở lên."),
        ],
    )
    stock = IntegerField(
        "Số lượng tồn kho",
        default=10,
        validators=[
            DataRequired(message="Vui lòng nhập số lượng tồn kho."),
            NumberRange(min=0, max=10000, message="Số lượng tồn kho phải lớn hơn hoặc bằng 0."),
        ],
    )
    is_featured = BooleanField(
        "Đánh dấu là Sản phẩm nổi bật (Hiển thị tại trang chủ)"
    )
    short_desc = StringField(
        "Mô tả tóm tắt",
        validators=[
            DataRequired(message="Vui lòng nhập mô tả tóm tắt."),
            Length(max=255, message="Mô tả tóm tắt tối đa 255 ký tự."),
        ],
    )
    description = TextAreaField(
        "Mô tả chi tiết nguyên liệu & hương vị",
        validators=[
            DataRequired(message="Vui lòng nhập mô tả chi tiết."),
            Length(min=10, max=5000, message="Mô tả chi tiết cần tối thiểu 10 ký tự."),
        ],
    )
    image_file = FileField(
        "Tải lên tệp ảnh bánh mới (jpg, png, avif, webp)",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "avif", "webp"], "Chỉ chấp nhận tệp ảnh (.jpg, .png, .avif, .webp)!"),
        ],
    )
    existing_image = StringField(
        "Hoặc đường dẫn ảnh nội bộ (vd: images/products/sinh-nhat-1.avif)",
        validators=[Optional(), Length(max=255)],
    )
    submit = SubmitField("Lưu sản phẩm")


class CategoryAdminForm(FlaskForm):
    """
    Biểu mẫu Thêm và Sửa danh mục bánh dành cho Quản trị viên (Màn hình ⑨).
    Kiến thức Chương 5:
    - Bắt lỗi dữ liệu bằng WTForms validators.
    - Hỗ trợ tải tệp ảnh lên bằng FileField hoặc chọn ảnh nội bộ có sẵn.
    """

    name = StringField(
        "Tên danh mục bánh",
        validators=[
            DataRequired(message="Vui lòng nhập tên danh mục."),
            Length(min=2, max=100, message="Tên danh mục phải từ 2 đến 100 ký tự."),
        ],
    )
    description = TextAreaField(
        "Mô tả danh mục",
        validators=[
            Optional(),
            Length(max=500, message="Mô tả danh mục tối đa 500 ký tự."),
        ],
    )
    image_file = FileField(
        "Tải lên ảnh danh mục mới (jpg, png, avif, webp)",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "avif", "webp"], "Chỉ chấp nhận tệp ảnh (.jpg, .png, .avif, .webp)!"),
        ],
    )
    existing_image = StringField(
        "Hoặc đường dẫn ảnh có sẵn (vd: images/categories/banh-donut.avif)",
        validators=[Optional(), Length(max=255)],
    )
    submit = SubmitField("Lưu danh mục")


class OrderStatusUpdateForm(FlaskForm):
    """
    Biểu mẫu cập nhật trạng thái đơn đặt hàng dành cho Quản trị viên (Màn hình ⑪).
    Kiến thức Chương 5 & 6:
    - Sử dụng SelectField với các hằng số trạng thái từ models.py.
    - Cập nhật và ghi vết thời gian vào OrderStatusHistory.
    """

    status = SelectField(
        "Trạng thái đơn hàng",
        choices=[
            (ORDER_STATUS_PENDING, ORDER_STATUS_PENDING),
            (ORDER_STATUS_SHIPPING, ORDER_STATUS_SHIPPING),
            (ORDER_STATUS_COMPLETED, ORDER_STATUS_COMPLETED),
            (ORDER_STATUS_CANCELLED, ORDER_STATUS_CANCELLED),
        ],
        validators=[DataRequired(message="Vui lòng chọn trạng thái đơn hàng.")],
    )
    submit = SubmitField("Cập nhật trạng thái")


class AdminLoginForm(FlaskForm):
    """
    Biểu mẫu Đăng nhập dành cho Quản trị viên (/admin/login).
    Kiến thức Chương 5:
    - Bắt lỗi dữ liệu bằng WTForms validators.
    - PasswordField ẩn ký tự mật khẩu.
    """

    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập admin."),
            Length(min=3, max=50, message="Tên đăng nhập từ 3 đến 50 ký tự."),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[DataRequired(message="Vui lòng nhập mật khẩu.")],
    )
    submit = SubmitField("Đăng nhập Quản trị")





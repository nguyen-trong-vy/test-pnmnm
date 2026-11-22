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

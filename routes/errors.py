"""
routes/errors.py - Xử lý lỗi tập trung cho các mã 400, 404, 405 (Chương 3 - Câu 9).

Yêu cầu môn học:
- Một hàm xử lý chung bằng cách xếp chồng các decorator @app.errorhandler(400/404/405).
- Nếu URL bắt đầu bằng /api/ -> trả JSON {"error": ..., "detail": ...} đúng mã trạng thái.
- Nếu URL giao diện web -> render trang error.html kế thừa base.html đúng mã trạng thái.
- Giải thích câu hỏi vấn đáp: dùng được biến `request` trong errorhandler dù không phải
  view function vì Flask vẫn đang giữ nguyên Request Context của yêu cầu gây lỗi.
"""

from flask import Flask, jsonify, render_template, request

ERROR_TITLES = {
    400: "Dữ liệu không hợp lệ",
    404: "Không tìm thấy trang hoặc dữ liệu",
    405: "Phương thức HTTP không được hỗ trợ",
}


def register_error_handlers(app: Flask) -> None:
    """Đăng ký bộ xử lý lỗi thống nhất cho ứng dụng Flask."""

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(405)
    def handle_http_error(error):
        code = getattr(error, "code", 500)
        title = ERROR_TITLES.get(code, "Đã xảy ra lỗi")
        detail = getattr(error, "description", "Yêu cầu không thể thực hiện.")

        # Đường dẫn API -> luôn trả JSON đúng mã lỗi HTTP
        if request.path.startswith("/api/"):
            return jsonify({"error": title, "detail": detail}), code

        # Đường dẫn Web -> trả trang HTML đẹp kế thừa base.html đúng mã lỗi HTTP
        return render_template("error.html", code=code, title=title, detail=detail), code

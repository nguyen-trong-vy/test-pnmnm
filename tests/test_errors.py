"""
tests/test_errors.py - Kiểm thử bộ xử lý lỗi tập trung 400, 404, 405 (Chương 3).
"""


def test_404_html_and_json(client):
    # Lỗi 404 trang web thông thường -> trả HTML
    res_html = client.get("/duong-dan-khong-ton-tai")
    assert res_html.status_code == 404
    assert "text/html" in res_html.content_type
    assert "404" in res_html.get_data(as_text=True)

    # Lỗi 404 đường dẫn API -> trả JSON
    res_json = client.get("/api/endpoint-khong-ton-tai")
    assert res_json.status_code == 404
    assert res_json.is_json
    data = res_json.get_json()
    assert "error" in data
    assert "detail" in data


def test_405_method_not_allowed(client):
    # Gửi DELETE vào route chỉ nhận GET -> 405
    res = client.delete("/")
    assert res.status_code == 405

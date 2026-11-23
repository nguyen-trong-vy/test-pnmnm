"""
tests/conftest.py - Fixtures kiểm thử tự động cho ứng dụng Tiệm bánh Yuu Cake.
"""

import pytest
from app import create_app
from extensions import db
from models import User
from seed import seed_database


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key-for-pytest"
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"


@pytest.fixture
def app():
    """Khởi tạo ứng dụng Flask với CSDL ảo trong RAM (in-memory) và nạp dữ liệu mẫu."""
    app_instance = create_app(config_class=TestConfig)

    with app_instance.app_context():
        db.create_all()
        seed_database()
        yield app_instance
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Khách hàng web thông thường (chưa đăng nhập admin)."""
    return app.test_client()


@pytest.fixture
def admin_client(app):
    """Khách hàng đã đăng nhập tài khoản Quản trị viên (admin)."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["admin_logged_in"] = True
        sess["admin_user"] = {
            "id": 1,
            "username": "admin",
            "full_name": "Quản trị viên Yuu Cake",
        }
    return client

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_search_cars(logged_in_page: Page):
    """TC-CAR-R01: Tìm kiếm xe theo tên/biển số (TODO)"""
    # TODO: Nhập từ khóa và kiểm tra kết quả bảng
    pass

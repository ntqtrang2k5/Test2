import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_delete_car(logged_in_page: Page):
    """TC-CAR-D01: Xóa xe khỏi hệ thống (TODO)"""
    # TODO: Thực hiện xóa xe và xác nhận kết quả
    pass

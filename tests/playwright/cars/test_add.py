import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_add_new_car(logged_in_page: Page):
    """TC-CAR-C01: Thêm xe mới vào hệ thống (TODO)"""
    # TODO: Điền form thêm xe và kiểm tra lưu thành công
    pass

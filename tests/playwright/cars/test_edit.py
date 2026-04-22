import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_edit_car_info(logged_in_page: Page):
    """TC-CAR-U01: Chỉnh sửa thông tin xe (TODO)"""
    # TODO: Tìm xe và cập nhật các trường thông tin
    pass

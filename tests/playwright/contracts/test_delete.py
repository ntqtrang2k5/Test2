import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_delete_preorder_only(logged_in_page: Page):
    """TC-HD-D01: Chỉ cho phép xóa hợp đồng đặt trước (TODO)"""
    # TODO: Kiểm tra nút xóa hiện/ẩn tùy theo trạng thái
    pass

@pytest.mark.django_db
def test_delete_active_restricted(logged_in_page: Page):
    """TC-HD-D02: Không cho phép xóa hợp đồng đang thuê/đã trả (TODO)"""
    pass

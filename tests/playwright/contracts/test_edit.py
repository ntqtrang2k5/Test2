import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_edit_preorder_contract(logged_in_page: Page):
    """TC-HD-U01: Chỉnh sửa hợp đồng đặt trước (TODO)"""
    # TODO: Tìm hợp đồng ở trạng thái 'Đặt trước' và chỉnh sửa
    pass

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_contract_extension(logged_in_page: Page):
    """TC-HD-EXT: Gia hạn hợp đồng đang thuê (TODO)"""
    # TODO: Tìm hợp đồng 'Đang thuê' và gia hạn ngày trả
    pass

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_create_contract_basic(logged_in_page: Page):
    """TC-HD-C01: Thêm mới hợp đồng - Luồng cơ bản (TODO)"""
    page = logged_in_page
    page.goto("/hop-dong/tao-moi/")
    # TODO: Thực hiện các bước tạo hợp đồng
    pass

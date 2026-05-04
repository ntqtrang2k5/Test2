import pytest
from playwright.sync_api import Page, expect
import re

@pytest.mark.django_db
def test_TC_HD_D01(logged_in_page: Page):
    """
    Steps:
    Xóa hợp đồng đặt trước thành công
    1. Vào danh sách Hợp đồng
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đặt trước"
    dat_truoc_rows = page.locator("tbody tr[data-status='Đặt trước']")
    
    if dat_truoc_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đặt trước' để thực hiện test.")
        
    first_row = dat_truoc_rows.first
    # Lấy mã hợp đồng để kiểm tra sau khi xóa
    contract_id = first_row.locator("td").first.inner_text()

    # 2. Click vào nút "Xem" của hợp đồng đó
    first_row.locator(".btn-view-premium").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 3. Bấm nút xóa và xử lý các dialog
    dialog_messages = []
    def handle_dialog(dialog):
        dialog_messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", handle_dialog)

    # Giả sử nút xóa có role là 'button' và tên là 'XÓA'
    page.get_by_role('button', name='XÓA').click()

    # Đợi một chút để cả hai dialog có thời gian xuất hiện và được xử lý
    page.wait_for_timeout(1000)

    # 4. Kiểm tra các thông báo
    warning_message = "CẢNH BÁO: Bạn có chắc chắn muốn XÓA VĨNH VIỄN hợp đồng này không?\nMọi dòng tiền liên quan sẽ bị xóa khỏi hệ thống tài chính."
    success_message = "Đã xóa hợp đồng và cập nhật lại dòng tiền!"
    
    assert warning_message in dialog_messages, f"Không thấy thông báo cảnh báo. Các thông báo đã hiện: {dialog_messages}"
    assert success_message in dialog_messages, f"Không thấy thông báo thành công. Các thông báo đã hiện: {dialog_messages}"

    # 5. Kiểm tra đã quay lại trang danh sách
    expect(page).to_have_url(re.compile(r"/hop-dong/"))

    # 6. Kiểm tra hợp đồng đã bị xóa khỏi danh sách
    search_input = page.get_by_placeholder("Tìm kiếm Mã HĐ, Tên khách, Xe...")
    search_input.fill(contract_id)
    page.wait_for_timeout(500)
    
    visible_rows = page.locator("tbody tr:visible")
    assert visible_rows.count() == 0, f"Hợp đồng {contract_id} vẫn còn tồn tại sau khi xóa."

@pytest.mark.django_db
def test_TC_HD_D02(logged_in_page: Page):
    """
    Steps:
    Không xóa hợp đồng đang thuê
    1. Vào danh sách Hợp đồng
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đang thuê"
    dang_thue_rows = page.locator("tbody tr[data-status='Đang thuê']")
    
    if dang_thue_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đang thuê' để thực hiện test.")
        
    # 2. Click vào nút "Xem" của hợp đồng đó
    first_row = dang_thue_rows.first
    first_row.locator(".btn-view-premium").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 3. Xác nhận nút "XÓA" không hiển thị
    delete_button = page.get_by_role('button', name='XÓA')
    expect(delete_button).not_to_be_visible()

@pytest.mark.django_db
def test_TC_HD_D03(logged_in_page: Page):
    """
    Steps:
    Không xóa hợp đồng đã trả
    1. Vào danh sách Hợp đồng
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đã trả xe" bằng cách tìm text trong hàng
    completed_rows = page.locator("tbody tr:has-text('Đã trả xe')")
    
    if completed_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đã trả xe' để thực hiện test.")
        
    # 2. Click vào nút "Xem" của hợp đồng đó
    first_row = completed_rows.first
    first_row.locator(".btn-view-premium").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 3. Xác nhận nút "XÓA" không hiển thị
    delete_button = page.get_by_role('button', name='XÓA')
    expect(delete_button).not_to_be_visible()

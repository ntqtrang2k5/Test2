import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
import re

@pytest.mark.django_db
def test_TC_HD_GH01(logged_in_page: Page):
    """
    TC-HD-GH01: Gia hạn thành công
    1. Chọn ngẫu nhiên hợp đồng ở trạng thái "Đang thuê".
    2. Chọn chỉnh sửa thời gian trả xe hợp lệ.
    3. Bấm Lưu và xác nhận thông báo thành công.
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đang thuê" và click vào nút "Xem" của nó
    dang_thue_rows = page.locator("tbody tr[data-status='Đang thuê']")
    
    if dang_thue_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đang thuê' để thực hiện test.")
        
    first_dang_thue_row = dang_thue_rows.first
    first_dang_thue_row.locator(".btn-view-premium").click()

    # Chờ trang chi tiết/chỉnh sửa tải xong
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 2. Chỉnh sửa thời gian trả xe hợp lệ
    end_date_input = page.locator("#d-end-date")
    old_end_date_str = end_date_input.input_value()
    old_end_date = datetime.strptime(old_end_date_str, "%d/%m/%Y")
    
    total_price_element = page.locator("#display-total-price")
    old_total_price_text = total_price_element.inner_text()

    # Tính ngày trả xe mới (thêm 2 ngày)
    new_end_date = old_end_date + timedelta(days=2)
    new_end_date_str = new_end_date.strftime("%d/%m/%Y")

    # Cập nhật ngày trả xe mới bằng cách truy cập trực tiếp vào instance flatpickr của element
    script = f"document.querySelector('#d-end-date')._flatpickr.setDate('{new_end_date_str}', true);"
    page.evaluate(script)

    # Chờ cho đến khi tổng tiền được cập nhật (thay vì chờ cố định)
    expect(total_price_element).not_to_have_text(old_total_price_text)

    # Lấy giá trị mới và so sánh
    new_total_price_text = total_price_element.inner_text()
    old_total_price = int(old_total_price_text.replace(".", "").replace(" đ", ""))
    new_total_price = int(new_total_price_text.replace(".", "").replace(" đ", ""))
    assert new_total_price > old_total_price, "Tổng tiền mới không lớn hơn tổng tiền cũ sau khi gia hạn."

    # 3. Bấm Lưu và xác nhận thông báo
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.accept()

    page.on("dialog", handle_dialog)

    # Dựa trên HTML: <button ...> <i ...></i> LƯU </button>
    page.get_by_role('button', name='LƯU').click()
    page.wait_for_timeout(500)

    assert dialog_message == "Cập nhật hợp đồng thành công!", f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

@pytest.mark.django_db
def test_TC_HD_GH02(logged_in_page: Page):
    """
    TC-HD-GH02: Gia hạn không thành công vì ngày trả xe không hợp lệ
    1. Chọn xem hợp đồng đang thuê.
    2. Chọn chỉnh sửa thời gian trả xe không hợp lệ (nhỏ hơn ngày cũ).
    3. Bấm Lưu và xác nhận thông báo lỗi.
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đang thuê" và click vào nút "Xem" của nó
    dang_thue_rows = page.locator("tbody tr[data-status='Đang thuê']")
    
    if dang_thue_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đang thuê' để thực hiện test.")
        
    first_dang_thue_row = dang_thue_rows.first
    first_dang_thue_row.locator(".btn-view-premium").click()

    # Chờ trang chi tiết/chỉnh sửa tải xong
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 2. Chỉnh sửa thời gian trả xe không hợp lệ
    end_date_input = page.locator("#d-end-date")
    old_end_date_str = end_date_input.input_value()
    old_end_date = datetime.strptime(old_end_date_str, "%d/%m/%Y")

    # Tính ngày trả xe mới (lùi lại 2 ngày)
    new_end_date = old_end_date - timedelta(days=2)
    new_end_date_str = new_end_date.strftime("%d/%m/%Y")

    # Cập nhật ngày trả xe mới
    script = f"document.querySelector('#d-end-date')._flatpickr.setDate('{new_end_date_str}', true);"
    page.evaluate(script)
    page.wait_for_timeout(500)

    # 3. Bấm Lưu và xác nhận thông báo lỗi
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.accept()

    page.on("dialog", handle_dialog)

    page.get_by_role('button', name='LƯU').click()
    page.wait_for_timeout(500)

    expected_error = "Lỗi: Gia hạn: Ngày kết thúc mới phải lớn hơn ngày kết thúc hiện tại!"
    assert dialog_message == expected_error, f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

@pytest.mark.django_db
def test_TC_HD_GH03(logged_in_page: Page):
    """
    TC-HD-GH03: Thoát trang thì hiện pop up xác nhận
    1. Chọn xem hợp đồng đang thuê.
    2. Chỉnh sửa thời gian trả xe hợp lệ.
    3. Bấm qua tab khác và xác nhận thông báo.
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm một hợp đồng "Đang thuê" và click vào nút "Xem" của nó
    dang_thue_rows = page.locator("tbody tr[data-status='Đang thuê']")
    
    if dang_thue_rows.count() == 0:
        pytest.fail("Không tìm thấy hợp đồng nào ở trạng thái 'Đang thuê' để thực hiện test.")
        
    first_dang_thue_row = dang_thue_rows.first
    first_dang_thue_row.locator(".btn-view-premium").click()

    # Chờ trang chi tiết/chỉnh sửa tải xong
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/hop-dong/(chi-tiet|detail)/"))

    # 2. Chỉnh sửa thời gian trả xe để làm "dirty" form
    end_date_input = page.locator("#d-end-date")
    old_end_date_str = end_date_input.input_value()
    old_end_date = datetime.strptime(old_end_date_str, "%d/%m/%Y")

    new_end_date = old_end_date + timedelta(days=2)
    new_end_date_str = new_end_date.strftime("%d/%m/%Y")

    script = f"document.querySelector('#d-end-date')._flatpickr.setDate('{new_end_date_str}', true);"
    page.evaluate(script)
    page.wait_for_timeout(500)

    # 3. Bấm qua tab khác và xác nhận thông báo
    dialog_message = None
    dialog_appeared = False
    def handle_dialog(dialog):
        nonlocal dialog_message, dialog_appeared
        dialog_appeared = True
        dialog_message = dialog.message
        dialog.dismiss() # Hủy việc rời trang

    page.on("dialog", handle_dialog)

    # Click vào tab "Tạo hợp đồng" để kích hoạt sự kiện
    page.locator("#nav-create-contract").click()
    page.wait_for_timeout(500)

    expected_message = "Thông tin chưa được lưu. Bạn có chắc chắn muốn rời khỏi trang này?"
    assert dialog_appeared, "Không thấy pop-up xác nhận rời trang."
    assert dialog_message == expected_message, f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

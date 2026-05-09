import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db
def test_TC_HD_R01(logged_in_page: Page):
    """
    Steps:
    Mở màn hình xem hợp đồng
    1. Chọn nút “Hợp đồng thuê”
    Expected:
    Hiển thị màn hình danh sách hợp đồng
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    # 1. Mở URL của màn hình danh sách hợp đồng
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 2. Kiểm tra xem tiêu đề của bảng danh sách có đúng không
    # Dựa trên HTML: <span id="list-table-title">Hợp đồng thuê</span>
    title_span = page.locator("#list-table-title")
    
    # 3. Xác nhận tiêu đề được hiển thị và có đúng nội dung
    expect(title_span).to_be_visible()
    expect(title_span).to_have_text("Hợp đồng thuê")

@pytest.mark.django_db
def test_TC_HD_R02(logged_in_page: Page):
    """
    Steps:
    Tìm hợp đồng theo mã / tên khách
    1. Nhập keyword (mã hợp đồng hoặc tên khách hàng)
2. Bấm tìm kiếm
    Expected:
    Hiển thị danh sách hợp đồng phù hợp: Mã hợp đồng,Khách hàng, Xe thuê, Thời gian thuê, Trạng thái, Tổng tiền, Thao tác
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # Giả sử chúng ta tìm kiếm hợp đồng có mã "HD001"
    search_keyword = "HD001"

    # 1. Nhập keyword vào ô tìm kiếm
    search_input = page.get_by_placeholder("Tìm kiếm Mã HĐ, Tên khách, Xe...")
    search_input.fill(search_keyword)

    # 2. Chờ kết quả tải lại (do có oninput event)
    page.wait_for_timeout(500) # Đợi một chút để JS áp dụng bộ lọc

    # 3. Kiểm tra xem kết quả có hiển thị đúng không
    # Lấy tất cả các dòng đang hiển thị trong bảng
    visible_rows = page.locator("tbody tr:visible")
    
    # Đảm bảo chỉ có một dòng được hiển thị
    expect(visible_rows).to_have_count(1)

    # Kiểm tra dòng duy nhất đó có chứa keyword đã tìm
    expect(visible_rows).to_contain_text(search_keyword)

    # 4. Kiểm tra sự hiện diện của các cột quan trọng trong header
    table_header = page.locator("thead")
    expect(table_header).to_contain_text("Mã HĐ")
    expect(table_header).to_contain_text("Khách hàng")
    expect(table_header).to_contain_text("Xe thuê")
    expect(table_header).to_contain_text("Thời gian thuê")
    expect(table_header).to_contain_text("Trạng thái")
    expect(table_header).to_contain_text("Tổng tiền")
    expect(table_header).to_contain_text("Thao tác")

@pytest.mark.django_db
def test_TC_HD_R03(logged_in_page: Page):
    """
    Steps:
    Không tìm thấy hợp đồng khi nhập từ khóa
    1. Nhập keyword không tồn tại
    Expected:
    Không hiển thị dữ liệu
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Nhập một keyword không tồn tại
    search_keyword = "KHONGTONTAI123"
    search_input = page.get_by_placeholder("Tìm kiếm Mã HĐ, Tên khách, Xe...")
    search_input.fill(search_keyword)

    # 2. Chờ kết quả tải lại
    page.wait_for_timeout(500)

    # 3. Kiểm tra rằng không có hàng dữ liệu nào được hiển thị
    visible_rows = page.locator("tbody tr:visible")
    expect(visible_rows).to_have_count(0)

    # 4. (Tùy chọn) Kiểm tra xem có thông báo "Không tìm thấy" hay không.
    # Giả sử có một hàng đặc biệt cho trường hợp này, ví dụ:
    # no_results_row = page.locator("#no-results-row")
    # expect(no_results_row).to_be_visible()
    # expect(no_results_row).to_contain_text("Không tìm thấy hợp đồng nào.")

@pytest.mark.django_db
def test_TC_HD_R05(logged_in_page: Page):
    """
    Steps:
    Lọc hợp đồng “Tất cả”
    1. chọn filter “Tất cả”
    Expected:
    Hiện danh sách tất cả hợp đồng theo; Mã HĐ, Khách hàng, Xe thuê, Thời gian thuê, Trạng thái, Tổng tiền, Thao tác
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Lấy số lượng hợp đồng từ tab "TẤT CẢ"
    # Dựa trên HTML: <div class="tab-value" id="count-all">36</div>
    count_all_text = page.locator("#count-all").inner_text()
    expected_count = int(count_all_text)

    # 2. Click vào tab "TẤT CẢ"
    # Dựa trên HTML: <div class="summary-card-tab tab-teal" onclick="filterContractList('all', this)">
    all_tab = page.locator(".summary-card-tab.tab-teal")
    all_tab.click()

    # 3. Chờ cho bộ lọc được áp dụng
    page.wait_for_timeout(500)

    # 4. Đếm số lượng hàng đang hiển thị trong bảng
    visible_rows = page.locator("tbody tr:visible")
    
    # 5. So sánh số lượng hàng với số lượng mong đợi
    expect(visible_rows).to_have_count(expected_count)

@pytest.mark.django_db
def test_TC_HD_R06(logged_in_page: Page):
    """
    Steps:
    Lọc hợp đồng “Đặt trước”
    1. chọn Đặt trước
    Expected:
    Chỉ hiển thị hợp đồng đặt trước
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm tab "ĐẶT TRƯỚC" và lấy số lượng hiển thị
    dat_truoc_tab = page.locator(".summary-card-tab:has-text('ĐẶT TRƯỚC')")
    count_text = dat_truoc_tab.locator(".tab-value").inner_text()
    expected_count = int(count_text)

    # 2. Click vào tab "ĐẶT TRƯỚC"
    dat_truoc_tab.click()

    # 3. Chờ cho bộ lọc được áp dụng
    page.wait_for_timeout(500)

    # 4. Lấy tất cả các dòng đang hiển thị
    visible_rows = page.locator("tbody tr:visible")

    # 5. Kiểm tra số lượng hàng có khớp với số lượng trên tab không
    expect(visible_rows, f"Số lượng hợp đồng hiển thị ({visible_rows.count()}) không khớp với con số trên tab ({expected_count}).").to_have_count(expected_count)

    # 6. Nếu có hàng nào được hiển thị, kiểm tra trạng thái của từng hàng
    if expected_count > 0:
        for row in visible_rows.all():
            # Giả sử cột trạng thái là cột thứ 5 (index 4)
            status_cell = row.locator("td").nth(4)
            expect(status_cell).to_contain_text("Đặt trước")
    else:
        # In ra thông báo nếu không có dữ liệu để kiểm tra
        print("Không có hợp đồng nào ở trạng thái 'Đặt trước' để kiểm tra.")

@pytest.mark.django_db
def test_TC_HD_R08(logged_in_page: Page):
    """
    Steps:
    Lọc hợp đồng “Quá hạn”
    1. chọn Quá hạn
    Expected:
    Chỉ hiển thị hợp đồng quá hạn
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm tab "ĐANG THUÊ" và lấy số lượng hiển thị
    dang_thue_tab = page.locator(".summary-card-tab:has-text('ĐANG THUÊ')")
    count_text = dang_thue_tab.locator(".tab-value").inner_text()
    expected_count = int(count_text)

    # 2. Click vào tab "ĐANG THUÊ"
    dang_thue_tab.click()

    # 3. Chờ cho bộ lọc được áp dụng
    page.wait_for_timeout(500)

    # 4. Lấy tất cả các dòng đang hiển thị
    visible_rows = page.locator("tbody tr:visible")

    # 5. Kiểm tra số lượng hàng có khớp với số lượng trên tab không
    expect(visible_rows, f"Số lượng hợp đồng hiển thị ({visible_rows.count()}) không khớp với con số trên tab ({expected_count}).").to_have_count(expected_count)

    # 6. Nếu có hàng nào được hiển thị, kiểm tra trạng thái của từng hàng
    if expected_count > 0:
        for row in visible_rows.all():
            # Giả sử cột trạng thái là cột thứ 5 (index 4)
            status_cell = row.locator("td").nth(4)
            expect(status_cell).to_contain_text("Đang thuê")
    else:
        # In ra thông báo nếu không có dữ liệu để kiểm tra
        print("Không có hợp đồng nào ở trạng thái 'Đang thuê' để kiểm tra.")

@pytest.mark.django_db
def test_TC_HD_R09(logged_in_page: Page):
    """
    Steps:
    Lọc hợp đồng “Đã trả”
    1. chọn Đã trả
    Expected:
    Chỉ hiển thị hợp đồng đã trả
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/")

    # 1. Tìm tab "QUÁ HẠN" và lấy số lượng hiển thị
    qua_han_tab = page.locator(".summary-card-tab:has-text('QUÁ HẠN')")
    count_text = qua_han_tab.locator(".tab-value").inner_text()
    expected_count = int(count_text)

    # 2. Click vào tab "QUÁ HẠN"
    qua_han_tab.click()

    # 3. Chờ cho bộ lọc được áp dụng
    page.wait_for_timeout(500)

    # 4. Lấy tất cả các dòng đang hiển thị
    visible_rows = page.locator("tbody tr:visible")

    # 5. Kiểm tra số lượng hàng có khớp với số lượng trên tab không
    expect(visible_rows, f"Số lượng hợp đồng hiển thị ({visible_rows.count()}) không khớp với con số trên tab ({expected_count}).").to_have_count(expected_count)

    # 6. Nếu có hàng nào được hiển thị, kiểm tra trạng thái của từng hàng
    if expected_count > 0:
        for row in visible_rows.all():
            # Giả sử cột trạng thái là cột thứ 5 (index 4)
            status_cell = row.locator("td").nth(4)
            expect(status_cell).to_contain_text("Quá hạn")
    else:
        # In ra thông báo nếu không có dữ liệu để kiểm tra
        print("Không có hợp đồng nào ở trạng thái 'Quá hạn' để kiểm tra.")

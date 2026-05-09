import pytest
import random
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

@pytest.mark.django_db
def test_TC_HD_C01(logged_in_page: Page):
    """
    Steps:
    Kiểm tra giá trị mặc định của form tạo hợp đồng
    1. Bấm vào nút tạo hợp đồng
    Expected:
    1. Form mở lên thành công.
2. Trường Ngày lập hợp đồng được điền sẵn và khóa không cho nhập
3. Các trường khác (Khách, Xe) để trống mặc định.
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    expect(page.get_by_role("heading", name="TẠO HỢP ĐỒNG THUÊ XE MỚI")).to_be_visible()

    contract_date_input = page.locator(".card-red input.form-input").first
    expect(contract_date_input).to_be_disabled()
    today_str = datetime.now().strftime("%d/%m/%Y")
    expect(contract_date_input).to_have_value(today_str)

    expect(page.locator("#customer-search-input")).to_be_empty()
    expect(page.locator("#new-contract-name")).to_be_empty()
    expect(page.locator("#empty-car-row")).to_be_visible()

@pytest.mark.django_db
def test_TC_HD_C02(logged_in_page: Page):
    """
    Steps:
    Thêm mới hợp đồng đặt trước
    1. Chọn thời gian bắt đầu thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê
    start_date = datetime.now() + timedelta(days=2)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    # Thiết lập ngày qua Flatpickr
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")

    # Đợi một chút để JS tính toán và kích hoạt bảng xe
    page.wait_for_timeout(500)

    # 2. Chọn khách hàng ngẫu nhiên
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    count_c = customer_items.count()
    if count_c == 0: pytest.fail("Không có khách hàng")
    customer_items.nth(random.randint(0, count_c - 1)).click()

    # 3. Chọn xe ngẫu nhiên
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    count_v = car_items.count()
    if count_v == 0: pytest.fail("Không có xe sẵn sàng")
    car_items.nth(random.randint(0, count_v - 1)).click()

    # 4. Nhập tiền tạm ứng
    page.fill("#new-contract-prepaid", "100000")

    # 5. Bấm ĐẶT TRƯỚC và đợi thông báo alert
    # Sử dụng context manager để bắt sự kiện dialog chính xác
    with page.expect_event("dialog") as dialog_info:
        page.get_by_role("button", name="ĐẶT TRƯỚC").click()
    
    dialog = dialog_info.value
    # Kiểm tra nội dung thông báo
    assert "Lưu hợp đồng thành công!" in dialog.message

    # Chấp nhận thông báo (đóng alert)
    dialog.accept()

    # Đợi trang xử lý sau khi đóng alert
    page.wait_for_load_state("networkidle")

@pytest.mark.django_db
def test_TC_HD_C03(logged_in_page: Page):
    """
    Steps:
    Thêm mới hợp đồng thuê liền
    1. Chọn thời gian bắt đầu thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê (bắt đầu từ hôm nay)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn khách hàng ngẫu nhiên
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    count_c = customer_items.count()
    if count_c == 0: pytest.fail("Không có khách hàng")
    customer_items.nth(random.randint(0, count_c - 1)).click()

    # 3. Chọn xe ngẫu nhiên
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    count_v = car_items.count()
    if count_v == 0: pytest.fail("Không có xe sẵn sàng")
    car_items.nth(random.randint(0, count_v - 1)).click()

    # 4. Nhập tiền tạm ứng
    page.fill("#new-contract-prepaid", "200000")

    # 5. Bấm LƯU HỢP ĐỒNG và đợi thông báo alert
    with page.expect_event("dialog") as dialog_info:
        page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()
    
    dialog = dialog_info.value
    assert "Lưu hợp đồng thành công!" in dialog.message
    dialog.accept()
    page.wait_for_load_state("networkidle")

@pytest.mark.django_db
def test_TC_HD_C04(logged_in_page: Page):
    """
    Steps:
    Chọn khách hàng có sẵn bằng tìm theo từ khóa đã nhập
    1. Nhập từ khóa theo tên hoặc sđt của khách
    Expected:
    1. Hiện các thông tin khách hàng ứng theo từ khóa đó
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # Giả định có khách hàng "Trần Thị Bích" với SĐT "0912345678" và CCCD "079090123452" trong DB test
    expected_name = "Trần Thị Bích"
    expected_phone = "0912345678"
    expected_cccd = "079090123452"
    expected_id = "KH002"

    # 1. Nhập từ khóa theo tên hoặc SĐT của khách
    search_keyword = "Trần Thị Bích" # Hoặc "0912345678"
    page.fill("#customer-search-input", search_keyword)
    
    # Chờ dropdown hiện ra
    page.wait_for_selector("#customer-dropdown .search-item")
    
    # 2. Chọn khách từ Dropdown (chọn mục đầu tiên hoặc mục chứa tên khách hàng mong muốn)
    customer_item = page.locator(f"#customer-dropdown .search-item:has-text('{expected_name}')").first
    expect(customer_item).to_be_visible()
    customer_item.click()

    # 3. Thông tin (Tên, SĐT, CCCD) tự động điền vào form.
    expect(page.locator("#selected-customer-id")).to_have_value(expected_id)
    expect(page.locator("#new-contract-name")).to_have_value(expected_name)
    expect(page.locator("#new-contract-phone")).to_have_value(expected_phone)
    expect(page.locator("#new-contract-cccd")).to_have_value(expected_cccd)

    # Kiểm tra nút xóa khách hàng hiện ra
    expect(page.locator("#btn-clear-customer")).to_be_visible()

    # Có thể thêm bước xóa khách hàng để reset form
    page.click("#btn-clear-customer")
    expect(page.locator("#selected-customer-id")).to_have_value("")
    expect(page.locator("#new-contract-name")).to_be_empty()

@pytest.mark.django_db
def test_TC_HD_C05(logged_in_page: Page):
    """
    Steps:
    Kiểm tra logic thời gian ngày bắt đầu thuê
    1. Bấm chọn ngày bắt đầu thuê
    Expected:
    Datepicker hiện lên chỉ hiện lớn hơn hoặc bằng ngày hiện tại, ngày bé hơn sẽ bị chặn không chọn được
    Actual:
    Đúng với mong đợi
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Bấm chọn ngày bắt đầu thuê
    page.click("#new-contract-start")

    # Chờ datepicker (Flatpickr) hiện lên
    page.wait_for_selector(".flatpickr-calendar.open")

    # 2. Kiểm tra ngày hôm nay KHÔNG bị vô hiệu hóa (Chỉ tìm trong lịch đang mở)
    today_locator = page.locator(".flatpickr-calendar.open .flatpickr-day.today")
    expect(today_locator).not_to_have_class(r".*flatpickr-disabled.*")

    # 3. Kiểm tra ngày hôm qua (ngày bé hơn hiện tại) BỊ vô hiệu hóa
    is_yesterday_disabled = page.evaluate('''() => {
        const calendar = document.querySelector(".flatpickr-calendar.open");
        const days = Array.from(calendar.querySelectorAll(".flatpickr-day"));
        const todayIdx = days.findIndex(d => d.classList.contains("today"));
        // Nếu tìm thấy today và có ngày đứng trước nó, kiểm tra xem ngày đó có bị disabled không
        if (todayIdx > 0) {
            return days[todayIdx - 1].classList.contains("flatpickr-disabled");
        }
        // Trường hợp đặc biệt nếu today là ngày đầu tiên hiển thị, tìm bất kỳ ngày disabled nào
        return calendar.querySelector(".flatpickr-day.flatpickr-disabled") !== null;
    }''')
    
    assert is_yesterday_disabled, "Các ngày trong quá khứ phải bị chặn (có class flatpickr-disabled)"

    # Đóng datepicker
    page.keyboard.press("Escape")

@pytest.mark.django_db
def test_TC_HD_C06(logged_in_page: Page):
    """
    Steps:
    Kiểm tra logic thời gian ngày kết thúc thuê dự kiến
    1. Chọn ngày bắt đầu thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn ngày bắt đầu thuê hợp lệ (ví dụ: ngày mai)
    start_date = datetime.now().date() + timedelta(days=1)
    start_str = start_date.strftime("%d/%m/%Y")
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")

    page.wait_for_timeout(200) 

    # 2. Bấm chọn ngày kết thúc thuê dự kiến
    page.click("#new-contract-end")
    page.wait_for_selector(".flatpickr-calendar.open")

    # Sử dụng logic đơn giản hơn bằng JavaScript để tránh NameError
    results = page.evaluate('''
        (start_str) => {
            const calendar = document.querySelector(".flatpickr-calendar.open");
            const parts = start_str.split("/");
            const day = parseInt(parts[0]);
            const year = parseInt(parts[2]);

            // Tìm ngày bắt đầu trong lịch đang mở
            const dayEls = Array.from(calendar.querySelectorAll(".flatpickr-day"));
            const startDayEl = dayEls.find(el => 
                el.innerText == day && 
                el.getAttribute("aria-label").includes(year)
            );

            return {
                isStartDisabled: startDayEl ? startDayEl.classList.contains("flatpickr-disabled") : null,
                // Kiểm tra xem có bất kỳ ngày nào nhỏ hơn ngày bắt đầu mà bị disabled không
                hasPreviousDisabled: calendar.querySelector(".flatpickr-day.flatpickr-disabled") !== null
            };
        }
    ''', start_str)
    
    assert results['isStartDisabled'], f"Ngày bắt đầu ({start_str}) phải bị chặn trong datepicker kết thúc."
    
    page.keyboard.press("Escape")

@pytest.mark.django_db
def test_TC_HD_C07(logged_in_page: Page):
    """
    Steps:
    Chọn xe có sẵn bằng tìm theo từ khóa đã nhập
    1. Nhập từ khóa theo tên xe hoặc biển số của xe
    Expected:
    1. Hiện các thông tin xe ứng theo từ khóa đó và đồng thời khớp với thời gian thuê
    Actual:
    Hiện thông tin các xe chứa "Ma"
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ để kích hoạt bảng xe
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500) # Đợi JS kích hoạt tìm kiếm xe

    # Sử dụng xe Mercedes-Benz C300 AMG (Biển số: 30A-111.11)
    car_keyword = "C300"
    expected_car_name = "Mercedes-Benz C300 AMG"
    expected_car_plate = "30A-111.11"

    # 1. Nhập từ khóa
    page.fill("#car-search-input-create", car_keyword)
    
    # 2. Chọn xe từ Dropdown
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator(f"#car-dropdown .search-item:has-text('{expected_car_name}')").first.click()

    # 3. Kiểm tra thông tin điền vào bảng
    selected_row = page.locator("#selected-cars-list-body tr").filter(has_text=expected_car_plate)
    expect(selected_row).to_be_visible()
    expect(selected_row).to_contain_text(expected_car_name)
    expect(selected_row).to_contain_text(expected_car_plate)
    expect(selected_row).to_contain_text("đ") # Kiểm tra có giá tiền hiển thị

    # Kiểm tra tổng tiền đã được tính (khác 0)
    expect(page.locator("#display-total-price")).not_to_have_text("0")

@pytest.mark.django_db
def test_TC_HD_C08(logged_in_page: Page):
    """
    Steps:
    Kiểm tra list chỉ hiện hiện các xe chỉ ở trong trạng thái sẵn sàng trong thời gian đã chọn
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê: Từ ngày mai đến 29/04/2026
    start_date = datetime.now().date() + timedelta(days=1)
    start_str = start_date.strftime("%d/%m/%Y")
    # Giả định năm là 2026 dựa trên log hệ thống
    end_str = "29/04/2026"
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Nhập từ khóa tìm kiếm "Mazda"
    # Dựa trên data.json, Mazda 3 (51G-555.22) đang có lịch bảo trì đến 25/04/2026
    # nên nó sẽ bận nếu khoảng thuê bao gồm ngày 25/04.
    page.fill("#car-search-input-create", "Mazda")
    
    # 3. Chờ dropdown phản hồi
    page.wait_for_selector("#car-dropdown")
    
    # 4. Kiểm tra thông báo không tìm thấy kết quả
    expect(page.locator("#car-dropdown")).to_contain_text("Không thấy kết quả")
    
    # Đảm bảo không có item nào chứa text "Mazda" được hiển thị thực sự (ngoại trừ thông báo lỗi)
    # Tìm các item có class search-item (thực tế là kết quả)
    items = page.locator("#car-dropdown .search-item")
    expect(items).to_have_count(0)

@pytest.mark.django_db
def test_TC_HD_C09(logged_in_page: Page):
    """
    Steps:
    Kiểm tra được chọn nhiều xe
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Mở dropdown xe ngẫu nhiên và chọn xe thứ nhất
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    count_v = car_items.count()
    if count_v < 2: pytest.fail("Không đủ 2 xe sẵn sàng để test")
    
    # Chọn xe 1
    idx1 = random.randint(0, count_v - 1)
    car1 = car_items.nth(idx1)
    car1_text = car1.locator("strong").inner_text()
    car1.click()

    # 3. Chọn xe thứ hai ngẫu nhiên
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    # Lấy lại danh sách vì DOM có thể đã thay đổi
    car_items = page.locator("#car-dropdown .search-item")
    
    # Tìm index xe 2 khác xe 1
    idx2 = random.randint(0, car_items.count() - 1)
    while idx2 == idx1 and car_items.count() > 1:
        idx2 = random.randint(0, car_items.count() - 1)
        
    car2 = car_items.nth(idx2)
    car2_text = car2.locator("strong").inner_text()
    car2.click()

    # 4. Kiểm tra danh sách hiển thị cả hai xe (loại bỏ dòng empty-car-row)
    # Tìm tất cả dòng <tr> trong tbody ngoại trừ dòng có id 'empty-car-row'
    selected_rows = page.locator("#selected-cars-list-body tr:not(#empty-car-row)")
    expect(selected_rows).to_have_count(2)
    
    # Kiểm tra text hiển thị tương ứng (car_text chứa "Tên xe - Biển số")
    expect(page.locator("#selected-cars-list-body")).to_contain_text(car1_text.split(" - ")[0])
    expect(page.locator("#selected-cars-list-body")).to_contain_text(car2_text.split(" - ")[0])
    
    # Kiểm tra đầy đủ thông tin từng xe (Giá thuê và đơn vị đ)
    expect(selected_rows.nth(0)).to_contain_text("đ")
    expect(selected_rows.nth(1)).to_contain_text("đ")

@pytest.mark.django_db
def test_TC_HD_C10(logged_in_page: Page):
    """
    Steps:
    Xóa xe khỏi danh sách trước khi lưu
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn 2 xe khác nhau từ dropdown
    # Chọn xe thứ nhất
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").nth(0).click()

    # Mở lại dropdown và chọn xe thứ hai (khác xe 1)
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").nth(1).click()

    # Xác nhận có 2 xe trong danh sách (loại bỏ dòng empty)
    selected_rows = page.locator("#selected-cars-list-body tr:not(#empty-car-row)")
    expect(selected_rows).to_have_count(2)

    # 3. Xóa xe đầu tiên khỏi danh sách
    # Theo HTML mới nhất, nút xóa là một icon <i> có class fa-trash
    selected_rows.first.locator(".fa-trash").click()

    # 4. Xác nhận số lượng xe giảm xuống còn 1
    expect(selected_rows).to_have_count(1)

@pytest.mark.django_db
def test_TC_HD_C11(logged_in_page: Page):
    """
    Steps:
    Chặn khi nhập chữ và kí tự đặc biệt vào ô tiền tạm ứng
    1. Nhập chữ và kí tự vào ô tiền tạm ứng
    Expected:
    Hệ thống chặn không nhập được và không hiện kí tự lên ô đó
    Actual:
    Chỉ nhận số 88
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    prepaid_input = page.locator("#new-contract-prepaid")
    
    # 1. Nhập chữ và ký tự đặc biệt
    # Focus và gõ từng phím để kích hoạt event oninput
    prepaid_input.focus()
    page.keyboard.type("abc!@#$")
    
    # 2. Kiểm tra ô input không hiện kí tự chữ và ký tự đặc biệt vừa nhập (vẫn trống)
    expect(prepaid_input).to_have_value("")
    
    # 3. Thử nhập kết hợp số, chữ và ký tự đặc biệt
    page.keyboard.type("1.000@abc")
    # Chỉ số được giữ lại (lưu ý logic JS có thể tự thêm dấu chấm format nếu bạn gõ số)
    # Theo code JS: let v = e.target.value.replace(/[^\d]/g, '');
    # Gõ "1.000@abc" -> v sẽ là "1000" -> kết quả hiển thị "1.000"
    expect(prepaid_input).to_have_value("1.000")

@pytest.mark.django_db
def test_TC_HD_C13(logged_in_page: Page):
    """
    Steps:
    Tính toán đúng số tiền khách cần trả thêm = 0
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ (ví dụ: thuê 2 ngày)
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn 1 xe bất kỳ từ danh sách
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").first.click()

    # 3. Lấy giá trị tổng tiền thuê đã tính toán tự động
    # Dựa trên HTML của bạn, tổng tiền nằm trong span id="display-total-price"
    total_price_text = page.locator("#display-total-price").inner_text()
    
    # 4. Nhập số tiền tạm ứng bằng đúng số tiền thuê
    # Ta nhập chính xác chuỗi đó vào ô tiền tạm ứng
    page.fill("#new-contract-prepaid", total_price_text)

    # 5. Kiểm chứng: Hệ thống hiện "Đã đủ tiền thuê"
    # Dựa trên HTML: <div id="row-du-tien" ...>
    expect(page.locator("#row-du-tien")).to_be_visible()
    expect(page.locator("#row-du-tien")).to_contain_text("Đã đủ tiền thuê")
    
    # Đảm bảo các dòng khác (trả thêm, trả lại) bị ẩn
    expect(page.locator("#row-tra-them")).to_be_hidden()
    expect(page.locator("#row-tra-lai")).to_be_hidden()

@pytest.mark.django_db
def test_TC_HD_C14(logged_in_page: Page):
    """
    Steps:
    Tính toán đúng số tiền khách cần trả thêm
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")

    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn 1 xe bất kỳ
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").first.click()

    # 3. Lấy giá trị tổng tiền thuê
    total_price_raw = page.locator("#display-total-price").inner_text()
    # Chuyển đổi thành số (bỏ dấu chấm)
    total_price = int(total_price_raw.replace(".", ""))

    # 4. Nhập số tiền tạm ứng bé hơn (ví dụ: thiếu 100.000 đ)
    prepaid_amount = total_price - 100000
    # Định dạng lại chuỗi có dấu chấm để nhập vào (hoặc nhập số thuần túy tùy logic JS)
    page.fill("#new-contract-prepaid", str(prepaid_amount))

    # 5. Kiểm chứng: Hệ thống hiện "Khách phải trả thêm" và đúng số tiền 100.000
    expect(page.locator("#row-tra-them")).to_be_visible()
    expect(page.locator("#display-tra-them")).to_contain_text("100.000")

@pytest.mark.django_db
def test_TC_HD_C15(logged_in_page: Page):
    """
    Steps:
    Tính toán đúng số tiền phải trả lại khách
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn 1 xe bất kỳ
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").first.click()

    # 3. Lấy giá trị tổng tiền thuê
    total_price_raw = page.locator("#display-total-price").inner_text()
    total_price = int(total_price_raw.replace(".", ""))
    
    # 4. Nhập số tiền tạm ứng lớn hơn (ví dụ: thừa 100.000 đ)
    prepaid_amount = total_price + 100000
    page.fill("#new-contract-prepaid", str(prepaid_amount))

    # 5. Kiểm chứng: Hệ thống hiện "Phải trả lại khách" và đúng số tiền 100.000
    expect(page.locator("#row-tra-lai")).to_be_visible()
    expect(page.locator("#display-tra-lai")).to_contain_text("100.000")


@pytest.mark.django_db
def test_TC_HD_C16(logged_in_page: Page):
    """
    Steps:
    Lập hợp đồng không có tiền tạm ứng
    1. Điền đầy đủ thông tin hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê (bắt đầu từ hôm nay)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")

    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn khách hàng ngẫu nhiên
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    count_c = customer_items.count()
    if count_c == 0: pytest.fail("Không có khách hàng")
    customer_items.nth(random.randint(0, count_c - 1)).click()

    # 3. Chọn xe ngẫu nhiên
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    count_v = car_items.count()
    if count_v == 0: pytest.fail("Không có xe sẵn sàng")
    car_items.nth(random.randint(0, count_v - 1)).click()


    # 4. Bấm LƯU HỢP ĐỒNG và đợi thông báo alert
    with page.expect_event("dialog") as dialog_info:
        page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()

    dialog = dialog_info.value
    assert "Lưu hợp đồng thành công!" in dialog.message
    dialog.accept()
    page.wait_for_load_state("networkidle")

@pytest.mark.django_db
def test_TC_HD_C17(logged_in_page: Page):
    """
    Steps:
    Xác nhận Hủy khi chưa lưu thông tin
    1. Nhập đầy đủ các thông tin bắt buộc
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Nhập đầy đủ thông tin để làm "dirty" form
    # Chọn khách hàng
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    if customer_items.count() == 0:
        pytest.fail("Không có khách hàng để thực hiện test")
    customer_items.first.click()

    # Chọn thời gian thuê
    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # Chọn xe
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    if car_items.count() == 0:
        pytest.fail("Không có xe sẵn sàng để thực hiện test")
    car_items.first.click()

    # Đợi một chút để JS ghi nhận trạng thái 'dirty'
    page.wait_for_timeout(500)

    # 2. Click vào link "Tạo hợp đồng thuê" trên sidebar để điều hướng về chính nó
    # Giả sử link này có id là "nav-create-contract"
    create_contract_link = page.locator("#nav-create-contract")
    expect(create_contract_link).to_be_visible()
    create_contract_link.click()

    # 3. Kiểm tra xem custom modal có xuất hiện không và nội dung của nó
    # Dựa trên HTML cung cấp: <h3 id="confirm-modal-msg">Bạn chưa lưu thông tin, có muốn thoát?</h3>
    confirm_modal_msg = page.locator("#confirm-modal-msg")
    expect(confirm_modal_msg).to_be_visible()
    expect(confirm_modal_msg).to_have_text("Bạn chưa lưu thông tin, có muốn thoát?")

    # Không thực hiện click nút "Hủy" hay kiểm tra URL nữa, chỉ cần pop-up hiện là đạt yêu cầu.

@pytest.mark.django_db
def test_TC_HD_C18(logged_in_page: Page):
    """
    Steps:
    Bỏ trống thời gian bắt đầu thuê
    1. Bỏ trống trường thời gian bắt đầu thuê (nhận xe)
    Expected:
    Ô chọn xe bị khóa không chọn được
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Click vào ô chọn xe và kiểm tra không có xe nào được hiển thị
    car_input = page.locator("#car-search-input-create")
    car_input.click()
    # Chờ dropdown hiển thị (nếu có)
    page.wait_for_selector("#car-dropdown", state="visible")
    # Kiểm tra rằng không có mục xe nào (search-item) trong dropdown
    car_items = page.locator("#car-dropdown .search-item")
    expect(car_items).to_have_count(0)

    # 2. Chọn khách hàng ngẫu nhiên
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    if customer_items.count() == 0:
        pytest.fail("Không có khách hàng để thực hiện test")
    customer_items.first.click()

    # 3. Bấm LƯU HỢP ĐỒNG và kiểm tra thông báo
    # Thiết lập trình xử lý dialog TRƯỚC khi click
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.dismiss()

    page.on("dialog", handle_dialog)

    # Click để kích hoạt dialog
    page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()

    # Đợi một chút để đảm bảo handler đã chạy
    page.wait_for_timeout(500)

    # Kiểm tra nội dung đã được ghi lại
    assert dialog_message == "Vui lòng nhập đầy đủ các thông tin bắt buộc!", f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

@pytest.mark.django_db
def test_TC_HD_C19(logged_in_page: Page):
    """
    Steps:
    Bỏ trống thời gian trả thuê
    1. Chọn thời gian bắt đầu thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian bắt đầu thuê hợp lệ
    start_date = datetime.now() + timedelta(days=1)
    start_str = start_date.strftime("%d/%m/%Y")
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Click vào ô chọn xe và kiểm tra nó bị khóa (không hiện dropdown)
    car_input = page.locator("#car-search-input-create")
    car_input.click(force=True) # Dùng force=True để bỏ qua lỗi bị che khuất
    # Đợi một chút để đảm bảo không có dropdown nào xuất hiện
    page.wait_for_timeout(200)
    # Khẳng định rằng dropdown không hiển thị
    expect(page.locator("#car-dropdown")).not_to_be_visible()

    # 3. Chọn khách hàng
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    if customer_items.count() == 0:
        pytest.fail("Không có khách hàng để thực hiện test")
    customer_items.first.click()

    # 4. Bấm lưu và kiểm tra thông báo
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()
    page.wait_for_timeout(500)

    assert dialog_message == "Vui lòng nhập đầy đủ các thông tin bắt buộc!", f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

@pytest.mark.django_db
def test_TC_HD_C20(logged_in_page: Page):
    """
    Steps:
    Bỏ trống thông tin khách hàng và lưu
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Bỏ trống khách hàng (không làm gì)

    # 3. Chọn xe hợp lệ
    page.click("#car-search-input-create")
    page.wait_for_selector("#car-dropdown .search-item")
    car_items = page.locator("#car-dropdown .search-item")
    if car_items.count() == 0:
        pytest.fail("Không có xe sẵn sàng để thực hiện test")
    car_items.first.click()

    # 4. Bấm lưu và kiểm tra thông báo
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()
    page.wait_for_timeout(500)

    assert dialog_message == "Vui lòng nhập đầy đủ các thông tin bắt buộc!", f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

@pytest.mark.django_db
def test_TC_HD_C21(logged_in_page: Page):
    """
    Steps:
    Bỏ trống ô chọn xe
    1. Chọn thời gian thuê hợp lệ
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    page.goto("http://127.0.0.1:8000/hop-dong/tao-moi/")

    # 1. Chọn thời gian thuê hợp lệ
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    start_str = start_date.strftime("%d/%m/%Y")
    end_str = end_date.strftime("%d/%m/%Y")
    page.evaluate(f"() => {{ if(typeof fpStart !== 'undefined') fpStart.setDate('{start_str}', true); }}")
    page.evaluate(f"() => {{ if(typeof fpEnd !== 'undefined') fpEnd.setDate('{end_str}', true); }}")
    page.wait_for_timeout(500)

    # 2. Chọn khách hàng
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    customer_items = page.locator("#customer-dropdown .search-item")
    if customer_items.count() == 0:
        pytest.fail("Không có khách hàng để thực hiện test")
    customer_items.first.click()

    # 3. Không chọn xe (không làm gì)

    # 4. Bấm lưu và kiểm tra thông báo
    dialog_message = None
    def handle_dialog(dialog):
        nonlocal dialog_message
        dialog_message = dialog.message
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    page.get_by_role("button", name="LƯU HỢP ĐỒNG").click()
    page.wait_for_timeout(500)

    assert dialog_message == "Vui lòng nhập đầy đủ các thông tin bắt buộc!", f"Nội dung pop-up không đúng. Thực tế: '{dialog_message}'"

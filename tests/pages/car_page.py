class CarPage:
    """Selectors and Actions for the Car module"""
    
    def __init__(self, page):
        self.page = page
        
        # List View Selectors
        self.ADD_CAR_BTN = "text='Thêm thông tin xe'"
        self.SEARCH_INPUT = "#car-search-input"
        self.CAR_ROWS = ".car-card" 
        
        # Form Selectors (Add/Edit)
        self.ADD_PLATE_INPUT = "#add-car-plate"
        self.EDIT_PLATE_INPUT = "#edit-car-plate"
        self.ADD_RENT_INPUT = "#add-car-price-day"
        self.EDIT_RENT_INPUT = "#edit-car-price"
        self.SAVE_BTN_ADD = "#btn-save"
        self.SAVE_BTN_EDIT = "#btn-save-car"
        self.CANCEL_BTN = "#btn-cancel"
        self.ERROR_MSG = ".error-message" 
        self.VIEW_BTN = ".btn-outline-view"
        self.DELETE_BTN_CARD_TMPL = "div.car-card[data-bien-so='{}'] .btn-action-delete"
        
        # Confirm Modal Selectors (from common.js/base.html)
        self.MODAL_CONFIRM_ROOT = "#confirm-modal-root"
        self.MODAL_CONFIRM_MSG = "#confirm-modal-msg"
        self.MODAL_CONFIRM_OK = "#confirm-modal-ok"
        self.MODAL_CONFIRM_CANCEL = "#confirm-modal-cancel"
        
        # Custom Dropdown Trigger Selectors
        self.BRAND_TRIGGER = 'label:has-text("Hãng Xe") + div .custom-dropdown-toggle'
        self.MODEL_TRIGGER = 'label:has-text("Loại Xe") + div .custom-dropdown-toggle'
        self.COLOR_TRIGGER = 'label:has-text("Màu Xe") + div .custom-dropdown-toggle'
        self.TYPE_TRIGGER = 'label:has-text("Kiểu Dáng") + div .custom-dropdown-toggle'
        self.YEAR_TRIGGER = 'label:has-text("Năm Sản Xuất") + div .custom-dropdown-toggle'
        self.STATUS_TRIGGER = 'label:has-text("Trạng Thái Hoạt Động") + div .custom-dropdown-toggle'
        self.SEATS_DISPLAY = '#add-car-seats, #edit-car-seats'
        self.ORIGIN_DISPLAY = '#add-car-country, #edit-car-country'
        
        # Option Selector Template
        self.OPTION_TMPL = '.custom-dropdown-menu div:has-text("{}")'

        # Filter Selectors
        self.FILTER_BRAND = "select#filter-brand"
        self.FILTER_MODEL = "select#filter-model"
        self.FILTER_SEATS = "select#filter-seats"
        self.FILTER_STATUS = "select#filter-status"
        self.FILTER_SUBMIT = "button.btn-filter-main"
        self.FILTER_RESET = "button.btn-outline-primary"
        self.EMPTY_MSG = "#empty-car-message"

    def navigate_to_list(self, base_url):
        try:
            self.page.goto(f"{base_url}/xe/")
        except Exception:
            if self.page.locator('a[href="/xe/"]').is_visible():
                self.page.click('a[href="/xe/"]')
            else:
                self.page.goto(f"{base_url}/xe/", wait_until="networkidle")
        
    def click_add_new(self):
        self.page.click(self.ADD_CAR_BTN)

    def select_custom_dropdown(self, trigger_selector, value):
        if not value: return
        self.page.locator(trigger_selector).scroll_into_view_if_needed()
        self.page.click(trigger_selector, force=True)
        option_selector = self.OPTION_TMPL.format(value)
        # Fast timeout (2s)
        self.page.wait_for_selector(option_selector, state="visible", timeout=2000)
        self.page.locator(option_selector).scroll_into_view_if_needed()
        self.page.click(option_selector, force=True)

    def fill_form(self, data):
        if 'hang_xe' in data: self.select_custom_dropdown(self.BRAND_TRIGGER, data['hang_xe'])
        if 'loai_xe' in data: self.select_custom_dropdown(self.MODEL_TRIGGER, data['loai_xe'])
        if 'kieu_dang' in data: self.select_custom_dropdown(self.TYPE_TRIGGER, data['kieu_dang'])
        
        if 'bien_so' in data:
            selector = self.ADD_PLATE_INPUT if self.page.locator(self.ADD_PLATE_INPUT).is_visible() else self.EDIT_PLATE_INPUT
            if self.page.locator(selector).is_visible() and self.page.locator(selector).is_editable():
                self.page.fill(selector, data['bien_so'])
        
        if 'nam_sx' in data: self.select_custom_dropdown(self.YEAR_TRIGGER, data['nam_sx'])
        if 'mau_xe' in data: self.select_custom_dropdown(self.COLOR_TRIGGER, data['mau_xe'])
        
        if 'gia_thue' in data:
            selector = self.ADD_RENT_INPUT if self.page.locator(self.ADD_RENT_INPUT).is_visible() else self.EDIT_RENT_INPUT
            self.page.fill(selector, str(data['gia_thue']))
            
        if 'trang_thai' in data: self.select_custom_dropdown(self.STATUS_TRIGGER, data['trang_thai'])

    def save(self):
        # Reset any previous messages
        self.last_dialog_message = None
        def handle_dialog(dialog):
            self.last_dialog_message = dialog.message
            dialog.dismiss()
            
        self.page.once("dialog", handle_dialog)
        
        if self.page.locator(self.SAVE_BTN_ADD).is_visible():
            self.page.click(self.SAVE_BTN_ADD, force=True)
        elif self.page.locator(self.SAVE_BTN_EDIT).is_visible():
            self.page.click(self.SAVE_BTN_EDIT, force=True)
        else:
            self.page.click("button:has-text('Lưu'), button:has-text('Cập nhật')", force=True)
            
        # Give a little time for the dialog to be captured if it was triggered
        self.page.wait_for_timeout(300)

    def get_error_message(self):
        try:
            self.page.wait_for_selector(self.ERROR_MSG, state="visible", timeout=1500)
        except:
            pass
        error_locator = self.page.locator(self.ERROR_MSG)
        if error_locator.count() > 0:
            return error_locator.first.inner_text()
        return None

    def get_field_value(self, selector):
        return self.page.input_value(selector)

    def get_dropdown_value(self, trigger_selector):
        return self.page.locator(trigger_selector).inner_text().strip()

    def is_field_enabled(self, selector):
        return self.page.is_enabled(selector)

    def is_save_disabled(self):
        selector = self.SAVE_BTN_ADD if self.page.locator(self.SAVE_BTN_ADD).is_visible() else self.SAVE_BTN_EDIT
        return self.page.is_disabled(selector)

    def get_origin_value(self):
        return self.page.locator(self.ORIGIN_DISPLAY).input_value().strip()

    def get_seats_value(self):
        return self.page.locator(self.SEATS_DISPLAY).input_value().strip()

    def is_readonly(self, selector):
        """Check if an input field is readonly or has pointer-events none"""
        is_readonly_attr = self.page.locator(selector).get_attribute("readonly") is not None
        is_disabled_attr = self.page.locator(selector).is_disabled()
        
        # Also check style for custom dropdowns
        style = self.page.locator(selector).get_attribute("style") or ""
        is_pointer_disabled = "pointer-events: none" in style or "opacity: 0.5" in style
        
        return is_readonly_attr or is_disabled_attr or is_pointer_disabled

    def has_error_highlight(self, selector):
        """Check if the field has the error class (border-color: #ef4444)"""
        # Usually added to the input or the parent dropdown
        classes = self.page.locator(selector).get_attribute("class") or ""
        if "input-error" in classes:
            return True
            
        # Check computed style for border color (red: rgb(239, 68, 68))
        color = self.page.locator(selector).evaluate("el => getComputedStyle(el).borderColor")
        return "rgb(239, 68, 68)" in color or "rgba(239, 68, 68" in color

    def get_focused_element_id(self):
        """Get the ID of the currently focused element"""
        return self.page.evaluate("document.activeElement.id")

    def click_delete_on_car(self, bien_so):
        selector = self.DELETE_BTN_CARD_TMPL.format(bien_so)
        self.page.locator(selector).scroll_into_view_if_needed()
        self.page.click(selector, force=True)

    def confirm_delete(self):
        self.page.click(self.MODAL_CONFIRM_OK, force=True)
        # Wait for modal to disappear
        self.page.wait_for_selector(self.MODAL_CONFIRM_ROOT, state="hidden", timeout=2000)

    def cancel_delete(self):
        self.page.click(self.MODAL_CONFIRM_CANCEL, force=True)
        self.page.wait_for_selector(self.MODAL_CONFIRM_ROOT, state="hidden", timeout=2000)

    def is_modal_visible(self):
        return self.page.locator(self.MODAL_CONFIRM_ROOT).is_visible()

    def apply_filters(self, brand=None, model=None, seats=None, status=None):
        if brand: self.page.select_option(self.FILTER_BRAND, value=brand)
        if model: self.page.select_option(self.FILTER_MODEL, value=model)
        if seats: self.page.select_option(self.FILTER_SEATS, value=str(seats))
        if status: self.page.select_option(self.FILTER_STATUS, value=status)
        self.page.click(self.FILTER_SUBMIT)
        self.page.wait_for_timeout(500)

    def reset_filters(self):
        self.page.click(self.FILTER_RESET)
        self.page.wait_for_timeout(500)


class ContractPage:
    """Selectors and Actions for the Contract module"""
    
    def __init__(self, page):
        self.page = page
        
        # Selectors
        self.CREATE_BTN = "a:has-text('Tạo hợp đồng thuê')"
        self.START_DATE = "#new-contract-start"
        self.END_DATE = "#new-contract-end"
        self.CUSTOMER_SEARCH = "#customer-search-input"
        self.CAR_SEARCH = "#car-search-input-create"
        self.SAVE_BTN = "button:has-text('LƯU HỢP ĐỒNG')"
        self.BOOK_BTN = "button:has-text('ĐẶT TRƯỚC')"
        
    def navigate_to_create(self):
        self.page.goto("/hop-dong/tao-moi/")
        
    def fill_customer(self, name):
        self.page.fill(self.CUSTOMER_SEARCH, name)
        self.page.wait_for_selector("#customer-dropdown .search-item")
        self.page.click(f"#customer-dropdown .search-item:has-text('{name}')")

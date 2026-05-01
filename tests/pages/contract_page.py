class ContractPage:
    def __init__(self, page):
        self.page = page
        self.URL_LIST = "/hop-dong/"
        self.URL_CREATE = "/hop-dong/create/"
        
        # Create form selectors
        self.START_DATE = "#new-contract-start"
        self.END_DATE = "#new-contract-end"
        self.CUSTOMER_SEARCH = "#customer-search-input"
        self.CAR_SEARCH = "#car-search-input-create"
        self.PREPAID_INPUT = "#new-contract-prepaid"
        self.SAVE_BTN = "button:has-text('LƯU HỢP ĐỒNG')"
        self.BOOK_BTN = "button:has-text('ĐẶT TRƯỚC')"
        
        # Display fields
        self.TOTAL_PRICE = "#display-total-price"
        self.DURATION_TEXT = "#contract-duration-text"
        
        # List filters
        self.SEARCH_LIST = ".list-search"
        self.TAB_ALL = ".tab-teal"
        self.TAB_ACTIVE = ".tab-blue"
        self.TAB_OVERDUE = ".tab-red"
        self.TAB_RETURNED = ".tab-green"

    def navigate_create(self, base_url):
        self.page.goto(f"{base_url}{self.URL_CREATE}")
        self.page.wait_for_load_state("networkidle")

    def select_customer(self, name):
        self.page.fill(self.CUSTOMER_SEARCH, name)
        self.page.wait_for_selector(f".search-item:has-text('{name}')")
        self.page.click(f".search-item:has-text('{name}')")

    def select_car(self, plate):
        self.page.fill(self.CAR_SEARCH, plate)
        self.page.wait_for_selector(f".search-item:has-text('{plate}')")
        self.page.click(f".search-item:has-text('{plate}')")

    def set_dates(self, start_str, end_str):
        # Using fill might trigger listeners
        self.page.fill(self.START_DATE, start_str)
        self.page.keyboard.press("Enter")
        self.page.fill(self.END_DATE, end_str)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(500)

    def save(self):
        self.page.click(self.SAVE_BTN)
        self.page.once("dialog", lambda d: d.dismiss())

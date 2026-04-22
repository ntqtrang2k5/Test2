class CarPage:
    """Selectors and Actions for the Car module"""
    
    def __init__(self, page):
        self.page = page
        
        # Selectors
        self.ADD_CAR_BTN = "#btn-add-car"
        self.SEARCH_INPUT = ".list-search"
        self.PLATE_INPUT = "#car-plate"
        self.NAME_INPUT = "#car-name"
        self.SUBMIT_BTN = "#btn-save-car"
        
    def navigate_to_list(self):
        self.page.goto("/quan-ly-xe/")
        
    def search_car(self, keyword):
        self.page.fill(self.SEARCH_INPUT, keyword)
        # TODO: Wait for table to filter

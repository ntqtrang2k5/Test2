from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://127.0.0.1:8080/xe/add/')
        # Login
        if page.locator('#username').is_visible():
            page.fill('#username', 'n2tester')
            page.fill('#password', '@n2tester')
            page.click('button[type=submit]')
            page.wait_for_url('**/xe/')
            page.goto('http://127.0.0.1:8080/xe/add/')
        
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        labels = page.locator('label').all_inner_texts()
        print("Labels found:", labels)
        
        # Check specific fields
        # Select Toyota
        page.click('label:has-text("Hãng Xe") + div')
        page.click('.custom-dropdown-menu div:has-text("Toyota")')
        page.wait_for_timeout(1000)
        
        # Select Vios
        page.click('label:has-text("Loại Xe") + div')
        page.click('.custom-dropdown-menu div:has-text("Vios")')
        page.wait_for_timeout(1000)

        for label_text in labels:
            if "Xuất" in label_text or "Số Chỗ" in label_text:
                try:
                    val = page.evaluate(f'Array.from(document.querySelectorAll("label")).find(el => el.innerText.includes("{label_text}")).nextElementSibling.innerText')
                    print(f"Label: {label_text} -> Value: {val}")
                except Exception as e:
                    print(f"Label: {label_text} -> Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    run()

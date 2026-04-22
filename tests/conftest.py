import pytest
import sys
import os
import django
from playwright.sync_api import sync_playwright

import shutil
from pathlib import Path

# Add the project root to sys.path so 'carrent' can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Tell pytest where the Django settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')

def pytest_sessionstart(session):
    """
    Before starting the test session, clone the production database
    to a test copy so we can use real data safely.
    """
    src = BASE_DIR / "db.sqlite3"
    dst = BASE_DIR / "test_db_copy.sqlite3"
    if src.exists():
        print(f"\n[Automation] Đang nhân bản dữ liệu từ {src.name} sang {dst.name}...")
        shutil.copy2(src, dst)

def pytest_configure():
    import django
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()

@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def logged_in_page(browser_instance):
    context = browser_instance.new_context()
    page = context.new_page()
    
    # Login logic
    page.goto("http://127.0.0.1:8000/login/")
    page.fill("input[name='username']", "n2tester")
    page.fill("input[name='password']", "@n2tester") # Assuming password is same for tester
    page.click("button[type='submit']")
    
    # Wait for login to complete
    page.wait_for_url("http://127.0.0.1:8000/")
    
    yield page
    context.close()

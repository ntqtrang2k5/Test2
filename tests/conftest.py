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
        print(f"\n[Automation] Cloning database from {src.name} to {dst.name}...")
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
    # Note: Using 127.0.0.1:8000 assumes the server is running. 
    # For a more robust test, use the live_server fixture if using pytest-django.
    base_url = "http://127.0.0.1:8000"
    page.goto(f"{base_url}/login/")
    page.fill("input[name='username']", "n2tester")
    page.fill("input[name='password']", "@n2tester")
    page.click("button[type='submit']")
    
    # Wait for login to complete and redirect to the dashboard (lich-xe)
    page.wait_for_url(f"{base_url}/lich-xe/")
    
    yield page
    context.close()

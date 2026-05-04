import pytest
import sys
import os
import django
from playwright.sync_api import sync_playwright
import shutil
from pathlib import Path
from datetime import datetime
import json
import re
from jinja2 import Template

# Add the project root to sys.path so 'carrent' can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Tell pytest where the Django settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')

# Global storage for test results
test_results = []

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
    
    # Prepare reports folder
    reports_dir = BASE_DIR / "02_TestReport"
    screenshots_dir = reports_dir / "screenshots"
    
    reports_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

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
def logged_in_page(browser_instance, request):
    context = browser_instance.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    
    # Store page in request for screenshot capture
    request.node.funcargs['page_instance'] = page
    
    # Login logic
    base_url = "http://127.0.0.1:8000"
    page.goto(f"{base_url}/login/")
    page.fill("input[name='username']", "n2tester")
    page.fill("input[name='password']", "@n2tester")
    page.click("button[type='submit']")
    
    # Wait for login to complete
    try:
        page.wait_for_url(f"{base_url}/lich-xe/", timeout=5000)
    except:
        pass
    
    yield page
    context.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        page = item.funcargs.get('logged_in_page') or item.funcargs.get('page_instance')
        
        screenshot_path = None
        error_message = ""
        expected = ""
        actual = ""
        
        if report.failed:
            if page:
                reports_dir = BASE_DIR / "02_TestReport"
                screenshots_dir = reports_dir / "screenshots"
                file_name = f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                full_path = screenshots_dir / file_name
                page.screenshot(path=str(full_path))
                screenshot_path = f"screenshots/{file_name}"
            
            error_message = str(report.longrepr)
            match_equal = re.search(r"assert '(.*?)' == '(.*?)'", error_message)
            if match_equal:
                actual = match_equal.group(1)
                expected = match_equal.group(2)
            else:
                match_diff = re.search(r"Expected: (.*?)\n\s*Actual: (.*?)", error_message, re.DOTALL)
                if match_diff:
                    expected = match_diff.group(1).strip()
                    actual = match_diff.group(2).strip()

        file_path = str(item.fspath)
        folder = "Other"
        if "playwright" in file_path:
            p = Path(file_path)
            if "cars" in p.parts: folder = "Cars"
            elif "contracts" in p.parts: folder = "Contracts"

        # Tách ID
        tc_id_match = re.search(r"(TC_[A-Z0-9_]+)", item.name)
        tc_id = tc_id_match.group(1) if tc_id_match else item.name

        # Extract steps, expected, and actual from docstring
        docstring = getattr(item.function, '__doc__', None)
        steps = "No steps provided."
        expected_from_doc = ""
        actual_from_doc = ""

        if docstring:
            docstring = docstring.strip()
            # Try to parse Steps, Expected, Actual
            steps_match = re.search(r"Steps:(.*?)(Expected:|Actual:|$)", docstring, re.DOTALL | re.IGNORECASE)
            expected_match = re.search(r"Expected:(.*?)(Actual:|Steps:|$)", docstring, re.DOTALL | re.IGNORECASE)
            actual_match = re.search(r"Actual:(.*?)(Expected:|Steps:|$)", docstring, re.DOTALL | re.IGNORECASE)

            if steps_match: steps = steps_match.group(1).strip()
            if expected_match: expected_from_doc = expected_match.group(1).strip()
            if actual_match: actual_from_doc = actual_match.group(1).strip()

            if not steps_match and not expected_match and not actual_match:
                steps = docstring

        if report.passed:
            actual = actual_from_doc or "Khớp với kết quả mong đợi (Passed)"
            expected = expected_from_doc or "Chạy qua tất cả các bước (Pass)"
        else:
            # For failed tests, we still want the parsed expected if available
            if expected_from_doc:
                expected = expected_from_doc
            # Actual will be the error message if not passed, but we can prepend the doc's actual if helpful
            # But usually for failures, 'actual' is the failure detail.
            # However, the user said "kiểm tra nội dung ... có chính xác không" based on Excel.
            # So if it's in Excel, I should use it.
            if actual_from_doc and not actual:
                actual = actual_from_doc

        test_results.append({
            'id': tc_id,
            'name': item.name.replace('_', ' '),
            'status': report.outcome,
            'duration': report.duration,
            'nodeid': item.nodeid,
            'folder': folder,
            'screenshot': screenshot_path,
            'expected': expected,
            'actual': actual,
            'steps': steps
        })

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    try:
        if not test_results:
            terminalreporter.write_line("\n[Automation] No test results collected.")
            return

        total = len(test_results)
        passed = sum(1 for r in test_results if r['status'] == 'passed')
        failed = sum(1 for r in test_results if r['status'] == 'failed')
        skipped = sum(1 for r in test_results if r['status'] == 'skipped')
        duration = sum(r['duration'] for r in test_results)

        folder_stats = {}
        for r in test_results:
            f = r['folder']
            if f not in folder_stats:
                folder_stats[f] = {'total': 0, 'passed': 0, 'failed': 0}
            folder_stats[f]['total'] += 1
            if r['status'] == 'passed':
                folder_stats[f]['passed'] += 1
            elif r['status'] == 'failed':
                folder_stats[f]['failed'] += 1

        template_path = BASE_DIR / "tests" / "report_template.html"
        if not template_path.exists():
            terminalreporter.write_line(f"\n[Automation] Error: Template not found at {template_path}")
            return

        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        html_content = template.render(
            generated_at=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            stats={
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': round(duration, 2)
            },
            folder_stats=folder_stats,
            results=test_results
        )

        output_dir = BASE_DIR / "02_TestReport"
        output_path = output_dir / "index.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        terminalreporter.write_line(f"\n[Automation] Report created at: {output_path}")
    except Exception as e:
        terminalreporter.write_line(f"\n[Automation] Error generating report: {e}")
        import traceback
        terminalreporter.write_line(traceback.format_exc())

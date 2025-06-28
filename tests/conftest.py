"""
Pytest configuration for headless dash testing.
"""

from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    """Configure Chrome options for headless dash testing."""
    options = Options()
    
    # Headless mode
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-web-security')
    
    # Additional stability options for CI/testing
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-features=SidePanelPinning')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    
    return options 
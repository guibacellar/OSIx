"""Chrome Driver Manager."""

import time
from selenium import webdriver
from configparser import ConfigParser


class FacebookDriver:
    """Facebook Driver Manager."""

    def __init__(self, config: ConfigParser) -> None:
        try:
            self.browser = webdriver.Chrome()
            self.login(config)
        except Exception as ex:
            print('[!!!] ERROR - You Probably don\'t Have the Chrome Driver Installed. Please, check https://sites.google.com/a/chromium.org/chromedriver/home to Install.')
            raise ex

    def get_browser(self) -> webdriver.Chrome:
        """Return the WebDriver."""
        return self.browser

    def login(self, config: ConfigParser) -> None:
        """Login on Facebook."""

        # Start Navigation
        self.browser.maximize_window()
        self.browser.get(f'https://www.facebook.com/')

        # Auto Login
        time.sleep(1)
        self.browser.find_element_by_id("email").send_keys(config['FACEBOOK']['email'])

        time.sleep(1)
        self.browser.find_element_by_id("pass").send_keys(config['FACEBOOK']['password'])

        time.sleep(1)
        self.browser.find_elements_by_name("login")[0].click()

        time.sleep(2)
        self.browser.minimize_window()

    def shutdown(self) -> None:
        """Shutdown Web Driver."""
        self.browser.close()


class ChromeDrivers:
    """Drivers Singleton Managment."""

    __FACEBOOK_DRIVER: FacebookDriver = None

    @staticmethod
    def shutdown() -> None:
        """Shutdown All Drivers."""
        if ChromeDrivers.__FACEBOOK_DRIVER is not None:
            ChromeDrivers.__FACEBOOK_DRIVER.shutdown()

    @staticmethod
    def get_fb_webdriver(config: ConfigParser) -> webdriver.Chrome:
        """Returns the FB WebDriver."""

        if ChromeDrivers.__FACEBOOK_DRIVER is None:
            ChromeDrivers.__FACEBOOK_DRIVER = FacebookDriver(config)

        return ChromeDrivers.__FACEBOOK_DRIVER.get_browser()
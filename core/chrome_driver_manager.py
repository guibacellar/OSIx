"""Chrome Driver Manager."""

import time
import logging

from os import path
from sys import platform

from typing import Optional

from configparser import ConfigParser
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger()


class FacebookDriver:
    """Facebook Driver Manager."""

    def __init__(self, config: ConfigParser) -> None:
        """Initialize Module."""

        try:
            executable_path = path.join("assets", 'chromedriver.exe' if platform == 'win32' else 'chromedriver')
            kwargs = {}
            if path.exists(executable_path):
                kwargs['executable_path'] = executable_path

            self.browser = webdriver.Chrome(**kwargs)
            self.login(config)
        except WebDriverException as ex:
            logger.fatal('[!!!] ERROR - You Probably don\'t Have the Chrome Driver Installed. Please, check https://sites.google.com/a/chromium.org/chromedriver/home to Install.')
            raise ex

    def get_browser(self) -> webdriver.Chrome:
        """Return the WebDriver."""
        return self.browser

    def login(self, config: ConfigParser) -> None:
        """Login on Facebook."""

        # Start Navigation
        self.browser.maximize_window()
        self.browser.get('https://www.facebook.com/')

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

    __FACEBOOK_DRIVER: Optional[FacebookDriver] = None

    @staticmethod
    def shutdown() -> None:
        """Shutdown All Drivers."""

        if ChromeDrivers.__FACEBOOK_DRIVER is not None:
            ChromeDrivers.__FACEBOOK_DRIVER.shutdown()

    @staticmethod
    def get_fb_webdriver(config: ConfigParser) -> webdriver.Chrome:
        """Return the FB WebDriver."""

        if ChromeDrivers.__FACEBOOK_DRIVER is None:
            ChromeDrivers.__FACEBOOK_DRIVER = FacebookDriver(config)

        return ChromeDrivers.__FACEBOOK_DRIVER.get_browser()

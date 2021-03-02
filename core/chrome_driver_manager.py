"""Chrome Driver Manager."""

import time
import logging
import zipfile

from os import path
from sys import platform

from typing import Dict, Optional

from configparser import ConfigParser
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from core.http_manager import HttpNavigationManager

logger = logging.getLogger()


class FacebookDriver:
    """Facebook Driver Manager."""

    def __init__(self, config: ConfigParser) -> None:
        """Initialize Module."""

        try:
            kwargs: Dict = self.__get_webdriver_kwargs(config=config)
            self.browser = webdriver.Chrome(**kwargs)

        except WebDriverException as ex:
            logger.fatal('[!!!] ERROR - You Probably don\'t Have the Chrome Driver Installed. Please, check "https://sites.google.com/a/chromium.org/chromedriver/home" to Install.')
            raise ex

        except Exception as ex:  # noqa: B902 - Fallback 1 - Try the SYSTEM ChromeWebDriver
            logger.error('', ex)  # pylint: disable=E1205
            self.browser = self.__init_fallback_system()

        self.login(config)

    def __init_fallback_system(self) -> webdriver.Chrome:
        """
        Fallback WebDriver Initialization to System Version.

        :return:
        """

        try:
            logger.warning('\t\tCHROME WEB DRIVER - Initialization Fail. Trying Fallback 1 - System Version')
            return webdriver.Chrome()

        except WebDriverException as ex:
            logger.fatal('[!!!] ERROR - You Probably don\'t Have the Chrome Driver Installed. Please, check "https://sites.google.com/a/chromium.org/chromedriver/home" to Install.')
            raise ex

    def __get_webdriver_kwargs(self, config: ConfigParser) -> Dict:
        """
        Return the WebDriver Initialization KWARGS.

        :return:
        """

        is_win32: bool = (platform == 'win32')
        executable_path: str = path.join("assets", 'chromedriver.exe' if platform == 'win32' else 'chromedriver')
        kwargs: Dict = {}

        # Check if Assets Exists, Otherwise, Download Them.
        if not path.exists(executable_path):
            downloadable_file_path: str = path.join('assets', 'chrome_driver.zip')

            logger.info('\t[+] Downloading Chrome Web Driver for %s', 'Windows' if is_win32 else 'Linux')
            HttpNavigationManager.download_file(
                config['WEB_NAVIGATION']['chrome_webdriver_download_uri_win32'] if is_win32 else
                config['WEB_NAVIGATION']['chrome_webdriver_download_uri_linux64'],
                downloadable_file_path
                )

            logger.info('\t\tUnzipping')
            with zipfile.ZipFile(downloadable_file_path, 'r') as zip_ref:
                zip_ref.extractall(path.dirname(executable_path))
            logger.info('\t\tDone')

        kwargs['executable_path'] = executable_path

        return kwargs

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

"""
Facebook Downloader Module.
"""
import time
from configparser import ConfigParser
from typing import Dict
from core.temp_file import TempFileHandler
from selenium.webdriver.common.keys import Keys
from core.base_module import BaseModule
from core.chrome_driver_manager import ChromeDrivers


class FacebookFriendListDownloader(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        target_profile: str = data['facebook']['current_target']
        target_file: str = f'facebook_friend_list/{target_profile}.html'

        # Module Activation Rule
        if target_profile is None or target_profile == '':
            print('\t\tTarget Profile Empty.')
            return

        # Check if Cacheds File Exists
        if TempFileHandler.file_exist(target_file):
            print(f'\t\tTarget File "{target_file}" Alread Exists. Skipping...')
            return

        # Init WebDriver
        print('\t\tDownloading Friends List: ', end='')
        browser = ChromeDrivers.get_fb_webdriver(config)
        browser.maximize_window()

        # Change to Mobile Version
        browser.get(f'https://m.facebook.com/{target_profile}')

        # Open Friends Page
        target_link = [item for item in browser.find_elements_by_tag_name("a") if '/friends?lst=' in str(item.get_attribute('href'))][0]
        browser.get(target_link.get_attribute("href"))

        # Auto Scroll to End :D
        list_size: int = len(browser.find_elements_by_class_name('profpic'))
        while True:
            body = browser.find_element_by_css_selector('body')

            for i in range(8):
                time.sleep(0.1)
                body.send_keys(Keys.PAGE_DOWN)

            # Wait to Load
            time.sleep(2)
            new_list_size: int = browser.find_elements_by_class_name('profpic')

            if list_size == new_list_size:
                # Double Check
                time.sleep(5)
                if list_size == new_list_size:
                    break

            list_size = new_list_size

        browser.minimize_window()

        # Extract Friends
        TempFileHandler.write_file_text(
            target_file,
            browser.page_source
        )

        print('OK')

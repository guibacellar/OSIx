"""Facebook Friend List Extractor."""

import logging

from configparser import ConfigParser
from typing import Dict

from bs4 import BeautifulSoup

from core import constants
from core.base_module import BaseModule
from core.chrome_driver_manager import ChromeDrivers
from core.temp_file import TempFileHandler

logger = logging.getLogger()


class FacebookIdResolver(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        target_profile: str = data['facebook']['current_target']
        target_file: str = f'facebook_id_resolver/{target_profile}.html'
        page_source: str = ''

        # Module Activation Rule
        if target_profile is None or target_profile == '':
            logger.info('\t\tTarget Profile Empty.')
            return

        # Check if Target Profile Alread in Data Struct
        if target_profile not in data['facebook']['profiles']:
            data['facebook']['profiles'][target_profile] = constants.SINGLE_FB_PROFILE_DATA_ITEM.copy()

        # Check if Current Target DO NOT HAVE the FB_ID Alread Resolved
        if data['facebook']['profiles'][target_profile]['id'] != '':
            return

        # Check if Cached File Exists
        if not TempFileHandler.file_exist(target_file):
            logger.info(f'\t\tDownloading "{target_profile}" for Facebook Id Resolver')

            # Init WebDriver
            browser = ChromeDrivers.get_fb_webdriver(config)
            browser.maximize_window()

            # Change to Mobile Version
            browser.get(f'https://m.facebook.com/{target_profile}')
            browser.minimize_window()

            # Write File
            TempFileHandler.write_file_text(target_file, browser.page_source)

            page_source = browser.page_source

        else:
            page_source = ''.join(TempFileHandler.read_file_text(target_file))

        # Open File to BS4
        soup: BeautifulSoup = BeautifulSoup(page_source, 'html.parser')

        # Find ID
        fb_id: str = soup.find('div', id='profile_tab_jewel').find('a')['href'].split('?')[1].replace('%3A', ':').split('&')[0].split('=')[1].split(':')[0]

        # Write
        data['facebook']['profiles'][target_profile]['id'] = fb_id

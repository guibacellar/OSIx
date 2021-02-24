"""
Instagram ID Resolver.

Created by: Th3 0bservator
Based on Work of: Pixie
"""

import logging
import json

from configparser import ConfigParser
from typing import Dict

from core import constants
from core.base_module import BaseModule
from core.temp_file import TempFileHandler
from core.http_manager import HttpNavigationManager

logger = logging.getLogger()


class InstagramIdResolver(BaseModule):
    """Instagram ID Resolver."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        target_profile: str = data['instagram']['current_target']
        target_file: str = f'instagram_id_resolver/{target_profile}.json'
        json_source: str = ''

        # Module Activation Rule
        if target_profile is None or target_profile == '':
            logger.info('\t\tTarget Profile Empty.')
            return

        # Check if Target Profile Already in Data Struct
        if target_profile not in data['instagram']['profiles']:
            data['instagram']['profiles'][target_profile] = constants.SINGLE_INSTAGRAM_PROFILE_DATA_ITEM.copy()

        # Check if Current Target DO NOT HAVE the Instagram ID Already Resolved
        if data['instagram']['profiles'][target_profile]['id'] != '':
            return

        # Check if Cached File Exists
        if not TempFileHandler.file_exist(target_file):
            logger.info(f'\t\tDownloading "{target_profile}" for Instagram Id Resolver')

            json_source = HttpNavigationManager.get(f'https://www.instagram.com/web/search/topsearch/?query={target_profile}')

            # Verify Common Errors
            if 'rate limited' in json_source:
                logger.error(f"Instagram Rate Limit Reached. Unable to Resolve '{target_profile}'. Try again in a few minutes.")
                return

        else:
            logger.info(f'\t\t"{target_profile}".json State File Already Exists.')
            json_source = ''.join(TempFileHandler.read_file_text(target_file))

        # Load Json
        json_data: Dict = json.loads(json_source)

        # Find Proper Record

        try:
            user_info: Dict = [
                item for item in json_data['users'] if item['user']['username'] == target_profile
                ][0]['user']

            # Write on Data
            data['instagram']['profiles'][target_profile]['id'] = user_info['pk']
            data['instagram']['profiles'][target_profile]['fullname'] = user_info['full_name']
            data['instagram']['profiles'][target_profile]['profile_pic'] = user_info['profile_pic_url']

        except IndexError:
            logger.info("\n\nInstagram Account is not Found.")

        # Write Temp File
        TempFileHandler.write_file_text(
            target_file,
            json_source
            )

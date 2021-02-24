"""
Facebook Friend List Extractor
"""
from bs4 import BeautifulSoup
from core import constants
from configparser import ConfigParser
from typing import Dict
from core.base_module import BaseModule
from core.temp_file import TempFileHandler
import re
import json


class FacebookFriendListExtractor(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        target_profile: str = data['facebook']['current_target']
        target_file: str = f'facebook_friend_list/{target_profile}.html'

        # Check if File Exists
        if not TempFileHandler.file_exist(target_file):
            print(f'\t\t Target File "{target_file}" not Exists.')

        # Check if Target Profile Alread in Data Struct
        if target_profile not in data['facebook']['profiles']:
            data['facebook']['profiles'][target_profile] = constants.SINGLE_FB_PROFILE_DATA_ITEM.copy()

        # Prepare RegEx
        profile_pic_regex: re = re.compile("url\('.*'\)")

        # Open File to BS4
        soup = BeautifulSoup(''.join(TempFileHandler.read_file_text(target_file)), 'html.parser')

        # Extract Friends
        timeline_div = soup\
            .find('div', id='viewport')\
            .find('div', id='rootcontainer')\
            .find('div', id='root')\
            .find('div', 'timeline')

        friends_blocks = timeline_div.find('header').find_next_sibling().children

        for single_block in friends_blocks:
            for single_friend_div in single_block.children:
                try:
                    friend_path: str = single_friend_div.find('a')['href']
                except:
                    friend_path: str = None

                friend_image_path: str = single_friend_div.find('i', 'profpic')['style']
                friend_name: str = list(single_friend_div.children)[1].find('a').text
                fb_id: str = json.loads(single_friend_div.find('a', 'touchable')['data-store'])['id']

                # Build new Data
                new_friend_item: Dict = constants.SINGLE_FB_FRIEND_DATA_ITEM.copy()
                new_friend_item['name'] = friend_name
                new_friend_item['id'] = fb_id
                new_friend_item['path'] = friend_path
                try:
                    new_friend_item['profile_pic'] = profile_pic_regex\
                            .findall(friend_image_path)[0]\
                            .replace("url('", '')\
                            .replace("')", "")\
                            .replace('\\3a', ':')\
                            .replace('\\3d', '=')\
                            .replace('\\26', '&')\
                            .replace(' ', '')
                except:
                    new_friend_item['profile_pic'] = friend_image_path

                # Add Into Data
                data['facebook']['profiles'][target_profile]['friends'].append(new_friend_item)

        total_friends: int = len(data['facebook']['profiles'][target_profile]['friends'])
        print(f'\t\t[+] Extracted {total_friends} Friends')

"""Facebook Friend List Extractor."""

from configparser import ConfigParser
import json
import re
import logging

from typing import Dict, Optional

from bs4 import BeautifulSoup, Tag

from core import constants
from core.base_module import BaseModule
from core.temp_file import TempFileHandler

logger = logging.getLogger()


class FacebookFriendListExtractor(BaseModule):
    """Temporary File Manager."""

    def __init__(self) -> None:
        """Module Initialization."""

        self.profile_pic_regex: re.Pattern = re.compile("url\\('.*'\\)")

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        target_profile: str = data['facebook']['current_target']
        target_file: str = f'facebook_friend_list/{target_profile}.html'

        # Module Activation Rule
        if target_profile is None or target_profile == '':
            logger.info('\t\tTarget Profile Empty.')
            return

        # Check if File Exists
        if not TempFileHandler.file_exist(target_file):
            logger.info(f'\t\t Target File "{target_file}" not Exists.')
            return

        # Check if Target Profile Alread in Data Struct
        if target_profile not in data['facebook']['profiles']:
            data['facebook']['profiles'][target_profile] = constants.SINGLE_FB_PROFILE_DATA_ITEM.copy()

        # Open File to BS4
        soup: BeautifulSoup = BeautifulSoup(''.join(TempFileHandler.read_file_text(target_file)), 'html.parser')

        # Extract Friends
        timeline_div: Tag = soup\
            .find('div', id='viewport')\
            .find('div', id='rootcontainer')\
            .find('div', id='root')\
            .find('div', 'timeline')

        friends_blocks: Tag = timeline_div.find('header').find_next_sibling().children

        self.__process_friends_blocks(
            friends_blocks=friends_blocks,
            target_profile=target_profile,
            data=data
            )

        total_friends: int = len(data['facebook']['profiles'][target_profile]['friends'])
        logger.info(f'\t\tExtracted {total_friends} Friends')

    def __process_friends_blocks(self, friends_blocks: Tag, target_profile: str, data: Dict) -> None:
        """
        Parse Friends List Block.

        :param friends_blocks: Friends List Block Tag
        :param target_profile: Target Profile
        :param data: Data Object
        :return: None
        """

        for single_block in friends_blocks:
            for single_friend_div in single_block.children:

                friend_path: Optional[str] = None
                try:
                    friend_path = single_friend_div.find('a')['href']
                except KeyError:
                    pass

                friend_image_path: str = single_friend_div.find('i', 'profpic')['style']
                friend_name: str = list(single_friend_div.children)[1].find('a').text
                fb_id: str = json.loads(single_friend_div.find('a', 'touchable')['data-store'])['id']

                # Build new Data
                new_friend_item: Dict = constants.SINGLE_FB_FRIEND_DATA_ITEM.copy()
                new_friend_item['name'] = friend_name
                new_friend_item['id'] = fb_id
                new_friend_item['path'] = friend_path

                try:
                    new_friend_item['profile_pic'] = self.profile_pic_regex\
                        .findall(friend_image_path)[0]\
                        .replace("url('", '')\
                        .replace("')", "")\
                        .replace('\\3a', ':')\
                        .replace('\\3d', '=')\
                        .replace('\\26', '&')\
                        .replace(' ', '')

                except KeyError:
                    new_friend_item['profile_pic'] = friend_image_path

                # Add Into Data
                data['facebook']['profiles'][target_profile]['friends'].append(new_friend_item)

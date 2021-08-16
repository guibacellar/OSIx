"""Steam Username Data Digger - Digger Downloaded Data for Usefull Information."""

import re
import logging

from configparser import ConfigParser
from typing import Dict, Optional

from bs4 import BeautifulSoup

from OSIx.core.base_username_data_digger import SimpleUsernameDataDigger
from OSIx.core.bs4_helper import BS4Helper
from OSIx.core.decorator import bs4_error_hander

logger = logging.getLogger()


class SteamUsernameDataDigger(SimpleUsernameDataDigger):
    """Steam Username Data Digger."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check Steam Section
        if 'steam' not in data:
            data['steam'] = {}

        logger.info('\t\tRunning...')
        h_result: Dict = self.__get_steam_data(
            username=username,
            config=config
            )

        # Add to Data
        data['steam'][username] = h_result

        # Check if Found Anything
        if h_result['steam_id'] is None:
            logger.info('\t\tUsername/SteamId Not Found.')
            return

    def __get_steam_data(self, username: str, config: ConfigParser) -> Dict:
        """Get the Steam Data."""

        # Download the Steam Profile Main Page Data
        base_url = config['MODULE_SteamUsernameDataDigger']['steam_main_profile_url'].replace('{0}', username)
        steam_data_profile: str = self._download_text(url=base_url, module='steam')

        # Load HTML
        bs4_helper_profile: BS4Helper = BS4Helper(soup=BeautifulSoup(steam_data_profile, 'html.parser'))

        steam_id: Optional[str] = self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_id_scan_regex'], steam_data_profile)

        if steam_id is None:
            return {
                'steam_id': None,
                'steam_id_64_dec': None,
                'username': None,
                'fullname': None,
                'location': None,
                'profile_pic': None
                }

        return {
            'steam_id': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_id_scan_regex'], steam_data_profile),
            'steam_id_64_dec': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_id_scan_regex'], steam_data_profile),
            'username': bs4_helper_profile.find_by_attribute(attribute_data=('class', 'actual_persona_name'), target_index=0, target_property='text', null_value=None),
            'fullname': self.__get_fullname(bs4_helper_profile),
            'location': bs4_helper_profile.clenup_string(bs4_helper_profile.soup.find_all(attrs={'class': 'header_real_name'})[0].find_all(attrs={'class': 'profile_flag'})[0].next_sibling),
            'profile_pic': self.__get_profile_image(bs4_helper_profile)
            }

    @bs4_error_hander()
    def __get_profile_image(self, bs4_helper_profile: BS4Helper) -> str:
        """Return the Profile Image."""

        return str(bs4_helper_profile.soup.find_all(attrs={'class': 'playerAvatarAutoSizeInner'})[0].find('img').attrs['src'])

    @bs4_error_hander()
    def __get_fullname(self, bs4_helper_profile: BS4Helper) -> str:
        """Return the FullName."""

        return str(bs4_helper_profile.soup.find_all(attrs={'class': 'header_real_name'})[0].find_all('bdi')[0].text)

    @bs4_error_hander()
    def __get_capture_group(self, regex: str, target: str, index: int = 0) -> Optional[str]:
        """Safe Get the Capture Group Value."""

        mt: Optional[re.Match[str]] = re.compile(regex).search(target)
        if mt is None:
            return None

        return str(mt.groups()[index])


class SteamIdFinderDataDigger(SimpleUsernameDataDigger):
    """Steam Id Finder Data Digger."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check if Found Anything
        h_result: Dict = {
            'steam_id_64_hex': None,
            'steam_id_3': None,
            'steam_id': None,
            'profile_state': None,
            'profile_creation_data': None,
            }

        if data['steam'][username]['steam_id'] is not None:
            # Get Data
            logger.info('\t\tRunning...')
            h_result = self.__get_steam_id_data(
                steam_id=data['steam'][username]['steam_id'],
                config=config
                )

        else:
            logger.info('\t\tSteamId Not Present.')

        # Update Data
        data['steam'][username].update(h_result)

    def __get_steam_id_data(self, steam_id: str, config: ConfigParser) -> Dict:
        """Get the Steam Finder Data."""

        # Download the Steam Profile Main Page Data
        base_url = config['MODULE_SteamUsernameDataDigger']['steam_finder_url'].replace('{0}', steam_id)
        steam_data_profile: str = self._download_text(url=base_url, module='steam')

        # Load HTML
        h_result: Dict = {
            'steam_id_64_hex': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_finder_id64_hex_regex'], steam_data_profile),
            'steam_id_3': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_finder_id3_regex'], steam_data_profile),
            'steam_id': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_finder_id_regex'], steam_data_profile),
            'profile_state': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_finder_profile_state_regex'], steam_data_profile),
            'profile_creation_data': self.__get_capture_group(config['MODULE_SteamUsernameDataDigger']['steam_finder_profile_created_regex'], steam_data_profile),
            }

        return h_result

    @bs4_error_hander()
    def __get_capture_group(self, regex: str, target: str, index: int = 0) -> Optional[str]:
        """Safe Get the Capture Group Value."""

        mt: Optional[re.Match[str]] = re.compile(regex).search(target)
        if mt is None:
            return None

        return str(mt.groups()[index])


class SteamDataPrinter(SimpleUsernameDataDigger):
    """Print Steam Data into Sysout."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check if Found Anything
        if data['steam'][username]['steam_id'] is None:
            logger.info('\t\tSteamId Not Present.')
            return

        # Dump the Output File
        if args['username_print_result']:
            logger.info(f'\t\tSteam Id..............: {data["steam"][username]["steam_id"]}')
            logger.info(f'\t\tSteam Id 3............: {data["steam"][username]["steam_id_3"]}')
            logger.info(f'\t\tSteam Id 64 Hex.......: {data["steam"][username]["steam_id_64_hex"]}')
            logger.info(f'\t\tSteam Id.64 Dec.......: {data["steam"][username]["steam_id_64_dec"]}')
            logger.info(f'\t\tUsername..............: {data["steam"][username]["username"]}')
            logger.info(f'\t\tFull Name.............: {data["steam"][username]["fullname"]}')
            logger.info(f'\t\tLocation..............: {data["steam"][username]["location"]}')
            logger.info(f'\t\tProfile Picture.......: {data["steam"][username]["profile_pic"]}')
            logger.info(f'\t\tProfile State.........: {data["steam"][username]["profile_state"]}')
            logger.info(f'\t\tProfile Creation Date.: {data["steam"][username]["profile_creation_data"]}')

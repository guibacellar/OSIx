"""Gravatar Username Data Digger - Digger Downloaded Data for Usefull Information."""

import re
import logging
import urllib
import urllib.parse

from configparser import ConfigParser
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, ResultSet, Tag

from OSIx.core.base_username_data_digger import SimpleUsernameDataDigger
from OSIx.core.bs4_helper import BS4Helper
from OSIx.core.decorator import bs4_error_hander

logger = logging.getLogger()


class GravatarUsernameDataDigger(SimpleUsernameDataDigger):
    """Gravatar Username Data Digger."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check Gravatar Section
        if 'gravatar' not in data:
            data['gravatar'] = {}

        logger.info('\t\tRunning...')
        h_result: Dict = self.__get_gravatar_data(
            username=username,
            config=config
            )

        # Add to Data
        data['gravatar'][username] = h_result

        # Check if Found Anything
        if h_result['username'] is None:
            logger.info('\t\tUsername Not Found.')
            return

    def __get_gravatar_data(self, username: str, config: ConfigParser) -> Dict:
        """Get the Gravatar Data."""

        # Download the Gravatar Profile Main Page Data
        base_url = config['MODULE_GravatarUsernameDataDigger']['profile_url'].replace('{0}', username)
        gravatar_data_profile: str = self._download_text(url=base_url, module='gravatar')

        # Check if Found
        if 'sorry, we couldn\'t find that' in gravatar_data_profile:
            return {
                'gravatar_id': None,
                'image': None,
                'username': None,
                'fullname': None,
                'location': None,
                'links': [],
                'gravatar_url': None
                }

        # Load HTML
        bs4_helper_profile: BS4Helper = BS4Helper(soup=BeautifulSoup(gravatar_data_profile, 'html.parser'))

        return {
            'gravatar_id': self.__get_capture_group(regex=config['MODULE_GravatarUsernameDataDigger']['gravatar_id_regex'], target=gravatar_data_profile, index=0),
            'image': self.__get_capture_group(regex=config['MODULE_GravatarUsernameDataDigger']['gravatar_image_regex'], target=gravatar_data_profile, index=0),
            'username': username,
            'fullname': self.__get_profile_fullname(bs4_helper_profile),
            'location': self.__get_location(bs4_helper_profile),
            'links': self.__get_links(bs4_helper_profile, config),
            'gravatar_url': base_url
            }

    @bs4_error_hander()
    def __get_capture_group(self, regex: str, target: str, index: int = 0) -> Optional[str]:
        """Safe Get the Capture Group Value."""

        mt: Optional[re.Match[str]] = re.compile(regex).search(target)
        if mt is None:
            return None

        return str(mt.groups()[index])

    @bs4_error_hander(on_error_return_value='')
    def __get_links(self, bs4_helper_profile: BS4Helper, config: ConfigParser) -> List:
        """Return the Username."""

        h_result: List = []

        list_details: ResultSet = [item for item in bs4_helper_profile.soup.find_all('ul', attrs={'class': 'list-details'}) if isinstance(item, Tag)]

        # Iterate over "Find Me Online" & "Contact Me" Lists
        for list_node in list_details:

            # Iterate over List Items (Contacts, Links, etc)
            for node in [item for item in list_node if isinstance(item, Tag)]:

                # Parse Single Info
                children: List = [item for item in node.children if isinstance(item, Tag)]

                if len(children) < 2:
                    continue

                is_target_js: bool = (children[1].find('a') is None)

                entry: Dict = {
                    'name': children[0].text,
                    'full_target': self.__resolve_gravatar_info(children[1]) if not is_target_js else self.__resolve_gravatar_info_obfuscation(str(children[1].find('script').next), config)
                    }
                entry['target'] = self.__sanitize(entry['full_target'])

                h_result.append(entry)

        return h_result

    def __resolve_gravatar_info(self, target: ResultSet) -> str:
        """Resolve Gravatar Information."""

        href: str = target.find('a').attrs['href']

        if href == '#':
            return str(target.find('a').text)

        return str(urllib.parse.unquote(target.find('a').attrs['href']))

    def __resolve_gravatar_info_obfuscation(self, info: str, config: ConfigParser) -> str:
        """Resolve Gravatar Information Obfuscation using JS."""

        if 'grav_email' in info:
            regex_a: str = config['MODULE_GravatarUsernameDataDigger']['gravatar_email_deobfuscation_regex']  # Capture This: ' grav_email( 'qualitybargain', 'mail.com' ); '

            return f'{self.__get_capture_group(regex_a, info, 0)}@{self.__get_capture_group(regex_a, info, 1)}'

        if 'xmpp' in info:
            regex_b: str = config['MODULE_GravatarUsernameDataDigger']['gravatar_email_xmpp_regex']  # Capture This: ' grav_email( 'qualitybargain', 'mail.com' ); '

            return f'{self.__get_capture_group(regex_b, info, 0)}'

        return info

    @bs4_error_hander(on_error_return_value='')
    def __get_profile_fullname(self, bs4_helper_profile: BS4Helper) -> str:
        """Return the Username."""

        return str(bs4_helper_profile.soup.find_all('div', attrs={'class', 'profile-description'})[0].find('h2').find('a').text)

    @bs4_error_hander(on_error_return_value='')
    def __get_location(self, bs4_helper_profile: BS4Helper) -> str:
        """Return the Profile Picture."""

        return str(bs4_helper_profile.soup.find_all('div', attrs={'class', 'profile-description'})[0].find('p').text)

    def __sanitize(self, content: str) -> str:
        """Sanitize String."""

        return content\
            .replace('aim:goim?screenname=', '')\
            .replace('ymsgr:sendim?', '')\
            .replace('skype:', '')


class GravatarDataPrinter(SimpleUsernameDataDigger):
    """Print Gravatar Data into Sysout."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check if Found Anything
        if data['gravatar'][username]['username'] is None:
            logger.info('\t\tUsername Not Present.')
            return

        # Dump the Output File
        if args['username_print_result']:
            logger.info(f'\t\tGravatar ID......: {data["gravatar"][username]["gravatar_id"]}')
            logger.info(f'\t\tUsername.........: {data["gravatar"][username]["username"]}')
            logger.info(f'\t\tFull Name........: {data["gravatar"][username]["fullname"]}')
            logger.info(f'\t\tProfile Picture..: {data["gravatar"][username]["image"]}')
            logger.info(f'\t\tLocation.........: {data["gravatar"][username]["location"]}')
            logger.info(f'\t\tLinks............: {len(data["gravatar"][username]["links"])}')

            for paste in data["gravatar"][username]["links"]:
                logger.info(f'\t\t\t{paste["name"]} ({paste["full_target"]}) > {paste["target"]}')

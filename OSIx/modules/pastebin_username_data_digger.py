"""Pastebin Username Data Digger - Digger Downloaded Data for Usefull Information."""

import logging

from configparser import ConfigParser
from typing import Dict, List

from bs4 import BeautifulSoup, ResultSet, Tag

from OSIx.core.base_username_data_digger import SimpleUsernameDataDigger
from OSIx.core.bs4_helper import BS4Helper
from OSIx.core.decorator import bs4_error_hander

logger = logging.getLogger()


class PastebinUsernameDataDigger(SimpleUsernameDataDigger):
    """Pastebin Username Data Digger."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check Pastebin Section
        if 'pastebin' not in data:
            data['pastebin'] = {}

        logger.info('\t\tRunning...')
        h_result: Dict = self.__get_pastebin_data(
            username=username,
            config=config
            )

        # Add to Data
        data['pastebin'][username] = h_result

        # Check if Found Anything
        if h_result['username'] is None:
            logger.info('\t\tUsername Not Found.')
            return

    def __get_pastebin_data(self, username: str, config: ConfigParser) -> Dict:
        """Get the Pastebin Data."""

        # Download the Pastebin Profile Main Page Data
        base_url = config['MODULE_PastebinUsernameDataDigger']['profile_url'].replace('{0}', username)
        pastebin_data_profile: str = self._download_text(url=base_url, module='pastebin')

        # Check if Found
        if 'Not Found (#404)' in pastebin_data_profile:
            return {
                'image': None,
                'views_count': None,
                'all_views_count': None,
                'created_at': None,
                'username': None,
                'public_pastes': []
                }

        # Load HTML
        bs4_helper_profile: BS4Helper = BS4Helper(soup=BeautifulSoup(pastebin_data_profile, 'html.parser'))

        return {
            'image': self.__get_image(bs4_helper_profile, config),
            'views_count': int(str(bs4_helper_profile.find_by_attribute(attribute_data=('class', 'views'), target_index=0, target_property='string', null_value=None)).replace(',', '').replace('.', '')),
            'all_views_count': int(str(bs4_helper_profile.find_by_attribute(attribute_data=('class', 'views -all'), target_index=0, target_property='string', null_value=None)).replace(',', '').replace('.', '')),
            'created_at': bs4_helper_profile.find_by_attribute(attribute_data=('class', 'date-text'), target_index=0, target_property='title', null_value=None),
            'username': self.__get_username(bs4_helper_profile),
            'public_pastes': self.__get_public_pastes(bs4_helper_profile, config)
            }

    @bs4_error_hander(on_error_return_value='')
    def __get_username(self, bs4_helper_profile: BS4Helper) -> str:
        """Return the Username."""

        return str(bs4_helper_profile.soup.find_all('div', attrs={'class', 'user-icon'})[0].find('img').attrs['alt'])

    @bs4_error_hander(on_error_return_value='')
    def __get_image(self, bs4_helper_profile: BS4Helper, config: ConfigParser) -> str:
        """Return the Profile Picture."""

        return config["MODULE_PastebinUsernameDataDigger"]["base_profile_pic_url"].replace(
            "{0}",
            bs4_helper_profile.soup.find_all('div', attrs={'class', 'user-icon'})[0].find('img').attrs['src']
            )

    @bs4_error_hander(on_error_return_value=[])
    def __get_public_pastes(self, bs4_helper_profile: BS4Helper, config: ConfigParser) -> List[Dict]:
        """The the Public Pastes List."""

        h_result: List = []

        # Load all Public Pastes
        table_rs: ResultSet = bs4_helper_profile.soup.find_all(attrs={'class': 'maintable'})[0].find_all('tr')

        if len(table_rs) == 0:
            return h_result

        table_rs = list(table_rs)[1:]

        for item in table_rs:
            children: List = [item for item in list(item.children) if isinstance(item, Tag)]

            h_result.append({
                'title': children[0].find('a').text,
                'short_url': children[0].find('a').attrs['href'],
                'full_url': config['MODULE_PastebinUsernameDataDigger']['base_paste_url'].replace('{0}', children[0].find('a').attrs['href']),
                'date': children[1].text,
                'expires_at': children[2].text,
                'views_count': int(children[3].text.replace('.', '').replace(',', ''))
                })

        return h_result


class PastebinDataPrinter(SimpleUsernameDataDigger):
    """Print Pastebin Data into Sysout."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check if Found Anything
        if data['pastebin'][username]['username'] is None:
            logger.info('\t\tUsername Not Present.')
            return

        # Dump the Output File
        if args['username_print_result']:
            logger.info(f'\t\tUsername.................: {data["pastebin"][username]["username"]}')
            logger.info(f'\t\tCreated at...............: {data["pastebin"][username]["created_at"]}')
            logger.info(f'\t\tViews Count..............: {data["pastebin"][username]["views_count"]}')
            logger.info(f'\t\tUsers Pastes Views Count.: {data["pastebin"][username]["all_views_count"]}')
            logger.info(f'\t\tProfile Picture..........: {data["pastebin"][username]["image"]}')
            logger.info(f'\t\tN. Public Pastes.........: {len(data["pastebin"][username]["public_pastes"])}')

            for paste in data["pastebin"][username]["public_pastes"]:
                logger.info(f'\t\t\t{paste["title"]} ({paste["date"]}) at {paste["full_url"]}')

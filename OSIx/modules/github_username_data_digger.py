"""GitHub Username Data Digger - Digger Downloaded Data for Usefull Information."""
import logging

from configparser import ConfigParser
from typing import Dict, List

from bs4 import BeautifulSoup, ResultSet, Tag

from OSIx.core.base_username_data_digger import SimpleUsernameDataDigger
from OSIx.core.bs4_helper import BS4Helper

logger = logging.getLogger()


class GithubUsernameDataDigger(SimpleUsernameDataDigger):
    """Github Username Data Digger."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Get all Data
        logger.info('\t\tRunning...')
        h_result: Dict = self.__get_gh_data(
            config=config,
            username=username
            )

        # Add to Data
        if 'github' not in data:
            data['github'] = {}

        data['github'][username] = h_result

        # Check if Found Anything
        if h_result['account_id'] is None:
            logger.info('\t\tUsername Not Found.')
            return

    def __get_gh_data(self, config: ConfigParser, username: str) -> Dict:
        """Download and Get GitHub Data."""

        # Download the GitHub Profile Page Data
        base_url = config['MODULE_GithubUsernameDataDigger']['profile_url'].replace('{0}', username)
        github_data_profile: str = self._download_text(url=base_url, module='github')

        # Load HTML
        bs4_helper_profile: BS4Helper = BS4Helper(soup=BeautifulSoup(github_data_profile, 'html.parser'))

        # Get all Data
        return {
            'profile_pic': bs4_helper_profile.find_by_attribute(attribute_data=('alt', 'Avatar'), target_index=0, target_property='src', null_value=None),
            'fullname': bs4_helper_profile.find_by_attribute(attribute_data=('itemprop', 'name'), target_index=0, target_property='string', null_value=None),
            'nickname': bs4_helper_profile.find_by_attribute(attribute_data=('itemprop', 'additionalName'), target_index=0, target_property='string', null_value=None),
            'bio': bs4_helper_profile.find_by_attribute(attribute_data=('class', 'user-profile-bio'), target_index=0, target_property='string', null_value=None),
            'location': bs4_helper_profile.find_by_attribute(attribute_data=('itemprop', 'homeLocation'), target_index=0, target_property='text', null_value=None),
            'website': bs4_helper_profile.find_by_attribute(attribute_data=('itemprop', 'url'), target_index=0, target_property='text', null_value=None),
            'account_id': bs4_helper_profile.find_by_attribute(attribute_data=('role', 'search'), target_index=0, target_property='data-scope-id', null_value=None),
            'repos': self.__get_repos(base_url),
            'followers': self.__get_followers(base_url),
            'following': self.__get_following(base_url)
            }

    def __get_following(self, base_url: str) -> List[Dict]:
        """Get the Following."""

        bs4_helper_following: BS4Helper = BS4Helper(
            soup=BeautifulSoup(self._download_text(url=base_url + '?tab=following', module='github'), 'html.parser')
            )

        all_following: List = []

        following_list_node: ResultSet = bs4_helper_following.soup.find_all(attrs={'class': 'd-inline-block no-underline mb-1'})

        if len(following_list_node) > 0:
            for item in following_list_node:
                if isinstance(item, Tag):

                    all_following.append(
                        {
                            'name': bs4_helper_following.find_by_attribute(attribute_data=('class', 'f4 Link--primary'), target_property='text', target_index=0, target=item),
                            'username': bs4_helper_following.find_by_attribute(attribute_data=('class', 'Link--secondary'), target_property='text', target_index=0, target=item),
                            'url': item.attrs['href']
                            }
                        )

        return all_following

    def __get_followers(self, base_url: str) -> List[Dict]:
        """Get User Followers."""

        bs4_helper_followers: BS4Helper = BS4Helper(
            soup=BeautifulSoup(self._download_text(url=base_url + '?tab=followers', module='github'), 'html.parser')
            )

        all_followers: List = []

        followers_list_node: ResultSet = bs4_helper_followers.soup.find_all(attrs={'class': 'd-inline-block no-underline mb-1'})

        if len(followers_list_node) > 0:
            for item in followers_list_node:
                if isinstance(item, Tag):
                    all_followers.append(
                        {
                            'name': bs4_helper_followers.find_by_attribute(attribute_data=('class', 'f4 Link--primary'), target_property='text', target_index=0, target=item),
                            'username': bs4_helper_followers.find_by_attribute(attribute_data=('class', 'Link--secondary'), target_property='text', target_index=0, target=item),
                            'url': item.attrs['href']
                            }
                        )

        return all_followers

    def __get_repos(self, base_url: str) -> List[Dict]:
        """Get Repo List."""

        bs4_helper_repos: BS4Helper = BS4Helper(
            soup=BeautifulSoup(self._download_text(url=base_url + '?tab=repositories', module='github'), 'html.parser')
            )

        all_repos: List = []

        repo_list_node: ResultSet = bs4_helper_repos.soup.find_all(attrs={'data-filterable-for': 'your-repos-filter'})

        if len(repo_list_node) > 0:
            for item in repo_list_node[0].children:
                if isinstance(item, Tag):
                    all_repos.append(
                        {
                            'name': bs4_helper_repos.find_by_attribute(attribute_data=('itemprop', 'name codeRepository'), target_property='text', target_index=0, target=item),
                            'description': bs4_helper_repos.find_by_attribute(attribute_data=('itemprop', 'description'), target_property='text', target_index=0, target=item),
                            'url': bs4_helper_repos.find_by_attribute(attribute_data=('itemprop', 'name codeRepository'), target_property='href', target_index=0, target=item),
                            'type': 'fork' if 'fork' in item.attrs['class'] else 'owner'
                            }
                        )

        return all_repos


class GithubDataPrinter(SimpleUsernameDataDigger):
    """Print GitHub Data into Sysout."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check the Activation and Get The Social Network Data
        can_activate, username = self._can_activate(data=data)

        if not can_activate or username is None:
            return

        # Check if Found Anything
        if data['github'][username]['account_id'] is None:
            logger.info('\t\tGitHub Account Id Not Present.')
            return

        if args['username_print_result']:
            logger.info(f'\t\tFull Name.......: {data["github"][username]["fullname"]}')
            logger.info(f'\t\tNick Name.......: {data["github"][username]["nickname"]}')
            logger.info(f'\t\tBio.............: {data["github"][username]["bio"]}')
            logger.info(f'\t\tLocation........: {data["github"][username]["location"]}')
            logger.info(f'\t\tWebSite.........: {data["github"][username]["website"]}')
            logger.info(f'\t\tAccount ID......: {data["github"][username]["account_id"]}')
            logger.info(f'\t\tProfile Picture.: {data["github"][username]["profile_pic"]}')

            logger.info(f'\t\tRepos...........: {len(data["github"][username]["repos"])}')
            _ = [logger.info(f'\t\t\t{item["name"]} ({item["description"]}) at https://github.com{item["url"]}') for item in data["github"][username]['repos']]  # type: ignore

            logger.info(f'\t\tFollowers.......: {len(data["github"][username]["followers"])}')
            _ = [logger.info(f'\t\t\t{item["username"]} ({item["name"]}) at https://github.com{item["url"]}') for item in data["github"][username]['followers']]  # type: ignore

            logger.info(f'\t\tFollowing.......: {len(data["github"][username]["following"])}')
            _ = [logger.info(f'\t\t\t{item["username"]} ({item["name"]}) at https://github.com{item["url"]}') for item in data["github"][username]['following']]  # type: ignore

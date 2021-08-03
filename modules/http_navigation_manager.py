"""HTTP Navigation Manager."""

from configparser import ConfigParser
from typing import Dict, List

import logging

import random

from core.base_module import BaseModule

from core.http_manager import HttpNavigationManager
logger = logging.getLogger()


class HttpNavigationManagerHandler(BaseModule):
    """HTTP Navigation Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check if Not have a Selected UA
        if 'web_navigation' not in data or 'user_agent' not in data['web_navigation']:
            data.update(
                {'web_navigation': {'user_agent': self.__choose_ua(config)}}
                )

        # Initialize Internal Modules
        HttpNavigationManager.init(data)

    def __choose_ua(self, config: ConfigParser) -> str:
        """Choose a Random UA."""

        if config:
            ua_list: List[str] = config['WEB_NAVIGATION']['useragent_list'].split('\n')
            return ua_list[random.Random().randint(1, len(ua_list) - 1)]  # nosec

        raise Exception("System Configuration Not Initialized")

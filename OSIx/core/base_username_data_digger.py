"""Base Module for Simple Username Data Diggers."""

import abc
import logging
import hashlib
from configparser import ConfigParser
from typing import Dict, Optional, Tuple

from OSIx.core.base_module import BaseModule
from OSIx.core.http_manager import HttpNavigationManager
from OSIx.core.temp_file import TempFileHandler

logger = logging.getLogger()


class SimpleUsernameDataDigger(BaseModule):
    """Simple Username Data Digger."""

    @abc.abstractmethod
    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """
        Base Run Description.

        :return: None
        """

    def _can_activate(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if Can Activate the Digger.

        :param data: Data Dict
        :return: A Boolean Indicator about the Activation and the Target Username
        """

        if 'username' not in data:
            logger.info('\t\tUsername Not Provided. Skipping...')
            return False, None

        target_username: str = data['username']['target_username']

        if target_username == '':
            logger.info('\t\tUsername Not Provided. Skipping...')
            return False, None

        return True, target_username

    def _download_text(self, url: str) -> str:
        """Download Remote Data."""

        # Check Temp File
        targer_file_name: str = hashlib.md5(url.encode('utf-8')).hexdigest()  # nosec

        # Load Temporary Files
        target_file_path: str = f'username_search/{targer_file_name}.json'

        if TempFileHandler.file_exist(target_file_path):
            return ''.join(TempFileHandler.read_file_text(target_file_path))

        # File Not Exists, Download and Save
        content: str = HttpNavigationManager.get(url)

        # Save Temp File
        TempFileHandler.write_file_text(target_file_path, content)

        # Return
        return content

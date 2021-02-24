"""Temporary Files Manager."""

from datetime import datetime
from configparser import ConfigParser
import os
from typing import Dict

import pytz

from core.base_module import BaseModule


class TempFileManager(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        if args['purge_temp_files']:
            self.purge_folder('data/temp/facebook_friend_list')
            self.purge_folder('data/temp/facebook_id_resolver')
        else:
            self.check_folder_items_age('data/temp/facebook_friend_list', int(config['TEMP_FILES']['facebook_friend_list_age_seconds']))
            self.check_folder_items_age('data/temp/facebook_id_resolver', int(config['TEMP_FILES']['facebook_id_page_age_seconds']))

    def check_folder_items_age(self, path: str, max_age_seconds: int) -> None:
        """
        Check Folder Items Age.

        :param path: Path to Check
        :param max_age_seconds: Max Age in Seconds
        :return: None
        """
        print(f'\t\t[+] Checking Age {path}')
        for file in os.scandir(path):
            file_age: int = int(os.stat(file).st_ctime)

            if (int(datetime.now(tz=pytz.UTC).timestamp()) - file_age) > max_age_seconds:
                os.remove(file)

    def purge_folder(self, path: str) -> None:
        """
        Purge a Single Folder.

        :param path: Folder Path
        :return:
        """

        print(f'\t\t[+] Purging {path}')

        for file in os.scandir(path):
            os.remove(file)

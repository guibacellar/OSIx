"""Temporary Files Manager."""

import os
import logging

from configparser import ConfigParser
from datetime import datetime
from typing import Dict

import pytz

from core.base_module import BaseModule
from core.temp_file import TempFileHandler

logger = logging.getLogger()


class TempFileManager(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Check Folder Structure
        self.__ensure_folder_structure(config=config)

        if args['purge_temp_files']:
            self.__purge_all(config=config)

        else:
            self.__check_by_age(config=config)

    def __ensure_folder_structure(self, config: ConfigParser) -> None:
        """Ensure the Folders Structure."""

        for temp_file_info in config['TEMP_FILES']:
            temp_def: str = config['TEMP_FILES'][temp_file_info]
            TempFileHandler.ensure_dir_struct(temp_def.split(';')[0])

    def __check_folder_items_age(self, path: str, max_age_seconds: int) -> None:
        """
        Check Folder Items Age.

        :param path: Path to Check
        :param max_age_seconds: Max Age in Seconds
        :return: None
        """
        logger.debug(f'\t\tChecking Age {path} for {max_age_seconds} seconds')
        for file in os.scandir(path):
            file_age: int = int(os.stat(file).st_ctime)

            if (int(datetime.now(tz=pytz.UTC).timestamp()) - file_age) > max_age_seconds:
                os.remove(file)

    def __purge_folder(self, path: str) -> None:
        """
        Purge a Single Folder.

        :param path: Folder Path
        :return:
        """

        logger.debug(f'\t\tPurging {path}')

        for file in os.scandir(path):
            os.remove(file)

    def __purge_all(self, config: ConfigParser) -> None:
        """Purge all Folders."""

        for temp_file_info in config['TEMP_FILES']:
            temp_def: str = config['TEMP_FILES'][temp_file_info]
            self.__purge_folder(temp_def.split(';')[0])

    def __check_by_age(self, config: ConfigParser) -> None:
        """Check Folders file By Age."""

        for temp_file_info in config['TEMP_FILES']:
            temp_def: str = config['TEMP_FILES'][temp_file_info]
            folder_name: str = temp_def.split(';')[0]
            age: int = int(temp_def.split(';')[1])
            self.__check_folder_items_age(f'data/temp/{folder_name}', age)

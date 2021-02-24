"""
OSIx - Open Source Intelligence eXplorer.

By: Th3 0bservator
"""

import sys
import argparse
import importlib
import os
import types
from uuid import uuid4
import logging
import logging.config

import random

from configparser import ConfigParser
from typing import Dict, List, Optional

from core.base_module import BaseModule
from core.temp_file import TempFileHandler
from core.chrome_driver_manager import ChromeDrivers
from core.http_manager import HttpNavigationManager

logger = logging.getLogger()

BANNER: str = '''
OSIx - Open Source Intelligence eXplorer
Version: 0.0.1
By: Th3 0bservator
'''


class OSIx:
    """OSIx Main Module."""

    def __init__(self) -> None:
        """Module Initialization."""

        self.config: Optional[ConfigParser] = None
        self.available_modules: List[str] = []
        self.args: Dict = {
            'job_name': '',
            'facebook_get_friends': False,
            'facebook_target_account': '',
            'purge_temp_files': False,
            'instagram_target_account': ''
            }
        self.data: Dict = {
            'web_navigation': {
                'user_agent': ''
                },
            'facebook': {
                'primary_target': '',
                'current_target': '',
                'profiles': {}  # Uses SINGLE_FB_PROFILE_DATA_ITEM
                },
            'instagram': {
                'primary_target': '',
                'current_target': '',
                'profiles': {}  # Uses SINGLE_INSTAGRAM_PROFILE_DATA_ITEM
                }
            }

    def main(self) -> int:
        """Application Entrypoint."""

        self.setup_logging()

        logger.info(BANNER)

        if not self.check_python_version():
            return 1

        # Ensure Temp Data Structure
        # PENDENTE: Melhorar Isso
        TempFileHandler.ensure_dir_struct('state')
        TempFileHandler.ensure_dir_struct('facebook_friend_list')
        TempFileHandler.ensure_dir_struct('facebook_id_resolver')
        TempFileHandler.ensure_dir_struct('instagram_id_resolver')

        self.handle_args()
        self.load_settings()
        self.list_modules()
        self.print_settings()

        if not self.config:
            return -1

        # Set Initial Data
        self.data['facebook']['primary_target'] = self.args['facebook_target_account']
        self.data['facebook']['current_target'] = self.args['facebook_target_account']
        self.data['instagram']['primary_target'] = self.args['instagram_target_account']
        self.data['instagram']['current_target'] = self.args['instagram_target_account']
        self.data['web_navigation']['user_agent'] = self.choose_ua()

        # Initialize Internal Modules
        HttpNavigationManager.init(self.data)

        # Load Modules
        logger.info('[*] Executing Pipeline:')
        for pipeline_item in self.config['PIPELINE']['pipeline_sequence'].split('\n'):
            logger.info(f'\t[+] {pipeline_item}')
            pipeline_item_meta: List[str] = pipeline_item.split('.')

            osix_module: types.ModuleType = importlib.import_module(f'modules.{pipeline_item_meta[0]}')
            module_instance: BaseModule = getattr(osix_module, pipeline_item_meta[1])()
            module_instance.run(
                config=self.config,
                args=self.args,
                data=self.data
                )

        # Shutdown all Drivers
        ChromeDrivers.shutdown()

        return 0

    def check_python_version(self) -> bool:
        """Check if the Current Python Version is Supported."""

        # Check Python Requirements
        major = sys.version_info[0]
        minor = sys.version_info[1]

        python_version = str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])

        if major != 3 or major == 3 and minor < 6:
            logger.fatal('This application requires at least, Python 3.7.6')
            logger.fatal(f'Current Installed Version is: {python_version}')
            return False

        return True

    def setup_logging(self) -> None:
        """Setup Log Config."""

        logging.config.fileConfig('logging.conf')

    def handle_args(self) -> None:
        """
        Handle Input Arguments.

        :return:
        """

        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument(
            '--job_name',
            type=str,
            action='store',
            dest='job_name',
            help='Job Name. Used to Save/Restore State File.',
            default=uuid4().hex.upper()
            )

        parser.add_argument(
            '--facebook_target_account',
            type=str,
            action='store',
            dest='facebook_target_account',
            help='Facebook Target Account',
            default=''
            )
        parser.add_argument(
            '--facebook_load_friends',
            action='store_true',
            dest='facebook_load_friends',
            help='Allow to Download and Parse the Target Account Friend List.',
            default=False
            )

        parser.add_argument(
            '--instagram_target_account',
            type=str,
            action='store',
            dest='instagram_target_account',
            help='Instagram Target Account',
            default=''
            )

        parser.add_argument(
            '--purge_temp_files',
            action='store_true',
            dest='purge_temp_files',
            help='Force Delete All Temporary Files.',
            default=False
            )

        args = parser.parse_args()

        self.args['facebook_get_friends'] = args.facebook_load_friends
        self.args['facebook_target_account'] = args.facebook_target_account
        self.args['purge_temp_files'] = args.purge_temp_files
        self.args['instagram_target_account'] = args.instagram_target_account
        self.args['job_name'] = args.job_name

    def list_modules(self) -> None:
        """
        List All Available Modules.

        :return: None
        """

        # Check Modules
        logger.info('[*] Installed Modules:')
        for file in os.listdir('modules'):
            if file not in ('__init__.py', '__pycache__'):
                logger.info(f'\t{file}')

    def load_settings(self) -> None:
        """
        Load the config.ini file into Settings Object.

        :return: None
        """

        logger.info('[*] Loading Configurations:')
        self.config = ConfigParser()
        self.config.read('config.ini')

    def print_settings(self) -> None:
        """
        Print all Settings into Console.

        :return: None
        """

        logger.info('[*] Operation Settings: ')
        for key, value in self.args.items():
            logger.info(f'\t{key} = {value}')

    def choose_ua(self) -> str:
        """Choose a Random UA."""

        if self.config:
            ua_list: List[str] = self.config['WEB_NAVIGATION']['useragent_list'].split('\n')
            return ua_list[random.Random().randint(1, len(ua_list) - 1)]  # nosec

        raise Exception("System Configuration Not Initialized")


if __name__ == '__main__':
    exit(OSIx().main())

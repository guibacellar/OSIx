"""
OSIx - Open Source Intelligence eXplorer.

By: Th3 0bservator
"""

import argparse
import importlib
import os
import types
from uuid import uuid4

from configparser import ConfigParser
from typing import Dict, List, Optional

from core.base_module import BaseModule
from core.temp_file import TempFileHandler
from core.chrome_driver_manager import ChromeDrivers

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
            'purge_temp_files': False
            }
        self.data = {
            'facebook': {
                'primary_target': '',
                'current_target': '',
                'profiles': {}  # Uses SINGLE_FB_PROFILE_DATA_ITEM
                }
            }

    def main(self) -> int:
        """Application Entrypoint."""

        print(BANNER)

        # Ensure Temp Data Structure
        # PENDENTE: Melhorar Isso
        TempFileHandler.ensure_dir_struct('state')
        TempFileHandler.ensure_dir_struct('facebook_friend_list')
        TempFileHandler.ensure_dir_struct('facebook_id_resolver')

        # PENDENTE: Setup Logging
        self.handle_args()
        self.load_settings()
        self.list_modules()
        self.print_settings()

        # Set Initial Data
        self.data['facebook']['primary_target'] = self.args['facebook_target_account']
        self.data['facebook']['current_target'] = self.args['facebook_target_account']

        if not self.config:
            return -1

        # Load Modules
        print('[*] Executing Pipeline:')
        for pipeline_item in self.config['PIPELINE']['pipeline_sequence'].split('\n'):
            print(f'\t[+] {pipeline_item}')
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
        self.args['job_name'] = args.job_name

    def list_modules(self) -> None:
        """
        List All Available Modules.

        :return: None
        """

        # Check Modules
        print('[*] Installed Modules:')
        for file in os.listdir('modules'):
            if file not in ('__init__.py', '__pycache__'):
                print(f'\t{file}')

    def load_settings(self) -> None:
        """
        Load the config.ini file into Settings Object.

        :return: None
        """

        print('[*] Loading Configurations: ', end='')
        self.config = ConfigParser()
        self.config.read('config.ini')
        print('OK')

    def print_settings(self) -> None:
        """
        Print all Settings into Console.

        :return: None
        """

        print('[*] Operation Settings: ')
        for key, value in self.args.items():
            print(f'\t{key} = {value}')


if __name__ == '__main__':
    exit(OSIx().main())

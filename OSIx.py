"""
OSIx - Open Source Intelligence eXplorer.

By: Th3 0bservator
"""

import sys
import importlib
import os
import types
import logging
import logging.config

from configparser import ConfigParser
from typing import Dict, List, Optional

from core.base_module import BaseModule
from core.chrome_driver_manager import ChromeDrivers
from core.dir_manager import DirectoryManagerUtils

logger = logging.getLogger()

BANNER: str = '''
OSIx - Open Source Intelligence eXplorer
Version: 0.0.2
By: Th3 0bservator
'''


class OSIx:
    """OSIx Main Module."""

    def __init__(self) -> None:
        """Module Initialization."""

        self.config: Optional[ConfigParser] = None
        self.available_modules: List[str] = []

    def main(self) -> int:
        """Application Entrypoint."""

        self.__setup_logging()

        logger.info(BANNER)

        if not self.check_python_version():
            return 1

        DirectoryManagerUtils.ensure_dir_struct('data/')
        DirectoryManagerUtils.ensure_dir_struct('data/temp/')
        DirectoryManagerUtils.ensure_dir_struct('data/export/')
        self.__load_settings()
        self.__list_modules()

        if not self.config:
            return -1

        # Load Modules
        args: Dict = {}
        data: Dict = {}
        logger.info('[*] Executing Pipeline:')
        for pipeline_item in self.config['PIPELINE']['pipeline_sequence'].split('\n'):

            if pipeline_item == '':
                continue

            logger.info(f'\t[+] {pipeline_item}')
            pipeline_item_meta: List[str] = pipeline_item.split('.')

            osix_module: types.ModuleType = importlib.import_module(f'modules.{pipeline_item_meta[0]}')
            module_instance: BaseModule = getattr(osix_module, pipeline_item_meta[1])()
            module_instance.run(
                config=self.config,
                args=args,
                data=data
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

    def __setup_logging(self) -> None:
        """Setup Log Config."""

        logging.config.fileConfig('logging.conf')

    def __list_modules(self) -> None:
        """
        List All Available Modules.

        :return: None
        """

        # Check Modules
        logger.info('[*] Installed Modules:')
        for file in os.listdir('modules'):
            if file not in ('__init__.py', '__pycache__'):
                logger.info(f'\t{file}')

    def __load_settings(self) -> None:
        """
        Load the config.ini file into Settings Object.

        :return: None
        """

        logger.info('[*] Loading Configurations:')
        self.config = ConfigParser()
        self.config.read('config.ini')


if __name__ == '__main__':
    exit(OSIx().main())

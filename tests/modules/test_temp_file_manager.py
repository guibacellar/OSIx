"""Temporary Files Manager Tests."""

import logging
import logging.config

import unittest
from typing import Dict
from configparser import ConfigParser

from core.dir_manager import DirectoryManagerUtils
from modules.temp_file_manager import TempFileManager


class TempFileManagerTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.config.fileConfig('logging.conf')

        self.config = ConfigParser()
        self.config.read('config.ini')

        DirectoryManagerUtils.ensure_dir_struct('data/')
        DirectoryManagerUtils.ensure_dir_struct('data/temp/')
        DirectoryManagerUtils.ensure_dir_struct('data/temp/state')

    def test_general(self):

        target: TempFileManager = TempFileManager()
        args: Dict = {'purge_temp_files': False}
        data: Dict = {}

        target.run(
            config=self.config,
            args=args,
            data=data
        )

    def test_purge_all(self):
        target: TempFileManager = TempFileManager()
        args: Dict = {'purge_temp_files': True}
        data: Dict = {}

        target.run(
            config=self.config,
            args=args,
            data=data
        )



"""GitHub Username Data Digger Tests."""
import json
import os
import shutil
import sys
import unittest
from typing import Dict
from configparser import ConfigParser
from uuid import uuid4
import hashlib

import requests.exceptions

from OSIx.core.temp_file import TempFileHandler
from OSIx.modules.github_username_data_digger import GithubUsernameDataDigger
from OSIx.modules.temp_file_manager import TempFileManager
from OSIx.modules.username_handler import UsernameScanner
from unittest import mock


class GithubUsernameDataDiggerTest(unittest.TestCase):

    def setUp(self) -> None:

        self.config = ConfigParser()
        self.config.read('config.ini')

        # Purge Temp File
        TempFileManager().run(
            config=self.config,
            args={'purge_temp_files': True},
            data={}
        )

    def mocked_get(*args, **kwargs):
        target_file: str = f'assets/github_responses/{hashlib.md5(args[0].encode("utf-8")).hexdigest()}.json'

        with open(target_file, 'r', encoding='utf-8') as file:
            return file.read()

    @mock.patch('OSIx.core.http_manager.HttpNavigationManager.get', side_effect=mocked_get)
    def test_run_elephant_user(self, _mocked_download_text):

        target: GithubUsernameDataDigger = GithubUsernameDataDigger()
        args: Dict = {'username_print_result': True}
        data: Dict = {'username': {'target_username': 'elephant'}}

        # First Run
        target.run(
            config=self.config,
            args=args,
            data=data
        )

        # Validated Basic Data
        self.assertEqual('https://avatars.githubusercontent.com/u/176842?v=4', data['github']['profile_pic'])
        self.assertEqual('Jonathan Suchland', data['github']['fullname'])
        self.assertEqual('elephant', data['github']['nickname'])
        self.assertEqual('Seattle, WA', data['github']['location'])
        self.assertEqual('http://jonathansuchland.com/', data['github']['website'])
        self.assertEqual('176842', data['github']['account_id'])
        self.assertEqual(None, data['github']['bio'])

        # Validate Repositories
        self.assertEqual(11, len(data['github']['repos']))
        self.assertEqual(data['github']['repos'][2], {'name': 'elastic', 'description': 'Elasticsearch client for Go.', 'url': '/elephant/elastic', 'type': 'fork'})
        self.assertEqual(data['github']['repos'][7], {'name': 'jquery-ui', 'description': 'The official jQuery user interface library.', 'url': '/elephant/jquery-ui', 'type': 'fork'})
        self.assertEqual(data['github']['repos'][10], {'name': 'Catnap', 'description': 'Quickly create a RESTful web server from any PHP object.', 'url': '/elephant/Catnap', 'type': 'owner'})

        # Validate Followers
        self.assertEqual(13, len(data['github']['followers']))
        self.assertEqual(data['github']['followers'][0], {'name': '', 'username': 'parth-jani', 'url': '/parth-jani'})
        self.assertEqual(data['github']['followers'][4], {'name': 'Navori Digital signage software', 'username': 'navori', 'url': '/navori'})
        self.assertEqual(data['github']['followers'][9], {'name': 'Jimmy Odom', 'username': 'MnkyPwz', 'url': '/MnkyPwz'})

        # Validate Following
        self.assertEqual(6, len(data['github']['following']))
        self.assertEqual(data['github']['following'][1], {'name': 'Jay Aniceto', 'username': 'jayncoke', 'url': '/jayncoke'})
        self.assertEqual(data['github']['following'][3], {'name': 'Jonathan Soeder', 'username': 'datapimp', 'url': '/datapimp'})
        self.assertEqual(data['github']['following'][5], {'name': 'Harper Reed', 'username': 'harperreed', 'url': '/harperreed'})

    @mock.patch('OSIx.core.http_manager.HttpNavigationManager.get', side_effect=mocked_get)
    def test_run_john_user(self, _mocked_download_text):

        target: GithubUsernameDataDigger = GithubUsernameDataDigger()
        args: Dict = {'username_print_result': True}
        data: Dict = {'username': {'target_username': 'john'}}

        # First Run
        target.run(
            config=self.config,
            args=args,
            data=data
        )

        # Validated Basic Data
        self.assertEqual('https://avatars.githubusercontent.com/u/1668?v=4', data['github']['profile_pic'])
        self.assertEqual('John McGrath', data['github']['fullname'])
        self.assertEqual('john', data['github']['nickname'])
        self.assertEqual('San Francisco, CA', data['github']['location'])
        self.assertEqual('https://twitter.com/wordie', data['github']['website'])
        self.assertEqual('1668', data['github']['account_id'])
        self.assertEqual('I\'m on the sustainability team at AWS, and prior to that co-founded Entelo. Interested in renewable energy, journalism, startups, and democracy.', data['github']['bio'])

        # Validate Repositories
        self.assertEqual(30, len(data['github']['repos']))
        self.assertEqual(data['github']['repos'][0], {'name': 'geocoder', 'description': 'Complete Ruby geocoding solution.', 'url': '/john/geocoder', 'type': 'fork'})
        self.assertEqual(data['github']['repos'][5], {'name': 'daily-numbers', 'description': None, 'url': '/john/daily-numbers', 'type': 'owner'} )
        self.assertEqual(data['github']['repos'][27], {'name': 'wrinkle', 'description': 'Moves content through space and time.', 'url': '/john/wrinkle', 'type': 'owner'})

        # Validate Followers
        self.assertEqual(50, len(data['github']['followers']))
        self.assertEqual(data['github']['followers'][2], {'name': 'Gupakg', 'username': 'Gupakg', 'url': '/Gupakg'})
        self.assertEqual(data['github']['followers'][13], {'name': '', 'username': 'anupworks', 'url': '/anupworks'})
        self.assertEqual(data['github']['followers'][25], {'name': '', 'username': 'jlsjefferson', 'url': '/jlsjefferson'})

        # Validate Following
        self.assertEqual(48, len(data['github']['following']))
        self.assertEqual(data['github']['following'][0], {'name': '', 'username': 'conslacksf', 'url': '/conslacksf'})
        self.assertEqual(data['github']['following'][14], {'name': 'Linus Torvalds', 'username': 'torvalds', 'url': '/torvalds'})
        self.assertEqual(data['github']['following'][47], {'name': 'André Arko', 'username': 'indirect', 'url': '/indirect'})

    @mock.patch('OSIx.core.http_manager.HttpNavigationManager.get', side_effect=mocked_get)
    def test_run_notfounduser001_user(self, _mocked_download_text):

        target: GithubUsernameDataDigger = GithubUsernameDataDigger()
        args: Dict = {'username_print_result': True}
        data: Dict = {'username': {'target_username': 'notfounduser001'}}

        # First Run
        with self.assertLogs() as captured:
            target.run(
                config=self.config,
                args=args,
                data=data
            )

        self.assertEqual(len(captured.records), 1)
        self.assertEqual(f'\t\tUsername Not Found.', captured.records[0].msg)

        # Validated Basic Data
        self.assertFalse('github' in data)

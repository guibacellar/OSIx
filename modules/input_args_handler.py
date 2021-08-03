"""Input Arguments Handler."""

from configparser import ConfigParser
from typing import Dict
from uuid import uuid4

import argparse
import logging

from core.base_module import BaseModule

logger = logging.getLogger()


class InputArgsHandler(BaseModule):
    """Module That Handle the Input Arguments."""

    __ARGS: Dict = {
        'job_name': {
            'param': '--job_name',
            'type': str,
            'action': 'store',
            'help': 'Job Name. Used to Save/Restore State File.',
            'default': uuid4().hex.upper()
            },
        'purge_temp_files': {
            'param': '--purge_temp_files',
            'type': str,
            'action': 'store_true',
            'help': 'Force Delete All Temporary Files',
            'default': False
            },
        'btc_wallet': {
            'param': '--btc_wallet',
            'type': str,
            'action': 'store',
            'help': 'BitCoin Wallet Address',
            'default': ''
            }
        }

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        parser = argparse.ArgumentParser(description='Process some integers.')

        # Add Parameters to Arg Parser
        for arg in InputArgsHandler.__ARGS:
            spec: Dict = InputArgsHandler.__ARGS[arg]

            parser.add_argument(
                spec['param'], action=spec['action'], dest=arg,
                help=spec['help'], default=spec['default']
                )

        # Parse Args
        input_args = parser.parse_args()

        # Add to Result Args
        for arg in InputArgsHandler.__ARGS:
            args.update(
                {arg: getattr(input_args, arg)}
                )

        # Print Settings
        for key, value in args.items():
            logger.info(f'\t\t{key} = {value}')

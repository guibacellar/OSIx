"""Bitcoint Wallet Handler."""

from configparser import ConfigParser
from typing import Dict

import logging
import requests

from core.base_module import BaseModule
from core.temp_file import TempFileHandler

logger = logging.getLogger()


class BitcoinWalletInfoDownloader(BaseModule):
    """Temporary File Manager."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Get Target
        if 'bitcoin' not in data:
            data.update(
                {
                    'bitcoin': {
                        'target_wallet': args['btc_wallet']
                        }
                    }
                )

        target_wallet = data['bitcoin']['target_wallet']
        target_file: str = f'bitcoin_wallet/{target_wallet}.json'

        # Module Activation Rule
        if target_wallet is None or target_wallet == '':
            logger.info('\t\tTarget BTC Wallet Empty.')
            return

        # Check if Cached File Exists
        if TempFileHandler.file_exist(target_file):
            logger.info(f'\t\tTarget File "{target_file}" Alread Exists. Skipping...')
            return

        logger.info('\t\tDownloading BitCoin Wallet Info')

        # Download Wallet Data
        response: requests.Response = requests.get(
            url=config['MODULE_BitcoinWalletInfoDownloader']['wallet_info_api'].replace('{0}', target_wallet)
            )

        # Check Result
        if response.status_code == 200:
            # Save temp File
            if TempFileHandler.write_file_text(target_file, response.content.decode('utf-8')):
                return

        else:
            logger.error(response.status_code)

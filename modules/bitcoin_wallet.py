"""Bitcoint Wallet Handler."""

from configparser import ConfigParser
from typing import Dict

import json
import logging
import time

import requests

from core.base_module import BaseModule
from core.temp_file import TempFileHandler

logger = logging.getLogger()


class BitcoinWalletInfoDownloader(BaseModule):
    """Download BitCoin Wallet Info."""

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

        target_wallet: str = data['bitcoin']['target_wallet']
        target_file: str = f'bitcoin_wallet/{target_wallet}_wallet.json'

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
            TempFileHandler.write_file_text(target_file, response.content.decode('utf-8'))

        else:
            logger.error(response.status_code)


class BitcoinWalletTransactionsDownloader(BaseModule):
    """Download the Bitcoint Wallet Transactions."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        target_wallet: str = data['bitcoin']['target_wallet']
        target_file: str = f'bitcoin_wallet/{target_wallet}_transactions.json'

        # Module Activation Rule
        if not args['btc_get_transactions']:
            return

        if target_wallet is None or target_wallet == '':
            logger.info('\t\tTarget BTC Wallet Empty.')
            return

        # Check if Cached File Exists
        if TempFileHandler.file_exist(target_file):
            logger.info(f'\t\tTarget File "{target_file}" Alread Exists. Skipping...')
            return

        logger.info('\t\tDownloading BitCoin Wallet Transactions')

        h_data: Dict = {
            'transactions': []
            }

        offset: int = 0
        while offset >= 0:

            # Download Wallet Data
            response: requests.Response = requests.get(
                url=config['MODULE_BitcoinWalletInfoDownloader']['wallet_transactions_api']
                .replace('{0}', target_wallet)
                .replace('{1}', str(offset))
                )

            # Check Result
            if response.status_code == 200:
                downloaded_data: Dict = json.loads(response.content.decode('utf-8'))

                # Update Page Indicator
                if len(downloaded_data['txs']) == 1000:
                    offset += 1000
                    time.sleep(10)

                else:
                    offset = -1

                h_data['transactions'] += downloaded_data['txs']

            else:
                logger.error(response.status_code)
                return

        # Save temp File
        TempFileHandler.write_file_text(target_file, json.dumps(h_data))

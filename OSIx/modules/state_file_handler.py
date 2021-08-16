"""State File Handler."""

from configparser import ConfigParser
from typing import Dict

import json
import logging

from OSIx.core.base_module import BaseModule
from OSIx.core.state_file import StateFileHandler

logger = logging.getLogger()


class LoadStateFileHandler(BaseModule):
    """Module that Loads Previous Created State File."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        state_file_name: str = config['MODULE_LoadStateFileHandler']['file_name'].replace("{0}", args['job_name'])

        if StateFileHandler.file_exist(state_file_name):
            data.update(
                json.loads(StateFileHandler.read_file_text(state_file_name))
                )
            logger.debug("\t\tState File Loaded.")


class SaveStateFileHandler(BaseModule):
    """Module that Save a New State File."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        state_file_name: str = config['MODULE_SaveStateFileHandler']['file_name'].replace("{0}", args['job_name'])

        StateFileHandler.write_file_text(
            state_file_name,
            json.dumps(data)
            )

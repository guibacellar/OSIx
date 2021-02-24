"""State File Handler."""

from configparser import ConfigParser
from typing import Dict

import json
from core.base_module import BaseModule
from core.temp_file import TempFileHandler


class LoadStateFileHandler(BaseModule):
    """Module that Loads Previous Created State File."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        state_file_name: str = f"state/{args['job_name']}.json"

        if TempFileHandler.file_exist(state_file_name):
            data.update(
                json.loads(''.join(TempFileHandler.read_file_text(state_file_name)))
                )
            print("\t\tState File Loaded.")


class SaveStateFileHandler(BaseModule):
    """Module that Save a New State File."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        state_file_name: str = f"state/{args['job_name']}.json"

        TempFileHandler.write_file_text(
            state_file_name,
            json.dumps(data)
            )

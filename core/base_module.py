"""OSIx Base Module."""

import abc
from configparser import ConfigParser
from typing import Dict


class BaseModule:
    """Base Module Declaration."""

    @abc.abstractmethod
    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """
        Base Run Description.

        :return: None
        """

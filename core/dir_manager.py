"""Directory Manager."""

import os
from typing import List


class DirectoryManagerUtils:
    """Directory Manager."""

    @staticmethod
    def ensure_dir_struct(path: str) -> None:
        """
        Ensur That Directory Exists.

        :param path:
        :return:
        """
        if not os.path.exists(path):
            os.mkdir(path)

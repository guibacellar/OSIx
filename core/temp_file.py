"""Temp File Handle."""

import os
from typing import List


class TempFileHandler:
    """Temporary File Hander."""

    @staticmethod
    def ensure_dir_struct(path: str) -> bool:
        if not os.path.exists(f'data/temp/{path}'):
            os.mkdir(f'data/temp/{path}')

    @staticmethod
    def file_exist(path: str) -> bool:
        """
        Returns if a File Exists.

        :param path: File Path
        :return:
        """

        return os.path.exists(f'data/temp/{path}')

    @staticmethod
    def read_file_text(path: str) -> List[str]:
        """
        Read All File Content.
        :param path: File Path
        :return: File Content
        """

        with open(f'data/temp/{path}', 'r', encoding='utf-8') as fs:
            return fs.readlines()

    @staticmethod
    def write_file_text(path: str, content:str) -> None:
        """
        Write Text Content into File.
        :param path: File Path
        :return: None
        """

        with open(f'data/temp/{path}', 'w', encoding='utf-8') as fs:
            fs.write(content)
            fs.flush()
            fs.close()

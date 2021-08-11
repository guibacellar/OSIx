"""Temp File Handle."""

import os
from typing import List


class TempFileHandler:
    """Temporary File Hander."""

    ROOT_PATH: str = os.path.join(os.getcwd())

    @staticmethod
    def ensure_dir_struct(path: str) -> None:
        """
        Ensur That Directory Exists.

        :param path:
        :return:
        """

        if not os.path.exists(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, 'data/temp/'))):
            os.mkdir(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, 'data/temp/')))

        if not os.path.exists(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, f'data/temp/{path}'))):
            os.mkdir(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, f'data/temp/{path}')))

    @staticmethod
    def file_exist(path: str) -> bool:
        """
        Return if a File Exists.

        :param path: File Path
        :return:
        """

        return os.path.exists(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, f'data/temp/{path}')))

    @staticmethod
    def read_file_text(path: str) -> List[str]:
        """
        Read All File Content.

        :param path: File Path
        :return: File Content
        """

        with open(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, f'data/temp/{path}')), 'r', encoding='utf-8') as file:
            return file.readlines()

    @staticmethod
    def write_file_text(path: str, content: str) -> None:
        """
        Write Text Content into File.

        :param path: File Path
        :return: None
        """

        with open(os.path.abspath(os.path.join(TempFileHandler.ROOT_PATH, f'data/temp/{path}')), 'w', encoding='utf-8') as file:
            file.write(content)
            file.flush()
            file.close()

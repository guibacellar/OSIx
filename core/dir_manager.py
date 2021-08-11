"""Directory Manager."""

import os


class DirectoryManagerUtils:
    """Directory Manager."""

    @staticmethod
    def ensure_dir_struct(path: str) -> None:
        """
        Ensur That Directory Exists.

        :param path:
        :return:
        """

        target_path: str = os.path.abspath(os.path.join(os.getcwd(), path))

        if not os.path.exists(target_path):
            os.mkdir(target_path)

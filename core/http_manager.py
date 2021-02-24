"""HTTP Navigation Manager."""

from typing import Dict, Optional

import requests


class HttpNavigationManager:
    """Http Navigation Manager."""

    __INSTANCE: Optional[requests.Session] = None

    @staticmethod
    def init(data: Dict) -> None:
        """Initialize Navigation Manager."""

        HttpNavigationManager.__INSTANCE = requests.Session()
        HttpNavigationManager.__INSTANCE.headers.update(
            {'User-Agent': data['web_navigation']['user_agent']}
            )

    @staticmethod
    def get(uri: str) -> str:
        """
        Realize a GET on Remote URI.

        :param uri: Target URI
        :return:
        """

        if not HttpNavigationManager.__INSTANCE:
            raise Exception("HttpNavigationManager not Initialized.")

        return HttpNavigationManager.__INSTANCE.get(uri).text

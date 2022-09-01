#!/usr/bin/env python3

import json


class Config:
    """
        Configuration json load
    """

    def __init__(self, path: str = "config/config.json") -> None:
        self.path: str = path

    def load(self) -> dict:
        """
            Load json configuration from file
        """
        with open(self.path, 'r') as f:
            data: dict = json.load(f)
        return data

    def getTheme(self) -> str:
        """
            Get the theme path
        """
        return self.load().get('assets_dir', 'assets/') + 'themes/' + self.load().get('theme', 'dark') + '.png'

#!/usr/bin/env python3

import json
from typing import Iterable

from .Logger import logger


class Config:
    """
        Configuration json load
    """

    DEFAULT_CONFIG: dict = {
        'screen_brightness': 'high',
        'assets_dir': 'assets/',
        'theme': 'dark',
        'display_width': 320,
        'display_height': 480,
        'hot_reload_config': False,
        'hot_reload_interval': 60,
        'dynamic_text_informations': [],
        'static_text_informations': [],
        'static_image': [],
        'debug': {
            'show': False,
            'x': 245,
            'y': 440,
            'font_color': (98, 114, 164),
            'font_size': 12,
            'transparent': True
        }
    }

    def __init__(self, path: str = 'config/config.json') -> None:
        self.path: str = path
        self.config: dict = {}

    def load(self) -> dict:
        """
            Load json configuration from file
        """
        with open(self.path, 'r') as f:
            self.config: dict = json.load(f)
        logger.info('Configuration loaded')
        return self.config

    def getTheme(self) -> str:
        """
            Get the theme path
        """
        logger.info('Get theme')
        return self.config.get('assets_dir', 'assets/') + 'themes/' + self.config.get('theme', 'dark') + '.png'

    def getKey(self, key: str, node: Iterable | None = None):
        """
            Get configuration value from key
        """
        try:
            if node:
                return next(self.__findKey(node, key))
            return next(self.__findKey(self.config, key))
        except StopIteration:
            return None

    def __findKey(self, node, kv: str):
        if isinstance(node, list):
            for i in node:
                for x in self.__findKey(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in self.__findKey(j, kv):
                    yield x
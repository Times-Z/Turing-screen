#!/usr/bin/env python3

import json


class Config:
    """
        Configuration json load
    """

    def __init__(self, path: str = "config/config.json") -> None:
        self.path = path

    def load(self) -> dict:
        """
            Load json configuration from file
        """
        with open(self.path, 'r') as f:
            data = json.load(f)
        return data

#!/usr/bin/env python3

import json


class Config:

    def __init__(self, path: str = "config/config.json") -> None:
        self.path = path

    def load(self) -> dict:
        with open(self.path, 'r') as f:
            data = json.load(f)
        return data
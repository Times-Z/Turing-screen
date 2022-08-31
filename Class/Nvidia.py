#!/usr/bin/env python3

import GPUtil


class Nvidia:

    @staticmethod
    def isAvailable() -> bool:
        """
            Check if GPU is available
        """
        return len(GPUtil.getGPUs()) > 0

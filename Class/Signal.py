#!/usr/bin/env python3

import signal
import os


class Signal:
    """
        Use Signal to handle quit stop program
    """

    def makeHandler(self, handler):
        """
            Make handler to handle sig term/quit
        """
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        if os.name == 'posix':
            signal.signal(signal.SIGQUIT, handler)

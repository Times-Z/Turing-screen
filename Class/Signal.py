#!/usr/bin/env python3

import signal
import os


class Signal:

    def makeHandler(self, handler):
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        if os.name == 'posix':
            signal.signal(signal.SIGQUIT, handler)

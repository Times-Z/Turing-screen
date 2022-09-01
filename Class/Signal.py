#!/usr/bin/env python3

import os
import signal
import sys
from time import sleep
from tracemalloc import Frame
from typing import Callable

from Class.Com import Com


class Signal:
    """
        Use Signal to handle quit stop program
    """

    def __init__(self, com: Com) -> None:
        self.com: Com = com

    def makeHandler(self, handler: Callable):
        """
            Make handler to handle sig term/quit
        """
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        if os.name == 'posix':
            signal.signal(signal.SIGQUIT, handler)

    def sigHandler(self, signum: int, frame: Frame):
        """
            Used to stop application with signal after send a full frame to device
        """
        if not self.com.serial.isOpen():
            self.com.serial.open()
        sleep(0.1)
        self.com.Clear()
        self.com.ScreenOff()
        try:
            sys.exit(0)
        except:
            os._exit(0)

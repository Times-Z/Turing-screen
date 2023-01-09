#!/usr/bin/env python3

import math

import pyamdgpuinfo

from .Logger import logger


class Radeon:

    def __init__(self, gpu_id: int = 1) -> None:
        self.gpu = pyamdgpuinfo.get_gpu(pyamdgpuinfo.detect_gpus() - gpu_id)

    @staticmethod
    def isAvailable() -> bool:
        """
            Check if GPU is available
        """
        return pyamdgpuinfo.detect_gpus() > 0

    def gpuLoad(self) -> float:
        """
            Get GPU load in percent
        """
        try:
            return (self.gpu.query_load()) * 100
        except:
            logger.warn("gpuLoad isn't available on this device")
            return math.nan

    def gpuPower(self):
        """
            Get GPU power in watt
        """
        try:
            return self.gpu.query_power()
        except:
            logger.warn("gpuPower isn't available on this device")
            return math.nan

    def gpuTemp(self) -> float:
        """
            Get GPU temperature in °C
        """
        try:
            return self.gpu.query_temperature()
        except:
            logger.warn("gpuTemp isn't available on this device")
            return math.nan

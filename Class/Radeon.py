#!/usr/bin/env python3

import pyamdgpuinfo


class Radeon:

    def __init__(self, gpu_id: int = 1) -> None:

        self.gpu = pyamdgpuinfo.get_gpu(pyamdgpuinfo.detect_gpus() - gpu_id)

    @staticmethod
    def isAvailable() -> bool:
        """
            Check if GPU is available
        """
        return pyamdgpuinfo.detect_gpus() > 0

    def gpuLoad(self):
        """
            Get GPU load in percent
        """
        return (self.gpu.query_load()) * 100

    def gpuPower(self):
        """
            Get GPU power in watt
        """
        return self.gpu.query_power()

    def gpuTemp(self):
        """
            Get GPU temperature in °C
        """
        return self.gpu.query_temperature()

#!/usr/bin/env python3

import os

import psutil
from psutil._common import bytes2human

from .Logger import logger
from .Nvidia import Nvidia
from .Radeon import Radeon


class Hardware:
    """
        Get hardware informations

        Auto detect CPU and GPU brand
    """

    CPU_FREQ_ATTR = ['current', 'min', 'max']
    RAM_INFO_ATTR = ['total', 'available', 'used', 'free', 'percent']
    SWAP_INFO_ATTR = ['total', 'used', 'free', 'percent', 'sin', 'sout']
    DISK_INFO_ATTR = ['total', 'used', 'free', 'percent']
    GPU_METHOD = ['gpuLoad', 'gpuPower', 'gpuTemp']

    def __init__(self) -> None:
        self.cpu_brand: str = self.__getCpuBrand()
        self.gpu_brand: str = self.__getGpuBrand()
        if self.gpu_brand == 'nvidia':
            self.gpu: Nvidia = Nvidia()
        elif self.gpu_brand == 'amd':
            self.gpu: Radeon = Radeon()
        else:
            self.gpu: None = None

    @staticmethod
    def getCurrentProgramMemoryUsage() -> str:
        process = psutil.Process(os.getpid())
        return bytes2human(process.memory_info().rss)

    def __getCpuBrand(self) -> str:
        """
            Get CPU brand based on sensor temparature
        """
        if 'coretemp' in psutil.sensors_temperatures():
            logger.info('intel cpu detected')
            return 'coretemp'
        elif 'k10temp' in psutil.sensors_temperatures():
            logger.info('amd cpu detected')
            return 'k10temp'
        else:
            logger.info('unknow cpu detected')
            return 'unknow'

    def __getGpuBrand(self) -> str:
        """
            Get GPU brand name
        """
        if Nvidia.isAvailable():
            logger.info('nvidia gpu detected')
            return 'nvidia'
        elif Radeon.isAvailable():
            logger.info('amd gpu detected')
            return 'amd'
        else:
            logger.info('unknow gpu detected')
            return 'unknow'

    def __formatString(self, value: float | int, rounded: bool = False, endString: str = '') -> str:
        """
            Format float or int to string
        """
        if rounded:
            return f'{round(value, 1)} {endString}'
        return f'{value} {endString}'

    def __ramGetInfos(self, attribute: str) -> int:
        """
            Wrapper for RAM infos
        """
        if attribute not in self.RAM_INFO_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.RAM_INFO_ATTR))
        return getattr(psutil.virtual_memory(), attribute)

    def __cpuGetFreqs(self, attribute: str) -> int:
        """
            Wrapper for CPU freqs
        """
        if attribute not in self.CPU_FREQ_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.CPU_FREQ_ATTR))
        return getattr(psutil.cpu_freq(), attribute)

    def __swapGetInfos(self, attribute: str) -> int:
        """
            Wrapper for SWAP infos
        """
        if attribute not in self.SWAP_INFO_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.SWAP_INFO_ATTR))
        return getattr(psutil.swap_memory(), attribute)

    def __gpuGetInfos(self, attribute: str) -> int:
        """
            Wrapper for GPUs class
        """
        if attribute not in self.GPU_METHOD:
            raise ValueError('Attribute can only be one of ' +
                             str(self.GPU_METHOD))
        match self.gpu_brand:
            case 'nvidia':
                return 'nvidia gpus are not currently supported'
            case 'amd':
                return getattr(Radeon, attribute)(self.gpu)
            case 'intel':
                return 'intel gpus are not currently supported'
            case default:
                return 'unknow gpus are not currently supported'

    def __diskGetUsage(self, path: str, attribute: str) -> int:
        if attribute not in self.DISK_INFO_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.DISK_INFO_ATTR))
        return getattr(psutil.disk_usage(path), attribute)

    def cpuGetCount(self, logical: bool = True) -> str:
        """
            Get CPU core count
        """
        return self.__formatString(psutil.cpu_count(logical))

    def cpuGetCurrentTemp(self, junction: bool = False) -> str:
        """
            Get CPU die temperature
        """
        is_junction_allowed: bool = False
        temps: list = psutil.sensors_temperatures()[self.cpu_brand]
        if len(temps) > 1:
            is_junction_allowed = True
        return self.__formatString(temps[1 if not junction and is_junction_allowed else 0].current, True, '°C')

    def cpuGetCurrentLoad(self) -> str:
        """
            Get CPU current load
        """
        return self.__formatString(psutil.cpu_percent(), endString='%')

    def cpuGetAverageLoad(self) -> str:
        """
            Get CPU load average
        """
        return self.__formatString([round(x / psutil.cpu_count() * 100, 1) for x in psutil.getloadavg()])

    def cpuGetCurrentFreq(self, Ghz: bool = True) -> str:
        """
            Get CPU current frequency
        """
        if Ghz:
            return self.__formatString(self.__cpuGetFreqs('current') / 1000, True, 'Ghz')
        return self.__formatString(self.__cpuGetFreqs('current'), True, 'Mhz')

    def cpuGetMaxFreq(self, Ghz: bool = True) -> str:
        """
            Get CPU max frequency
        """
        if Ghz:
            return self.__formatString(self.__cpuGetFreqs('max') / 1000, True, 'Ghz')
        return self.__formatString(self.__cpuGetFreqs('max'), True, 'Mhz')

    def cpuGetMinFreq(self, Ghz: bool = True) -> str:
        """
            Get CPU min frequency
        """
        if Ghz:
            return self.__formatString(self.__cpuGetFreqs('min') / 1000, True, 'Ghz')
        return self.__formatString(self.__cpuGetFreqs('min'), True, 'Mhz')

    def ramGetPercent(self) -> str:
        """
            Get RAM total value
        """
        return self.__formatString(self.__ramGetInfos('percent'), endString='%')

    def ramGetTotal(self) -> str:
        """
            Get RAM total value
        """
        return bytes2human(self.__ramGetInfos('total'))

    def ramGetAvailable(self) -> str:
        """
            Get RAM available value
        """
        return bytes2human(self.__ramGetInfos('available'))

    def ramGetUsed(self) -> str:
        """
            Get RAM used value
        """
        return bytes2human(self.__ramGetInfos('used'))

    def ramGetFree(self) -> str:
        """
            Get RAM free value
        """
        return bytes2human(self.__ramGetInfos('free'))

    def swapGetTotal(self) -> str:
        """
            Get SWAP total value
        """
        return self.__formatString(self.__swapGetInfos('total'), endString='%')

    def swapGetUsed(self) -> str:
        """
            Get SWAP used value
        """
        return bytes2human(self.__swapGetInfos('used'))

    def swapGetFree(self) -> str:
        """
            Get SWAP free value
        """
        return bytes2human(self.__swapGetInfos('free'))

    def swapGetPercent(self) -> str:
        """
            Get SWAP percent value
        """
        return bytes2human(self.__swapGetInfos('percent'))

    def swapGetSin(self) -> str:
        """
            Get SWAP sin value
        """
        return bytes2human(self.__swapGetInfos('sin'))

    def swapGetSout(self) -> str:
        """
            Get SWAP sout value
        """
        return bytes2human(self.__swapGetInfos('sout'))

    def gpuGetLoad(self) -> str:
        """
            Get the GPU load percent
        """
        return self.__formatString(self.__gpuGetInfos('gpuLoad'), True, '%')

    def gpuGetPower(self) -> str:
        """
            Get the GPU power in watt
        """
        return self.__formatString(self.__gpuGetInfos('gpuPower'), True, 'Watts')

    def gpuGetTemp(self) -> str:
        """
            Get the GPU power in watt
        """
        return self.__formatString(self.__gpuGetInfos('gpuTemp'), endString='°C')

    def diskGetTotal(self, path: str) -> str:
        """
            Get the disk total size
        """
        return bytes2human(self.__diskGetUsage(path, 'total'))

    def diskGetUsed(self, path: str) -> str:
        """
            Get the disk used space
        """
        return bytes2human(self.__diskGetUsage(path, 'used'))

    def diskGetFree(self, path: str) -> str:
        """
            Get the disk free space
        """
        return bytes2human(self.__diskGetUsage(path, 'free'))

    def diskGetPercent(self, path: str) -> str:
        """
            Get the disk percent
        """
        return self.__formatString(self.__diskGetUsage(path, 'percent'), endString='%')

    def userGetName(self) -> str:
        """
            Get the current user name
        """
        return psutil.users()[0].name

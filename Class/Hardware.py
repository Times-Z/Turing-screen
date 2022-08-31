#!/usr/bin/env python3

import psutil
from psutil._common import bytes2human

from Class.Nvidia import Nvidia
from Class.Radeon import Radeon


class Hardware:
    """
        Get hardware informations

        Auto detect CPU and GPU brand
    """

    CPU_FREQ_ATTR = ['current', 'min', 'max']
    RAM_INFO_ATTR = ['total', 'available', 'used', 'free', 'percent']
    SWAP_INFO_ATTR = ['total', 'used', 'free', 'percent', 'sin', 'sout']
    GPU_METHOD = ['gpuLoad', 'gpuPower', 'gpuTemp']

    def __init__(self) -> None:
        self.cpu_brand = self.__getCpuBrand()
        self.gpu_brand = self.__getGpuBrand()
        if self.gpu_brand == 'nvidia':
            self.gpu = Nvidia()
        elif self.gpu_brand == 'amd':
            self.gpu = Radeon()
        else:
            self.gpu = None

    def __getCpuBrand(self):
        """
            Get CPU brand based on sensor temparature
        """
        if 'coretemp' in psutil.sensors_temperatures():
            return 'coretemp'
        elif 'k10temp' in psutil.sensors_temperatures():
            return 'k10temp'
        else:
            return 'unknow'

    def __getGpuBrand(self) -> str:
        """
            Get GPU brand name
        """
        if Nvidia.isAvailable():
            return 'nvidia'
        elif Radeon.isAvailable():
            return 'amd'
        else:
            return 'unknow'

    def __formatString(self, value: float | int, rounded: bool = False, endString: str = "") -> str:
        """
            Format float or int to string
        """
        if rounded:
            return f'{round(value, 1)}{endString}'
        return f'{value}{endString}'

    def __ramGetInfos(self, attribute: str) -> str:
        """
            Wrapper for RAM infos
        """
        if attribute not in self.RAM_INFO_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.RAM_INFO_ATTR))
        data = getattr(psutil.virtual_memory(), attribute)
        if attribute == 'percent':
            return self.__formatString(data, endString='%')
        return bytes2human(data)

    def __cpuGetFreqs(self, attribute: str, Ghz: bool = True) -> str:
        """
            Wrapper for CPU freqs
        """
        if attribute not in self.CPU_FREQ_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.CPU_FREQ_ATTR))
        if Ghz:
            return self.__formatString(getattr(psutil.cpu_freq(), attribute) / 1000, True, "Ghz")
        return self.__formatString(getattr(psutil.cpu_freq(), attribute), True, "Mhz")

    def __swapGetInfos(self, attribute: str) -> str:
        """
            Wrapper for SWAP infos
        """
        if attribute not in self.SWAP_INFO_ATTR:
            raise ValueError('Attribute can only be one of ' +
                             str(self.SWAP_INFO_ATTR))
        data = getattr(psutil.swap_memory(), attribute)
        if attribute == 'percent':
            return self.__formatString(data, endString='%')
        return bytes2human(data)

    def __gpuGetInfos(self, attribute: str) -> str:
        """
            Wrapper for GPUs class
        """
        if attribute not in self.GPU_METHOD:
            raise ValueError('Attribute can only be one of ' +
                             str(self.GPU_METHOD))
        match self.gpu_brand:
            case 'nvidia':
                return 'nvidia'
            case 'amd':
                return getattr(Radeon, attribute)(self.gpu)
            case 'intel':
                return 'intel'
            case default:
                return 'default'

    def cpuGetCount(self, logical: bool = True) -> str:
        """
            Get CPU core count
        """
        return self.__formatString(psutil.cpu_count(logical))

    def cpuGetCurrentTemp(self, junction: bool = False) -> str:
        """
            Get CPU die temperature
        """
        return self.__formatString(psutil.sensors_temperatures()[self.cpu_brand][0 if not junction else 1].current, True, '°C')

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
        return self.__cpuGetFreqs('current', Ghz)

    def cpuGetMaxFreq(self, Ghz: bool = True) -> str:
        """
            Get CPU max frequency
        """
        return self.__cpuGetFreqs('max', Ghz)

    def cpuGetMinFreq(self, Ghz: bool = True) -> str:
        """
            Get CPU min frequency
        """
        return self.__cpuGetFreqs('min', Ghz)

    def ramGetPercent(self) -> str:
        """
            Get RAM total value
        """
        return self.__ramGetInfos('percent')

    def ramGetTotal(self) -> str:
        """
            Get RAM total value
        """
        return self.__ramGetInfos('total')

    def ramGetAvailable(self) -> str:
        """
            Get RAM available value
        """
        return self.__ramGetInfos('available')

    def ramGetUsed(self) -> str:
        """
            Get RAM used value
        """
        return self.__ramGetInfos('used')

    def ramGetFree(self) -> str:
        """
            Get RAM free value
        """
        return self.__ramGetInfos('free')

    def swapGetTotal(self) -> str:
        """
            Get SWAP total value
        """
        return self.__swapGetInfos('total')

    def swapGetUsed(self) -> str:
        """
            Get SWAP used value
        """
        return self.__swapGetInfos('used')

    def swapGetFree(self) -> str:
        """
            Get SWAP free value
        """
        return self.__swapGetInfos('free')

    def swapGetPercent(self) -> str:
        """
            Get SWAP percent value
        """
        return self.__swapGetInfos('percent')

    def swapGetSin(self) -> str:
        """
            Get SWAP sin value
        """
        return self.__swapGetInfos('sin')

    def swapGetSout(self) -> str:
        """
            Get SWAP sout value
        """
        return self.__swapGetInfos('sout')

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


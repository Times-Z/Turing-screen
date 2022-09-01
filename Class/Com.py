#!/usr/bin/env python3

import serial
import serial.tools.list_ports


class Com:
    """
        Com port communication
    """

    RESET: int = 101
    CLEAR: int = 102
    SCREEN_OFF: int = 108
    SCREEN_ON: int = 109
    SET_BRIGHTNESS: int = 110
    DISPLAY_BITMAP: int = 197
    BRIGHTNESS_LEVEL: dict[str, int] = {
        'high': 0,
        'medium': 128,
        'low': 255
    }
    COM_PORT: list[str] = [
        '/dev/ttyACM0'
        'COM3'
    ]

    def __init__(self, config: dict):
        if 'com_port' in config:
            port: str = config.get('com_port', '/dev/ttyACM0')
        else:
            port: str = self.auto_detect_com_port()
        self.serial: serial.Serial = serial.Serial(
            port, 115200, timeout=1, rtscts=1)
        self.ScreenOn()
        self.SetBrightness(self.BRIGHTNESS_LEVEL.get(
            config.get('screen_brightness', 0), 0))

    def auto_detect_com_port(self) -> str | None:
        """
            Try to auto discover port com
        """
        ports: list = serial.tools.list_ports.grep('.', include_links=True)
        for port in ports:
            if port.device in self.COM_PORT:
                return port.device
            return None

    def SendReg(self, cmd: int, x: int, y: int, ex: int, ey: int) -> None:
        """
            Send command to hardware
        """
        byteBuffer: bytearray = bytearray(6)
        byteBuffer[0] = (x >> 2)
        byteBuffer[1] = (((x & 3) << 6) + (y >> 4))
        byteBuffer[2] = (((y & 15) << 4) + (ex >> 6))
        byteBuffer[3] = (((ex & 63) << 2) + (ey >> 8))
        byteBuffer[4] = (ey & 255)
        byteBuffer[5] = cmd
        self.serial.write(bytes(byteBuffer))

    def Reset(self) -> None:
        """
            Reset screen
        """
        self.SendReg(self.RESET, 0, 0, 0, 0)

    def Clear(self) -> None:
        """
            Clear screen
        """
        self.SendReg(self.CLEAR, 0, 0, 0, 0)

    def ScreenOff(self) -> None:
        """
            Set screen to OFF
        """
        self.SendReg(self.SCREEN_OFF, 0, 0, 0, 0)

    def ScreenOn(self) -> None:
        """
            Set screen to ON
        """
        self.SendReg(self.SCREEN_ON, 0, 0, 0, 0)

    def SetBrightness(self, level: int) -> None:
        """
            Set brightness level from 0 to 255
        """
        assert 255 >= level >= 0, 'Brightness level must be [0-255]'
        self.SendReg(self.SET_BRIGHTNESS, level, 0, 0, 0)

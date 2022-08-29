#!/usr/bin/env python3
import os
import signal
import psutil
from Class import Com, Display
import pyamdgpuinfo

import serial

COM_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
ASSET_DIR = "assets/"
THEME = "template.png"

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 480

stop = False


def makeHandler():
    signal.signal(signal.SIGINT, sigHandler)
    signal.signal(signal.SIGTERM, sigHandler)
    if os.name == 'posix':
        signal.signal(signal.SIGQUIT, sigHandler)


def sigHandler(signum, frame):
    global stop
    stop = True


if __name__ == "__main__":

    makeHandler()

    serial_com = serial.Serial(COM_PORT, BAUDRATE, timeout=1, rtscts=1)
    com = Com(serial_com)
    display = Display(com, serial_com, DISPLAY_WIDTH, DISPLAY_HEIGHT)

    # Display background image
    display.DisplayBitmap(ASSET_DIR + "themes/" + THEME)

    while not stop:
        display.DisplayText(str(psutil.cpu_percent()) + " %", 80,
                            30, background_image=ASSET_DIR + "themes/" + THEME, sleep_time=2)

        display.DisplayText(str(pyamdgpuinfo.get_gpu(0).query_load()) + " %", 80,
                            50, background_image=ASSET_DIR + "themes/" + THEME, sleep_time=2)
        # sleep(5)

    # while not stop:
        # DisplayText(lcd_comm, str(datetime.now().time()), 160, 2,
        #             font=ASSET_DIR + "fonts/roboto/Roboto-Bold.ttf",
        #             font_size=20,
        #             font_color=(255, 0, 0),
        #             background_image=ASSET_DIR + "themes/3.5inchTheme2_theme_background.png")

        # DisplayProgressBar(lcd_comm, 10, 40,
        #                    width=140, height=30,
        #                    min_value=0, max_value=100, value=bar_value,
        #                    bar_color=(255, 255, 0), bar_outline=True,
        #                    background_image="res/example.png")

        # DisplayProgressBar(lcd_comm, 160, 40,
        #                    width=140, height=30,
        #                    min_value=0, max_value=19, value=bar_value % 20,
        #                    bar_color=(0, 255, 0), bar_outline=False,
        #                    background_image="res/example.png")

        # bar_value = (bar_value + 2) % 101

    serial_com.close()

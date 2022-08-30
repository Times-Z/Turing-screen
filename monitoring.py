#!/usr/bin/env python3
import threading
from time import sleep
from tracemalloc import Frame
from typing import Callable

import psutil
import pyamdgpuinfo
import serial

from Class import Com, Config, Display, Signal

stop = False


def sigHandler(signum: int, frame: Frame):
    """
        Used to stop application with signal after send a full frame to device
    """
    global stop
    stop = True


def generateThread(target: Callable, kwargs: dict) -> threading.Thread:
    """
        Generate a thread with target and kwargs
    """
    return threading.Thread(target=target, kwargs=kwargs)


if __name__ == "__main__":

    config = Config().load()
    theme = config.get("assets_dir") + "themes/" + config.get("theme")

    Signal().makeHandler(sigHandler)
    serial_com = serial.Serial(config.get(
        "com_port"), config.get("baudrate"), timeout=1, rtscts=1)
    com = Com(serial_com)
    display = Display(com, serial_com, config)

    # Display background image
    display.DisplayBitmap(theme)

    while not stop:
        threads = []

        text_information = {
            "cpu_load": {
                "text": str(psutil.cpu_percent()) + " %",
                "x": 80,
                "y": 30,
                "background_image": theme,
            },
            "cpu_freq": {
                "text": str(round(psutil.cpu_freq().current / 1000, 1)) + " Ghz",
                "x": 160,
                "y": 30,
                "background_image": theme,
            },
            "cpu_temp": {
                "text": str(round(psutil.sensors_temperatures().get(config.get("cpu_temp_device_name"))[0].current,1)) + " °",
                "x": 240,
                "y": 30,
                "background_image": theme,
            },
            "gpu_load": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_load(), 1)) + " %",
                "x": 80,
                "y": 90,
                "background_image": theme,
            },
            "gpu_power": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_power(), 1)) + " Watt",
                "x": 160,
                "y": 90,
                "background_image": theme,
            },
            "gpu_temp": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_temperature(), 1)) + " °",
                "x": 240,
                "y": 90,
                "background_image": theme,
            },
            "ram_percent_usage": {
                "text": str(psutil.virtual_memory().percent) + " %",
                "x": 80,
                "y": 140,
                "background_image": theme,
            },
            "ram_number_usage": {
                "text": str(round(psutil.virtual_memory().used /2.**30, 1)) + " / " + str(round(psutil.virtual_memory().total /2.**30, 1)) + " Gb",
                "x": 160,
                "y": 140,
                "background_image": theme,
            },
            "lan_ip": {
                "text": str(psutil.net_if_addrs().get(config.get("network_interface"))[0].address),
                "x": 80,
                "y": 195,
                "background_image": theme,
            }
        }

        for name in text_information:
            threads.append(generateThread(
                display.DisplayText, text_information.get(name)))

        for thread in threads:
            thread.start()
            sleep(config.get('refresh_interval'))

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

#!/usr/bin/env python3

import os
import threading
from time import time
from tracemalloc import Frame
from typing import Callable

import psutil
import pyamdgpuinfo
import serial
from psutil._common import bytes2human

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
        Generate a thread with target function and kwargs
    """
    return threading.Thread(target=target, kwargs=kwargs)


if __name__ == "__main__":

    config = Config().load()
    theme = config.get("assets_dir") + "themes/" + config.get("theme") + ".png"

    Signal().makeHandler(sigHandler)
    serial_com = serial.Serial(config.get(
        "com_port"), config.get("baudrate"), timeout=1, rtscts=1)
    com = Com(serial_com, config)
    display = Display(com, serial_com, config)

    display.DisplayBitmap(theme)
    display.DisplayText(str(psutil.users()
                        [0].name), 80, 235, background_image=theme)
    # display.DisplayBitmap(config.get("assets_dir") + "imgs/heart.gif", 100,300)

    while not stop:
        start_time = time()  # start time of the loop

        threads = []

        text_information = {
            "cpu_load": {
                "text": str(psutil.cpu_percent()) + " %",
                "x": 80,
                "y": 17,
                "background_image": theme,
            },
            "cpu_freq": {
                "text": str(round(psutil.cpu_freq().current / 1000, 1)) + " Ghz",
                "x": 155,
                "y": 17,
                "background_image": theme,
            },
            "cpu_temp": {
                "text": str(round(psutil.sensors_temperatures().get(config.get("cpu_temp_device_name"))[0].current, 1)) + " °",
                "x": 260,
                "y": 17,
                "background_image": theme,
            },
            "gpu_load": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_load(), 1)) + " %",
                "x": 80,
                "y": 67,
                "background_image": theme,
            },
            "gpu_power": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_power(), 1)) + " Watt",
                "x": 155,
                "y": 67,
                "background_image": theme,
            },
            "gpu_temp": {
                "text": str(round(pyamdgpuinfo.get_gpu(0).query_temperature(), 1)) + " °",
                "x": 260,
                "y": 67,
                "background_image": theme,
            },
            "ram_percent_usage": {
                "text": str(psutil.virtual_memory().percent) + " %",
                "x": 80,
                "y": 117,
                "background_image": theme,
            },
            "ram_number_usage": {
                "text": str(bytes2human(psutil.virtual_memory().used)) + " in use",
                "x": 155,
                "y": 117,
                "background_image": theme,
            },
            "disk_usage_root": {
                "text": "/ : " + str(psutil.disk_usage("/").percent) + " %",
                "x": 80,
                "y": 157,
                "background_image": theme,
                "font_size": 14,
            },
            "disk_usage_home": {
                "text": "/home : " + str(psutil.disk_usage("/home").percent) + " %",
                "x": 155,
                "y": 157,
                "background_image": theme,
                "font_size": 14,
            },
            "disk_usage_hdd": {
                "text": "/mnt/HDD : " + str(psutil.disk_usage("/mnt/HDD").percent) + " %",
                "x": 80,
                "y": 177,
                "background_image": theme,
                "font_size": 14,
            },
            "disk_usage_encrypted": {
                "text": "/mnt/DATA_ENCRYPTED : " + str(psutil.disk_usage("/mnt/DATA_ENCRYPTED").percent) + " %",
                "x": 80,
                "y": 197,
                "background_image": theme,
                "font_size": 14,
            },
        }

        if config.get("show_fps"):
            text_information['fps'] = {
                "text": "FPS : " + str(round(1.0 / (time() - start_time), 1)),
                "x": 265,
                "y": 465,
                "background_image": theme,
                "font_size": 12,
                "font_color": (98, 114, 164)
            }
        for name in text_information:
            threads.append(generateThread(
                display.DisplayText, text_information.get(name)))

        # for picture in sorted(os.listdir(config.get("assets_dir") + "imgs/surf")):
            # threads.append(generateThread(
            #     display.DisplayBitmap, {
            #         "bitmap_path": config.get("assets_dir") + "imgs/surf/" + picture,
            #         "x": 100,
            #         "y": 300,
            #     }))

        # threads.append(generateThread(
        #     display.DisplayBitmap, {
        #     "bitmap_path": config.get("assets_dir") + "imgs/surf.gif",
        #     "x": 100,
        #     "y": 300,
        # }))

        for thread in threads:
            if not serial_com.isOpen():
                serial_com.open()
            thread.start()
            thread.join()
            if serial_com.isOpen():
                serial_com.close()
        print("FPS: ", round(1.0 / (time() - start_time), 1),
              end="\r", flush=True, )

    if not serial_com.isOpen():
        serial_com.open()
    com.Clear()
    com.ScreenOff()

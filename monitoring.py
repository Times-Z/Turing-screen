#!/usr/bin/env python3

import os
import threading
from time import sleep, time
from tracemalloc import Frame
from typing import Callable

import psutil

from Class import Com, Config, Display, Hardware, Signal

stop = False


def sigHandler(signum: int, frame: Frame):
    """
        Used to stop application with signal after send a full frame to device
    """
    global stop
    stop = True if signum else False if frame else False


def generateTextInformations(target: str, dynamic: bool = True) -> threading.Thread:
    """
        Generate text informations in threads
    """
    for named_item in config.get(target, []):
        element = next(iter(named_item.values()))
        param = element['param'] if 'param' in element else None
        value = getattr(Hardware, element['metric'])(hardware) if param is None else getattr(
            Hardware, element['metric'])(hardware, param)
        text = display.generateText(
            value, element['prefix_txt'] if 'prefix_txt' in element else '')

        if dynamic:
            threads.append(
                threading.Thread(
                    target=display.DisplayText, kwargs={
                        'text': text,
                        'x': element['x'],
                        'y': element['y'],
                        'background_image': theme if 'transparent' in element and element['transparent'] == True else element['background_image'],
                        'font_size': element['font_size'] if 'font_size' in element else 20,
                    })
            )
        else:
            display.DisplayText(
                text, element['x'], element['y'], background_image=theme if 'transparent' in element and element['transparent'] == True else element['background_image'])


if __name__ == "__main__":
    config = Config().load()
    theme = config.get('assets_dir', 'assets/') + 'themes/' + \
        config.get('theme', 'dark') + '.png'

    Signal().makeHandler(sigHandler)
    com = Com(config)
    display = Display(com, com.serial, config)
    hardware = Hardware()

    display.DisplayBitmap(theme)
    generateTextInformations('static_text_informations', False)
    display.DisplayBitmap(config.get('assets_dir', 'assets/') + 'imgs/docker.png', 130,300)

    while not stop:
        start_time = time()

        threads = []

        generateTextInformations('dynamic_text_informations')

        if config.get('show_fps', False):
            fps_conf = config.get('show_fps', {})
            if fps_conf['show']:
                threads.append(
                    threading.Thread(
                        target=display.DisplayText, kwargs={
                            'text': fps_conf['text'] + str(round(1.0 / (time() - start_time), 1)),
                            'x': fps_conf['x'],
                            'y': fps_conf['y'],
                            'font_color': tuple(fps_conf['font_color']),
                            'font_size': fps_conf['font_size'],
                            'background_image': theme if 'transparent' in fps_conf and fps_conf['transparent'] == True else fps_conf['background_image'],
                        })
                )

        # for picture in sorted(os.listdir(config.get('assets_dir', 'assets/') + 'imgs/surf')):
        #     threads.append(generateThread(
        #         display.DisplayBitmap, {
        #             "bitmap_path": config.get('assets_dir', 'assets/') + 'imgs/surf/' + picture,
        #             "x": 100,
        #             "y": 300,
        #         }))

        for thread in threads:
            if not com.serial.isOpen():
                com.serial.open()
            thread.start()
            thread.join()
            if com.serial.isOpen():
                com.serial.close()
        print("Total frame/s: ", round(1.0 / (time() - start_time), 1),
              end="\r", flush=True, )
        if config.get('hot_reload_config', False):
            config = Config().load()

    if not com.serial.isOpen():
        com.serial.open()
    com.Clear()
    com.ScreenOff()

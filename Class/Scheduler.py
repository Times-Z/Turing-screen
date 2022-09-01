#!/usr/bin/env python3

import threading
from time import time

from Class.Com import Com
from Class.Config import Config
from Class.Display import Display
from Class.Hardware import Hardware


class Scheduler:

    def __init__(self, config: dict, theme: str, display: Display, com: Com) -> None:
        self.STOPPING: bool = False
        self.config: dict = config
        self.theme: str = theme
        self.display: Display = display
        self.com: Com = com
        self.hardware: Hardware = Hardware()
        self.threads: list[threading.Thread] = []

    def run(self, params: dict) -> None:
        static: str = params.get('static', '')
        dynamic: str = params.get('dynamic', '')
        self.generateTextInformation(static, False)
        while not self.STOPPING:
            start_time = time()
            self.generateTextInformation(dynamic)
            self.displayFps(start_time)
            self.runThreads()
            if self.config.get('hot_reload_config', False):
                self.config = Config().load()

    def generateTextInformation(self, target: str, dynamic: bool = True) -> threading.Thread:
        """
        Generate text information
        """
        for named_item in self.config.get(target, []):
            element: dict = next(iter(named_item.values()))
            param: str = element['param'] if 'param' in element else None
            value: str = getattr(Hardware, element['metric'])(self.hardware) if param is None else getattr(
                Hardware, element['metric'])(self.hardware, param)
            text: str = self.display.generateText(
                value, element['prefix_txt'] if 'prefix_txt' in element else '')
            if dynamic:
                self.threads.append(
                    threading.Thread(
                        target=self.display.displayText, kwargs={
                            'text': text,
                            'x': element['x'],
                            'y': element['y'],
                            'background_image': self.theme if 'transparent' in element and element['transparent'] == True else element['background_image'],
                            'font_size': element['font_size'] if 'font_size' in element else 20,
                        })
                )
            else:
                self.display.displayText(
                    text, element['x'], element['y'], background_image=self.theme if 'transparent' in element and element['transparent'] == True else element['background_image'])

    def runThreads(self) -> None:
        """
            Run threads and wait for thread job end
        """
        thread: threading.Thread
        for thread in self.threads:
            if not self.com.serial.isOpen():
                self.com.serial.open()
            thread.start()
            thread.join()
            if self.com.serial.isOpen():
                self.com.serial.close()
        self.threads.clear()

    def displayFps(self, start_time: float) -> None:
        """
            Display FPS if configured
        """
        if self.config.get('show_fps', False):
            fps_conf: dict = self.config.get('show_fps', {})
            if fps_conf['show']:
                fps: str = str(round(1.0 / (time() - start_time), 1))
                self.threads.append(
                    threading.Thread(
                        target=self.display.displayText, kwargs={
                            'text': fps_conf['text'] + fps,
                            'x': fps_conf['x'],
                            'y': fps_conf['y'],
                            'font_color': tuple(fps_conf['font_color']),
                            'font_size': fps_conf['font_size'],
                            'background_image': self.theme if 'transparent' in fps_conf and fps_conf['transparent'] == True else fps_conf['background_image'],
                        }
                    )
                )
                print("Total frame/s: " + fps, end="\r", flush=True)

#!/usr/bin/env python3

from ast import arguments
import threading
from time import time

from Class.Com import Com
from Class.Config import Config
from Class.Display import Display
from Class.Hardware import Hardware


class Scheduler:
    """
        Schedule display job
    """

    def __init__(self, config: dict, theme: str, display: Display, com: Com) -> None:
        self.STOPPING: bool = False
        self.config: dict = config
        self.theme: str = theme
        self.display: Display = display
        self.com: Com = com
        self.hardware: Hardware = Hardware()
        self.threads: list[threading.Thread] = []

    def run(self, params: dict) -> None:
        """
            Run the scheduler with params like :

            {
                'static': 'my_conf_key_for_static_elem',
                'dynamic': 'my_conf_key_for_dynamic_elem'
            }
        """
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

            arguments = {
                'text': text,
                'x': element['x'],
                'y': element['y'],
                'font_path': element['font_path'] if 'font_path' in element else self.display.DEFAULT_PARAM['font_path'],
                'font_size': element['font_size'] if 'font_size' in element else self.display.DEFAULT_PARAM['font_size'],
                'font_color': element['font_color'] if 'font_color' in element else self.display.DEFAULT_PARAM['font_color'],
                'background_color': element['background_color'] if 'background_color' in element else self.display.DEFAULT_PARAM['background_color'],
                'background_image': self.theme if 'transparent' in element and element[
                    'transparent'] == True else element['background_image'] if 'background_image' in element else self.display.DEFAULT_PARAM['background_image'],
            }

            if dynamic:
                self.threads.append(threading.Thread(
                    target=self.display.displayText, kwargs=arguments))
            else:
                self.display.displayText(**arguments)

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
                arguments = self.display.DEFAULT_PARAM.copy()
                arguments.update(
                    text=fps_conf['text'] + fps,
                    x=fps_conf['x'],
                    y=fps_conf['y'],
                    font_color=tuple(fps_conf['font_color']),
                    font_size=fps_conf['font_size'],
                    background_image=self.theme if 'transparent' in fps_conf and fps_conf[
                        'transparent'] == True else self.display.DEFAULT_PARAM['background_image']
                )
                self.threads.append(threading.Thread(
                    target=self.display.displayText, kwargs=arguments))
                print("Total frame/s: " + fps, end="\r", flush=True)

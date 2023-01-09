#!/usr/bin/env python3

import threading
from time import sleep, time

from .Com import Com
from .Config import Config
from .Display import Display
from .Hardware import Hardware
from .Logger import logger


class Scheduler:
    """
        Schedule display job
    """

    WARN_THREAD_NUMBER: int = 5
    STOPPING: bool = False

    def __init__(self, configuration: Config, theme: str, display: Display, com: Com) -> None:
        self.configuration: Config = configuration
        self.config: dict = configuration.config
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
                'dynamic': 'my_conf_key_for_dynamic_elem',
                'images': 'my_conf_key_for_images'
            }
        """
        self.display.displayBitmap(self.theme, 0, 0)
        txt_static: str = params.get('txt_static', '')
        txt_dynamic: str = params.get('txt_dynamic', '')
        img_static: str = params.get('img_static', '')
        self.__generateImage(img_static)
        self.__generateTextInformation(txt_static, False)
        while not self.STOPPING:
            if threading.activeCount() > self.WARN_THREAD_NUMBER:
                logger.warning('Active hread count is high ' +
                               str(threading.active_count()))
            start_time = time()
            self.__generateTextInformation(txt_dynamic)
            self.__displayFps(start_time)
            self.__runThreads(self.threads)
            if self.config.get('hot_reload_config', False):
                update_running: bool = self.__isThreadRunning(
                    'update-config-thread')
                if not update_running:
                    self.__runThreads([
                        threading.Thread(
                            name='update-config-thread',
                            target=self.__updateConfiguration,
                            args=[self.config.get('hot_reload_interval', 60)]
                        )
                    ], False)

    def __generateTextInformation(self, target: str, dynamic: bool = True) -> threading.Thread:
        """
            Generate text information
        """
        named_item: dict
        for named_item in self.config.get(target, []):
            element: dict = next(iter(named_item.values()))
            text: str = self.__getMetricValue(
                element['metric'] if 'metric' in element else None,
                element['param'] if 'param' in element else None
            )
            if not text:
                text: str = element['text'] if 'text' in element else ''
            final_text: str = self.display.generateText(
                text, element['prefix_txt'] if 'prefix_txt' in element else '')

            arguments = {
                'text': final_text,
                'x': element['x'] if self.configuration.getKey('x', element) else self.display.DEFAULT_TEXT_PARAM['x'],
                'y': element['y'] if self.configuration.getKey('y', element) else self.display.DEFAULT_TEXT_PARAM['y'],
                'font_path': element['font_path'] if self.configuration.getKey('font_path', element) else self.display.DEFAULT_TEXT_PARAM['font_path'],
                'font_size': element['font_size'] if self.configuration.getKey('font_size', element) else self.display.DEFAULT_TEXT_PARAM['font_size'],
                'font_color': tuple(element['font_color']) if self.configuration.getKey('font_color', element) else self.display.DEFAULT_TEXT_PARAM['font_color'],
                'background_color': element['background_color'] if self.configuration.getKey('background_color', element) else self.display.DEFAULT_TEXT_PARAM['background_color'],
                'background_image': self.theme if self.configuration.getKey('transparent', element) and element[
                    'transparent'] == True else element['background_image'] if self.configuration.getKey('background_image', element) else self.display.DEFAULT_TEXT_PARAM['background_image'],
            }

            if dynamic:
                self.threads.append(threading.Thread(
                    name=list(named_item.keys())[0], target=self.display.displayText, kwargs=arguments))
            else:
                self.display.displayText(**arguments)

    def __generateImage(self, target: str, dynamic: bool = False):
        named_item: dict
        for named_item in self.config.get(target, []):
            element: dict = self.configuration.getKey(
                list(named_item.keys())[0])
            arguments = self.display.DEFAULT_BITMAP_PARAM.copy()
            imgs_path = self.configuration.getKey('assets_dir') + 'imgs/'

            arguments = {
                'bitmap_path': imgs_path + element['name'] if self.configuration.getKey('name', element) else imgs_path + self.display.DEFAULT_BITMAP_PARAM['bitmap_path'],
                'x': element['x'] if self.configuration.getKey('x', element) else self.display.DEFAULT_BITMAP_PARAM['x'],
                'y': element['y'] if self.configuration.getKey('y', element) else self.display.DEFAULT_BITMAP_PARAM['y']
            }

            if not dynamic:
                self.display.displayBitmap(**arguments)

    def __runThreads(self, threads: list[threading.Thread], wait_thread: bool = True) -> None:
        """
            Run threads and wait for thread job end
        """
        thread: threading.Thread
        for thread in threads:
            if not self.com.serial.isOpen():
                self.com.serial.open()
            thread.start()
            if wait_thread:
                thread.join()
            if self.com.serial.isOpen():
                self.com.serial.close()
        threads.clear()

    def __displayFps(self, start_time: float) -> None:
        """
            Display FPS if configured
        """
        if self.config.get('debug', False):
            debug_conf: dict = self.config.get('debug', {})
            if debug_conf['show']:
                fps: str = str(round(1.0 / (time() - start_time), 1))
                ram: str = Hardware.getCurrentProgramMemoryUsage()
                fps_arg = self.display.DEFAULT_TEXT_PARAM.copy()
                ram_arg = self.display.DEFAULT_TEXT_PARAM.copy()
                fps_arg.update(
                    text='FPS : ' + fps,
                    x=debug_conf['x'],
                    y=debug_conf['y'],
                    font_color=tuple(debug_conf['font_color']),
                    font_size=debug_conf['font_size'],
                    background_image=self.theme if 'transparent' in debug_conf and debug_conf[
                        'transparent'] == True else self.display.DEFAULT_TEXT_PARAM['background_image']
                )
                ram_arg.update(
                    text='RAM : ' + ram,
                    x=debug_conf['x'],
                    y=debug_conf['y'] + 20,
                    font_color=tuple(debug_conf['font_color']),
                    font_size=debug_conf['font_size'],
                    background_image=self.theme if 'transparent' in debug_conf and debug_conf[
                        'transparent'] == True else self.display.DEFAULT_TEXT_PARAM['background_image']
                )
                self.threads.append(threading.Thread(
                    name='debug-fps', target=self.display.displayText, kwargs=fps_arg))
                self.threads.append(threading.Thread(
                    name='debug-ram', target=self.display.displayText, kwargs=ram_arg))

    def __isThreadRunning(self, thread_name: str) -> bool:
        for thread in threading.enumerate():
            if thread_name in thread.name:
                return True
        return False

    def __updateConfiguration(self, update_time: int = 60) -> None:
        self.config = Config().load()
        self.threads.append(
            threading.Thread(
                target=self.com.SetBrightness,
                args=[self.com.BRIGHTNESS_LEVEL.get(
                    self.config.get('screen_brightness', 0), 0)]
            )
        )
        logger.info(threading.current_thread().name +
                    ' sleeping for ' + str(update_time) + ' secs')
        sleep(update_time)

    def __getMetricValue(self, metric: str | None, param: str | None) -> str:
        """
            Get the metric value from Hardware
        """
        if metric:
            if param:
                return getattr(Hardware, metric)(self.hardware, param)
            return getattr(Hardware, metric)(self.hardware)
        return ''

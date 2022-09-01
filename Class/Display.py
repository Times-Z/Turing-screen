#!/usr/bin/env python3

import struct

import serial
from PIL import Image, ImageDraw, ImageFont, PyAccess

from .Com import Com


class Display:
    """
        Display class
    """

    DEFAULT_PARAM: dict = {
        'text': 'Sample Text',
        'x': 0,
        'y': 0,
        'font_path': 'roboto/Roboto-Regular.ttf',
        'font_size': 20,
        'font_color': (255, 255, 255),
        'background_color': (0, 0, 0),
        'background_image': None
    }

    def __init__(self, com: Com, ser: serial.Serial, config: dict) -> None:
        self.com: Com = com
        self.serial: serial.Serial = ser
        self.config: dict = config
        self.DISPLAY_WIDTH: int = config.get('display_width', 320)
        self.DISPLAY_HEIGHT: int = config.get('display_height', 480)

    def displayPILImage(self, image: Image.Image, x: int, y: int, gif: bool = False) -> None:
        """
            Display Pillow image

            x and y set the place on pixel in the screen
        """
        image_height: int = image.size[1]
        image_width: int = image.size[0]

        assert image_height > 0, 'Image width must be > 0'
        assert image_width > 0, 'Image height must be > 0'

        self.com.SendReg(self.com.DISPLAY_BITMAP, x, y, x +
                         image_width - 1, y + image_height - 1)

        frames: int = 1
        if gif:
            frames = image.n_frames
        for frame in range(0, frames):
            try:
                if gif:
                    image.seek(frame+1)
                pix: PyAccess.PyAccess = image.load()
                line: bytes = bytes()
                for h in range(image_height):
                    for w in range(image_width):
                        R: int = pix[w, h][0] >> 3
                        G: int = pix[w, h][1] >> 2
                        B: int = pix[w, h][2] >> 3

                        rgb: int = (R << 11) | (G << 5) | B
                        line += struct.pack('H', rgb)

                        # Send image data by multiple of DISPLAY_WIDTH bytes
                        if len(line) >= self.DISPLAY_WIDTH * 8:
                            self.serial.write(line)
                            line = bytes()
                # Write last line if needed
                if len(line) > 0:
                    self.serial.write(line)
            except EOFError:
                pass  # end of sequence gif

    def displayBitmap(self, bitmap_path: str, x=0, y=0) -> None:
        """
            Display bitmap on 0/0 by default
        """
        image: Image.Image = Image.open(bitmap_path)
        self.displayPILImage(
            image, x, y, True if ".gif" in bitmap_path else False)

    def displayText(self, text: str, x: int, y: int, font_path: str, font_size: int, font_color: tuple, background_color: tuple, background_image: str | None) -> None:
        """
        Convert text to bitmap using PIL and display it

        Provide the background image path to display text with transparent background
        """
        assert len(text) > 0, 'Text must not be empty'
        assert font_size > 0, "Font size must be > 0"

        if background_image is None:
            text_image: Image.Image = Image.new(
                'RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), background_color)
        else:
            text_image: Image.Image = Image.open(background_image)

        font: ImageFont.FreeTypeFont = ImageFont.truetype(self.config.get(
            'assets_dir', 'assets/') + 'fonts/' + font_path, font_size)
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(text_image)
        draw.text((x, y), text, font=font, fill=font_color)

        ascent, descent = font.getmetrics()
        text_width = font.getmask(text).getbbox()[2] + (ascent - 7)
        text_height = font.getmask(text).getbbox()[3] + descent
        text_image = text_image.crop(box=(x, y, min(
            x + text_width, self.DISPLAY_WIDTH), min(y + text_height, self.DISPLAY_HEIGHT)))

        self.displayPILImage(text_image, x, y)

    def displayProgressBar(self, x: int, y: int, width: int, height: int, min_value=0, max_value=100,
                           value=50,
                           bar_color=(0, 0, 0),
                           bar_outline=True,
                           background_color=(255, 255, 255),
                           background_image: str = '') -> None:
        """
        Generate a progress bar and display it

        Provide the background image path to display progress bar with transparent background
        """

        assert x + width <= self.DISPLAY_WIDTH, 'Progress bar width exceeds display width'
        assert y + height <= self.DISPLAY_HEIGHT, 'Progress bar height exceeds display height'
        assert min_value <= value <= max_value, 'Progress bar value shall be between min and max'

        if len(background_image) <= 0:
            bar_image: Image.Image = Image.new(
                'RGB', (width, height), background_color)
        else:
            bar_image: Image.Image = Image.open(background_image)
            bar_image: Image.Image = bar_image.crop(
                box=(x, y, x + width, y + height))

        # Draw progress bar
        bar_filled_width: float = value / (max_value - min_value) * width
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(bar_image)
        draw.rectangle([0, 0, bar_filled_width-1, height-1],
                       fill=bar_color, outline=bar_color)

        if bar_outline:
            # Draw outline
            draw.rectangle([0, 0, width-1, height-1],
                           fill=None, outline=bar_color)

        self.displayPILImage(bar_image, x, y)

    def generateText(self, text: str, prefix: str = None) -> str:
        """
            Generate text string for display
        """
        txt: str = ''
        if prefix:
            txt: str = prefix + ' '
        txt: str = txt + text
        return txt

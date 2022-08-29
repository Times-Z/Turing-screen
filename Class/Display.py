#!/usr/bin/env python3

import struct
from time import sleep

import serial
from PIL import Image, ImageDraw, ImageFont

from monitoring import ASSET_DIR

from .Com import Com


class Display:
    """
        Display class
    """

    def __init__(self, com: Com, serial: serial, display_width: int, display_height: int) -> None:
        self.com = com
        self.serial = serial
        self.DISPLAY_WIDTH = display_width
        self.DISPLAY_HEIGHT = display_height

    def DisplayPILImage(self, image: Image, x: int, y: int) -> None:
        """
            Display Pillow image

            x and y set the place on pixel in the screen
        """
        image_height = image.size[1]
        image_width = image.size[0]

        assert image_height > 0, 'Image width must be > 0'
        assert image_width > 0, 'Image height must be > 0'

        self.com.SendReg(self.com.DISPLAY_BITMAP, x, y, x +
                         image_width - 1, y + image_height - 1)

        pix = image.load()
        line = bytes()
        for h in range(image_height):
            for w in range(image_width):
                R = pix[w, h][0] >> 3
                G = pix[w, h][1] >> 2
                B = pix[w, h][2] >> 3

                rgb = (R << 11) | (G << 5) | B
                line += struct.pack('H', rgb)

                # Send image data by multiple of DISPLAY_WIDTH bytes
                if len(line) >= self.DISPLAY_WIDTH * 8:
                    self.serial.write(line)
                    line = bytes()

        # Write last line if needed
        if len(line) > 0:
            self.serial.write(line)

        sleep(0.01)  # Wait 10 ms after picture display

    def DisplayBitmap(self, bitmap_path: str, x=0, y=0) -> None:
        """
            Display bitmap on 0/0 by default
        """
        image = Image.open(bitmap_path)
        self.DisplayPILImage(image, x, y)

    def DisplayText(self, text: str, x=0, y=0,
                    font=ASSET_DIR + "fonts/roboto/Roboto-Regular.ttf",
                    font_size=20,
                    font_color=(0, 0, 0),
                    background_color=(255, 255, 255),
                    background_image: str = None,
                    sleep_time: int = None) -> None:
        """
        Convert text to bitmap using PIL and display it

        Provide the background image path to display text with transparent background
        """
        assert len(text) > 0, 'Text must not be empty'
        assert font_size > 0, "Font size must be > 0"

        if background_image is None:
            # A text bitmap is created with max width/height by default : text with solid background
            text_image = Image.new(
                'RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), background_color)
        else:
            # The text bitmap is created from provided background image : text with transparent background
            text_image = Image.open(background_image)

        # Draw text with specified color & font
        font = ImageFont.truetype(font, font_size)
        d = ImageDraw.Draw(text_image)
        d.text((x, y), text, font=font, fill=font_color)

        # Crop text bitmap to keep only the text
        ascent, descent = font.getmetrics()
        text_width = font.getmask(text).getbbox()[2]
        text_height = font.getmask(text).getbbox()[3] + descent
        text_image = text_image.crop(box=(x, y, min(
            x + text_width, self.DISPLAY_WIDTH), min(y + text_height, self.DISPLAY_HEIGHT)))

        self.DisplayPILImage(text_image, x, y)
        if sleep_time:
            sleep(sleep_time)

    def DisplayProgressBar(self, x: int, y: int, width: int, height: int, min_value=0, max_value=100,
                           value=50,
                           bar_color=(0, 0, 0),
                           bar_outline=True,
                           background_color=(255, 255, 255),
                           background_image: str = None) -> None:
        """
        Generate a progress bar and display it

        Provide the background image path to display progress bar with transparent background
        """

        assert x + width <= self.DISPLAY_WIDTH, 'Progress bar width exceeds display width'
        assert y + height <= self.DISPLAY_HEIGHT, 'Progress bar height exceeds display height'
        assert min_value <= value <= max_value, 'Progress bar value shall be between min and max'

        if background_image is None:
            # A bitmap is created with solid background
            bar_image = Image.new('RGB', (width, height), background_color)
        else:
            # A bitmap is created from provided background image
            bar_image = Image.open(background_image)

            # Crop bitmap to keep only the progress bar background
            bar_image = bar_image.crop(box=(x, y, x + width, y + height))

        # Draw progress bar
        bar_filled_width = value / (max_value - min_value) * width
        draw = ImageDraw.Draw(bar_image)
        draw.rectangle([0, 0, bar_filled_width-1, height-1],
                       fill=bar_color, outline=bar_color)

        if bar_outline:
            # Draw outline
            draw.rectangle([0, 0, width-1, height-1],
                           fill=None, outline=bar_color)

        self.DisplayPILImage(bar_image, x, y)

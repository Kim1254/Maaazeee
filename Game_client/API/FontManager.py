import os
import numpy as np

from PIL import Image, ImageDraw, ImageFont

from GUI.Util import *
from GUI.GameCanvas import MatrixScalar


class FontManager:
    def __init__(self, path, size):
        self.__font = ImageFont.truetype(font=os.getcwd() + '/' + path, size=size)
        self.__color = '#ffffff'
        self.__alpha = 255
        self.__valid = True

    def SetColor(self, *args):
        if self.__valid is False:
            return
        if self.__font is None:
            return

        self.__color = RGB_IntArrayToStr(args[:3])

        if len(args) == 4:
            self.__alpha = args[3]

    def GetColor(self, *args):
        if self.__valid is False:
            return None
        if self.__font is None:
            return None

        return self.__color

    def GetHeight(self, text=None):
        if text is None:
            text = 'a'

        t = 0

        for char in text:
            x, y = self.__font.getsize(char)
            t = max(t, y)

        return t

    def GetWidth(self, text):
        if text is None:
            return 0

        w = 0

        for char in text:
            x, y = self.__font.getsize(char)
            w += x

        return w

    def GetTextImage(self, string: str):
        if self.__valid is False:
            return None
        if self.__font is None:
            return None

        ary = None

        for char in string:
            x, y = self.__font.getsize(char)

            image = Image.new('RGBA', (x, y))

            draw = ImageDraw.Draw(image)
            draw.text((0, 0), char, font=self.__font, fill=self.__color)

            arr = np.array(image).astype('uint8')

            if ary is None:
                ary = arr
            else:
                if ary.shape[0] != arr.shape[0]:
                    dist = abs(ary.shape[0] - arr.shape[0])
                    if ary.shape[0] < arr.shape[0]:
                        temp = np.full(dist * ary.shape[1] * 4, 0).astype('uint8').reshape(dist, ary.shape[1], 4)
                        ary = np.concatenate((ary, temp), axis=0)
                    else:
                        temp = np.full(dist * arr.shape[1] * 4, 0).astype('uint8').reshape(dist, arr.shape[1], 4)
                        arr = np.concatenate((arr, temp), axis=0)
                ary = np.concatenate((ary, arr), axis=1)

        ary = MatrixScalar(ary, [255, 255, 255, self.__alpha])
        return ary

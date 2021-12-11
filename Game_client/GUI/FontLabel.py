from tkinter import Label
from copy import deepcopy

from API.FontManager import *
from GUI.GameCanvas import cv2Tk


class FontLabel(Label):
    def __init__(self, master, cnf={}, **kw):
        super(type(self), self).__init__(master, cnf, **kw)

        self.text = None
        self.font = None
        self.font_image = None

    def SetFont(self, path, size):
        self.font = FontManager(path, size)
        self.font.SetColor(0, 0, 0)

    def SetColor(self, *args):
        if self.font is None:
            return
        self.font.SetColor(*args)

    def SetText(self, string):
        if self.font is None:
            return

        self.text = string
        array = self.font.GetTextImage(string)
        self.font_image = cv2Tk(array)
        self['image'] = self.font_image

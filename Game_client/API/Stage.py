import time

from API.SoundManager import ChannelList
from API.PathFind import *


class Stage:
    def __init__(self, master, map):
        self.map = map
        self.master = master

        self.w = self.t = 0
        self.ran_x = self.ran_y = 0
        self.border_x = self.border_y = 0

        self.history = None
        self.valid = False

    def Load(self):
        self.valid = True
        xx = self.border_x - 2
        yy = self.border_y - 2
        ww = (self.w + 1) * min(20, len(self.map[0])) + 3
        tt = (self.w + 1) * min(20, len(self.map)) + 3
        points = [xx, yy,
                  xx + ww, yy,
                  xx + ww, yy + tt,
                  xx, yy + tt]
        self.master.canvas.create_polygon(points, fill='#ffffff', outline='#000000')

        self.master.manager.ResetMoveCount()
        self.master.canvas.BuildMap(self.ran_x, self.ran_y, self.w, self.w, self.map)
        self.master.canvas.offset_coord = (0, 0)
        self.master.manager.map = self.map

    def CannotMove(self):
        self.master.sound.Play('./data/sound/warning.mp3', ChannelList.Effect)

    def Exit(self):
        self.master.Command(self, 'MainScreen')
        self.valid = False

    def Next(self):
        self.master.Command(self, 'NextStage')

    def Clear(self):
        self.master.window.unbind("<Key>")
        self.master.canvas.DeactivateControl()
        self.master.canvas.RemoveDirection()

        self.history = deepcopy(self.master.manager.history)

    def Retry(self):
        pass

    def Event_Exit(self, event):
        self.Exit()

    def Event_Next(self, event):
        self.Next()

from enum import Enum
from copy import deepcopy


class Stage(Enum):
    Tutorial = 0


class GameManager:
    def SetMap(self, new_map):
        self.map = new_map

    def ResetMoveCount(self):
        self.history.clear()

    def SetPosition(self, new_position):
        self.position = new_position
        self.history.append(deepcopy(new_position))

    def Move(self, x, y):
        self.position[0] += x
        self.position[1] += y
        self.history.append(deepcopy(self.position))

    def Check(self, pos=None):
        if self.map is None:
            return 1
        if pos is None:
            pos = [self.position[0], self.position[1]]

        if pos[0] >= len(self.map[0]):
            return 1
        if pos[1] >= len(self.map):
            return 1

        return self.map[pos[1]][pos[0]]

    def CanMove(self):
        x = self.position[0]
        y = self.position[1]

        # ↑ ↓ ← →
        rs = [False, False, False, False]
        if self.Check([x, y - 1]) != 1:
            rs[0] = True
        if self.Check([x, y + 1]) != 1:
            rs[1] = True
        if self.Check([x - 1, y]) != 1:
            rs[2] = True
        if self.Check([x + 1, y]) != 1:
            rs[3] = True

        return rs

    def __init__(self):
        self.stage = None
        self.map = None
        self.position = [0, 0]
        self.history = []

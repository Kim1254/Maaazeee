from random import *
from copy import deepcopy

import numpy as np


def Make_Map(w, t):
    map = np.full(w * t, 0).astype('uint8').reshape(t, w).tolist()

    XP = [0, 1, 0, -1]
    YP = [-1, 0, 1, 0]

    # 주변 벽
    for x in range(w):
        map[0][x] = 1
        map[t - 1][x] = 1
    for y in range(1, t - 1):
        map[y][0] = 1
        map[y][w - 1] = 1
    # 안을 아무것도 없는 상태로
    '''
    for y in range(1, t - 1):
        for x in range(1, w - 1):
            map[y][x] = 0
    '''

    # 기둥
    for y in range(2, t - 2, 2):
        for x in range(2, w - 2, 2):
            map[y][x] = 1
    # 기둥에서 상하좌우로 벽 생성
    for y in range(2, t - 2, 2):
        for x in range(2, w - 2, 2):
            d = randint(0, 3)
            if x > 2:
                # 2번째 열부터 왼쪽으로는 벽을 만들지 않음
                d = randint(0, 2)
            map[y + YP[d]][x + XP[d]] = 1

    map[1][1] = 2
    map[t - 2][w - 2] = 3

    return map

import time
import heapq

from collections import deque
from copy import deepcopy

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def heuristic(node, goal, d1=1, d2=2 ** 0.5):  # Diagonal Distance
    dx = abs(node.position[0] - goal.position[0])
    dy = abs(node.position[1] - goal.position[1])
    return d1 * (dx + dy) + (d2 - 2 * d1) * min(dx, dy)


def aStar(original_maze):
    maze = deepcopy(original_maze)
    start, end = None, None

    for line in maze:
        if 2 in line:
            start = (maze.index(line), line.index(2))
        if 3 in line:
            end = (maze.index(line), line.index(3))

    if None in (start, end):
        return None

    # startNode와 endNode 초기화
    startNode = Node(None, start)
    endNode = Node(None, end)

    # openList, closedList 초기화
    openList = []
    closedList = []

    visit = []
    search = []

    # openList에 시작 노드 추가
    openList.append(startNode)

    # endNode를 찾을 때까지 실행
    while openList:
        # 현재 노드 지정
        currentNode = openList[0]
        currentIdx = 0
        # 이미 같은 노드가 openList에 있고, f 값이 더 크면
        # currentNode를 openList안에 있는 값으로 교체
        for index, item in enumerate(openList):
            if item.f < currentNode.f:
                currentNode = item
                currentIdx = index

        # openList에서 제거하고 closedList에 추가
        openList.pop(currentIdx)
        closedList.append(currentNode)

        # 현재 노드가 목적지면 current.position 추가하고
        # current의 부모로 이동
        if currentNode == endNode:
            path = []
            current = currentNode
            while current is not None:
                # maze 길을 표시하려면 주석 해제
                # x, y = current.position
                path.append((current.position[1], current.position[0]))
                current = current.parent
            return [path[::-1], search]  # reverse

        children = []
        # 인접한 xy좌표 전부
        for newPosition in [(0, -1), (0, 1), (-1, 0), (1, 0)]:

            # 노드 위치 업데이트
            nodePosition = (
                currentNode.position[0] + newPosition[0],  # X
                currentNode.position[1] + newPosition[1])  # Y

            # 미로 maze index 범위 안에 있어야함
            within_range_criteria = [
                nodePosition[0] > (len(maze) - 1),
                nodePosition[0] < 0,
                nodePosition[1] > (len(maze[len(maze) - 1]) - 1),
                nodePosition[1] < 0,
            ]

            if any(within_range_criteria):  # 하나라도 true면 범위 밖임
                continue

            # 장애물이 있으면 다른 위치 불러오기
            if maze[nodePosition[0]][nodePosition[1]] == 1:
                continue

            node = Node(currentNode, nodePosition)
            search.append((nodePosition[1], nodePosition[0]))
            children.append(node)

        # 자식들 모두 loop
        for child in children:
            # 자식이 closedList에 있으면 continue
            if child in closedList:
                continue

            # f, g, h값 업데이트
            child.g = currentNode.g + 1
            child.h = ((child.position[0] - endNode.position[0]) ** 2) + ((child.position[1] - endNode.position[1]) ** 2)
            child.f = child.g + child.h

            # 자식이 openList에 있으고, g값이 더 크면 continue
            if len([openNode for openNode in openList if child == openNode and child.g > openNode.g]) > 0:
                continue

            openList.append(child)
            visit.append((child.position[1], child.position[0]))

    return [visit, search]


def BFS(original_map):
    map = deepcopy(original_map)
    n = len(map) # height

    x, y, ex, ey = -1, -1, -1, -1

    for line in map:
        if 2 in line:
            x, y = line.index(2), map.index(line)
        if 3 in line:
            ex, ey = line.index(3), map.index(line)

    if -1 in (x, y, ex, ey):
        return None

    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    q = []
    q = deque()
    q.append((x, y))

    visit = []
    search = []

    while q:
        x, y = q.popleft()
        visit.append((x, y))

        if ex == x and ey == y:
            return [visit, search]

        for i in range(4):
            nx = x + dx[i]
            ny = y + dy[i]
            if 0 <= nx < len(map[0]) and 0 <= ny < n:
                if map[ny][nx] != 1:
                    map[ny][nx] = 1
                    q.append((nx, ny))
                    search.append((nx, ny))

    return [visit, search]


def DFS(original_map):
    map = deepcopy(original_map)
    n = len(map) # height

    x, y, ex, ey = -1, -1, -1, -1

    for line in map:
        if 2 in line:
            x, y = line.index(2), map.index(line)
        if 3 in line:
            ex, ey = line.index(3), map.index(line)

    if -1 in (x, y, ex, ey):
        return None

    stack = [(y, x)]

    visit = []
    search = []

    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    while len(stack) > 0:
        now = stack.pop()  # 스택의 가장 마지막 데이터 추출
        x, y = now[1], now[0]
        visit.append((x, y))

        if x == ex and y == ey:  # 정답 여부 검사
            break

        for i in range(4):
            xx = x + dx[i]
            yy = y + dy[i]

            if 0 <= xx < len(map[0]) and 0 <= yy < n:
                if map[yy][xx] != 1:
                    map[yy][xx] = 1
                    stack.append((yy, xx))
                    search.append((xx, yy))

    return [visit, search]


def BackTracking(maze, ex, ey):
    dx=[-1, 1, 0, 0]
    dy=[0, 0, -1, 1]

    foots = [[ex, ey]]
    foot = maze[ex][ey]
    while True:
        for di in range(4):
            x = ex + dx[di]
            y = ey + dy[di]
            if maze[x][y] == foot-1:
                foots.append([x, y])
                ex = x
                ey = y
                foot = maze[x][y]
                break
        if foot == 1:
            foots.reverse()
            return foots


def Dijkstra(original_map):
    map = deepcopy(original_map)
    n = len(map)  # height

    x, y, ex, ey = -1, -1, -1, -1

    for line in map:
        if 2 in line:
            x, y = map.index(line), line.index(2)
        if 3 in line:
            ex, ey = map.index(line), line.index(3)

    if -1 in (x, y, ex, ey):
        return None

    q = []
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    map1 = [[-1] * len(map[n - 1]) for _ in range(n)]
    map1[x][y] = 0
    heapq.heappush(q, (1, (x, y)))

    find_list = []
    find_list = deque()

    while True:
        dist, (x, y) = heapq.heappop(q)
        find_list.append((x, y))

        if map[x][y] == 3:
            break

        for i in range(4):
            xx = x + dx[i]
            yy = y + dy[i]
            if 0 <= xx < n and 0 <= yy < len(map[n - 1]) and map1[xx][yy] < 0:
                if map[xx][yy] != 1:
                    map1[xx][yy] = dist
                    heapq.heappush(q, (dist + 1, (xx, yy)))

    route = BackTracking(map1, ex, ey)
    route.append((ex, ey))

    visit = []
    for elem in route:
        visit.append([elem[1], elem[0]])

    return [visit, []]

from threading import Thread

from API.Stage import *
from API.FontManager import *
from API.MapBuilder import *
from API.TextMapping import *

import API.TextMapping as tm

from GUI.ImagedButton import *


class Default(Stage):
    def __init__(self, master, map=None):
        super(Default, self).__init__(master, map)

        self.using = False
        self.th_kill = False
        self.threading = False

        self.title = 'Level -6143191234'

        self.remove = []
        self.checkbox = []
        self.pointer = []

        self.entry = []

        self.path_find = 0

        self.offset_x, self.offset_y = 0, 0

    def SetMap(self, level):
        self.map = map_list[level]
        if level <= 5:
            self.title = Translate("#GAME_GameText_Default_Title").format(level)
        else:
            self.title = Translate("#GAME_GameText_Default_CustomTitle")

    def Load(self):
        self.using = True

        old_canvas = self.master.canvas
        self.master.canvas = GameCanvas(self.master, width=self.master.width, height=self.master.tall, bg='black',
                                        relief='solid')
        self.master.canvas['bg'] = '#ffffff'

        self.master.canvas.create_image('./image/bg/bg1.png',
                                        0, 0, self.master.width, self.master.tall,
                                        anchor=NW)

        if self.map is None:
            self.MakeCustomMap()
            old_canvas.destroy()
            return

        self.w = int(self.master.width / 2.5) // min(20, max(len(self.map), len(self.map[0])))

        y = 55

        y_len = min(20, len(self.map))
        x_len = min(20, len(self.map[0]))

        self.ran_x = 40 + (self.master.width // 2 - self.w * x_len) / 2
        self.ran_y = self.border_y = (self.master.tall - self.w * y_len) / 2 - 8
        self.border_x = self.ran_x

        super(type(self), self).Load()
        self.offset_x, self.offset_y = 0, 0

        self.remove.clear()

        del_x = (self.ran_x + ((self.w + 1) * x_len - 48) / 2,
                 self.ran_x + ((self.w + 1) * x_len - 48) / 2,
                 self.ran_x - 48,
                 self.ran_x + ((self.w + 1) * x_len))
        del_y = (self.ran_y - 48,
                 self.ran_y + ((self.w + 1) * y_len),
                 self.ran_y + ((self.w + 1) * y_len - 48) / 2,
                 self.ran_y + ((self.w + 1) * y_len - 48) / 2)

        self.pointer.clear()
        if self.offset_y > 0:
            button = ImagedButton(del_x[0], del_y[0], 'MoveScreen 0')
            button.SetImage('./image/default/pointer00.png',
                            './image/default/pointer01.png',
                            './image/default/pointer02.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if len(self.map) - self.offset_y > 20:
            button = ImagedButton(del_x[1], del_y[1], 'MoveScreen 1')
            button.SetImage('./image/default/pointer10.png',
                            './image/default/pointer11.png',
                            './image/default/pointer12.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if self.offset_x > 0:
            button = ImagedButton(del_x[2], del_y[2], 'MoveScreen 2')
            button.SetImage('./image/default/pointer20.png',
                            './image/default/pointer21.png',
                            './image/default/pointer22.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if len(self.map[0]) - self.offset_x > 20:
            button = ImagedButton(del_x[3], del_y[3], 'MoveScreen 3')
            button.SetImage('./image/default/pointer30.png',
                            './image/default/pointer31.png',
                            './image/default/pointer32.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        x = self.master.width * 0.65

        font = FontManager('font/NanumSquareEB.ttf', 30)
        font.SetColor(0, 0, 0, 255)

        array = font.GetTextImage(self.title)

        self.master.canvas.create_FontImage(array, self.master.width * 0.65, y, anchor=NW)
        y += array.shape[0] + 10

        retry = ImagedButton(x, y, 'Retry')
        retry.SetImage(
            TImg('./image/default/retry0'), TImg('./image/default/retry1'), TImg('./image/default/retry2'),
            80, 80)
        retry.canvas_hook(self.master.canvas)

        exit = ImagedButton(x + 100, y, 'Stage_Exit')
        exit.SetImage(
            TImg('./image/default/exit0'), TImg('./image/default/exit1'), TImg('./image/default/exit2'),
            80, 80)
        exit.canvas_hook(self.master.canvas)

        y += 90

        image = self.master.canvas.create_image('./image/default/key.png', x, y, 30, 30, anchor=NW)
        self.remove.append(self.master.canvas.image[-1])

        font = FontManager('font/NanumSquareR.ttf', 16)
        font.SetColor(0, 0, 0, 255)
        array = font.GetTextImage(Translate("#GAME_GameText_Default_SearchType"))

        label = self.master.canvas.create_FontImage(array, x + 35, y + (30 - array.shape[0]) // 2)
        self.remove.append(self.master.canvas.font_image[-1])

        y += 35

        string = ['AStar', 'Dijkstra', 'DFS', 'BFS']

        self.checkbox.clear()
        xx = x
        for i in range(4):
            image = self.master.canvas.create_image(
                './image/default/checkbox_{}.png'.format('on' if i == self.path_find else 'off'),
                xx, y, 20, 20, anchor=NW)
            self.checkbox.append(image)
            self.remove.append(self.master.canvas.image[-1])
            xx += 30

            array = font.GetTextImage(Translate("#GAME_" + string[i]))
            label = self.master.canvas.create_FontImage(array, xx, y + (20 - array.shape[0]) // 2)
            self.remove.append(self.master.canvas.font_image[-1])
            xx += array.shape[1] + 10

            if i == 1:
                xx = x
                y += 30

        y = self.master.tall - 100

        width = 40

        font = FontManager('font/NanumSquareR.ttf', 20)
        font.SetColor(0, 0, 0, 255)

        array = font.GetTextImage('00:00')
        self.master.canvas.create_image('./image/default/timer.png', x, y, width, width, anchor=NW)

        x += width + 10
        timer = self.master.canvas.create_FontImage(array, x, y + (width - array.shape[0]) // 2)
        x += array.shape[1] + 20

        array = font.GetTextImage('0')
        self.master.canvas.create_image('./image/default/move.png', x, y, width, width, anchor=NW)
        x += width + 10

        move = self.master.canvas.create_FontImage(array, x, y + (width - array.shape[0]) // 2)

        temp = np.full((self.master.tall, self.master.width, 4), 255).astype('uint8')
        array = MatrixScalar(temp, [0, 0, 0, 255])

        image = self.master.canvas.create_image(array, 0, 0, anchor=NW)

        old_canvas.destroy()

        alpha = 255
        while self.master.valid:
            alpha = max(0, alpha - 10)
            new_ary = MatrixScalar(array, [255, 255, 255, alpha])
            new_img = cv2Tk(new_ary)

            for elem in self.master.canvas.image:
                if elem[0] == image:
                    self.master.canvas.itemconfigure(elem[0], image=new_img)
                    elem[2] = new_img
                    self.master.canvas.update()
                    break

            if alpha == 0:
                break
            time.sleep(0.001)

        for elem in self.master.canvas.image:
            if elem[0] == image:
                self.master.canvas.image.remove(elem)
                break
        self.master.canvas.delete(image)

        self.using = False

        for i in range(4):
            self.master.canvas.tag_bind(self.checkbox[i], '<ButtonRelease-1>', self.Event_CheckBox)
        for elem in self.pointer:
            elem.Event_Bind()

        retry.Event_Bind()
        exit.Event_Bind()
        self.OpenThread(timer, move)

        self.master.next_key = time.time()
        self.master.window.bind("<Key>", self.master.KeyInput)
        self.master.canvas.ActivateControl()

    def OpenThread(self, timer_image, move_image):
        def update(self, img_time, img_move, event_time):
            self.threading = True
            font = FontManager('font/NanumSquareR.ttf', 20)
            font.SetColor(0, 0, 0)
            while self.valid:
                if self.th_kill:
                    break
                passed = int(time.time() - event_time)
                min = passed // 60
                sec = passed % 60
                string = '{0:0>2}:{1:0>2}'.format(min, sec)

                array = font.GetTextImage(string)
                new_image = cv2Tk(array)

                for elem in self.master.canvas.font_image:
                    if elem[0] == img_time:
                        self.master.canvas.itemconfigure(img_time, image=new_image)
                        elem[1], elem[2] = array, new_image
                        self.master.canvas.update()
                        break

                if self.master.manager.history is not None:
                    string = '{}'.format(len(self.master.manager.history))
                    array = font.GetTextImage(string)
                    new_image = cv2Tk(array)

                    for elem in self.master.canvas.font_image:
                        if elem[0] == img_move:
                            self.master.canvas.itemconfigure(img_move, image=new_image)
                            elem[1], elem[2] = array, new_image
                            self.master.canvas.update()
                            break

                time.sleep(0.01)
            self.threading = False

        th = Thread(target=update, args=(self, timer_image, move_image, time.time()), daemon=True)
        th.start()

    def Event_CheckBox(self, event):
        x, y = event.x, event.y
        w = 0

        for elem in self.master.canvas.image:
            if elem[0] == self.checkbox[0]:
                w = elem[1].shape[1]
                break

        click = None

        for elem in self.checkbox:
            coord = self.master.canvas.coords(elem)
            if coord[0] <= x <= coord[0] + w and coord[1] <= y <= coord[1] + w:
                click = elem
                break

        for elem in self.checkbox:
            rgba = image2rgba('./image/default/checkbox_{}.png'.format('on' if elem == click else 'off'), w, w)
            image = cv2Tk(rgba)
            for eleme in self.master.canvas.image:
                if eleme[0] == elem:
                    self.master.canvas.itemconfigure(eleme[0], image=image)
                    eleme[1] = rgba
                    eleme[2] = image
        self.master.canvas.update()
        self.path_find = self.checkbox.index(click)

    def Exit(self):
        self.master.window.unbind("<Key>")
        self.master.canvas.DeactivateControl()

        self.valid = False
        self.using = False

        temp = np.full((self.master.tall, self.master.width, 4), 255).astype('uint8')
        array = MatrixScalar(temp, [0, 0, 0, 0])

        image = self.master.canvas.create_image(array, 0, 0, anchor=NW)
        array = MatrixScalar(temp, [0, 0, 0, 255])

        alpha = 0
        while self.master.valid:
            alpha = min(255, alpha + 10)
            new_ary = MatrixScalar(array, [255, 255, 255, alpha])
            new_img = cv2Tk(new_ary)

            for elem in self.master.canvas.image:
                if elem[0] == image:
                    elem[2] = new_img
                    self.master.canvas.itemconfigure(elem[0], image=new_img)
                    self.master.canvas.update()
                    break

            if alpha == 255:
                break
            time.sleep(0.001)

        super(type(self), self).Exit()

    def Clear(self):
        super(type(self), self).Clear()

        def func(self):
            self.th_kill = True
            while self.threading:
                pass
            self.th_kill = False
            self.ShowPath()

        th = Thread(target=func, args=(self,), daemon=True)
        th.start()

    def ShowPath(self):
        self.using = True

        for i in range(4):
            self.master.canvas.tag_unbind(self.checkbox[i], '<ButtonRelease-1>')

        for elem in self.remove:
            if elem in self.master.canvas.image:
                self.master.canvas.delete(elem[0])
                self.master.canvas.image.remove(elem)
            elif elem in self.master.canvas.font_image:
                self.master.canvas.delete(elem[0])
                self.master.canvas.font_image.remove(elem)
        self.master.canvas.update()

        self.UpdateOffset(-self.offset_x, -self.offset_y, False)

        c_map = self.master.canvas.canvas_map
        timer = time.time()
        if 0 < len(self.map) <= 20 and 0 < len(self.map[0]) <= 20:
            while self.valid:
                passed = min((time.time() - timer) / 0.5, 1.0)
                rgb = [255 - int(255 * passed), 255 - int(34 * passed), 255]
                c_str = RGB_IntArrayToStr(rgb)

                for elem in self.history:
                    x, y = elem

                    if self.map[y][x] != 3:
                        self.master.canvas.itemconfigure(c_map[y][x], fill=c_str)

                self.master.canvas.update()
                if passed == 1.0:
                    break
                time.sleep(0.001)

            timer = time.time()
            while self.valid:
                passed = min((time.time() - timer) / 0.5, 1.0)
                rgb = [0, 221 - int(100 * passed), 255 - int(100 * passed)]
                c_str = RGB_IntArrayToStr(rgb)

                for elem in self.history:
                    x, y = elem
                    if self.map[y][x] != 3:
                        self.master.canvas.itemconfigure(c_map[y][x], fill=c_str)

                self.master.canvas.update()
                if passed == 1.0:
                    break
                time.sleep(0.001)

        path = None
        if self.path_find == 0:
            path = aStar(self.map)
        elif self.path_find == 1:
            path = Dijkstra(self.map)
        elif self.path_find == 2:
            path = DFS(self.map)
        elif self.path_find == 3:
            path = BFS(self.map)

        if path is None:
            return

        for elem in path[0]:
            x, y = elem
            c_x, c_y = x - self.offset_x, y - self.offset_y
            if c_x < 0:
                self.UpdateOffset(-20, 0, False)
                c_x = x - self.offset_x
            elif c_x >= 20:
                self.UpdateOffset(20, 0, False)
                c_x = x - self.offset_x
            if c_y < 0:
                self.UpdateOffset(0, -20, False)
                c_y = y - self.offset_y
            elif c_y >= 20:
                self.UpdateOffset(0, 20, False)
                c_y = y - self.offset_y
            if self.map[y][x] != 3:
                while self.valid:
                    t_color = [0x67, 0x99, 0xdd]
                    color = RGB_StrToIntArray(self.master.canvas.itemcget(c_map[c_y][c_x], 'fill'))

                    for i in range(3):
                        if color[i] < t_color[i]:
                            color[i] = min(t_color[i], color[i] + 3)
                        elif color[i] > t_color[i]:
                            color[i] = max(t_color[i], color[i] - 3)
                    c_str = RGB_IntArrayToStr(color)

                    self.master.canvas.itemconfigure(c_map[c_y][c_x], fill=c_str)
                    self.master.canvas.update()
                    if color == t_color:
                        break

                    time.sleep(0.001)

        x, y = self.master.width * 0.7, self.master.tall - 110

        font = FontManager('font/NanumSquareR.ttf', 16)
        font.SetColor(0, 0, 0)
        array = font.GetTextImage(Translate("#GAME_GameText_Default_TotalMove"))
        y -= array.shape[0]
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        x += array.shape[1]

        string = ['AStar', 'Dijkstra', 'DFS', 'BFS']
        font.SetColor(0x67, 0x99, 0xdd)
        array = font.GetTextImage(Translate("#GAME_" + string[self.path_find]))
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        x += array.shape[1]

        font.SetColor(0, 0, 0)
        array = font.GetTextImage(': ')
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        x += array.shape[1]

        ft = font

        mylen, length = len(self.history), len(path[0])
        if mylen > length:
            yy = y
            array = ft.GetTextImage(Translate("#GAME_GameText_Default_Failure2"))
            y -= array.shape[0] + 20
            self.master.canvas.create_FontImage(array, self.master.width * 0.8 - array.shape[1] / 2, y, anchor=NW)

            array = ft.GetTextImage(Translate("#GAME_GameText_Default_Failure1"))
            y -= array.shape[0] + 5
            self.master.canvas.create_FontImage(array, self.master.width * 0.8 - array.shape[1] / 2, y, anchor=NW)
            y = yy

            ft.SetColor(255, 50, 50)
        else:
            next = ImagedButton(self.master.width * 0.65 + 50, y - 90, 'NextStage')
            next.SetImage(
                TImg('./image/default/next0'), TImg('./image/default/next1'), TImg('./image/default/next2'),
                80, 80)
            next.canvas_hook(self.master.canvas)
            next.Event_Bind()

            if mylen == length:
                ft.SetColor(225, 228, 0)
            else:
                ft = FontManager('font/NanumSquareEB.ttf', 16)
                ft.SetColor(30, 220, 25)

        array = ft.GetTextImage('{}'.format(len(path[0])))
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        x += array.shape[1]

        self.using = False

    def Retry(self):
        def func(self):
            self.th_kill = True
            while self.threading:
                pass
            self.th_kill = False

            self.valid = False
            while self.using is True:
                pass
            self.valid = True

            self.Outro()
        th = Thread(target=func, args=(self,), daemon=True)
        th.start()

    def Outro(self):
        temp = np.full((self.master.tall, self.master.width, 4), 255).astype('uint8')
        array = MatrixScalar(temp, [0, 0, 0, 0])

        self.master.canvas.create_image(array, 0, 0, anchor=NW)
        elem = self.master.canvas.image[-1]
        array = MatrixScalar(temp, [0, 0, 0, 255])

        alpha = 0
        while self.valid:
            alpha = min(255, alpha + 10)
            new_ary = MatrixScalar(array, [255, 255, 255, alpha])
            new_img = cv2Tk(new_ary)

            self.master.canvas.itemconfigure(elem[0], image=new_img)
            elem[2] = new_img
            self.master.canvas.update()

            if alpha == 255:
                break
        self.Load()

    def UpdateOffset(self, x_plus, y_plus, event=True):
        if (x_plus, y_plus) == (0, 0):
            return
        self.offset_y = max(0, min(len(self.map) - 20, self.offset_y + y_plus))
        self.offset_x = max(0, min(len(self.map[0]) - 20, self.offset_x + x_plus))
        self.master.canvas.offset_coord = (self.offset_x, self.offset_y)

        y_len = min(20, len(self.map))
        x_len = min(20, len(self.map[0]))

        self.master.canvas.UpdateMap(self.map, (self.offset_x, self.offset_y), self.master.manager.position)

        del_x = (self.ran_x + ((self.w + 1) * x_len - 48) / 2,
                 self.ran_x + ((self.w + 1) * x_len - 48) / 2,
                 self.ran_x - 48,
                 self.ran_x + ((self.w + 1) * x_len))
        del_y = (self.ran_y - 48,
                 self.ran_y + ((self.w + 1) * y_len),
                 self.ran_y + ((self.w + 1) * y_len - 48) / 2,
                 self.ran_y + ((self.w + 1) * y_len - 48) / 2)

        rm = []
        for elem in self.pointer:
            for image in self.master.canvas.image:
                if image[0] == elem.GetID():
                    rm.append(image)
                    break

        for elem in rm:
            self.master.canvas.delete(elem[0])
            self.master.canvas.image.remove(elem)

        self.pointer.clear()
        if self.offset_y > 0:
            button = ImagedButton(del_x[0], del_y[0], 'MoveScreen 0')
            button.SetImage('./image/default/pointer00.png',
                            './image/default/pointer01.png',
                            './image/default/pointer02.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if len(self.map) - self.offset_y > 20:
            button = ImagedButton(del_x[1], del_y[1], 'MoveScreen 1')
            button.SetImage('./image/default/pointer10.png',
                            './image/default/pointer11.png',
                            './image/default/pointer12.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if self.offset_x > 0:
            button = ImagedButton(del_x[2], del_y[2], 'MoveScreen 2')
            button.SetImage('./image/default/pointer20.png',
                            './image/default/pointer21.png',
                            './image/default/pointer22.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if len(self.map[0]) - self.offset_x > 20:
            button = ImagedButton(del_x[3], del_y[3], 'MoveScreen 3')
            button.SetImage('./image/default/pointer30.png',
                            './image/default/pointer31.png',
                            './image/default/pointer32.png',
                            48, 48)
            button.canvas_hook(self.master.canvas)
            self.pointer.append(button)

        if event:
            for elem in self.pointer:
                elem.Event_Bind()

    def MakeCustomMap(self):
        font = FontManager('font/NanumSquareEB.ttf', 25)
        font.SetColor(0, 0, 0)

        x = self.master.width * 0.5
        y = self.master.tall * 0.1

        self.remove.clear()

        array = font.GetTextImage(Translate("#GAME_GameText_Default_Title_AllClear"))
        self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)
        self.remove.append(self.master.canvas.font_image[-1])
        y += array.shape[0] + 15

        font = FontManager('font/NanumSquareR.ttf', 20)
        font.SetColor(0, 0, 0)

        array = font.GetTextImage(Translate("#GAME_GameText_Default_Announcement1"))
        self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)
        self.remove.append(self.master.canvas.font_image[-1])
        y += array.shape[0] + 5

        text = Translate("#GAME_GameText_Default_Announcement2")
        x -= font.GetWidth(text) / 2
        font_tall = font.GetHeight(text)

        array = font.GetTextImage(Translate("#GAME_GameText_Default_Announcement3_1"))
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        self.remove.append(self.master.canvas.font_image[-1])
        x += array.shape[1]

        font.SetColor(25, 255, 25)
        array = font.GetTextImage(Translate("#GAME_GameText_Default_Announcement3_2"))
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        self.remove.append(self.master.canvas.font_image[-1])
        x += array.shape[1]

        font.SetColor(0, 0, 0)
        array = font.GetTextImage(Translate("#GAME_GameText_Default_Announcement3_3"))
        self.master.canvas.create_FontImage(array, x, y, anchor=NW)
        self.remove.append(self.master.canvas.font_image[-1])
        y += font_tall + 20

        font = FontManager('font/NanumSquareEB.ttf', 20)
        font.SetColor(0, 0, 0)

        x = self.master.width * 0.375

        array = font.GetTextImage(Translate("#GAME_GameText_Default_Width"))
        self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)

        self.entry.clear()

        entry = Entry(self.master.window)
        entry.place(relx=0.275, relwidth=0.2, y=y + array.shape[0] + 5, height=30)
        self.entry.append(entry)

        x = self.master.width * 0.625

        array = font.GetTextImage(Translate("#GAME_GameText_Default_Height"))
        self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)

        entry = Entry(self.master.window)
        entry.place(relx=0.525, relwidth=0.2, y=y + array.shape[0] + 5, height=30)
        self.entry.append(entry)

        x = self.master.width * 0.5
        y += array.shape[0] + 60

        button = ImagedButton(x - 40, y, 'MakeMap')
        button.SetImage(
            TImg('./image/default/make0'), TImg('./image/default/make1'), TImg('./image/default/make2'),
            80, 80)
        button.canvas_hook(self.master.canvas)
        button.Event_Bind()

        self.master.canvas.update()
        self.master.window.update()

    def MakeMap(self):
        if len(self.entry) != 2:
            return

        err = False
        try:
            wide = int(self.entry[0].get())
            tall = int(self.entry[1].get())

            if not 10 <= wide <= 200 or not 10 <= tall <= 200:
                err = True
            else:
                self.map = Make_Map(wide, tall)
                self.Load()
        except ValueError:
            err = True

        if err:
            for elem in self.remove:
                if not elem in self.master.canvas.font_image:
                    continue
                self.master.canvas.delete(elem[0])
                self.master.canvas.font_image.remove(elem)

            self.remove.clear()

            x = self.master.width * 0.5
            y = self.master.tall * 0.1

            font = FontManager('font/NanumSquareEB.ttf', 25)
            font.SetColor(0, 0, 0)

            array = font.GetTextImage(Translate("#GAME_GameText_Default_Title_Error"))
            self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)
            self.remove.append(self.master.canvas.font_image[-1])
            y += array.shape[0] + 15

            font = FontManager('font/NanumSquareR.ttf', 20)
            font.SetColor(255, 30, 30)

            array = font.GetTextImage(
                Translate("#GAME_GameText_Default_Text_Error1").format(self.entry[0].get(), self.entry[1].get()))
            self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)
            self.remove.append(self.master.canvas.font_image[-1])
            y += array.shape[0] + 5

            font.SetColor(0, 0, 0)

            array = font.GetTextImage(Translate("#GAME_GameText_Default_Text_Error2"))
            self.master.canvas.create_FontImage(array, x - array.shape[1] / 2, y, anchor=NW)
            self.remove.append(self.master.canvas.font_image[-1])



map_list = [
    [  # 0
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    [  # 1
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    [  # 2
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    [  # 3
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    [  # 4
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    [  # 5
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],

    None
]

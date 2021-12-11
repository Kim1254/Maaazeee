from tkinter.font import Font
from threading import Thread

from API.Stage import *
from API.PathFind import *
from API.TextMapping import *

from GUI.GameCanvas import *
from GUI.ColoredLabel import *
from GUI.Util import *


class Tutorial(Stage):
    def __init__(self, master):
        super(Tutorial, self).__init__(master, None)
        self.map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.identifier = False

    def Load(self):
        self.master.canvas['bg'] = '#000000'

        self.w = self.master.width // 20

        self.ran_x = self.master.width - 50 - self.w * len(self.map[0])
        self.ran_y = -50 - self.w * len(self.map)
        self.border_x = self.ran_x
        self.border_y = 90

        super(Tutorial, self).Load()

        self.master.canvas.create_line(int(self.master.width * 0.05), 90, int(self.master.width * 0.35), 90,
                                       fill='#000000', save=True)

        self.identifier = False
        font = Font(family='Tahoma', size=32)
        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Welcome1"),
                      bg='#000000', bd='0', relief="solid", font=font)
        label.place(relx=0.025, relwidth=0.35, y=45, height=40)
        self.master.lbl_list.append(label)

        font = Font(family='Tahoma', size=12)

        label = Label(self.master.window,
                      text=Translate("#GAME_GameText_Tutorial_Welcome2"),
                      bg='#000000', bd='0', relief="solid", font=font)
        label.place(relx=0.025, relwidth=0.35, y=100)
        self.master.lbl_list.append(label)

        self.master.canvas.image.clear()
        image = self.master.canvas.create_image('./image/tutorial/keycursor.png', self.master.width * 0.05, 196, 200, 92, anchor=W)
        rgba = self.master.canvas.image[0][1]

        new_rgba = MatrixScalar(rgba, [255, 255, 255, 0])
        new_img = cv2Tk(new_rgba)
        self.master.canvas.image[0][2] = new_img
        self.master.canvas.itemconfigure(image, image=new_img)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Destination"), bg='#000000', bd='0',
                      relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=250)
        self.master.lbl_list.append(label)

        label = ColoredLabel(self.master.window, text=Translate("#GAME_GameText_Tutorial_Button_Skip"), font=font)
        label.place(relx=0.6, relwidth=0.3, y=self.master.tall - 50)
        label.configure(bg='#000000')
        label.Event_Unbind()
        self.master.lbl_list.append(label)

        self.ImageFadeIn(image, rgba)

        label.Event_Bind()
        label.bind("<ButtonRelease-1>", self.Event_Next)

        label = Label(self.master.window,
                      text=Translate("#GAME_GameText_Tutorial_Loading"), bg='#ffffff', fg='#000000', bd='1',
                      relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=290)
        self.master.lbl_list.append(label)

        self.Move_Map()

        text = Translate("#GAME_GameText_Tutorial_Complete")
        self.UpdateText(self.master.window, label, text)
        self.identifier = True

        self.master.next_key = time.time()
        self.master.window.bind("<Key>", self.master.KeyInput)
        self.master.canvas.ActivateControl()

    def ImageFadeIn(self, image, default_rgba):
        while self.valid:
            rgb = RGB_StrToIntArray(self.master.canvas['bg'])

            for i in range(0, 3):
                if rgb[i] < 255:
                    rgb[i] = min(255, rgb[i] + 8)

            new_rgba = MatrixScalar(default_rgba, [255, 255, 255, rgb[0]])
            new_img = cv2Tk(new_rgba)
            self.master.canvas.image[0][2] = new_img
            self.master.canvas.itemconfigure(image, image=new_img)

            color = RGB_IntArrayToStr(rgb)

            self.master.canvas['bg'] = color
            for label in self.master.lbl_list:
                label.configure(bg=color)
            self.master.canvas.update()

            if rgb == [255, 255, 255]:
                break

            time.sleep(0.001)

    def Move_Map(self):
        length = len(self.master.canvas.rect)
        counter = 0
        breaker = False

        while self.valid and breaker is False:
            for i in range(0, len(self.master.canvas.rect)):
                if 1 + counter // 10 < length - i:
                    continue

                s = self.master.canvas.rect[i]

                sqr_coord = self.master.canvas.coords(s)
                vertex_coord = [sqr_coord[0], sqr_coord[1], sqr_coord[2] - sqr_coord[0], sqr_coord[5] - sqr_coord[1]]
                destination = 91 + (self.w + 1) * (i // len(self.map[0]))
                if vertex_coord[1] == destination:
                    if i == 0:
                        breaker = True
                        break
                    else:
                        continue
                vertex_coord[1] = min(destination, vertex_coord[1] + 20)

                self.master.canvas.coord_square(s, vertex_coord)
                self.master.canvas.update()
            counter = min(counter + 2, length * 10)
            time.sleep(0.01)

    def UpdateText(self, window, label, new_text):
        while self.valid:
            rgb = RGB_StrToIntArray(label['fg'])

            for i in range(0, 3):
                rgb[i] = min(rgb[i] + 1, 255)

            if rgb == [255, 255, 255]:
                break

            label.configure(fg=RGB_IntArrayToStr(rgb))
            window.update()

        label.configure(text=new_text)

        while self.valid:
            rgb = RGB_StrToIntArray(label['fg'])

            for i in range(0, 3):
                rgb[i] = max(rgb[i] - 1, 0)

            if rgb == [0, 0, 0]:
                break

            label.configure(fg=RGB_IntArrayToStr(rgb))
            window.update()

    def CannotMove(self):
        super(Tutorial, self).CannotMove()
        for label in self.master.lbl_list:
            if str(label.cget('bd')) == '1':
                label['text'] = Translate("#GAME_GameText_Tutorial_Unable_to_go")
                label['fg'] = '#ff0000'
                self.master.window.update()

                def Reset(self, label, event_time):
                    while self.valid and self.identifier is True:
                        if time.time() - event_time >= 2.0:
                            break
                    if self.identifier is False:
                        return

                    label['text'] = Translate("#GAME_GameText_Tutorial_Text_Cheerup")
                    label['fg'] = '#000000'
                    self.master.window.update()

                th = Thread(target=Reset, args=(self, label, time.time()), daemon=True)
                th.start()

    def Clear(self):
        super(Tutorial, self).Clear()
        self.__Tutorial_End()

    def __Tutorial_End(self):
        self.master.window.unbind("<Key>")
        self.master.canvas.DeactivateControl()

        self.identifier = False
        self.master.Fadeout(None, [255, 255, 255])
        self.master.canvas.destroy()

        self.master.canvas = GameCanvas(self.master, width=self.master.width, height=self.master.tall, bg='black', relief='solid')
        self.master.canvas['bg'] = '#ffffff'

        self.ran_y = 90

        super(Tutorial, self).Load()

        c_map = self.master.canvas.canvas_map
        for line in c_map:
            for row in line:
                self.master.canvas.itemconfigure(row, fill='#ffffff', outline='#ffffff')

        fade_color = 255

        font = Font(family='Tahoma', size=20)
        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Clear"),
                      fg='#ffffff', bg='#ffffff', bd='1', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=45, height=40)
        self.master.lbl_list.append(label)

        font = Font(family='Tahoma', size=12)
        color1_label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Desc1"),
                             fg='#ffffff', bg='#ffffff', bd='0', relief="solid", font=font)
        color1_label.place(relx=0.05, relwidth=0.3, y=125, height=20)
        self.master.lbl_list.append(color1_label)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Desc2"),
                      fg='#ffffff', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=145, height=20)
        self.master.lbl_list.append(label)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Desc3"),
                      fg='#ffffff', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=190, height=20)
        self.master.lbl_list.append(label)

        color2_label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_Desc4"),
                             fg='#ffffff', bg='#ffffff', bd='0', relief="solid", font=font)
        color2_label.place(relx=0.05, relwidth=0.3, y=210, height=20)
        self.master.lbl_list.append(color2_label)

        a_star = ColoredLabel(self.master.window, text=Translate("#GAME_AStar"), font=font)
        a_star.place(relx=0.05, relwidth=0.15, y=240, height=25)
        a_star.configure(fg='#ffffff', bg='#ffffff')
        a_star.Event_Unbind()
        self.master.lbl_list.append(a_star)

        dijkstra = ColoredLabel(self.master.window, text=Translate("#GAME_Dijkstra"), font=font)
        dijkstra.place(relx=0.21, relwidth=0.15, y=240, height=25)
        dijkstra.configure(fg='#ffffff', bg='#ffffff')
        dijkstra.Event_Unbind()
        self.master.lbl_list.append(dijkstra)

        dfs = ColoredLabel(self.master.window, text=Translate("#GAME_DFS"), font=font)
        dfs.place(relx=0.05, relwidth=0.15, y=270, height=25)
        dfs.configure(fg='#ffffff', bg='#ffffff')
        dfs.Event_Unbind()
        self.master.lbl_list.append(dfs)

        bfs = ColoredLabel(self.master.window, text=Translate("#GAME_BFS"), font=font)
        bfs.place(relx=0.21, relwidth=0.15, y=270, height=25)
        bfs.configure(fg='#ffffff', bg='#ffffff')
        bfs.Event_Unbind()
        self.master.lbl_list.append(bfs)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_TryPathFind"),
                      fg='#000000', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=self.master.tall - 60, height=30)
        self.master.lbl_list.append(label)

        exit = ColoredLabel(self.master.window, text=Translate("#GAME_GameText_Tutorial_Terminate"), font=font)
        exit.place(relx=0.6, relwidth=0.3, y=self.master.tall - 50)
        exit.configure(fg='#ffffff', bg='#ffffff')
        exit.Event_Unbind()
        self.master.lbl_list.append(exit)

        self.master.window.update()

        while self.valid:
            fade_color = max(0, fade_color - 10)
            for y in range(len(c_map)):
                for x in range(len(c_map[y])):
                    color = [255, 255, 255]
                    if self.map[y][x] == 1:
                        color = [0x80, 0x80, 0x80]
                    elif self.map[y][x] == 2:
                        color = [0x10, 0xdd, 0x10]
                    elif self.map[y][x] == 3:
                        color = [0xdd, 0x10, 0x10]

                    for i in range(len(color)):
                        color[i] = min(255, fade_color + color[i])

                    color_string = RGB_IntArrayToStr(color)
                    border_string = RGB_IntArrayToStr([fade_color, fade_color, fade_color])
                    self.master.canvas.itemconfigure(c_map[y][x], fill=color_string, outline=border_string)

            for label in self.master.lbl_list:
                color = [0, 0, 0]
                if label == color1_label:
                    color = [0x00, 0xaa, 0xcc]
                elif label == color2_label:
                    color = [0xcc, 0xaa, 0x00]

                for i in range(len(color)):
                    color[i] = min(255, fade_color + color[i])

                color_string = RGB_IntArrayToStr(color)
                label.configure(fg=color_string)

            self.master.window.update()
            self.master.canvas.update()
            if fade_color == 0:
                break

            time.sleep(0.001)

        for i in range(3):
            color = [255, 255, 255]

            timer, passed = time.time(), 0.0
            while passed < 1.0:
                passed = min((time.time() - timer) / 0.5, 1.0)
                color[0] = 255 - int(255 * passed)
                color[1] = 255 - int(34 * passed)
                c_str = RGB_IntArrayToStr(color)

                for elem in self.history:
                    if self.map[elem[1]][elem[0]] == 0:
                        self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)
                self.master.canvas.update()
                time.sleep(0.01)

            time.sleep(0.2)

            if i != 2:
                timer, passed = time.time(), 0.0
                while passed < 1.0:
                    passed = min((time.time() - timer) / 0.5, 1.0)
                    color[0] = int(255 * passed)
                    color[1] = 0xdd + int(0x22 * passed)
                    c_str = RGB_IntArrayToStr(color)

                    for elem in self.history:
                        if self.map[elem[1]][elem[0]] == 0:
                            self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)
                    self.master.canvas.update()
                    time.sleep(0.01)

        a_star.Event_Bind()
        dijkstra.Event_Bind()
        dfs.Event_Bind()
        bfs.Event_Bind()
        exit.Event_Bind()

        a_star.bind("<ButtonRelease-1>", self.FindPath_AStar)
        dijkstra.bind("<ButtonRelease-1>", self.FindPath_Dijkstra)
        dfs.bind("<ButtonRelease-1>", self.FindPath_DFS)
        bfs.bind("<ButtonRelease-1>", self.FindPath_BFS)
        exit.bind("<ButtonRelease-1>", self.Event_Next)

        self.identifier = True

    def Event_Next(self, event):
        self.master.window.unbind("<Key>")
        self.master.canvas.DeactivateControl()

        def func(self):
            self.valid = False
            while self.identifier is False:
                pass
            self.valid = True
            self.Next()
        th = Thread(target=func, args=(self,), daemon=True)
        th.start()

    def FindPath_AStar(self, event):
        path = aStar(self.map)
        self.ShowPath(path)

    def FindPath_DFS(self, event):
        path = DFS(self.map)
        self.ShowPath(path)

    def FindPath_BFS(self, event):
        path = BFS(self.map)
        self.ShowPath(path)

    def FindPath_Dijkstra(self, event):
        path = Dijkstra(self.map)
        self.ShowPath(path)

    def ShowPath(self, path):
        if self.identifier is False:
            return

        self.identifier = False
        removal = []
        for label in self.master.lbl_list:
            if int(str(label['bd'])) == 0:
                removal.append(label)

        for label in removal:
            self.master.lbl_list.remove(label)
            label.destroy()

        font = Font(family='Tahoma', size=12)
        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_PathFind_Desc1"),
                      fg='#ffbb00', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=110, height=20)
        self.master.lbl_list.append(label)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_PathFind_Desc2"),
                      fg='#000000', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=130, height=20)
        self.master.lbl_list.append(label)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_PathFind_Desc3"),
                      fg='#6799ff', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=165, height=20)
        self.master.lbl_list.append(label)

        label = Label(self.master.window, text=Translate("#GAME_GameText_Tutorial_PathFind_Desc4"),
                      fg='#000000', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=185, height=40)
        self.master.lbl_list.append(label)

        label = Label(self.master.window,
                      text=Translate("#GAME_GameText_Tutorial_PathFind_MoveCount").format(len(path[0])),
                      fg='#000000', bg='#ffffff', bd='0', relief="solid", font=font)
        label.place(relx=0.05, relwidth=0.3, y=self.master.tall - 100, height=30)
        self.master.lbl_list.append(label)

        self.master.window.update()

        c_map = self.master.canvas.canvas_map

        while self.valid:
            breaker = True
            for y in range(len(c_map)):
                for x in range(len(c_map[y])):
                    if self.map[y][x] == 0:
                        c_str = self.master.canvas.itemcget(c_map[y][x], 'fill')

                        if c_str != '#ffffff':
                            breaker = False

                        color = RGB_StrToIntArray(c_str)
                        for i in range(3):
                            color[i] = min(255, color[i] + 5)
                        c_str = RGB_IntArrayToStr(color)

                        self.master.canvas.itemconfigure(c_map[y][x], fill=c_str)

            self.master.canvas.update()

            if breaker:
                break

            time.sleep(0.01)

        for i in range(2):
            color = [255, 255, 255]
            orange = [0xff, 0xbb, 0x00]
            purple = [0x67, 0x99, 0xff]

            timer, passed = time.time(), 0.0
            while self.valid and passed < 1.0:
                passed = min((time.time() - timer) / 0.5, 1.0)
                for j in range(3):
                    color[j] = min(255, int(255 * (1.0 - passed)) + orange[j])
                c_str = RGB_IntArrayToStr(color)

                for elem in path[1]:
                    if self.map[elem[1]][elem[0]] == 0:
                        self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)

                for j in range(3):
                    color[j] = min(255, int(255 * (1.0 - passed)) + purple[j])
                c_str = RGB_IntArrayToStr(color)

                for elem in path[0]:
                    if self.map[elem[1]][elem[0]] == 0:
                        self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)
                self.master.canvas.update()
                time.sleep(0.01)

            time.sleep(0.2)

            if i != 1:
                timer, passed = time.time(), 0.0
                while self.valid and passed < 1.0:
                    passed = min((time.time() - timer) / 0.5, 1.0)
                    for j in range(3):
                        color[j] = min(255, int(255 * passed) + orange[j])
                    c_str = RGB_IntArrayToStr(color)

                    for elem in path[1]:
                        if self.map[elem[1]][elem[0]] == 0:
                            self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)

                    for j in range(3):
                        color[j] = min(255, int(255 * passed) + purple[j])
                    c_str = RGB_IntArrayToStr(color)

                    for elem in path[0]:
                        if self.map[elem[1]][elem[0]] == 0:
                            self.master.canvas.itemconfigure(c_map[elem[1]][elem[0]], fill=c_str)
                    self.master.canvas.update()
                    time.sleep(0.01)
        self.identifier = True

    def Next(self):
        self.master.window.unbind("<Key>")
        self.master.canvas.DeactivateControl()
        self.master.Fadeout(None, [255, 255, 255])
        self.master.canvas.delete(ALL)

        super(type(self), self).Next()

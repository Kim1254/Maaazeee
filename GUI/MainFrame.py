from random import *

from tkinter.font import *

from GUI.ColoredLabel import ColoredLabel
from GUI.GameCanvas import *
from GUI.FontLabel import *

from API.GameManager import *
from API.SoundManager import *
from API.PathFind import *
from API.TextMapping import *
from API.FontManager import *

import API.TextMapping as tm

from STAGE.Tutorial import Tutorial as TutorialStage
from STAGE.Default import Default as DefaultStage


class MainWindow:
    def __init__(self, width, tall):
        super(MainWindow, self).__init__()

        self.page = Page.Main
        self.valid = True

        self.manager = GameManager()
        self.sound = SoundManager()

        self.window = Tk()

        self.window.protocol("WM_DELETE_WINDOW", self.Exit)

        self.width = width
        self.tall = tall

        self.sw = self.window.winfo_screenwidth()
        self.st = self.window.winfo_screenheight()

        self.title_text = ''

        self.lbl_list = []

        self.random_x = 0
        self.random_y = 0

        self.next_key = 0
        self.kill_thread = False

        resolution = '{0}x{1}+{2}+{3}'.format(self.width, self.tall, (self.sw - self.width) // 2,
                                              (self.st - self.tall) // 2)
        self.window.geometry(resolution)
        self.window.resizable(False, False)

        self.canvas = None

        self.stage = None
        self.tutorial_used = False
        self.stage_level = -1

        self.master_volume = 0.5
        self.volume_check = False

        self.MainScreen()
        self.window.mainloop()

    def Command(self, caller, cmd, **kw):
        if cmd == 'Move':
            dir = kw.get('direction')
            if dir is None or dir < 0 or dir > 3:
                return

            if self.manager.CanMove()[dir] is False:
                self.stage.CannotMove()
                return

            x, y = 0, 0
            if dir == 0:
                y = -1
            elif dir == 1:
                y = 1
            elif dir == 2:
                x = -1
            elif dir == 3:
                x = 1

            self.manager.Move(x, y)

            pos = self.manager.position
            off_x, off_y = 0, 0
            if type(self.stage) is DefaultStage:
                off_x, off_y = self.stage.offset_x, self.stage.offset_y
                c_x, c_y = pos[0] - off_x, pos[1] - off_y

                if c_x < 0:
                    self.stage.UpdateOffset(-20, 0)
                elif c_x >= 20:
                    self.stage.UpdateOffset(20, 0)
                if c_y < 0:
                    self.stage.UpdateOffset(0, -20)
                elif c_y >= 20:
                    self.stage.UpdateOffset(0, 20)

                off_x, off_y = self.stage.offset_x, self.stage.offset_y

            self.canvas.UpdateCurrent(pos[0], pos[1], off_x, off_y,
                                      True if kw.get('input') == 'mouse' else False)

            if self.manager.Check() == 3:
                self.Command(self, 'Clear')
            else:
                self.sound.Play('./sound/move.mp3', ChannelList.Effect)
        elif cmd == 'Clear':
            self.sound.Play('./sound/clear.mp3', ChannelList.Effect)
            self.stage.Clear()
        elif cmd == 'NextStage':
            self.stage_level = min(6, self.stage_level + 1)
            self.stage = DefaultStage(self)
            self.stage.SetMap(self.stage_level)
            self.stage.Load()
        elif cmd == 'MainScreen':
            self.MainScreen()
        elif cmd == 'Stage_Exit':
            self.stage.Exit()
        elif cmd == 'Retry':
            if self.stage.valid:
                self.stage.Retry()
        elif cmd[:10] == 'MoveScreen':
            if len(cmd) != 12:
                return
            if type(self.stage) is not DefaultStage:
                return

            slot = int(cmd[11:])
            dist_x = (0, 0, -20, 20)
            dist_y = (-20, 20, 0, 0)
            self.stage.UpdateOffset(dist_x[slot], dist_y[slot])
        elif cmd == 'MakeMap':
            if type(self.stage) is not DefaultStage:
                return
            self.stage.MakeMap()


        #elif expr:

    def Fadeout(self, target=None, color=None):
        if target is None:
            target = [self.canvas.line, self.lbl_list, self.canvas.rect, self.canvas.image]
        if color is None:
            color = [0, 0, 0]

        if self.lbl_list in target:
            for label in self.lbl_list:
                if type(label) is ColoredLabel:
                    label.Event_Unbind()

        timer = time.time()
        while self.valid:
            breaker = True
            for i in target:
                if len(i) != 0:
                    breaker = False
                    break

            if breaker:
                break

            if self.canvas.line in target:
                rm_list = []
                for line in self.canvas.line:
                    rgb = RGB_StrToIntArray(self.canvas.itemcget(line, 'fill'))

                    for i in range(0, 3):
                        if rgb[i] > color[i]:
                            rgb[i] = max(color[i], rgb[i] - 10)
                        elif rgb[i] < color[i]:
                            rgb[i] = min(color[i], rgb[i] + 10)

                    if rgb == color:
                        self.canvas.delete(line)
                        rm_list.append(line)
                    else:
                        self.canvas.itemconfig(line, fill=RGB_IntArrayToStr(rgb))
                for elem in rm_list:
                    self.canvas.line.remove(elem)

            if self.lbl_list in target:
                rm_list = []
                for label in self.lbl_list:
                    rgb = RGB_StrToIntArray(label['bg'])

                    for i in range(0, 3):
                        if rgb[i] > color[i]:
                            rgb[i] = max(color[i], rgb[i] - 10)
                        elif rgb[i] < color[i]:
                            rgb[i] = min(color[i], rgb[i] + 10)

                    if rgb == color:
                        label.destroy()
                        rm_list.append(label)
                    else:
                        label['bg'] = RGB_IntArrayToStr(rgb)
                for elem in rm_list:
                    self.lbl_list.remove(elem)

            if self.canvas.rect in target:
                rm_list = []
                for s in self.canvas.rect:
                    rgb = RGB_StrToIntArray(self.canvas.itemcget(s, 'fill'))

                    for i in range(0, 3):
                        if rgb[i] > color[i]:
                            rgb[i] = max(color[i], rgb[i] - 10)
                        elif rgb[i] < color[i]:
                            rgb[i] = min(color[i], rgb[i] + 10)

                    if rgb == color:
                        self.canvas.delete(s)
                        rm_list.append(s)
                    else:
                        self.canvas.itemconfig(s, fill=RGB_IntArrayToStr(rgb))

                for elem in rm_list:
                    self.canvas.rect.remove(elem)

            if self.canvas.image in target:
                passed = min((time.time() - timer) / 0.5, 1.0)
                if passed < 1.0:
                    alpha = int(255 * (1.0 - passed))
                    for img in self.canvas.image:
                        new_rgba = MatrixScalar(img[1], [255, 255, 255, alpha])
                        new_img = cv2Tk(new_rgba)
                        self.canvas.itemconfigure(img[0], image=new_img)
                        img[2] = new_img
                else:
                    self.canvas.remove_image()
                    target.remove(self.canvas.image)

            self.canvas.update()
            self.window.update()
            time.sleep(0.001)

    def KeyInput(self, event):
        if time.time() - self.next_key < 0.2:
            return

        direction = -1
        if event.keysym == 'Up':
            direction = 0
        elif event.keysym == 'Down':
            direction = 1
        elif event.keysym == 'Left':
            direction = 2
        elif event.keysym == 'Right':
            direction = 3

        self.Command(None, 'Move', direction=direction)
        self.next_key = time.time()

    def Tutorial(self, event):
        self.page = Page.Start
        #self.sound.Fadeout(ChannelList.Background, 0)
        self.sound.Volume(ChannelList.Background, self.master_volume * 0.2)

        self.Fadeout()
        self.canvas.delete(ALL)

        if self.tutorial_used is False:
            self.stage = TutorialStage(self)
            self.tutorial_used = True
        else:
            self.stage = DefaultStage(self)
            self.stage.SetMap(self.stage_level)
        self.stage.Load()

    def OptionScreen(self, event):
        self.Fadeout([self.lbl_list])
        w, t = int(self.width * 0.8), int(self.tall * 0.8)

        label = Label(self.window, bg='#ffffff', relief="solid")
        label.place(relx=0.15, rely=0.1, relwidth=0.7, relheight=0.7)
        self.lbl_list.append(label)

        label = FontLabel(self.window, bg='#ffffff', relief="solid")
        label.place(relx=0.35, rely=0.15, relwidth=0.3, height=30)
        label.SetFont("font/NanumSquareEB.ttf", 20)
        label.SetText(Translate("#GAME_OptionText_Language"))
        self.lbl_list.append(label)

        label = FontLabel(self.window, bg='#ffffff', relief="solid")
        label.place(relx=0.325, rely=0.3, relwidth=0.15, height=30)
        label.SetFont("font/NanumSquareR.ttf", 20)
        if tm.game_language == translation_korean:
            label.SetColor(0, 200, 0)
        label.SetText(Translate("#GAME_OptionText_Korean"))
        label.bind("<Enter>", self.Event_EnterLanguage)
        label.bind("<Leave>", self.Event_LeaveLanguage)
        label.bind("<ButtonRelease-1>", self.Event_SetLanguage)
        self.lbl_list.append(label)

        label = FontLabel(self.window, bg='#ffffff', relief="solid")
        label.place(relx=0.525, rely=0.3, relwidth=0.15, height=30)
        label.SetFont("font/NanumSquareR.ttf", 20)
        if tm.game_language == translation_english:
            label.SetColor(0, 200, 0)
        label.SetText(Translate("#GAME_OptionText_English"))
        label.bind("<Enter>", self.Event_EnterLanguage)
        label.bind("<Leave>", self.Event_LeaveLanguage)
        label.bind("<ButtonRelease-1>", self.Event_SetLanguage)
        self.lbl_list.append(label)

        label = FontLabel(self.window, bg='#ffffff', bd=0, relief="solid")
        label.place(relx=0.2, rely=0.42, relwidth=0.6, height=30)
        label.SetFont("font/NanumSquareEB.ttf", 14)
        label.SetText(Translate("#GAME_OptionText_LanguageAnnouncement"))
        label.bind("<ButtonRelease-1>", self.Event_SetLanguage)
        self.lbl_list.append(label)

        label = FontLabel(self.window, bg='#ffffff', relief="solid")
        label.place(relx=0.35, rely=0.5, relwidth=0.3, height=30)
        label.SetFont("font/NanumSquareEB.ttf", 20)
        label.SetText(Translate("#GAME_OptionText_Volume"))
        self.lbl_list.append(label)

        label = Label(self.window, bg='#000000', bd=0, relief="solid")
        label.place(relx=0.35, rely=0.675, relwidth=0.3, height=5)
        self.lbl_list.append(label)

        label = Label(self.window, bg='#ffffff', bd=2, relief="solid")
        label.place(x=self.width * 0.35 + self.width * 0.3 * self.master_volume,
                    y=self.tall * 0.675 - 5, width=13, height=13)
        label.bind("<Button-1>", self.Event_VolumeActive)
        label.bind("<ButtonRelease-1>", self.Event_VolumeDeactive)
        label.bind('<Motion>', self.Event_VolumeCheck)
        self.lbl_list.append(label)

        font = Font(family='Tahoma', size=12)
        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Resume"), font=font)
        label.place(relx=0.5, rely=0.85, relwidth=0.3, height=30)
        label.bind("<ButtonRelease-1>", self.Resume)
        self.lbl_list.append(label)

    def Event_EnterLanguage(self, event):
        color = event.widget.font.GetColor()
        if color == '#00c800':
            return

        event.widget.SetColor(200, 0, 0)
        event.widget.SetText(event.widget.text)

    def Event_LeaveLanguage(self, event):
        color = event.widget.font.GetColor()
        if color == '#00c800':
            return

        event.widget.SetColor(0, 0, 0)
        event.widget.SetText(event.widget.text)

    def Event_SetLanguage(self, event):
        color = event.widget.font.GetColor()
        if color == '#00c800':
            return

        if event.widget.text == Translate("#GAME_OptionText_Korean"):
            tm.game_language = translation_korean
        else:
            tm.game_language = translation_english

        for label in self.lbl_list:
            if type(label) is not FontLabel:
                continue
            if label.font.GetColor() == '#00c800':
                label.SetColor(0, 0, 0)
                label.SetText(label.text)
                break

        event.widget.SetColor(0, 200, 0)
        event.widget.SetText(event.widget.text)


    def Event_VolumeActive(self, event):
        event.widget['bg'] = '#ff0000'
        self.volume_check = True

    def Event_VolumeDeactive(self, event):
        event.widget['bg'] = '#ffffff'
        self.volume_check = False

    def Event_VolumeCheck(self, event):
        if self.volume_check is False:
            return

        adj = self.width * 0.3 * self.master_volume
        x = event.x + adj
        x = max(0, min(self.width * 0.3, x))

        self.master_volume = x / (self.width * 0.3)

        self.sound.Volume(ChannelList.Background, self.master_volume * 0.3)
        self.sound.Volume(ChannelList.Effect, self.master_volume)
        event.widget.place(x=self.width * 0.35 + self.width * 0.3 * self.master_volume)

    def AuthorScreen(self, event):
        self.Fadeout([self.lbl_list])

        font = Font(family='Tahoma', size=12)
        label = Label(self.window, text=Translate("#GAME_CreatorList_Context"),
                      bg='#ffffff', relief="solid", font=font, justify=LEFT, anchor=NW)
        label.place(relx=0.15, rely=0.1, relwidth=0.7, relheight=0.7)
        self.lbl_list.append(label)

        font = Font(family='Tahoma', size=16)
        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Resume"), font=font)
        label.place(relx=0.5, rely=0.85, relwidth=0.3, height=30)
        label.bind("<ButtonRelease-1>", self.Resume)
        self.lbl_list.append(label)

    def Resume(self, event):
        self.Fadeout([self.lbl_list])

        self.title_text = Translate("#GAME_Title")
        self.window.title(self.title_text)

        font = Font(family='Tahoma', size=32)
        label = Label(self.window, text=self.title_text, bg='#ffffff', relief="solid", font=font)
        label.place(relx=0.3, relwidth=0.4, y=40)
        self.lbl_list.append(label)

        font = Font(family='Tahoma', size=16)
        label = ColoredLabel(self.window,
                             text=Translate("#GAME_MainText_Start" if not self.tutorial_used
                                            else "#GAME_MainText_Continue"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 250)
        label.bind("<ButtonRelease-1>", self.Tutorial)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Option"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 200)
        label.bind("<ButtonRelease-1>", self.OptionScreen)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_CreatorList"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 150)
        label.bind("<ButtonRelease-1>", self.AuthorScreen)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Quit"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 100)
        label.bind("<ButtonRelease-1>", self.ExitBtn)
        self.lbl_list.append(label)

    def ExitBtn(self, event):
        self.Exit()

    def Exit(self):
        self.valid = False
        self.window.destroy()

    def MainScreen(self):
        old_canvas = self.canvas

        self.title_text = Translate("#GAME_Title")
        self.window.title(self.title_text)

        self.canvas = GameCanvas(self, width=self.width, height=self.tall, bg='black', relief='solid')
        self.canvas['bg'] = '#000000'

        self.canvas.canvas_map.clear()
        self.canvas.rect.clear()
        self.canvas.line.clear()
        self.canvas.image.clear()
        self.canvas.font_image.clear()

        self.sound.Play('./sound/lobby.mp3', ChannelList.Background, 1, self.master_volume * 0.3)

        self.page = Page.Main

        for label in self.lbl_list:
            label.destroy()
        self.lbl_list.clear()

        self.random_x = randrange(-10, 5)
        self.random_y = randrange(-16, 8)
        w = self.width // 10

        for i in range(1, 20):
            self.canvas.create_line(self.random_x + w * i, 0, self.random_x + w * i, self.tall, fill='#ffffff')
            self.canvas.create_line(0, self.random_y + w * i, self.width, self.random_y + w * i, fill='#ffffff')

        font = Font(family='Tahoma', size=32)
        label = Label(self.window, text=self.title_text, bg='#ffffff', relief="solid", font=font)
        label.place(relx=0.3, relwidth=0.4, y=40)
        self.lbl_list.append(label)

        font = Font(family='Tahoma', size=16)
        label = ColoredLabel(self.window,
                             text=Translate("#GAME_MainText_Start" if not self.tutorial_used
                                            else "#GAME_MainText_Continue"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 250)
        label.bind("<ButtonRelease-1>", self.Tutorial)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Option"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 200)
        label.bind("<ButtonRelease-1>", self.OptionScreen)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_CreatorList"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 150)
        label.bind("<ButtonRelease-1>", self.AuthorScreen)
        self.lbl_list.append(label)

        label = ColoredLabel(self.window, text=Translate("#GAME_MainText_Quit"), font=font)
        label.place(relx=0.4, relwidth=0.2, y=self.tall - 100)
        label.bind("<ButtonRelease-1>", self.ExitBtn)
        self.lbl_list.append(label)

        xx = self.random_x + 1
        yy = self.random_y + 1
        ww = w - 1

        next_draw = time.time()
        clr = '#ff6464'

        if old_canvas is not None:
            old_canvas.destroy()

        while self.valid and self.page == Page.Main:
            now = time.time()

            rm_list = []
            for s in self.canvas.rect:
                rgb = RGB_StrToIntArray(self.canvas.itemcget(s, 'fill'))

                for i in range(0, 3):
                    rgb[i] = max(0, rgb[i] - 4)

                if rgb == [0, 0, 0]:
                    self.canvas.delete(s)
                    rm_list.append(s)
                else:
                    color = RGB_IntArrayToStr(rgb)
                    self.canvas.itemconfig(s, fill=color)

            for elem in rm_list:
                self.canvas.rect.remove(elem)

            if now - next_draw >= 0.1:
                points = [xx, yy,
                          xx + ww, yy,
                          xx + ww, yy + ww,
                          xx, yy + ww]
                self.canvas.create_polygon(points, fill=clr, save='rect')

                if randrange(0, 2) == 1 and xx <= self.width:
                    xx += w
                else:
                    yy += w

                if xx > self.width or yy > self.tall:
                    xx = self.random_x + 1
                    yy = self.random_y + 1

                    if randrange(0, 2) == 1:
                        xx += w * randrange(1, 3)
                    else:
                        yy += w * randrange(1, 3)

                    rand = randrange(1, 4)
                    if rand == 1:
                        clr = '#ff6464'
                    elif rand == 2:
                        clr = '#64ff64'
                    else:
                        clr = '#6464ff'
                    next_draw = now + 1
                else:
                    next_draw = now

            self.window.update()
            time.sleep(0.01)

import PIL.Image

from GUI.GameCanvas import *


class ImagedButton:
    def __init__(self, *args):
        self.__canvas = None
        self.__id = -1

        self.__image = [None, None, None]
        self.x, self.y = args[0], args[1]
        self.__command = args[2]

    def canvas_hook(self, canvas: GameCanvas):
        if canvas is None:
            return

        self.__canvas = canvas
        self.__id = super(GameCanvas, canvas).create_image(self.x, self.y, {'image': self.__image[0], 'anchor': NW})
        canvas.image.append([self.__id, None, self.__image[0]])

    def SetCommand(self, cmd):
        self.__command = cmd

    def GetID(self):
        return self.__id

    def Event_Bind(self):
        if self.__id == -1:
            return

        self.__canvas.tag_bind(self.__id, "<Enter>", self.Event_Enter)
        self.__canvas.tag_bind(self.__id, "<Leave>", self.Event_Leave)
        self.__canvas.tag_bind(self.__id, "<Button-1>", self.Event_Push)
        self.__canvas.tag_bind(self.__id, "<ButtonRelease-1>", self.Event_Click)

    def Event_Unbind(self):
        if self.__id == -1:
            return

        self.__canvas.tag_unbind(self.__id, "<Enter>")
        self.__canvas.tag_unbind(self.__id, "<Leave>")
        self.__canvas.tag_unbind(self.__id, "<Button-1>")
        self.__canvas.tag_unbind(self.__id, "<ButtonRelease-1>")

    def Event_Enter(self, event):
        if self.__id == -1:
            return

        self.__canvas.itemconfigure(self.__id, image=self.__image[1])
        self.__canvas.update()

    def Event_Leave(self, event):
        if self.__id == -1:
            return

        self.__canvas.itemconfigure(self.__id, image=self.__image[0])
        self.__canvas.update()

    def Event_Push(self, event):
        if self.__id == -1:
            return

        self.__canvas.itemconfigure(self.__id, image=self.__image[2])
        self.__canvas.update()

    def Event_Click(self, event):
        if self.__id == -1:
            return

        self.__canvas.itemconfigure(self.__id, image=self.__image[1])
        self.__canvas.update()

        self.__canvas.main.Command(self, self.__command)

    def SetImage(self, *args):
        for i in range(3):
            rgba = cv2.resize(cv2.imread(args[i], cv2.IMREAD_UNCHANGED), args[3:])
            rgba = cv2.cvtColor(rgba, cv2.COLOR_BGR2RGBA)
            img = ImageTk.PhotoImage(image=PIL.Image.fromarray(rgba))
            self.__image[i] = img

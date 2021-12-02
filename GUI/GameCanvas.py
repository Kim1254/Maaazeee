from tkinter import *

import numpy as np
import cv2
import PIL.Image
from PIL import ImageTk


def image2rgba(*args):
    rgba = cv2.resize(cv2.imread(args[0], cv2.IMREAD_UNCHANGED), args[1:])
    rgba = cv2.cvtColor(rgba, cv2.COLOR_BGR2RGBA)
    return rgba


def cv2Tk(rgba):
    return ImageTk.PhotoImage(image=PIL.Image.fromarray(rgba))


def MatrixScalar(rgba, color):
    x, y = len(rgba[0]), len(rgba)

    rgbaa = np.array(rgba)
    ca = np.array(color) / 255

    rgbaa = rgbaa * ca
    rgbaa = rgbaa.astype('uint8').reshape(y, x, 4)

    return rgbaa


class GameCanvas(Canvas):
    def __init__(self, master=None, cnf={}, **kw):
        self.canvas_map = []
        self.rect = []
        self.line = []
        self.image = []
        self.font_image = []

        self.main = master

        self.current = ()
        self.offset_coord = ()

        self.direction_width = 0
        self.direction_tall = 0
        self.direction_list = []
        self.direction_show = False

        self.dir_image = []

        self.lock = False

        super(GameCanvas, self).__init__(master.window, cnf, **kw)

        self.pack()

    def IsCursorVisible(self):
        off_coord = (self.current[0] - self.offset_coord[0], self.current[1] - self.offset_coord[1])
        if 0 <= off_coord[0] < 20 and 0 <= off_coord[1] < 20:
            return True
        return False

    def CheckCursor(self, event):
        x, y = 0, 0
        remove = True

        if self.IsCursorVisible():
            off_coord = (self.current[0] - self.offset_coord[0], self.current[1] - self.offset_coord[1])
            coord = self.coords(self.canvas_map[off_coord[1]][off_coord[0]])
            x = event.x - coord[0]
            y = event.y - coord[1]

            if -self.direction_width < x < 2 * self.direction_width:
                if -2 < y < self.direction_tall + 2:
                    remove = False

            if -self.direction_tall < y < 2 * self.direction_tall:
                if -2 < x < self.direction_width + 2:
                    remove = False

        if remove is True:
            if self.direction_show is True:
                self.RemoveDirection()
        else:
            if self.direction_show is False:
                self.CreateDirection()

    def ReleaseCursor(self, event):
        if self.direction_show is False:
            return
        if self.IsCursorVisible() is False:
            return

        off_coord = (self.current[0] - self.offset_coord[0], self.current[1] - self.offset_coord[1])

        coord = self.coords(self.canvas_map[off_coord[1]][off_coord[0]])
        x = event.x - coord[0]
        y = event.y - coord[1]

        index = -1

        if 0 < x < self.direction_width:
            if -self.direction_tall < y < 0:
                index = 0
            elif 0 < y - self.direction_tall < self.direction_tall:
                index = 1
        elif 0 < y < self.direction_tall:
            if -self.direction_width < x < 0:
                index = 2
            elif 0 < x - self.direction_width < self.direction_width:
                index = 3

        if index != -1:
            self.main.Command(None, 'Move', direction=index, input='mouse')

    def CreateDirection(self):
        if self.main is None:
            return
        if len(self.dir_image) == 0:
            return
        if self.IsCursorVisible() is False:
            return

        create = True if len(self.direction_list) == 0 else False

        move = self.main.manager.CanMove()
        off_coord = (self.current[0] - self.offset_coord[0], self.current[1] - self.offset_coord[1])

        coord = self.coords(self.canvas_map[off_coord[1]][off_coord[0]])

        for i in range(0, 4):
            x = coord[0] + 1
            y = coord[1] + 1
            w = self.direction_width - 2
            t = self.direction_tall - 2

            if i == 0:
                y -= self.direction_tall + 2
            elif i == 1:
                y += self.direction_tall + 2
            elif i == 2:
                x -= self.direction_width + 2
            else:
                x += self.direction_width + 2

            id = i * 2 + (0 if move[i] else 1)
            if create:
                image = self.create_image(np.full(4, 0).astype('uint8').reshape(1, 1, 4), x, y, anchor=NW)
                self.direction_list.append(image)

            for elem in self.image:
                if elem[0] == self.direction_list[i]:
                    self.coords(elem[0], x, y)
                    self.itemconfigure(elem[0], image=self.dir_image[id][1])
                    elem[1] = self.dir_image[id][0]
                    elem[2] = self.dir_image[id][1]
        self.update()
        self.direction_show = True

    def RemoveDirection(self):
        for image in self.direction_list:
            for elem in self.image:
                if elem[0] == image:
                    new_img = cv2Tk(np.full(4, 0).astype('uint8').reshape(1, 1, 4))
                    self.itemconfigure(elem[0], image=new_img)
                    elem[2] = new_img
        self.update()
        self.direction_show = False

    def UpdateCurrent(self, x, y, off_x, off_y, mouse=False):
        c_x, c_y = self.current[0] - off_x, self.current[1] - off_y

        if 0 <= c_x < 20 and 0 <= c_y < 20:
            self.itemconfig(self.canvas_map[c_y][c_x], fill='#ffffff')

        c_x, c_y = x - off_x, y - off_y
        self.itemconfig(self.canvas_map[c_y][c_x], fill='#10dd10')
        self.RemoveDirection()

        self.current = (x, y)

        if mouse is True:
            self.CreateDirection()

    def create_line(self, *args, **kw):
        save = kw.get('save')
        if save is not None:
            del kw['save']
        else:
            save = True

        rs = super(GameCanvas, self).create_line(args, **kw)

        if save is True:
            self.line.append(rs)

        return rs

    def create_polygon(self, points=None, **option):
        if points is None:
            return None
        save = option.get('save')
        if save is not None:
            del option['save']

        rs = super(GameCanvas, self).create_polygon(points, option)

        if save == 'rect':
            self.rect.append(rs)

        return rs

    def coord_square(self, sqr, c=None):
        if c is None:
            c = [0, 0, 0, 0]
        self.coords(sqr, c[0], c[1], c[0] + c[2], c[1], c[0] + c[2], c[1] + c[3], c[0], c[1] + c[3])

    def create_image(self, *args, **kw):
        rgba = None
        if len(args) == 5:  # image, x, y, w, h
            rgba = cv2.resize(cv2.imread(args[0], cv2.IMREAD_UNCHANGED), args[3:])
            rgba = cv2.cvtColor(rgba, cv2.COLOR_BGR2RGBA)
        else:  # array, x, y
            rgba = args[0]
        img = cv2Tk(rgba)
        kw['image'] = img

        rs = super(GameCanvas, self).create_image(args[1:3], **kw)
        self.image.append([rs, rgba, img])

        return rs

    def create_FontImage(self, *args, **kw):
        rgba = args[0]
        img = ImageTk.PhotoImage(image=PIL.Image.fromarray(rgba))
        kw['image'] = img
        kw['anchor'] = NW

        rs = super(GameCanvas, self).create_image(args[1:3], **kw)
        self.font_image.append([rs, rgba, img])

        return rs

    def remove_image(self, image=None):
        for img in self.image:
            if image is None or img == image:
                self.delete(img[0])
                self.image.remove(img)

    def BuildMap(self, x, y, w, t, map):
        if map is None:
            return
        if len(map) == 0:
            return

        xx = x + 1
        yy = y + 1
        self.direction_width = w - 2
        self.direction_tall = t - 2

        self.dir_image.clear()
        for i in range(8):
            name = './image/tutorial/dir{0}{1}.png'.format(i // 2, 'g' if i % 2 == 0 else 'r')
            rgba = image2rgba(name, w - 2, t - 2)
            img = cv2Tk(rgba)
            self.dir_image.append([rgba, img])

        self.canvas_map.clear()

        for ypos in range(0, min(20, len(map))):
            line = []
            for xpos in range(0, min(20, len(map[ypos]))):
                points = [xx, yy,
                          xx + self.direction_width, yy,
                          xx + self.direction_width, yy + self.direction_tall,
                          xx, yy + self.direction_tall]

                if map[ypos][xpos] == 1:
                    rs = self.create_polygon(points, fill='#808080', outline='#000000', width=1, save='rect')
                elif map[ypos][xpos] == 2:
                    self.main.manager.SetPosition([xpos, ypos])
                    self.current = (xpos, ypos)
                    rs = self.create_polygon(points, fill='#10dd10', outline='#000000', width=1, save='rect')
                elif map[ypos][xpos] == 3:
                    rs = self.create_polygon(points, fill='#dd1010', outline='#000000', width=1, save='rect')
                else:
                    rs = self.create_polygon(points, fill='#ffffff', outline='#000000', width=1, save='rect')
                line.append(rs)
                xx += w + 1
            xx = x + 1
            yy += t + 1
            self.canvas_map.append(line)

    def UpdateMap(self, map, size, current):
        if map is None:
            return
        if len(map) == 0 or len(self.canvas_map) == 0:
            return

        for y in range(size[1], min(size[1] + 20, len(map))):
            for x in range(size[0], min(size[0] + 20, len(map[y]))):
                c_x, c_y = x - size[0], y - size[1]
                if map[y][x] == 1:
                    self.itemconfigure(self.canvas_map[c_y][c_x], fill='#808080')
                elif [x, y] == current:
                    self.itemconfigure(self.canvas_map[c_y][c_x], fill='#10dd10')
                elif map[y][x] == 3:
                    self.itemconfigure(self.canvas_map[c_y][c_x], fill='#dd1010')
                else:
                    self.itemconfigure(self.canvas_map[c_y][c_x], fill='#ffffff')
        self.update()

    def ActivateControl(self):
        self.bind('<Motion>', self.CheckCursor)
        self.bind('<ButtonRelease-1>', self.ReleaseCursor)

    def DeactivateControl(self):
        self.unbind('<Motion>')
        self.unbind('<ButtonRelease-1>')

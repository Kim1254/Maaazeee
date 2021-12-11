from enum import Enum, auto


class Page(Enum):
    Main = 0
    Start = auto()


# '#012345' -> [0x01, 0x23, 0x45]
def RGB_StrToIntArray(string):
    r = int(string[1:3], 16)
    g = int(string[3:5], 16)
    b = int(string[5:7], 16)
    return [r, g, b]


def RGB_IntArrayToStr(li):
    red = str(hex(li[0]))[2:]
    green = str(hex(li[1]))[2:]
    blue = str(hex(li[2]))[2:]

    return '#{0:0>2}{1:0>2}{2:0>2}'.format(red, green, blue)
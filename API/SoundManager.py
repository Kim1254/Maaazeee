import pygame.mixer as mixer

from enum import Enum, auto


class ChannelList(Enum):
    Begin = -1
    Background = auto()
    Effect = auto()
    End = auto()


class SoundManager:
    def __init__(self):
        # @frequency: Sampling rate,
        # 44100(CD), 16000(Naver TTS), 24000(Google TTS)
        self.freq = 16000

        # @bitsize:
        # 8, -8, 16, -16
        self.bitsize = -16

        # @Channel:
        # 1 = mono, 2 = stereo
        self.channels = 1

        # @Buffer:
        # Number of samples(experiment to get right sound)
        self.buffer = 2048

        self.__volume = 1.0

        mixer.init(self.freq, self.bitsize, self.channels, self.buffer)
        mixer.set_num_channels(ChannelList.End.value)

    def __del__(self):
        mixer.quit()

    def Valid(self, channel: ChannelList):
        if channel == ChannelList.Begin or channel == ChannelList.End:
            return False
        return True

    def Play(self, fp, channel: ChannelList, loop=0, volume=1.0):
        if self.Valid(channel) is False:
            return
        sound = mixer.Sound(fp)
        if sound is None:
            return

        if mixer.Channel(channel.value).get_busy():
            mixer.Channel(channel.value).stop()

        mixer.Channel(channel.value).play(sound, loop)
        mixer.Channel(channel.value).set_volume(volume)

    def Fadeout(self, channel: ChannelList, time=1):
        if self.Valid(channel) is False:
            return
        if mixer.Channel(channel.value).get_busy() is False:
            return

        mixer.Channel(channel.value).fadeout(time)

    def Volume(self, channel: ChannelList, ratio):
        if self.Valid(channel) is False:
            return
        if mixer.Channel(channel.value).get_busy() is False:
            return

        mixer.Channel(channel.value).set_volume(ratio)

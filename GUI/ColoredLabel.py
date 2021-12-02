from tkinter import Label


class ColoredLabel(Label):
    def Event_Enter(self, event):
        self.configure(fg='red')

    def Event_Leave(self, event):
        self.configure(fg='black')

    def Event_Bind(self):
        self.bind("<Enter>", self.Event_Enter)
        self.bind("<Leave>", self.Event_Leave)

    def bind(self, sequence=None, func=None):
        i = super(ColoredLabel, self).bind(sequence, func, "+")
        self.bind_list.append([sequence, i])
        return i

    def Event_Unbind(self):
        self.configure(fg='black')
        for li in self.bind_list:
            #print('Unbind({0}): {1} {2}'.format(self['text'], li[0], li[1]))
            self.unbind(li[0], li[1])
            self.unbind_all(li[0])
        self.bind_list.clear()

    def __init__(self, master=None, text="", font=None):
        super(ColoredLabel, self).__init__(master, text=text, bg='#ffffff', relief="solid", font=font)
        self.bind_list = []
        self.Event_Bind()
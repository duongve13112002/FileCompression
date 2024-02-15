import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle


class AnimationGui(tk.Label):
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
            self.config(background='bisque')
        frames = []

        try:
            for i in count(1):
                img = im.copy().resize((100,100))
                img = img.convert(mode="RGBA")
                frames.append(ImageTk.PhotoImage(img))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

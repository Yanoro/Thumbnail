#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from helper import *

class Movie():

    '''
    Tkinter freakouts whenever we try to create a frame in a thread that isn't the main one
    so we want to call set_frame after initializing the object
    '''
    def __init__(self, movie_name, movie_dir, width=200, height=200):
        movie_dir = create_movie_dir(movie_name)
        # No need to get more images if we already have some
        if not list(os.listdir(movie_dir)):
            crawler = GoogleImageCrawler(storage = {'root_dir': movie_dir})
            get_new_images(movie_name, crawler)
        self.movie_name = movie_name
        self.movie_path = movie_dir + movie_name
        self.width = width
        self.height = height
        self.frame = None

    def load_image(self, mainframe, col, row, fastMode=False):
        def load_thumbnail(fMode):
            imagePath = getThumbnails(self.movie_name, fast_mode=fMode)
            self.thumbnail = load_image(imagePath)
            if self.frame is None:
                raise Exception("[!] load_thumbnail called without having set the frame previously!")
            ttk.Label(self.frame, image=self.thumbnail).grid(column=0, row=0)

        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()

        self.frame = ttk.Frame(mainframe, width=self.width, height=self.height)
        self.frame.grid(column=col, row=row)

        load_thumbnail(fastMode)

        thumb = ttk.Label(self.frame, image=self.thumbnail)
        thumb.grid(column=0, row=0)

        ttk.Label(self.frame, text=self.movie_name).grid(column=0, row=1)

        m = Menu(self.frame, tearoff=0)
        m.add_command(label ="Change thumbnail", command=lambda : load_thumbnail(False))
        thumb.bind("<Button-3>", do_popup)

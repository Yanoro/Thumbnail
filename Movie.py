#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from helper import *

class Movie():

    '''
    Tkinter freakouts whenever we try to create a frame in a thread that isn't the main one
    so we want to call set_frame after initializing the object
    '''
    def __init__(self, movie_name, width=200, height=200):
        movie_dir = create_movie_dir(movie_name)
        # No need to get more images if we already have some
        if not list(os.listdir(movie_dir)):
            crawler = GoogleImageCrawler(storage = {'root_dir': movie_dir})
            get_new_images(movie_name, crawler)
        self.movie_name = movie_name
        self.width = width
        self.height = height

    def load_thumbnail(self, fastMode=False):
        imagePath = getThumbnails(self.movie_name, fastMode)
        self.thumbnail = load_image(imagePath)

    '''
    We expect that mainframe is a Scrollabe object
    '''
    def set_frame(self, mainframe, col, row):
        self.frame = ttk.Frame(mainframe, width=self.width, height=self.height)
        self.frame.grid(column=col, row=row)

        thumb = ttk.Label(self.frame, image=self.thumbnail)
        thumb.grid(column=0, row=0)

        ttk.Label(self.frame, text=self.movie_name).grid(column=0, row=1)

        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()

        m = Menu(self.frame, tearoff=0)
        m.add_command(label ="Cut")
        m.add_command(label ="Copy")
        m.add_command(label ="Paste")
        m.add_command(label ="Reload")
        m.add_separator()
        m.add_command(label ="Rename")

        thumb.bind("<Button-3>", do_popup)

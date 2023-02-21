#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from helper import *
import asyncio, os

class Movie():

    '''
    Tkinter freakouts whenever we try to create a frame in a thread that isn't the main one
    so we want to call set_frame after initializing the object
    '''
    def __init__(self, movie_name, movie_dir, app_loop, width=200, height=200):
        movie_dir = create_movie_dir(movie_name)
        # No need to get more images if we already have some
        if not list(os.listdir(movie_dir)):
            crawler = GoogleImageCrawler(storage = {'root_dir': movie_dir})
            get_new_images(movie_name, crawler)
        self.movie_name = movie_name
        self.movie_path = movie_dir
        self.app_loop = app_loop
        self.width = width
        self.height = height
        self.frame = None
        self.getting_images = False

    def load_image(self, mainframe, col, row):
        async def load_thumbnail(relative_direction):
            def watch_movie():
                movie_fullpath = os.getcwd() + '/' + self.movie_name
                print(movie_fullpath)
                try:
                    print(os.listdir(movie_fullpath))
                    movieFile = [f for f in os.listdir(movie_fullpath) if f[-3:] == "mkv"  or f[-3:] == "mp4" or f[-3:] == "avi"][0]
                except Exception as err:
                    print("Failed to find movie file: ", err)
                    return

                print(movieFile)
                os.system('mpv --sub-auto=all \"' + movie_fullpath + '\"')
            def do_popup(event):
                try:
                    m.tk_popup(event.x_root, event.y_root)
                finally:
                    m.grab_release()

            # Make sure that we are avoiding race conditions in case a user tries to
            # load multiple thumbnails too quickly
            if self.getting_images:
                print("Getting images already!")
                return
            self.getting_images = True
            load_thumbnail.index = max(load_thumbnail.index + relative_direction, 0)
            # If it isn't the first time we are loading an image then we must be in the event loop
            # and thus need to get the new images asynchronously
            if relative_direction == 0:
                imagePath = getThumbnails(self.movie_name, load_thumbnail.index)
            else:
                imagePath = await self.app_loop.loop.run_in_executor(None, getThumbnails, self.movie_name, load_thumbnail.index)

            self.thumbnail = load_image(imagePath)
            if self.frame is None:
                raise Exception("[!] load_thumbnail called without having set the frame previously!")
            thumb = ttk.Label(self.frame, image=self.thumbnail)
            thumb.grid(column=0, row=0)

            ttk.Label(self.frame, text=self.movie_name).grid(column=0, row=1)

            m = Menu(self.frame, tearoff=0)
            m.add_command(label ="Watch", command=lambda: watch_movie())
            m.add_command(label ="Next thumbnail", command=lambda: self.app_loop.add_task(load_thumbnail(1)))
            m.add_command(label ="Previous thumbnail", command=lambda: self.app_loop.add_task(load_thumbnail(-1)))

            thumb.bind("<Button-3>", do_popup)
            self.getting_images = False

        load_thumbnail.index = 0

        self.frame = ttk.Frame(mainframe, width=self.width, height=self.height)
        self.frame.grid(column=col, row=row)

        asyncio.run(load_thumbnail(0))

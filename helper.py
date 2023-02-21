#!/usr/bin/env python3

import sys, os, time, glob, subprocess, readchar, threading, asyncio
from tkinter import *
from tkinter import ttk
from icrawler.builtin import GoogleImageCrawler
from PIL import ImageTk, Image

class Scrollable(ttk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame, width=16):

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y, expand=False)

        self.canvas = Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        ttk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=NW)


    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width = canvas_width)

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

def get_new_images(search_term, crawler):
    print("[!] Getting images for: ", search_term)
    crawler.crawl(keyword=search_term,
                  file_idx_offset='auto',
                  offset=1,
                  max_num=3)

def getThumbnails(search_term, index):
    target_dir = create_movie_dir(search_term)
    google_Crawler = GoogleImageCrawler(storage = {'root_dir': target_dir})

    try:
        target_files = list(os.listdir(target_dir))
    except FileNotFoundError:
        target_files = []

    prev_len = len(target_files)
    while prev_len < index + 1: #Loop until we know we have the index we want
        get_new_images(search_term, google_Crawler)
        target_files = list(os.listdir(target_dir))
        new_len = len(target_files)
        if prev_len == new_len:
            print("[!] get_new_images failed to load more images! Exiting...")
            sys.exit(-1)
        elif prev_len > new_len:
            print("[!] Images were deleted while querying google for more! Exiting...")
            sys.exit(-1)
        prev_len = new_len

    filePath = os.getcwd() + '/' + target_dir + target_files[index]
    return filePath


def load_image(img_name):
    img = Image.open(img_name)
    img_2 = img.resize((200,200))
    return ImageTk.PhotoImage(img_2)

'''
Create the images/${MOVIE_NAME} directory
and return it's path
'''
def create_movie_dir(movie_name):
    dir = 'images/' + movie_name + '/'
    os.system('mkdir -p \'' + dir + '\'')
    return dir


#!/usr/bin/env python3

import sys, os, time, glob, subprocess, readchar, threading
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

def padding_zeros(n):
    zeros = 1
    while (n / 10) >= 1:
        n /= 10
        zeros += 1
    return '0' * (6 - zeros)

def get_new_images(search_term, crawler):
    print("[!] Getting images for: ", search_term)
    #The crawler that we are using has some annoying output that we would rather ignore for now
    #Changing sys.stdout doesn't work so we have to do it this way
    #https://stackoverflow.com/questions/977840/redirecting-fortran-called-via-f2py-output-in-python/978264#978264
    #null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    #save = os.dup(1), os.dup(2)
    #os.dup2(null_fds[0], 1)
    #os.dup2(null_fds[1], 2)

    crawler.crawl(keyword=search_term,
                  file_idx_offset='auto',
                  offset=1,
                  max_num=5)

    #os.dup2(save[0], 1)
    #os.dup2(save[1], 2)
    #os.close(null_fds[0])
    #os.close(null_fds[1])

'''
Function used to concurrently crawl through different search querys
Stores each search query in ./images/$QUERY/
'''
def get_new_images_batch(search_terms):
    threads = []

    for search_term in search_terms:
        # For some reason the set_storage method isn't working so we have to create
        # a new icrawler object each time we want to change storage locations
        crawler = GoogleImageCrawler(storage = {'root_dir': 'images/' + search_term + '/'})
        thread = threading.Thread(target=get_new_images, args=(search_term, crawler))
        thread.start()
        threads += [thread]

    for thread in threads:
        thread.join()

'''
Given a search term, crawl through google for images and
prompt the user until he chooses an image, returns the image's path

fast_mode ignores the user and chooses the first option always, best used for debugging
'''
def getThumbnails(search_term, fast_mode=False):
    target_dir = create_movie_dir(search_term)
    google_Crawler = GoogleImageCrawler(storage = {'root_dir': target_dir})
    done = False

    max_index = 1 # Stores biggest index we got so far
    index = 0 # Current Index
    increment = 5 # How many images do we download each time we crawl

    try:
        target_files = list(os.listdir(target_dir))
    except FileNotFoundError:
        target_files = []

    while not done:
        prev_len = len(target_files)
        # We need to reload on images whenever our list of images is empty
        # or we already took a look on all of them
        if prev_len == 0 or index == prev_len - 1:
            get_new_images(search_term, google_Crawler)
            target_files = list(os.listdir(target_dir))
            new_len = len(target_files)
            if prev_len == new_len:
                print("[!] get_new_images failed to load more images! Exiting...")
                sys.exit(-1)
            elif prev_len > new_len:
                print("[!] Images were deleted while querying google for more! Exiting...")
                sys.exit(-1)

        filename = target_files[index]

        # Skip the entire user prompting process
        if fast_mode:
            break

        proc = subprocess.Popen(['display', target_dir + filename])
        while True:
            print("Press enter to choose this image, < to go to previous images ",
                    "and press > for the next image!")
            input_ch = readchar.readchar()
            if input_ch == '\n':
                done = True
                break
            if input_ch == '<':
                if index == 0:
                    print("[!] This is the first image!")
                    continue
                index -= 1
                break
            if input_ch == '>':
                index += 1
                break
        proc.terminate()

    abs_path = os.getcwd() + '/' + target_dir
    return abs_path + filename

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
    os.system('mkdir -p ' + dir)
    return dir

#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
import sys, os, time, glob
import concurrent.futures
from concurrent.futures import wait
from icrawler.builtin import GoogleImageCrawler
from helper import *
from Movie import Movie


root = Tk()
root.title("Thumbnail viewer")

mainframe = ttk.Frame(root, padding="1 0 12 12")
mainframe.grid(column=0,row=0, sticky=(N, W, E, S))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

movies_mainframe = Scrollable(mainframe, width=64)

mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
'''
Sometimes we are already going to have the images directory,
so we need to make sure it's properly filtered
'''
dirs = [x.path.split('/')[1] for x in os.scandir('.') if x.path.split('/')[1] != 'images'
                                                      and x.is_dir()
                                                      and x.path.split('/')[1] != '.git']

print(dirs)
imgs = []

#get_new_images_batch(dirs)

futures = []
movies = []
# We need to asynchronously initialize all movies to have any hope of a reasonable wait time
with concurrent.futures.ThreadPoolExecutor() as executor:
    for movie_name in dirs:
        futures += [executor.submit(Movie, movie_name)]
    for future in concurrent.futures.as_completed(futures):
        movie = future.result()
        movies += [movie]

row = 0
col = 0
for movie in movies:
    movie.load_thumbnail(fastMode=True)
    movie.set_frame(movies_mainframe, col, row)
    col += 1

movies_mainframe.update()
root.mainloop()

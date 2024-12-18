#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
import sys, os, time, glob, asyncio
import concurrent.futures
from concurrent.futures import wait
from icrawler.builtin import GoogleImageCrawler
from helper import *
from Movie import Movie
from app_loop import app_loop

if (len(sys.argv) < 2):
    print("[!] Format: {} <Path>".format(sys.argv[0]))
    sys.exit(-1)

main_gui_interval = 1/60  #How many times per seconds should we update the gui
target_path = sys.argv[1]

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
os.chdir(target_path)
dirs = [x.path.split('/')[1] for x in os.scandir('.')
        if x.path.split('/')[1] != 'images' and x.is_dir() and x.path.split('/')[1] != '.git']

print(os.getcwd())
print(dirs)
imgs = []

futures = []
movies = []

event_loop = asyncio.get_event_loop()
app_loop = app_loop(event_loop)

# We need to asynchronously initialize all movies to have any hope of a reasonable wait time
with concurrent.futures.ThreadPoolExecutor() as executor:
    for movie_name in dirs:
        futures += [executor.submit(Movie, movie_name, target_path, app_loop)]
    for future in concurrent.futures.as_completed(futures):
        movie = future.result()
        movies += [movie]
        print("[*] Done: ", movie.movie_name)

row = 0
col = 0
for movie in movies:
    movie.load_image(movies_mainframe, col, row)
    col += 1
    if col == 5:
        row += 1
        col = 0

os.chdir('.') # Once everything is done we go back to our original directory

movies_mainframe.update()

app_loop.add_task(app_loop.update_loop(root, main_gui_interval))
app_loop.start_loop()
app_loop.close()

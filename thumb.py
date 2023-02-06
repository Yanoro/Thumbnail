#!/usr/bin/env python3
from icrawler.builtin import GoogleImageCrawler
import sys, os, time, glob
import subprocess
import readchar


def padding_zeros(n):
    zeros = 1
    while (n / 10) >= 1:
        n /= 10
        zeros += 1
    return '0' * (6 - zeros)


if len(sys.argv) < 2:
    print("[!] Format: {} <search term>".format(sys.argv[0]))
    sys.exit(-1)

search_term = sys.argv[1]
target_dir = 'images/' + search_term + '/'

os.system('mkdir ' + target_dir + " 2>/dev/null")
google_Crawler = GoogleImageCrawler(storage = {'root_dir': target_dir})

index = 1
increment = 5 # How many images do we download each time we crawl

while True:
    padding = padding_zeros(index)
    if ((index - 1) % increment) == 0:
        print("[!] Getting more images...")
        #The crawler that we are using has some annoying output that we would rather ignore for now
        #Changing sys.stdout doesn't work so we have to do it this way
        #https://stackoverflow.com/questions/977840/redirecting-fortran-called-via-f2py-output-in-python/978264#978264
        null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        save = os.dup(1), os.dup(2)
        os.dup2(null_fds[0], 1)
        os.dup2(null_fds[1], 2)

        google_Crawler.crawl(keyword = search_term,
                             file_idx_offset='auto',
                             offset = index,
                             max_num = increment)

        os.dup2(save[0], 1)
        os.dup2(save[1], 2)
        os.close(null_fds[0])
        os.close(null_fds[1])

    ext = [filename for filename in os.listdir(target_dir)
               if filename.startswith(padding + str(index))][0].split('.')[1]

    filename = padding + str(index) + '.' + ext
    proc = subprocess.Popen(['display', target_dir + filename])

    time.sleep(1)
    subprocess.call(['xdotool', 'click', '1'])
    print("Press enter to choose this image, otherwise press any other key for the next")
    x = readchar.readchar()
    proc.terminate()
    if x == '\n':
        break
    index += 1

print(os.getcwd())
print(glob.glob(os.getcwd() + '/' + target_dir))
abs_path = os.getcwd() + '/' + target_dir

#Remove unused files from directory
for file in os.listdir(abs_path):
    fname = file.split('/')[-1]
    print(fname)
    if fname != filename:
        os.remove(abs_path + fname)

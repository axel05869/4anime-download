# I made this project while learning webscraping in python so maybe the code is a little bit mess to you
# project started on 1/13/21
# you can find this project on https://github.com/axel05869/4anime-downloader

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm # for download progress
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os


class colors:
    reset = "\033[0m"
    yellow = "\033[33m"
    red = "\033[31m"
    magenta = "\033[35m"

# modify this if you want to save file to other location
def savePath():
    path = str(Path.home()/'Downloads'/'Anime'/modefied_title)
    return path


def makePath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    print(f'\nfile will be saved to ({path})')
    

def establishConnection(url): # this will only check if site is up
    i = 1
    check = requests.get(url)
    while check.status_code != 200:
        if i != 5:
            check = requests.get(url)
            print(f'{check.status_code} error, Retry: {i}')
            i += 1
        else:
            print('Cannot establish a connection!')
            os.system("pause")
            exit()


def runDownloader(index):
    href = link[index]['href'] # this will be the link to the episode
    downloadEpisode(href,savePath(),index)


def downloadEpisode(url,path,index):
    episodenumber = index + 1
    episodenumber = str(episodenumber)
    
    # get direct link
    html_episode = requests.get(url).text
    soup_episode = BeautifulSoup(html_episode, 'lxml')
    direct_link = soup_episode.find('source')['src']

    # get file name
    if direct_link.find('/'):
        filename = direct_link.rsplit('/', 1)[1]
    saveTo = f'{path}/{filename}'

    # start download
    chunk_size = 256
    r = requests.get(direct_link, stream=True)
    total_size = int(r.headers['content-length'])
    with open(saveTo, 'wb') as f:
        for chunk in tqdm(iterable = r.iter_content(chunk_size=chunk_size), desc=f'[{colors.magenta}ep{episodenumber}{colors.reset}]', 
        total = int(total_size/chunk_size), ncols=90, unit = 'KB', colour='red'): # docs https://tqdm.github.io/docs/tqdm/
            f.write(chunk)
    print(f'[Complete]')


#========== START===========

print('''

            ,.  ,.
            ||  ||
           ,''--''.     \033[31m4-anime\033[0m
          : (.)(.) :    \033[31mDownloader\033[0m
         ,'   __   `.
         :  /    \  :
         : |      | :
   -axl- `._m____m_,' 

'''
)

print('example: https://4anime.to/anime/jujutsu-kaisen-tv')
while True:
    animelink = input('> ')
    if '4anime.to/anime' in animelink:
        break
    else:
        print('invalid link!')
        continue

establishConnection(animelink)

# request for html from site
html_main = requests.get(animelink).text
soup_main = BeautifulSoup(html_main, 'lxml')

# get the anime info
title = soup_main.find('p', {'class': 'single-anime-desktop'}).text
chapterlist = soup_main.find('ul', {'class': 'episodes range active'})
link = chapterlist.find_all('a')

# get total episodes
totalEpisodes = []
i = 0
for item in link:
    totalEpisodes.append(int(link[i].text))
    i += 1

# arrange and display total episodes
print(f'\n{colors.yellow}Episodes:{colors.reset}')
episodes = []
i = 0
while i < len(totalEpisodes):
    episodes.append(totalEpisodes[i:i+20]) # append every 20 episodes
    i += 20
for item in episodes:
    print(item)
print(f'{title} has a total of {len(totalEpisodes)} episode(s)')


howto1 = '\n - Single Episode: input the episode number'
howto2 = '\n - All Episodes: Leave Blank(Press [Enter])'
howto3 = '\n - Range of Episodes: input the [start-end] of episodes to download. seperated by \'-\' ex. (10-20)'
print(f'\n{colors.yellow}Download Options:{colors.reset}{howto1}{howto2}{howto3}')

# ask for download range and loop if input is incorrect
while True:
    scanRange = input('\n> ')
    isDownloadAll = False
    isSingleDownload = False
    isDownloadRange = False
    # download all mode
    if scanRange == '':
        isDownloadAll = True
        break
    # single download mode
    if '-' not in scanRange:
        isSingleDownload = True
        scanRange = int(scanRange)
        if scanRange in totalEpisodes:
            break
        else:
            print(f'not in range! choose only between {totalEpisodes[0]} and {totalEpisodes[-1]}')
            continue
    # download range mode
    if '-' in scanRange:
        isDownloadRange = True
        split = scanRange.split('-')
        start = int(split[0])
        end = int(split[1])
        if start in totalEpisodes and end in totalEpisodes:
            break
        else:
            print(f'not in range! choose only between {totalEpisodes[0]} and {totalEpisodes[-1]}')
            continue
    else:
        print('invalid input!')
        continue


# remove special char from title to be used as a folder name
modefied_title = ''
for char in title:
    if char.isalnum() or char == ' ':
        modefied_title += char

makePath(savePath()) # will also print where the file will be saved


# output
if isDownloadAll:
    print(f'Downloading all episodes of {title}...')
    dwded = 0 # num of episodes that are already downloaded
    needtobedwded = len(link) # num of episodes that needs to be downloaded
    i = 0

    for item in link:
        process = ThreadPoolExecutor()
        try: # run 2 download process at a time
            dwded += 2
            print(f'\nSTATUS - [{dwded}/{needtobedwded}]\n')

            dl = process.submit(runDownloader,i)
            i += 1
            dl2 = process.submit(runDownloader,i)
            i += 1
            dl.result()
            dl2.result()
        except IndexError:
            pass

if isSingleDownload:
    print(f'Downloading episode {scanRange} of {title}...')
    print('\nSTATUS - [1/1]\n')
    i = scanRange - 1 # index starts at 0
    runDownloader(i)

if isDownloadRange:
    print(f'Downloading {start} to {end} episodes of {title}...')
    dwded = 0
    needtobedwded = ((end + 1) - start)
    i = start - 1 # index starts at 0

    while i != end:
        process = ThreadPoolExecutor()
        try: # run 2 download process at a time
            dwded += 2
            print(f'\nSTATUS - [{dwded}/{needtobedwded}]\n')

            dl = process.submit(runDownloader,i)
            i += 1
            dl2 = process.submit(runDownloader,i)
            i += 1
            dl.result()
            dl2.result()
        except IndexError:
            pass
        
os.system("pause")
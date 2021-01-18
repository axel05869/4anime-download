# I made this project while learning webscraping in python so maybe the code is a little bit mess to you
# project started on 1/13/21
# you can find this project on https://github.com/axel05869/4anime-downloader

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm # for download progress
from pathlib import Path
import os


class colors: # https://cutt.ly/QjU7y2c
    reset = "\033[0m"
    yellow = "\033[33m"
    red = "\033[31m"


# short for direct video link grabber
def DVLG(episode_link):
    html_episode = requests.get(episode_link).text
    soup_episode = BeautifulSoup(html_episode, 'lxml')
    direct_link = soup_episode.find('source')['src']
    return direct_link


def downloadEpisode(url,path):
    # get file name
    if url.find('/'):
        filename = url.rsplit('/', 1)[1]
    saveTo = f'{path}/{filename}'

    print(f'\n[started] - {filename}')
    chunk_size = 256
    r = requests.get(url, stream=True)
    total_size = int(r.headers['content-length'])
    with open(saveTo, 'wb') as f:
        for chunk in tqdm(iterable = r.iter_content(chunk_size=chunk_size), total = int(total_size/chunk_size), ncols=90, unit = 'KB', colour='red'): # docs https://tqdm.github.io/docs/tqdm/
            f.write(chunk)
    print(f'{colors.red}Download Complete!{colors.reset}')


def makePath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    print(f'file will be saved to ({path})')


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

# get the html from the site
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
    if scanRange == '':
        isDownloadAll = True
        break
    if '-' not in scanRange:
        isSingleDownload = True
        scanRange = int(scanRange)
        break
    if '-' in scanRange:
        isDownloadRange = True
        split = scanRange.split('-')
        start = int(split[0])
        end = int(split[1])
        # check if input is in the range of episodes list
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

# modify this if you want to save file to other location
path = str(Path.home()/'Downloads'/'Anime'/modefied_title)

# output
if isDownloadAll:
    print(f'\nDownloading all episodes of {title}...')
    makePath(path) # will also print where the file will be saved
    i = 0
    for item in link:
        final_link = link[i]['href']
        directLink = DVLG(final_link)
        downloadEpisode(directLink,path)
        i += 1

if isSingleDownload:
    print(f'\nDownloading episode {scanRange} of {title}...')
    makePath(path)
    final_link = link[scanRange - 1]['href']
    directLink = DVLG(final_link)
    downloadEpisode(directLink,path)

if isDownloadRange:
    print(f'\nDownloading {start} to {end} episodes of {title}...')
    makePath(path)
    i = start - 1 # index starts at 0
    while i != end:
        final_link = link[i]['href']
        directLink = DVLG(final_link)
        downloadEpisode(directLink,path)
        i += 1
        
os.system("pause")
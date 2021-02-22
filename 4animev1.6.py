from bs4 import BeautifulSoup
import requests
import re
import os
from pathlib import Path
from tqdm import tqdm
import webbrowser

class colors:
    reset = "\033[0m"
    yellow = "\033[33m"
    red = "\033[31m"
    magenta = "\033[35m"


def savePath():
    path = str(Path.home()/'Downloads'/'Anime'/modefied_title) # modify, if you want to save to other location
    return path


def makePath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    print(f'\n{colors.yellow}file will be saved to:{colors.reset} {path}')


def downloadEpisode(url,index,path):
    episodenumber = index + 1
    episodenumber = str(episodenumber)
    
    # extract urls
    try:
        html_ep = requests.get(url).text
    except:
        print(f'{colors.red}Connection error!{colors.reset}')
        os.system('pause')
        exit()
    soup_ep = BeautifulSoup(html_ep, 'html.parser')
    script = soup_ep.find_all('script') # to reduce the url results
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(script)) # convert soup to text to work

	# sort out other links
    videolink = ''
    for url in urls:
	    if '.mp4' in url: # this is the video
			# remove unnecessary char
	        for char in url:
	            if '\\' not in char:
	                videolink = videolink + char

    # get file name
    if videolink.find('/'):
        filename = videolink.rsplit('/', 1)[1]
    saveTo = f'{path}/{filename}'

    print(videolink)
    
    # start download
    count = 0
    while count <= 2: # loop 2x if error
        if count != 2:
            try:
                chunk_size = 256
                r = requests.get(videolink, stream=True)
                total_size = int(r.headers['content-length'])
                with open(saveTo, 'wb') as f:
                    for chunk in tqdm(iterable = r.iter_content(chunk_size=chunk_size), desc=f'[ep{episodenumber}]', 
                    total = int(total_size/chunk_size), ncols=90, unit = 'KB', colour='red'): # docs https://tqdm.github.io/docs/tqdm/
                        f.write(chunk)
                print(f'[Complete]')
                break
            except:
                print(f'{colors.red}Error downloading!{colors.reset}')
                count += 1
                print(f'retrying: {count}/2')
                continue
        else:
            print(f'{colors.yellow}opening on browser instead{colors.reset}\n')
            webbrowser.open(videolink)
            print('next episode will start to download, exit if none')
            os.system('pause')
            break
    


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


# request data
try:
    html_main = requests.get(animelink).text
except:
    print(f'{colors.red}Connection error!{colors.reset}')
    os.system('pause')
    exit()
soup_main = BeautifulSoup(html_main, 'lxml')

# get data
title = soup_main.find('p', {'class': 'single-anime-desktop'}).text
chapterlist = soup_main.find('ul', {'class': 'episodes range active'})
eplinks = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(chapterlist))

# append all episode number to list
totalEpisodes = []
i = 1
for item in eplinks:
    totalEpisodes.append(i)
    i += 1

print(f'\n{colors.yellow}{title} has a total of {len(totalEpisodes)} episode(s){colors.reset}')

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
        scanRange = int(scanRange)
        if scanRange in totalEpisodes:
            isSingleDownload = True
            break
        else:
            print(f'not in range! choose only between {totalEpisodes[0]} and {totalEpisodes[-1]}')
            continue

    # download range mode
    if '-' in scanRange:
        split = scanRange.split('-')
        start = int(split[0])
        end = int(split[1])
        if start in totalEpisodes and end in totalEpisodes:
            isDownloadRange = True
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
    needtobedwded = len(eplinks) # num of episodes that needs to be downloaded
    i = 0

    for item in eplinks:
        dwded += 1
        print(f'\nSTATUS - [{dwded}/{needtobedwded}]\n')
        downloadEpisode(eplinks[i],i,savePath())
        i+=1
        

if isSingleDownload:
    print(f'Downloading episode {scanRange} of {title}...')
    print('\nSTATUS - [1/1]\n')
    i = scanRange - 1 # index starts at 0, -1 will allow to get list correctly
    downloadEpisode(eplinks[i],i,savePath())


if isDownloadRange:
    print(f'Downloading {start} to {end} episodes of {title}...')
    dwded = 0
    needtobedwded = ((end + 1) - start)
    i = start - 1

    while i != end:
        dwded += 1
        print(f'\nSTATUS - [{dwded}/{needtobedwded}]\n')
        downloadEpisode(eplinks[i],i,savePath())
        i += 1
    
print('the program will exit')
os.system("pause")
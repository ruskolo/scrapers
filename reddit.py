# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import sys
import time
import re
import urllib.request as ur
import urllib.parse
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValue

opener = ur.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
base_url = 'https://old.reddit.com'
ace_player = '%USERPROFILE%\\AppData\\Roaming\\ACEStream\\player\\ace_player.exe'

def getDefaultBrowser():
    with OpenKey(HKEY_CURRENT_USER,
                 r"Software\Classes\http\shell\open\command") as key:
        cmd = QueryValue(key, None)
    return cmd

def playWebStream(uri):
    browser_str = getDefaultBrowser()
    replace_str = '-new-window ' + uri
    play_str = browser_str.replace('-url \"%1\"', replace_str)
    os.system(play_str)

def playAceStream(acelink):
    play_str = ace_player + ' ' + acelink
    print('Playing ' + str(acelink) + '...')
    try:
        os.system(play_str)
    except KeyboardInterrupt:
        sys.exit()
    except:
        print('No such channel')
        return
    return

def getWebLinks(soup):
    print('')
    i = 1
    streams = {}
    for item in soup.findAll('div', {"class": re.compile('^ thing')}):
        for a in item.find_all('a', {'rel' : 'nofollow'}):
            if 'r/soccerstreams/' not in str(a) and 'time.is' not in str(a) and 'parent' not in str(a):
                if i < 10:
                    spaces = '  '
                else:
                    spaces = ' '
                print('{}.{}{}'.format(i, spaces, a.text))
                streams[i] = (a['href'])
                i += 1
    return streams

def getAceLinks(thread_info):
    os.system('cls')
    print('')
    print('{} - {} ({} CET)'.format(thread_info[0], thread_info[1], str(thread_info[2]).zfill(4)))
    print('')
    page = opener.open(thread_info[3])
    soup = BeautifulSoup(page, 'html.parser')
    ace = True
    i = 1
    streams = {}
    for item in soup.findAll('code'):
        if 'acestream://' in str(item):
            no_code_tag = str(item).split('<code>')[1].split('</code>')[0].strip()
            for b in no_code_tag.split('\n'):
                stream_link = b.split('acestream://')[1].split(' ')[0]
                stream_info = b.replace(('acestream://' + stream_link), '').strip()
                if i < 10:
                    spaces = '  '
                else:
                    spaces = ' '
                print('{}.{}{}'.format(i, spaces, stream_info))
                streams[i] = stream_link
                i += 1
    if not streams:
        shit = input('No acestreams. Get shit streams? (y/n): ')
        if shit == 'y':
            streams = getWebLinks(soup)
            if not streams:
                print('No shit streams either. Returning...')
                time.sleep(2)
                getMatchThreads()
            ace = False
        else:
            getMatchThreads()
    while True:
        print('')
        try:
            choice = int(input('Stream no.?: '))
            if ace:
                playAceStream(streams[choice])
            else:
                playWebStream(streams[choice])
        except KeyboardInterrupt:
            getMatchThreads()
        except Exception as e:
            continue

def getAceThreads(thread_info):
    ace_threads = {}
    i = 1
    for key, info in thread_info.items():
        for link in info[3]:
            page = opener.open(info[3])
            soup = BeautifulSoup(page, 'html.parser')
            
            for item in soup.findAll('code'):
                if 'acestream://' in str(item):
                    no_code_tag = str(item).split('<code>')[1].split('</code>')[0].strip()
                    for b in no_code_tag.split('\n'):
                        stream_link = b.split('acestream://')[1].split(' ')[0]
                        stream_info = b.replace(('acestream://' + stream_link), '').strip()
                        thread_info[key] = thread_info[key] + (stream_info, stream_link,)
                    i += 1
                else:
                    continue
    print(thread_info)
    sys.exit()
    
def printMatchMenu(thread_info):
    os.system('cls')
    print('')
    for key, info in thread_info.items():
        if key < 10:
            spaces = '  '
        else:
            spaces = ' '
        print('{}.{}{} - {} ({} CET)'.format(key, spaces, info[0], info[1], str(info[2]).zfill(4)))    
        

def getMatchThreads():
    os.system('cls')
    print('Fetching matches...')    
    uri = 'https://old.reddit.com/r/soccerstreams/'
    page = opener.open(uri)
    soup = BeautifulSoup(page, 'html.parser')
    thread_info = {} # key=i, values=(home_team[0], away_team[1], match_time[2], link[3])
    i = 1
    print('')
    for item in soup.findAll('div', {"class": re.compile('^ thing')}):
        match_url = item.get('data-permalink')
        if '_gmt_' in match_url:
            match_info = match_url.split('/')[5]
            match_time = int(match_info.split('_gmt_')[0])
            if match_time < 2200:
                match_time += 200
            else:
                match_time -= 2200
            home_team = ' '.join(match_info.split('_gmt_')[1].split('_vs_')[0].split('_')).title()
            try:
                away_team = ' '.join(match_info.split('_gmt_')[1].split('_vs_')[1].split('_')).title()
            except:
                away_team = ''
                
            link = base_url + match_url
            url = urllib.parse.urlsplit(link)
            url = list(url)
            url[2] = urllib.parse.quote(url[2])
            url = urllib.parse.urlunsplit(url)
            
            thread_info[i] = home_team, away_team, match_time, url
            
            i += 1
    
    printMatchMenu(thread_info)
    #print('')
    #only_ace = input('Only show matches with acestreams? (y/n): ')
    #if only_ace == 'y':
        #getAceThreads(thread_info)
    print('')
    try:
        choice = int(input('Match no.?: '))
        print('')
        getAceLinks(thread_info[choice])
    except KeyboardInterrupt:
        print('Exiting...')
        print('')
        sys.exit()
    except Exception as e:
        print(e)
        time.sleep(10)
        getMatchThreads()

getMatchThreads()
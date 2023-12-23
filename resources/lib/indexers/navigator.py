# -*- coding: utf-8 -*-

'''
    hir_tv Add-on
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html
import random

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

base_log_info = f'hirtv.hu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://hirtv.hu'

BR_VERS = [
    ['%s.0' % i for i in range(18, 43)],
    ['61.0.3163.79', '61.0.3163.100', '62.0.3202.89', '62.0.3202.94', '63.0.3239.83', '63.0.3239.84', '64.0.3282.186', '65.0.3325.162', '65.0.3325.181', '66.0.3359.117', '66.0.3359.139',
     '67.0.3396.99', '68.0.3440.84', '68.0.3440.106', '68.0.3440.1805', '69.0.3497.100', '70.0.3538.67', '70.0.3538.77', '70.0.3538.110', '70.0.3538.102', '71.0.3578.80', '71.0.3578.98',
     '72.0.3626.109', '72.0.3626.121', '73.0.3683.103', '74.0.3729.131'],
    ['11.0']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']

ind_ex = random.randrange(len(RAND_UAS))
r_u_a = RAND_UAS[ind_ex].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[ind_ex]))

cookies = {
    '_vid': '',
    'req_dt': '',
    '__e_inc': '1',
}

headers = {
    'authority': 'hirtv.hu',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': r_u_a,
    'x-requested-with': 'XMLHttpRequest',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))      

    def root(self):
        self.addDirectoryItem("Műsorok", f"get_musorok&url={base_url}/hirtv_musorok", '', 'DefaultFolder.png')
        self.addDirectoryItem("Videók", f"get_video", '', 'DefaultFolder.png')
        
        #Hiradók:
        hirado_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=|tags=hirad%C3%B3|videok_szama=150"
        hirado_quoted_url = quote_plus(hirado_url)
        self.addDirectoryItem("Hiradók", f"ext_categs&url={hirado_quoted_url}", '', 'DefaultFolder.png')        
        
        #Belföld:
        belfold_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=Belf%C3%B6ld|videok_szama=150"
        belfold_quoted_url = quote_plus(belfold_url)
        self.addDirectoryItem("Belföld", f"ext_categs&url={belfold_quoted_url}", '', 'DefaultFolder.png')        
        
        #Külföld:
        kulfold_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=K%C3%BClf%C3%B6ld|videok_szama=150"
        kulfold_quoted_url = quote_plus(kulfold_url)
        self.addDirectoryItem("Külföld", f"ext_categs&url={kulfold_quoted_url}", '', 'DefaultFolder.png')
        
        #live:
        self.addDirectoryItem("Élő", f"play_live&url=https://stream.hirtv.hu/delayed.php.m3u8", '', 'DefaultFolder.png', isFolder=False)        

        #-- TODO:
        # ezeknél valami miatt kevés tartalom jelenik csak meg
        # (a 150 videót így is betölti, de van hogy csak havi 1-2 videót mutat
        #  talán jobb ajax lehívás kellene..)
        #
        # #Színes:
        # szines_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=sz%C3%ADnes|videok_szama=150"
        # szines_quoted_url = quote_plus(szines_url)
        # self.addDirectoryItem("Színes", f"ext_categs&url={szines_quoted_url}", '', 'DefaultFolder.png')
        #
        # #Gazdaság:
        # gazdasag_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=Gazdas%C3%A1g|videok_szama=150"
        # gazdasag_quoted_url = quote_plus(gazdasag_url)
        # self.addDirectoryItem("Gazdaság", f"ext_categs&url={gazdasag_quoted_url}", '', 'DefaultFolder.png')
        #  
        # #sport:
        # sport_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=Sport|tags=|videok_szama=150"
        # sport_quoted_url = quote_plus(sport_url)
        # self.addDirectoryItem("Sport", f"ext_categs&url={sport_quoted_url}", '', 'DefaultFolder.png')
        #  
        # #Kultúra:
        # kultura_url = f"{base_url}/?block=Video_Endless_Ajax_2021&ajax=1&param=category=kultura|tags=|videok_szama=150"
        # kultura_quoted_url = quote_plus(kultura_url)
        # self.addDirectoryItem("Kultúra", f"ext_categs&url={kultura_quoted_url}", '', 'DefaultFolder.png')
        
        self.endDirectory()

    def extCatergorys(self, url, image_url, full_title, content):
        
        import requests
        from bs4 import BeautifulSoup
        import re        
        
        response = requests.get(url, cookies=cookies, headers=headers).json()
        
        results = []
        
        for block in response["blocks"]:
            soup = BeautifulSoup(block, "html.parser")
        
            title = soup.find("h2").get_text(strip=True)
        
            date_element = soup.find("span", class_="small")
            date = date_element.get_text(strip=True) if date_element else None
            date_day = re.findall(r'(.*).,', date)[0].strip()
            date_hour = re.findall(r'.,(.*)', date)[0].strip()
        
            image_url = soup.find("img")["src"]
        
            link = soup.find("a")["href"]
        
            entry = {
                "date_day": date_day,
                "date_hour": date_hour,
                "title": title,
                "image_url": image_url,
                "link": f"{base_url}{link}"
            }
        
            results.append(entry)
        
        for result in results:
            item_date_day = result['date_day']
            if item_date_day:
                try:
                    item_date_hour = result['date_hour']
                    
                    item_title = result['title']
                    item_image_url = result['image_url']
                    item_link = result['link']
                    
                    full_title = f'{item_date_day} - {item_date_hour} - {item_title}'
                    
                    content = f'{item_date_day} - {item_date_hour}\n\n{item_title}'
                    
                    self.addDirectoryItem(f'[B]{full_title}[/B]', f'ext_video&url={item_link}&image_url={item_image_url}&full_title={full_title}&content={content}', item_image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': content})        
                except:
                    xbmc.log(f'{base_log_info}| extCatergorys | item_date_day: {item_date_day}', xbmc.LOGINFO)

        self.endDirectory('movies')

    def getMusorok(self, url, image_url, full_title, content):
    
        html_source = requests.get(url, cookies=cookies, headers=headers)
        
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        shows = []
        
        for show_div in soup.find_all('div', class_='col-12 col-sm-6 col-md-4 mt-4'):
            title = show_div.find('h2', class_='font-weight-bold').text.strip()
        
            content_elem = show_div.find('div', class_='d-block mt-1')
            if content_elem:
                content_tag = content_elem.find('p')
                content = content_tag.text.strip() if content_tag else content_elem.text.strip()
            else:
                content = ''
        
            try:
                videok_url = re.findall(r'href=\"(/kereses.*)\"', str(show_div))[0].strip()
            except IndexError:
                print('')
        
            image_url = show_div.find('img', class_='img-fluid')['src']
        
            show_data = {
                'title': title,
                'content': content,
                'videok_url': videok_url,
                'image_url': image_url
            }
        
            shows.append(show_data)
        
        for show in shows:
            
            full_title = show['title']
            
            content = show['content']
            
            show_videok = show['videok_url']
            show_videok_url = f'https://hirtv.hu{show_videok}'
            show_videok_url = re.sub(r'&amp;', r'&', show_videok_url)
            
            show_image = show['image_url']
            item_image_url = f'https://hirtv.hu{show_image}'
            
            self.addDirectoryItem(f'[B]{full_title}[/B]', f'ext_musorok&url={quote_plus(show_videok_url)}&image_url={item_image_url}&full_title={full_title}&content={content}', item_image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': content})    
    
    
        self.endDirectory('movies')    

    def getVideo(self, url, image_url, full_title, content):
        
        import requests
        from bs4 import BeautifulSoup
        import re

        response = requests.get('https://hirtv.hu/?block=Video_Endless_Ajax_2021&ajax=1&page=1&param=category=|datum=|megjelenes=2|site=1|tags=|videok_szama=250', cookies=cookies, headers=headers).json()
        
        results = []
        
        for block in response["blocks"]:
            soup = BeautifulSoup(block, "html.parser")
        
            title = soup.find("h2").get_text(strip=True)
        
            date_element = soup.find("span", class_="small")
            date = date_element.get_text(strip=True) if date_element else None
            date_day = re.findall(r'(.*).,', date)[0].strip()
            date_hour = re.findall(r'.,(.*)', date)[0].strip()
        
            image_url = soup.find("img")["src"]
        
            link = soup.find("a")["href"]
        
            entry = {
                "date_day": date_day,
                "date_hour": date_hour,
                "title": title,
                "image_url": image_url,
                "link": f"{base_url}{link}"
            }
        
            results.append(entry)
        
        for result in results:
            item_date_day = result['date_day']
            if item_date_day:
                try:
                    item_date_hour = result['date_hour']
                    
                    item_title = result['title']
                    item_image_url = result['image_url']
                    item_link = result['link']
                    
                    full_title = f'{item_date_day} - {item_date_hour} - {item_title}'
                    
                    content = f'{item_date_day} - {item_date_hour}\n\n{item_title}'
                    
                    self.addDirectoryItem(f'[B]{full_title}[/B]', f'ext_video&url={item_link}&image_url={item_image_url}&full_title={full_title}&content={content}', item_image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': content})        
                except:
                    xbmc.log(f'{base_log_info}| getVideo | item_date_day: {item_date_day}', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def extVideo(self, url, image_url, full_title, content, genre):
        import requests
        import json
        from bs4 import BeautifulSoup
        import re
        
        html_source = requests.get(url, cookies=cookies, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        try:
            json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            
            video_object_data = {}
            
            for script in json_scripts:
                try:
                    data = json.loads(script.contents[0].strip())
                    if data.get('@type') == 'VideoObject':
                        video_object_data = data
                        break
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            
            try:
                genre = video_object_data['genre']
            except KeyError:
                genre = ''
            
            if content == None:
                content = full_title
            
            embedUrl = video_object_data['embedUrl']
        except:    
            embedUrl = re.findall(r'<meta.*content=\"(.*m3u8)\"', str(soup))[0].strip()
            genre = ''
            
            if content == None:
                content = full_title            

        self.addDirectoryItem(f'[B]{full_title}[/B]', f'play_movie&url={embedUrl}&image_url={image_url}&full_title={full_title}&content={content}&genre={genre}', image_url, 'DefaultMovies.png', isFolder=False, meta={'title': full_title, 'plot': f"{genre}\n{content}"})
        
        self.endDirectory('movies')

    def extMusorok(self, url, image_url, full_title, genre):

        resp = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.find_all('article')
        
        for article in articles:
            category_title_element = article.find('h4', class_='color-red')
            link_element = article.find('a', href=True)
            title_element = article.find('span', class_='font-weight-bold')
            image_element = article.find('img')

            if category_title_element and link_element and title_element:
                genre = category_title_element.text.strip()
                
                link = link_element['href']
                
                card_link = f'https://hirtv.hu{link}'
                
                full_title = title_element.text.strip()

                if image_element and 'src' in image_element.attrs:
                    image_url = image_element['src']
                else:
                    image_url = ''
                
                self.addDirectoryItem(f'[B]{full_title}[/B]', f'get_embed&url={card_link}&image_url={image_url}&full_title={full_title}&genre={genre}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': f"{genre}\n\n{full_title}"})
        
        try:
            next_page = soup.find('a', class_='font-weight-bold', string='>').get('href', None)
            if next_page:
                page_num = re.findall(r'_page=(.*)', str(next_page))[0].strip()
                get_searched = re.findall(r'search_txtf=(.*?)&', str(next_page))[0].strip()
                next_p = f'{base_url}/kereses?search_txtf={get_searched}&content_sel=video&datestart_txtf=&dateend_txtf=&current_page={page_num}'
                next_page_link_quoted_url = quote_plus(next_p)
                
                self.addDirectoryItem('[I]Következő oldal[/I]', f'ext_musorok&url={next_page_link_quoted_url}', '', 'DefaultFolder.png') 
        except AttributeError:
            xbmc.log(f'{base_log_info}| extMusorok | next_page_link | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def getEmbed(self, url, image_url, full_title, genre):

        response = requests.get(url, cookies=cookies, headers=headers).text
        
        try:
            embed_id = re.findall(r'iframe.*?src=\"https://.*?embed/(.*?)\"', str(response))[0].strip()
            
            video_url = f'{base_url}/video/{embed_id}'
            
            self.addDirectoryItem(f'[B]{full_title}[/B]', f'ext_video&url={video_url}&image_url={image_url}&full_title={full_title}&genre={genre}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': f"{genre}\n\n{full_title}"})
        except:
            xbmc.log(f'{base_log_info}| getEmbed | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("hirtv.hu", "Nem található videó a cikkben", time=5000)

        self.endDirectory('movies')

    def playMovie(self, url, image_url, full_title, genre):
        xbmc.log(f'{base_log_info}| playMovie | playing URL: {url}', xbmc.LOGINFO)

        play_item = xbmcgui.ListItem(path=url)
        from inputstreamhelper import Helper
        is_helper = Helper('hls')
        if is_helper.check_inputstream():
        
            play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
            
            try:
                play_item.setProperty('inputstream.adaptive.stream_headers', url.split("|")[1])
                play_item.setProperty('inputstream.adaptive.manifest_headers', url.split("|")[1])
            except:
                pass
            
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        
        xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def playLive(self, url):
        
        url_live = f'{url}|Origin=https%3A//hirtv.hu&Referer=https%3A//hirtv.hu&User-Agent=Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/71.0.3578.98%20Safari/537.36'
        
        xbmc.log(f'{base_log_info}| playMovie | url_live: {url_live}', xbmc.LOGINFO)
        
        play_item = xbmcgui.ListItem(path=url_live)
        
        xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)  
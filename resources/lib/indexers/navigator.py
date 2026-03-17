# -*- coding: utf-8 -*-

'''
    hir_tv Add-on
    Copyright (C) 2026 heg, vargalex

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
import resolveurl
from resources.lib.modules.utils import py2_decode, py2_encode
import html
import random

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

addon_obj = xbmcaddon.Addon()
version = addon_obj.getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

base_log_info = f'hirtv.hu | v{version} | Kodi: {kodi_version[:5]}'
xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

icon_png = os.path.join(addon_obj.getAddonInfo('path'), 'icon.png')

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_path = self.addon.getAddonInfo('path')
        self.addon_icon = os.path.join(self.addon_path, 'icon.png')
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            pass

    def root(self):
        self.addDirectoryItem(
            "Hír TV - 60 perccel késleltetett adás", "play_live&url=https://hirtv.origo.hu/adas",
            self.addon_icon, 'DefaultFolder.png', 
            isFolder=False, meta={'plot': '60 perccel késleltetett adás'})
        
        self.endDirectory()

    def playLive(self, url):
        try:
            resp = requests.get(url, timeout=20)
            v_id = re.search(r'videa\.hu/player\?v=([a-zA-Z0-9]+)', resp.text).group(1)
            test_url = f"https://videa.hu/player?v={v_id}"
            resolved_url = resolveurl.resolve(test_url)
            if resolved_url:
                play_item = xbmcgui.ListItem(path=resolved_url)
                if '.m3u8' in resolved_url.lower():
                    play_item.setProperty('inputstream', 'inputstream.adaptive')
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                    play_item.setMimeType('application/vnd.apple.mpegurl')
                    play_item.setContentLookup(False)
                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
            else:
                xbmcplugin.setResolvedUrl(syshandle, False, xbmcgui.ListItem())
        except Exception as e:
            xbmcplugin.setResolvedUrl(syshandle, False, xbmcgui.ListItem())

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

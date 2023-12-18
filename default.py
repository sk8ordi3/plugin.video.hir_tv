# -*- coding: utf-8 -*-

'''
    hir_tv Add-on
    Copyright (C) 2020 heg, vargalex

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

image_url = params.get('image_url')
full_title = params.get('full_title')
title = params.get('title')
content = params.get('content')
genre = params.get('genre')
next_page_link = params.get('next_page_link')

if action is None:
    navigator.navigator().root()

elif action == 'get_video':
    navigator.navigator().getVideo(url, image_url, full_title, content)

elif action == 'ext_video':
    navigator.navigator().extVideo(url, image_url, full_title, content, genre)
    
elif action == 'get_musorok':
    navigator.navigator().getMusorok(url, image_url, full_title, content)

elif action == 'ext_musorok':
    navigator.navigator().extMusorok(url, image_url, full_title, genre)

elif action == 'get_embed':
    navigator.navigator().getEmbed(url, image_url, full_title, genre)

elif action == 'ext_categs':
    navigator.navigator().extCatergorys(url, image_url, full_title, content)

elif action == 'play_movie':
    navigator.navigator().playMovie(url, image_url, full_title, genre)
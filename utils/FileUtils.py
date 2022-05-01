# -*- coding: utf-8 -*-
import os
from config.settings import BASE_DIR
from urllib.request import urlretrieve
import uuid


def get_and_save(source_url):
    if source_url[-3:] == 'gif':
        path = os.path.join(BASE_DIR, "sources", "GIF", "%s.gif" % ''.join(str(uuid.uuid1()).replace('-', '')))
    elif source_url[-3:] == 'png':
        path = os.path.join(BASE_DIR, "sources", "IMG", "%s.png" % ''.join(str(uuid.uuid1()).replace('-', '')))
    elif source_url[-3:] == 'jpg':
        path = os.path.join(BASE_DIR, "sources", "IMG", "%s.jpg" % ''.join(str(uuid.uuid1()).replace('-', '')))
    elif source_url[-3:] == 'mp3':
        path = os.path.join(BASE_DIR, "sources", "Mp3", "%s.mp3" % ''.join(str(uuid.uuid1()).replace('-', '')))
    elif source_url[-3:] == 'wav':
        path = os.path.join(BASE_DIR, "sources", "Mp3", "%s.wav" % ''.join(str(uuid.uuid1()).replace('-', '')))
    elif source_url[-3:] == 'mp4':
        path = os.path.join(BASE_DIR, "sources", "Video", "%s.mp4" % ''.join(str(uuid.uuid1()).replace('-', '')))
    else:
        return None
    urlretrieve(source_url, path)
    return path


def remove_file(*args):
    for file in args:
        if os.path.exists(file):
            os.remove(file)

# todo 增加移除目录和目录下的文件函数

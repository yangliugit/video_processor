# -*- coding: utf-8 -*-
from PIL import Image
import os
from utils.MyLog import globalLog
from config.settings import BASE_DIR
import uuid


class GIFSplit(object):

    def __init__(self, file_name):
        self.file_name = file_name      # 传入的文件名
        self.dir_name = self.file_name[:-4]     # 根据文件名创建存放分帧图片的文件夹
        # 拼接图片文件的完整路径, 路劲为： 根目录/sources/GIF/{file_name}
        self.gif_path = os.path.join(BASE_DIR, 'sources', 'GIF', file_name)
        self.gif_frames = self.make_dir()

    def make_dir(self):
        """用于创建存放分帧图片的文件夹"""
        gif_frame_path = os.path.join(os.path.dirname(self.gif_path), self.dir_name)
        try:
            os.mkdir(gif_frame_path)
            return gif_frame_path
        except FileExistsError:
            globalLog.warning('<%s>文件夹已存在' % gif_frame_path)
            new_gif_frame_path = os.path.join(os.path.dirname(self.gif_path), self.dir_name + '_' + str(uuid.uuid1()))
            os.mkdir(new_gif_frame_path)
            return new_gif_frame_path

    def framing(self):
        """GIF图片分帧"""
        img = Image.open(self.gif_path)
        try:
            while True:
                curr = img.tell()
                name = os.path.join(self.gif_frames, '%s.png' % str(curr + 1))
                img.save(name)
                img.seek(curr+1)
        except EOFError:
            return self.gif_frames


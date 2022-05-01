# -*- coding: utf-8 -*-
import cv2
import glob
import os
from config.settings import BASE_DIR
import uuid
from common.AnalysisMedia import avi_to_mp4
from utils.FileUtils import remove_file


def resize(img_array, align_mode):
    _height = len(img_array[0])
    _width = len(img_array[0][0])
    for i in range(1, len(img_array)):
        img = img_array[i]
        height = len(img)
        width = len(img[0])
        if align_mode == 'small':
            if height < _height:
                _height = height
            if width < _width:
                _width = width
        else:
            if height > _height:
                _height = height
            if width > _width:
                _width = width

    for i in range(0, len(img_array)):
        img1 = cv2.resize(img_array[i], (_width, _height), interpolation=cv2.INTER_CUBIC)
        img_array[i] = img1

    return img_array, (_width, _height)


def images_to_video(path, fps=24):
    img_array = []
    # 根据图片类型获取, 修改类型 和 截取参数
    png_list = sorted(glob.glob(path + '/*'), key=lambda x: int(os.path.basename(x)[:-4]))
    for filename in png_list:
        img = cv2.imread(filename)
        if img is None:
            print(filename + " is error!")
            continue
        img_array.append(img)

    # 图片的大小需要一致
    img_array, size = resize(img_array, 'small')
    # video_name = path.split('\\')[-1]
    video_out_path = os.path.join(BASE_DIR, 'sources', 'Video',
                                  'concatPNG_' + ''.join(str(uuid.uuid1())).replace('-', '') + '.avi')
    # fourcc: DIVX、
    out = cv2.VideoWriter(video_out_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    mp4_video = avi_to_mp4(video_out_path)
    remove_file(video_out_path)
    return mp4_video

if __name__ == '__main__':
    images_to_video(os.path.join(BASE_DIR, 'sources', 'GIF', '722d542400b811ec9bf4d050996a9735'))

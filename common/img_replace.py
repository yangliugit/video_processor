# -*- coding: utf-8 -*-
import cv2
import numpy as np
from config.settings import BASE_DIR
import os
import uuid
import time


def get_center(image):
    img = cv2.imread(image)

    # 获取图片的行、列、通道数
    image_rows, image_cols, image_channels = img.shape

    # 获取中心点
    center = [int(image_cols / 2), int(image_rows / 2)]

    return center


def backend_replace(image, backend):
    img = cv2.imread(image)
    # 固定参数缩放
    img = cv2.resize(img, (400, 450))

    img_back = cv2.imread(backend)
    # 固定参数缩放
    img_back = cv2.resize(img_back, (450, 650))

    # 更改背景图片比例，等比例缩放 0.2倍，参数可调整
    # img_back = cv2.resize(img_back, None, fx=0.8, fy=0.8)

    # 分析前景图片，准备抠图
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 设置抠图颜色区间，在区间内的值为255 - 白色， 低于low的值和高于up的值为 0 - 黑色
    # lower_color = np.array([78, 43, 46])
    # upper_color = np.array([99, 255, 255])

    lower_color = np.array([156, 43, 46])
    upper_color = np.array([180, 255, 255])

    # 抠图操作 - 使原图中需要抠出的区域变为黑色
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # 腐蚀、膨胀，去除白点
    erode = cv2.erode(mask, None, iterations=1)
    dilate = cv2.dilate(erode, None, iterations=1)

    # 获取缩放后图片的行列参数
    img_rows, img_cols, img_channels = img.shape
    back_rows, back_cols, back_channels = img_back.shape

    # 确定背景图起始替换点位置
    image_center = [int(img_rows / 2), int(img_cols / 2)]
    backend_center = [int(back_rows / 2), int(back_cols / 2)]

    # 遍历替换背景图中的点
    for i in range(img_rows):
        for j in range(img_cols):
            if dilate[i, j] == 0:
                img_back[backend_center[0] - image_center[0] + i, backend_center[1] - image_center[1] + j] \
                    = img[i, j]
    my_uuid = str(uuid.uuid1()).replace('-', '')
    img_back_path = os.path.join(BASE_DIR, 'sources', 'IMG', '%s.jpg' % my_uuid)
    cv2.imwrite(img_back_path, img_back)
    return img_back_path


def image_overlay(image_path, backend_path, x=562, y=1000, is_resize=0):
    """
    AI形象添加背景
    :param image_path: AI形象全路径
    :param backend_path: 背景全路径
    :param x: AI形象放置在背景的坐标点X
    :param y: AI形象放置在背景的坐标点Y
    :param is_resize: 是否更改AI形象，是 - 1， 否 - 0
    :return: 合成后的图片全路径
    """
    # start = time.time()
    # 入参需要判断，前景必须是png， 背景可以为jpg和png
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # 根据业务更改形象大小
    if is_resize == 1:
        image = cv2.resize(image, (342, 516))

    backend = cv2.imread(backend_path, cv2.IMREAD_UNCHANGED)
    # backend = cv2.resize(backend, (1398, 2106))
    # 获取原始背景图片的行、列、通道数
    backend_rows, backend_cols, backend_channels = backend.shape

    backend_bgra = None

    # 判断背景是三通道，如果是-增加alpha通道，默认255-全不透明；如果为4通道则不处理
    if backend_channels == 3:
        # 给背景jpg添加alpha通道
        b_channel, g_channel, r_channel = cv2.split(backend)
        # 255为完全不透明， 0 为完全透明; ones()-把数组元素全部变成 1
        alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
        backend_bgra = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    elif backend_channels == 4:
        backend_bgra = backend

    # 获取前景图片的行、列、通道数
    image_rows, image_cols, image_channels = image.shape

    """
    # 根据前景和背景中心位置替换背景
    # 获取中心位置
    backend_center = [int(backend_rows / 2), int(backend_cols / 2)]
    image_center = [int(image_rows / 2), int(image_cols / 2)]

    for i in range(image_rows):
        for j in range(image_cols):
            if not (image[i, j] == np.array([255, 255, 255, 0])).all():
                backend_bgra[backend_center[0] - image_center[0] + i, backend_center[1] - image_center[1] + j] \
                    = image[i, j]
    """
    # 自定义AI形象放置的点位
    backend_point = [int(y), int(x)]
    image_center = [int(image_rows / 2), int(image_cols / 2)]

    # print(image_center)
    # print([int(backend_rows / 2), int(backend_cols / 2)])
    # print(image[0, 0], image[0, 1])

    for i in range(image_rows):
        for j in range(image_cols):
            # 判断非透明像素，最后一个通道数=0，则为透明
            if not (image[i, j] == np.array([255, 255, 255, 0]))[3]:
                backend_bgra[backend_point[0] - image_center[0] + i, backend_point[1] - image_center[1] + j] \
                    = image[i, j]

    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    file_path = os.path.join(BASE_DIR, 'sources', 'IMG', f"{my_uuid}.png")
    cv2.imwrite(file_path, backend_bgra)
    # end = time.time() - start
    # print("1处理一次合并的时间为： %s " % str(end))
    return file_path


def background_add_image(image_path, backend_path, x=0, y=10, is_resize=0):
    """
    AI形象添加背景
    :param image_path: 前景图全路径
    :param backend_path: 背景图全路径
    :param x: 前景图在背景的坐标点X
    :param y: 前景图在背景的坐标点Y
    :param is_resize: 是否更改前景图大小，是 - 1， 否 - 0
    :return: 合成后的图片全路径
    """
    # 入参需要判断，前景必须是png， 背景可以为jpg和png
    # 读取前景和背景
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    backend = cv2.imread(backend_path, cv2.IMREAD_UNCHANGED)

    # 读取前景和背景图片的行、列、通道数
    image_rows, image_cols, image_channels = image.shape
    backend_rows, backend_cols, backend_channels = backend.shape

    # 根据业务更改前景图片固定大小
    if is_resize == 1:
        image = cv2.resize(image, (342, 516))
    # 适配背景宽度
    elif is_resize == 0:
        # 调整图片适配背景大小
        image = cv2.resize(image, (backend_cols, image_rows))

    backend_bgra = None
    img_bgra = None

    # 判断背景是三通道，如果是-增加alpha通道，默认255-全不透明；如果为4通道则不处理
    if backend_channels == 3:
        # 给背景jpg添加alpha通道
        b_channel, g_channel, r_channel = cv2.split(backend)
        # 255为完全不透明， 0 为完全透明; ones()-把数组元素全部变成 1
        alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
        backend_bgra = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    elif backend_channels == 4:
        backend_bgra = backend

    if image_channels == 3:
        # 给背景jpg添加alpha通道
        b_img_channel, g_img_channel, r_img_channel = cv2.split(image)
        # 255为完全不透明， 0 为完全透明; ones()-把数组元素全部变成 1
        alpha_channel = np.ones(b_img_channel.shape, dtype=b_img_channel.dtype) * 255
        img_bgra = cv2.merge((b_img_channel, g_img_channel, r_img_channel, alpha_channel))
    elif image_channels == 4:
        img_bgra = image

    # 重新获取前景图片的行、列、通道数，因为上面根据业务转换过大小
    c_image_rows, c_image_cols, c_image_channels = img_bgra.shape

    # 自定义AI形象放置的点位
    backend_point = [int(y), int(x)]

    # cv2.imshow('fg', img_bgra)
    # cv2.imshow('bg', backend_bgra)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    for i in range(c_image_rows):
        for j in range(c_image_cols):
            # 判断是否存在像素
            if any(np.array(img_bgra[i, j])):
                backend_bgra[backend_point[0] + i, backend_point[1] + j] = img_bgra[i, j]

    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    file_path = os.path.join(BASE_DIR, 'sources', 'IMG', f"addPNG_{my_uuid}.png")
    cv2.imwrite(file_path, backend_bgra)
    # end = time.time() - start
    return file_path


# def image_overlay2(image_path, backend_path, x=562, y=1000):
#     """
#     AI形象添加背景
#     :param image_path: AI形象全路径
#     :param backend_path: 背景全路径
#     :param x: AI形象放置在背景的坐标点X
#     :param y: AI形象放置在背景的坐标点Y
#     :return: 合成后的图片全路径
#     """
#     start = time.time()
#     # 入参需要判断，前景必须是png， 背景可以为jpg和png
#     image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
#     image = cv2.resize(image, (400, 450))
#
#     backend = cv2.imread(backend_path, cv2.IMREAD_UNCHANGED)
#     # backend = cv2.resize(backend, (1398, 2106))
#     # 获取原始背景图片的行、列、通道数
#     backend_rows, backend_cols, backend_channels = backend.shape
#
#     # 获取前景图片的行、列、通道数
#     image_rows, image_cols, image_channels = image.shape
#
#     backend_bgra = None
#
#     # 判断背景是三通道，如果是-增加alpha通道，默认255-全不透明；如果为4通道则不处理
#     if backend_channels == 3:
#         # 给背景jpg添加alpha通道
#         b_channel, g_channel, r_channel = cv2.split(backend)
#         # 255为完全不透明， 0 为完全透明
#         alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
#         backend_bgra = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
#     elif backend_channels == 4:
#         backend_bgra = backend
#
#     # 自定义AI形象放置的点位
#     backend_point = [int(y), int(x)]
#     image_center = [int(image_rows / 2), int(image_cols / 2)]
#
#     roi = backend_bgra[0:image_rows, 0:image_cols]
#     # TODO TODO
#     img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     ret, mask = cv2.threshold(img2gray, 170, 255, cv2.THRESH_BINARY)
#     mask_inv = cv2.bitwise_not(mask)
#     img1_bg = cv2.bitwise_and(roi, roi, mask=mask)
#     img1_fg = cv2.bitwise_and(image, image, mask=mask_inv)
#
#     cv2.imshow('mask', mask)
#     cv2.imshow('inv', mask_inv)
#     cv2.imshow('backend', img1_bg)
#     cv2.imshow('fg', img1_fg)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#
#
#     # my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
#     # file_path = os.path.join(BASE_DIR, 'sources', 'IMG', f"{my_uuid}.png")
#     # cv2.imwrite(file_path, roi)
#     # end = time.time() - start
#     # print("2处理一次合并的时间为： %s " % str(end))
#     # return file_path
#     end = time.time() - start
#     print("2处理一次合并的时间为： %s " % str(end))

if __name__ == '__main__':
    # image1 = r'E:\py_project\video_synthetic\sources\IMG\pic\2x\1@2x.png'
    image1 = r'E:\py_project\video_synthetic\sources\IMG\3893255b30ee11eca7bee1d87dc47399.jpg'
    backend1 = r'E:\py_project\video_synthetic\sources\IMG\ca89fb7930ef11eca548e1d87dc47399.png'

    p1 = background_add_image(image1, backend1, 0, 0)
    print(p1)

# p2 = image_overlay2(image1, backend1, 562, 900)

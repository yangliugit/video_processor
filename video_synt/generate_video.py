# -*- coding: utf-8 -*-
from common.SplitGIF import GIFSplit
from common.ImgMergeVideo import images_to_video
from common.AnalysisMedia import *
from utils.MyLog import globalLog
import time
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from utils.FileUtils import get_and_save, remove_file
from utils.alioss import upload_file_to_oss
from common.img_replace import image_overlay
from common.img_replace import get_center
from common.img_replace import background_add_image
import shutil
from common.image_add_text import ImgText

app = FastAPI()


class Image(BaseModel):
    imageUrl: str = None


class FigureRequest(BaseModel):
    # source_list
    sourceURLs: list = None

    # 0-IMG_list，1-GIF_list
    sourceType: str = None

    # 背景图片 jpg or png
    backendURL: str = None

    # 形象放置点位
    point: list = None


class Mp3Video(BaseModel):
    mp3URL: str = None
    figureURL: str = None
    duration: float = None


class ConcatVideo(BaseModel):
    videoList: list = None


class TextBaseVideoRequest(BaseModel):
    # source_list
    sourceURLs: list = None

    # 0-IMG_list，1-GIF_list
    sourceType: str = None

    # 背景图片 jpg or png
    backendURL: str = None

    # 形象放置点位
    point: list = None

    # 文字放置点位
    textPoint: list = None

    # 文字
    text: str = None

    # 文字大小
    fontSize: int = None

    # 文字颜色
    fontColor: list = None

    # 标题参数 {"titleText": "", "titleSize": 1, "titleColor": [255, 255, 255], "titlePoint": [100, 200]}
    titleInfo: dict = None

    # 作者参数 {"ownText": "", "ownSize": 1, "ownColor": [255, 255, 255], "ownPoint": [100, 200]}
    ownInfo: dict = None

    # 前景图片 {"frontImageUrl": "", "frontImagePoint": [], "isResize": 0}
    frontImageInfo: dict = None


@app.post("/video/getCenter")
def get_image_center(request_date: Image):
    start = time.time()
    image_url = request_date.imageUrl

    response = {"code": "999999", "message": "get image's center fail", "time": 0, "center": []}

    # 参数校验
    if image_url.endswith('.png') or image_url.endswith('.jpg'):
        try:
            # 保存图片
            image_path = get_and_save(image_url)

            # 获取中心点
            center = get_center(image_path)

            response["code"] = "000000"
            response["message"] = "get center success"
            response["time"] = time.time() - start
            response["center"] = center

            return response

        except Exception as e:
            globalLog.exception(e)
            response["message"] = str(e)
            response["time"] = time.time() - start
            return response
    else:
        response["message"] = "image's type error"
        return response


@app.post("/video/generateFigure")
def generate_figure(request_date: FigureRequest):
    start = time.time()
    source_list = request_date.sourceURLs
    source_type = request_date.sourceType
    backend_url = request_date.backendURL
    point = request_date.point
    x = point[0]
    y = point[1]

    response = {"code": "999999", "message": "sourceList error", "time": 0, "videoUrl": "", "videoDuration": 0}

    try:
        # 预设形象路径
        path = os.path.join(BASE_DIR, 'sources', 'IMG', f"{''.join(str(uuid.uuid1()).replace('-', ''))}")
        os.makedirs(path)

        if backend_url:
            # 保存背景图片
            backend_path = get_and_save(backend_url)

            # 资源列表过滤，参数校验
            if source_type == "0":
                deal_list = [pic for pic in source_list if pic.endswith('.png')]
                if deal_list:
                    for index, source in enumerate(deal_list):
                        # todo 开启多线程下载到本地
                        img_path = get_and_save(source)
                        result_path = image_overlay(img_path, backend_path, x, y)

                        # 移动合并背景的图片到指定目录path下
                        os.rename(result_path, os.path.join(path, f"{str(index + 1)}.png"))

                else:
                    response["time"] = time.time() - start
                    return response

            elif source_type == "1":
                deal_list = [gif for gif in source_list if gif.endswith('.gif')]
                if deal_list:
                    gif_path = get_and_save(deal_list[0])

                    # 拆分GIF -> png
                    gif_to_png_path = GIFSplit(gif_path[-36:]).framing()

                    for img in os.listdir(gif_to_png_path):
                        img_path = os.path.join(gif_to_png_path, img)
                        print(img_path)
                        result_path = image_overlay(img_path, backend_path, x, y)

                        # 移动合并的图片到指定目录path下
                        os.rename(result_path, os.path.join(path, f"{str(img[:-4])}.png"))

                else:
                    response["time"] = time.time() - start
                    return response

            # 根据图片路径生成视频
            video_path = images_to_video(path, 24)
            globalLog.info("PNG to video success, videoPath : %s " % video_path)

            # 获取video时长
            video_duration = duration_video(video_path)
            globalLog.info("Video's duration : %s " % video_duration)

            # 上传 oss
            oss_path = upload_file_to_oss(video_path)

            if oss_path:
                globalLog.info("Video upload success, url : %s " % oss_path)
                # remove_file(png_to_video_path)
                # globalLog.info("Video remove from local success...... ")
                response["code"] = '000000'
                response["message"] = 'success'
                response["time"] = time.time() - start
                response["videoUrl"] = oss_path
                response["videoDuration"] = video_duration
                return response
            else:
                globalLog.error("Video upload fail, videoPath : %s " % video_path)
                response["message"] = 'Upload OSS fail'
                response["time"] = time.time() - start
                return response
    except Exception as e:
        globalLog.exception(e)
        response["message"] = str(e)
        response["time"] = time.time() - start
        return response


@app.post("/video/mp3ToVideo")
def mp3_to_video(request_date: Mp3Video):
    start = time.time()
    mp3_url = request_date.mp3URL
    base_video_url = request_date.figureURL
    base_video_duration = request_date.duration
    try:
        # 参数校验
        # print(png_path)
        # if png_path.endswith(".gif") is False:
        #     return {"code": "999999", "message": "参数类型错误，请上传gif: ", "time": time.time() - start}

        # save Mp3
        mp3_path = get_and_save(mp3_url)
        globalLog.info("Save mp3 success, Mp3Path: %s " % mp3_path)
        # 获取 Mp3 时长
        mp3_duration = duration_mp3(mp3_path)
        globalLog.info("Mp3's duration : %s " % mp3_duration)

        # save Video
        video_path = get_and_save(base_video_url)
        globalLog.info("Save base video success, VideoPath: %s " % video_path)

        # 根据时长生成视频
        if base_video_duration != 0:
            times = int(mp3_duration / base_video_duration)
        else:
            raise ZeroDivisionError
        globalLog.info("wait cut video's duration : %s " % str((times+1) * base_video_duration))
        globalLog.info("Video cycle times :  %s " % str(times + 1))
        concat_video_path = concat_video_by_times(video_path, 24, times + 1, cut_end_time=mp3_duration)
        globalLog.info("Generate videos success, path : %s " % concat_video_path)

        # 添加背景音乐
        add_path = video_add_audio(concat_video_path, mp3_path, 24)
        globalLog.info("Video add Mp3 success, path : %s " % add_path)

        oss_path = upload_file_to_oss(add_path)
        if oss_path:
            globalLog.info("Video upload success, url : %s " % oss_path)
            # remove_file(png_to_video_path)
            # globalLog.info("Video remove from local success...... ")
            return {"code": "000000", "message": "success", "time": time.time() - start, "videoUrl": oss_path}
        else:
            globalLog.error("Video upload fail, videoPath : %s " % add_path)
            return {"code": "999999", "message": "视频文件上传阿里云失败", "time": time.time() - start, "videoUrl": oss_path}
    except Exception as e:
        globalLog.exception(e)
        return {"code": "999999", "message": "系统未知异常: " + str(e), "time": time.time() - start}


@app.post("/video/textBaseVideo")
def generate_figure_text(request_date: TextBaseVideoRequest):
    start = time.time()
    source_list = request_date.sourceURLs
    source_type = request_date.sourceType
    backend_url = request_date.backendURL
    point = request_date.point
    text_point = request_date.textPoint
    text = request_date.text
    font_size = request_date.fontSize
    font_color = request_date.fontColor
    title_info = request_date.titleInfo
    own_info = request_date.ownInfo
    front_image_info = request_date.frontImageInfo
    if font_color:
        font_color = tuple(font_color)

    # 前景图片预留判断
    front_image_path = None

    x = point[0]
    y = point[1]
    text_x = text_point[0]
    text_y = text_point[1]

    response = {"code": "999999", "message": "sourceList error", "time": 0, "videoUrl": "", "videoDuration": 0}

    try:
        # 预设形象路径
        path = os.path.join(BASE_DIR, 'sources', 'IMG', f"{''.join(str(uuid.uuid1()).replace('-', ''))}")
        os.makedirs(path)

        if backend_url:
            # 保存背景图片
            backend_path = get_and_save(backend_url)
            if front_image_info:
                front_image_path = get_and_save(front_image_info["frontImageUrl"])
            globalLog.info("save backend png success, path: %s" % backend_path)

            # 资源列表过滤，参数校验
            if source_type == "0":
                deal_list = [pic for pic in source_list if pic.endswith('.png')]
                if deal_list:
                    for index, source in enumerate(deal_list):
                        # todo 开启多线程下载到本地
                        img_path = get_and_save(source)

                        # 开始背景图片添加形象
                        backend_add_figure_path = image_overlay(img_path, backend_path, x, y, 0)

                        # 开始背景图片添加正文
                        result_path = ImgText(text, backend_add_figure_path, font_size, font_color, text_x, text_y).draw_text()
                        if title_info: # {"titleText": "", "titleSize": 1, "titleColor": [255, 255, 255], "titlePoint": [100, 200]}
                            result_path = ImgText(title_info["titleText"], result_path, title_info["titleSize"], tuple(title_info["titleColor"]), title_info["titlePoint"][0], title_info["titlePoint"][1]).draw_text()
                        if own_info: # {"ownText": "", "ownSize": 1, "ownColor": [255, 255, 255], "ownPoint": [100, 200]}
                            result_path = ImgText(own_info["ownText"], result_path, own_info["ownSize"], tuple(own_info["ownColor"]), own_info["ownPoint"][0], own_info["ownPoint"][1]).draw_text()
                        if front_image_info: # {"frontImageUrl": "", "frontImagePoint": [], "isResize": 0}
                            result_path = background_add_image(front_image_path, result_path, front_image_info["frontImagePoint"][0], front_image_info["frontImagePoint"][1], front_image_info["isResize"])
                            print(result_path)

                        # 移动合并背景的图片到指定目录path下
                        os.rename(result_path, os.path.join(path, f"{str(index + 1)}.png"))

                else:
                    response["time"] = time.time() - start
                    return response

            # 根据图片路径生成视频
            video_path = images_to_video(path, 24)
            # video_path = images_to_video(path, len(source_list))
            globalLog.info("PNG to video success, videoPath : %s " % video_path)

            # 获取video时长
            video_duration = duration_video(video_path)
            globalLog.info("Video's duration : %s " % video_duration)

            # 上传 oss
            oss_path = upload_file_to_oss(video_path)

            if oss_path:
                globalLog.info("Video upload success, url : %s " % oss_path)
                # remove_file(png_to_video_path)
                # globalLog.info("Video remove from local success...... ")
                response["code"] = '000000'
                response["message"] = 'success'
                response["time"] = time.time() - start
                response["videoUrl"] = oss_path
                response["videoDuration"] = video_duration
                return response
            else:
                globalLog.error("Video upload fail, videoPath : %s " % video_path)
                response["message"] = 'Upload OSS fail'
                response["time"] = time.time() - start
                return response
    except Exception as e:
        globalLog.exception(e)
        response["message"] = str(e)
        response["time"] = time.time() - start
        return response


@app.post('/video/concatVideos')
def concat_videos(request_date: ConcatVideo):
    start = time.time()
    video_url_list = request_date.videoList

    response = {"code": "999999", "message": "videoList error", "time": 0, "videoUrl": ""}

    deal_list = [video_url for video_url in video_url_list if video_url.endswith('.mp4')]

    try:
        # 参数校验
        if deal_list:
            # 合并视频
            result_path = concat_video_by_urls(deal_list)
            # 上传oss
            oss_path = upload_file_to_oss(result_path)

            if oss_path:
                globalLog.info("Video upload success, url : %s " % oss_path)
                # remove_file(png_to_video_path)
                # globalLog.info("Video remove from local success...... ")
                response["code"] = '000000'
                response["message"] = 'success'
                response["time"] = time.time() - start
                response["videoUrl"] = oss_path
                return response
            else:
                globalLog.error("Video upload fail, videoPath : %s " % result_path)
                response["message"] = 'Upload OSS fail'
                response["time"] = time.time() - start
                return response
        else:
            response["message"] = 'without .mp4 file in list'
            return response

    except Exception as e:
        globalLog.exception(e)
        response["message"] = str(e)
        response["time"] = time.time() - start
        return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=10012,
                workers=1)

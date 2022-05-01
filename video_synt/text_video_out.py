# -*- coding: utf-8 -*-
from common.image_add_text import ImgText
import time
from common.AnalysisMedia import *
from utils.FileUtils import get_and_save, remove_file
from common.img_replace import image_overlay
from common.SplitGIF import GIFSplit
from common.ImgMergeVideo import images_to_video
from utils.alioss import upload_file_to_oss
from utils.MyLog import globalLog
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel


app = FastAPI()


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


@app.post("/video/textBaseVideo")
def generate_figure(request_date: TextBaseVideoRequest):
    start = time.time()
    source_list = request_date.sourceURLs
    source_type = request_date.sourceType
    backend_url = request_date.backendURL
    point = request_date.point
    text_point = request_date.textPoint
    text = request_date.text
    font_size = request_date.fontSize
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

            # 资源列表过滤，参数校验
            if source_type == "0":
                deal_list = [pic for pic in source_list if pic.endswith('.png')]
                if deal_list:
                    for index, source in enumerate(deal_list):
                        # todo 开启多线程下载到本地
                        img_path = get_and_save(source)

                        # 开始背景图片添加形象
                        backend_add_figure_path = image_overlay(img_path, backend_path, x, y)

                        # 开始背景图片添加文字
                        result_path = ImgText(text, backend_add_figure_path, font_size, text_x, text_y).draw_text()

                        # 移动合并背景的图片到指定目录path下
                        os.rename(result_path, os.path.join(path, f"{str(index + 1)}.png"))

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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=10013,
                workers=1)

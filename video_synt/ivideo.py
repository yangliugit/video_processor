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
app = FastAPI()


class Gif(BaseModel):
    gif_url: str = None


class Png(BaseModel):
    png_path: str = None


class Mp3Video(BaseModel):
    mp3_url: str = None
    base_video_url: str = None
    base_video_duration: float = None


@app.post("/video/gifToVideo")
def gif_to_video(request_date: Gif):
    start = time.time()
    gif_url = request_date.gif_url
    try:
        # 参数校验
        if gif_url.endswith(".gif") is False:
            return {"code": "999999", "message": "参数 错误，请上传gif: ", "time": time.time() - start}

        # 保存gif
        gif_path = get_and_save(gif_url)
        globalLog.info("Save gif success, gifPath: %s " % gif_path)

        # 拆分GIF -> png
        gif_to_png_path = GIFSplit(gif_path[-36:]).framing()
        globalLog.info("Split GIF success, PNGPath: %s " % gif_to_png_path)

        # png to video
        png_to_video_path = images_to_video(gif_to_png_path, 24)
        globalLog.info("PNG to video success, videoPath : %s " % png_to_video_path)

        # 获取video时长
        video_duration = duration_video(png_to_video_path)
        globalLog.info("Video's duration : %s " % video_duration)

        oss_path = upload_file_to_oss(png_to_video_path)
        if oss_path:
            globalLog.info("Video upload success, url : %s " % oss_path)
            # remove_file(png_to_video_path)
            # globalLog.info("Video remove from local success...... ")
            return {"code": "000000", "message": "success", "time": time.time() - start, "videoUrl": oss_path,
                    "videoDuration": video_duration}
        else:
            globalLog.error("Video upload fail, videoPath : %s " % png_to_video_path)
            return {"code": "999999", "message": "视频文件上传阿里云失败", "time": time.time() - start, "videoUrl": oss_path}
    except Exception as e:
        globalLog.error(str(e))
        return {"code": "999999", "message": "系统未知异常: " + str(e), "time": time.time() - start}


@app.post("/video/jpgToVideo")
def jpg_to_video(request_date: Png):
    start = time.time()
    png_path = request_date.png_path
    try:
        # 参数校验
        pass

        # png to video
        png_to_video_path = images_to_video(png_path, 24)
        globalLog.info("jpg to video success, videoPath : %s " % png_to_video_path)

        # 获取video时长
        video_duration = duration_video(png_to_video_path)
        globalLog.info("Video's duration : %s " % video_duration)

        oss_path = upload_file_to_oss(png_to_video_path)
        if oss_path:
            globalLog.info("Video upload success, url : %s " % oss_path)
            # remove_file(png_to_video_path)
            # globalLog.info("Video remove from local success...... ")
            return {"code": "000000", "message": "success", "time": time.time() - start, "videoUrl": oss_path,
                    "videoDuration": video_duration}
        else:
            globalLog.error("Video upload fail, videoPath : %s " % png_to_video_path)
            return {"code": "999999", "message": "视频文件上传阿里云失败", "time": time.time() - start, "videoUrl": oss_path}
    except Exception as e:
        globalLog.error(str(e))
        return {"code": "999999", "message": "系统未知异常: " + str(e), "time": time.time() - start}


@app.post("/video/mp3ToVideo")
def mp3_to_video(request_date: Mp3Video):
    start = time.time()
    mp3_url = request_date.mp3_url
    base_video_url = request_date.base_video_url
    base_video_duration = request_date.base_video_duration
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
        globalLog.info("Video cycle times :  %s " % str(times + 1))
        concat_video_path = concat_video_by_times(video_path, 24, times + 1)
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
        globalLog.error(str(e))
        return {"code": "999999", "message": "系统未知异常: " + str(e), "time": time.time() - start}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=10012,
                workers=1)

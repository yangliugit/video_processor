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


class Item1(BaseModel):
    # gif_url: str = None
    mp3_url: str = None


@app.post("/video/giftovideo")
@globalLog.catch()
def video_synt(request_date: Item1):
    start = time.time()
    # gif_url = request_date.gif_url
    mp3_url = request_date.mp3_url
    try:
        # Todo 参数校验
        pass
        # gif_path = get_and_save(gif_url)
        # globalLog.info("Save gif success, gifPath: %s " % gif_path)
        mp3_path = get_and_save(mp3_url)
        globalLog.info("Save mp3 success, Mp3Path: %s " % mp3_path)

        # gif_to_png_path = GIFSplit(gif_path[-36:]).framing()
        # gif_to_png_path = os.path.join(BASE_DIR, 'sources', 'IMG', 'cut_pic')
        # png_to_video_path = images_to_video(gif_to_png_path, 24)
        png_to_video_path = os.path.join(BASE_DIR, 'sources', 'Video', 'default_video.avi')

        globalLog.info("Begin generate video !")
        mp3_duration = duration_mp3(mp3_path)
        # video_duration = duration_video(png_to_video_path)
        video_duration = 0.96
        globalLog.info("Video's duration : %s " % video_duration)
        globalLog.info("Mp3's duration : %s " % mp3_duration)
        if video_duration != 0:
            times = int(mp3_duration / video_duration)
        else:
            raise ZeroDivisionError
        globalLog.info("video cycle times :  %s " % str(times + 1))
        concat_video_path = concat_video_by_times(png_to_video_path, 24, times+1)
        globalLog.info("Generate videos success, path : %s " % concat_video_path)
        add_path = video_add_audio(concat_video_path, mp3_path, 24)
        globalLog.info("Video add Mp3 success, path : %s " % add_path)
        oss_path = upload_file_to_oss(add_path)
        if oss_path:
            remove_file(concat_video_path, add_path, mp3_path)
            globalLog.info("Video remove success...... ")
            globalLog.info("Video upload success, url : %s " % oss_path)
            return {"message": "success", "time": time.time() - start, "video_url": oss_path}
        else:
            globalLog.error("Video upload fail, path : %s " % add_path)
            return {"message": "fail", "time": time.time() - start, "video_url": None}
    except Exception as e:
        globalLog.error(str(e))
        return {"message": "系统未知异常: " + str(e), "time": time.time() - start}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=10012,
                workers=1)

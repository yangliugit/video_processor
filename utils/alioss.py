# -*- coding: utf-8 -*-
import oss2
import time

ENDPOINT = "http://oss-cn-hangzhou.aliyuncs.com"
ACCESS_KEY_ID = "*******"
ACCESS_KEY_SECRET = "************"
BUCKET_NAME = "vdp-cool"


def upload_file_to_oss(all_file_name):
    today = time.strftime('%Y%m%d', time.localtime())
    source_url = "http://vdp-cool.oss-cn-hangzhou.aliyuncs.com/"
    online_file_path = 'myvideo/' + today + '/' + all_file_name[-36:]
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    result = bucket.put_object_from_file(online_file_path, all_file_name)
    if result.status == 200:
        return source_url + online_file_path

# if __name__ == '__main__':
#     a = upload_file_to_oss(
#         r'E:\py_project\video_synthetic\sources\Video\video_audio_add_2d471e26fb7511ebbf5ad050996a9735.mp4')
#     print(a)

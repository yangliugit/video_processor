# -*- coding: utf-8 -*-
import librosa
from config.settings import BASE_DIR
from moviepy.editor import *
from utils import voice_changer
import natsort
from random import randint
import os
import uuid
from utils.FileUtils import get_and_save

target_path = os.path.join(BASE_DIR, 'sources')


def duration_mp3(audio_path):
    duration = librosa.get_duration(filename=audio_path)
    return duration


def duration_video(video_path):
    clip = VideoFileClip(video_path)
    return clip.duration


def get_audio_from_video(video_path):
    """
    func-根据视频文件获取视频中的音频, 返回音频路径
    :param video_path: 视频路径
    :return: 音频存放路径
    """
    # 处理路径
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    target_audio_path = os.path.join(target_path, 'Mp3')
    if not os.path.exists(target_audio_path):
        os.makedirs(target_audio_path)
    audio_file_path = os.path.join(target_audio_path, f'{my_uuid}.wav')
    # 视频/音频处理
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_file_path)
    return audio_file_path


def update_bgm_vol(bgm_path, multiples):
    """
    func - 调整音量倍数
    :param bgm_path: 音乐路径
    :param multiples: 音量倍数
    :return: 调整后的音乐文件路径
    """
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    music = AudioFileClip(bgm_path)
    target_audio_path = os.path.join(target_path, 'Mp3')
    if not os.path.exists(target_audio_path):
        os.makedirs(target_audio_path)
    mul_audio_file_path = os.path.join(target_audio_path, f'multiples_{my_uuid}.wav')
    # 调整音量的倍数
    out_music = music.fx(afx.volumex, multiples).fx(afx.audio_fadein, 0.5).fx(afx.audio_fadeout, 1)
    # 保存调整后的音乐
    out_music.write_audiofile(mul_audio_file_path)
    return mul_audio_file_path


def voice_change(audio_path):
    """

    :param audio_path:
    :return:
    """
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    target_voice_path = os.path.join(target_path, 'Mp3')
    if not os.path.exists(target_voice_path):
        os.makedirs(target_voice_path)
    change_voice_path = os.path.join(target_voice_path, f'change_{my_uuid}.wav')
    # 加载音乐资源
    y, sr = librosa.load(audio_path)

    # 修改
    """
     '''机器人'''
    # y = speed(3, y, sr)
    # y = spread(3, y, sr)

    '''童声'''
    #y = pitch(6, y, sr)
    #y = shrinkstep(10, y, sr)
    """
    voice_changer.pitch(6, y, sr)
    y = voice_changer.shrinkstep(10, y, sr)
    librosa.output.write_wav(change_voice_path, y, sr)
    return change_voice_path


def cut_video(old_path, tuple_list):
    """
    :param old_path: 待切割视频
    :param tuple_list: 支持多组分段切割，参数-[('00:00:06', '00:11:06'),('11:11:06', '11:11:20')]
    :return:
    """
    if os.path.exists(old_path):
        # 创建目录
        file_name = os.path.basename(os.path.splitext(old_path)[0])
        video_path = os.path.join(target_path, file_name)
        if not os.path.exists(video_path):
            os.makedirs(video_path)

        # 处理视频
        video = VideoFileClip(old_path)
        video_long = video.duration
        for tp in tuple_list:
            start_time = int(tp[0].split(':')[0]) * 3600 + int(tp[0].split(':')[1]) * 60 + int(tp[0].split(':')[2]) * 1
            end_time = int(tp[1].split(':')[0]) * 3600 + int(tp[1].split(':')[1]) * 60 + int(tp[1].split(':')[2]) * 1
            if video_long > end_time:
                cut = video.subclip(start_time, end_time)
                cut.write_videofile(os.path.join(video_path, f"{file_name}-{start_time}~{end_time}.mp4"))
            else:
                print("时间区间有误，请修正！！！")
        return video_path


def concat_video(wait_concat_path):
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    video_list = []
    for root, dirs, files in os.walk(wait_concat_path):
        files = natsort.natsorted(files)
        for file in files:
            if os.path.splitext(file)[1] == '.mp4':
                file_path = os.path.join(root, file)
                video = VideoFileClip(file_path)
                print(video.size)
                video_list.append(video.resize([1280, 960]))
    final_clip = concatenate_videoclips(video_list)
    target_concat_path = os.path.join(target_path, 'Video')
    if not os.path.exists(target_concat_path):
        os.makedirs(target_concat_path)
    concat_file_path = os.path.join(target_concat_path, f"concat_video_{my_uuid}.mp4")
    final_clip.write_videofile(concat_file_path, fps=24, codec="mpeg4", remove_temp=True)
    return concat_file_path


def concat_video_by_times(video_path, fps=24, times=1, cut_end_time=None):
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    video_list = []
    video = VideoFileClip(video_path)
    for i in range(0, times):
        video_list.append(video)
    # 根据入参cut_end_time 剪切视频

    if cut_end_time:
        final_clip = concatenate_videoclips(video_list).subclip(0, cut_end_time)
    else:
        final_clip = concatenate_videoclips(video_list)
    target_concat_path = os.path.join(target_path, 'Video')
    if not os.path.exists(target_concat_path):
        os.makedirs(target_concat_path)
    concat_file_path = os.path.join(target_concat_path, f"concat_video_{my_uuid}.mp4")
    final_clip.write_videofile(concat_file_path, fps=fps, codec="libx264", remove_temp=True)
    return concat_file_path


def concat_video_by_urls(video_url_list, fps=24):
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    video_list = []
    for video_url in video_url_list:
        save_path = get_and_save(video_url.strip())
        video = VideoFileClip(save_path)
        video_list.append(video)
    final_clip = concatenate_videoclips(video_list)
    # final_clip = CompositeVideoClip(video_list)
    target_concat_path = os.path.join(target_path, 'Video')
    if not os.path.exists(target_concat_path):
        os.makedirs(target_concat_path)
    concat_file_path = os.path.join(target_concat_path, f"concat_video_{my_uuid}.mp4")
    final_clip.write_videofile(concat_file_path, fps=fps, codec="libx264", remove_temp=True)
    return concat_file_path


def video_add_audio(video, audio, fps=24):
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    target_add_path = os.path.join(target_path, 'Video', f'video_audio_add_{my_uuid}.mp4')
    video_vfc = VideoFileClip(video)
    add_video = video_vfc.set_audio(AudioFileClip(audio))
    add_video.write_videofile(target_add_path, fps=fps, codec="libx264", remove_temp=True)
    return target_add_path


def avi_to_mp4(video_path, fps=24):
    my_uuid = ''.join(str(uuid.uuid1())).replace('-', '')
    video = VideoFileClip(video_path)
    save_path = os.path.join(target_path, 'Video')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    mp4_file_path = os.path.join(save_path, f"{my_uuid}.mp4")
    video.write_videofile(mp4_file_path, fps=fps, codec="libx264", remove_temp=True)
    return mp4_file_path

#
if __name__ == '__main__':
#     video1 = os.path.join(BASE_DIR, 'sources', 'Video', 'silence_video.avi')
#     print(duration_video(video1))
#     path = r'E:\py_project\video_synthetic\sources\Mp3\2b283e4a2cd511ec98e0d050996a9735.wav'
#     print(duration_mp3(path))
    video_urls = ["http://vdp-cool.oss-cn-hangzhou.aliyuncs.com/myvideo/20211020/cff1840631a111ecaca4d050996a9735.mp4",
                  "http://vdp-cool.oss-cn-hangzhou.aliyuncs.com/myvideo/20211020/cff1840631a111ecaca4d050996a9735.mp4"]
    print(concat_video_by_urls(video_urls))
    # print(concat_video(r'E:\py_project\video_synthetic\sources\Video'))

    # print(concat_video_by_times(r'E:\py_project\video_synthetic\sources\Video\e8a5bb8a2cd911ecb787d050996a9735.mp4', 24, 20))
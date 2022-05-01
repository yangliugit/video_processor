# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import uuid
from config.settings import BASE_DIR
import os


class ImgText:
    def __init__(self, text, png_path, font_size=50, font_color=None, x=10, y=10):
        # 背景文件路径
        if font_color is None:
            self.font_color = (0, 0, 0)
        else:
            self.font_color = font_color
        self.png_path = png_path
        # 文本
        self.text = text
        # 字体大小
        self.font_size = font_size
        # 字体大小
        self.font = ImageFont.truetype(os.path.join(BASE_DIR, 'common', 'pingfang.ttf'), font_size)
        # 字的起始位置
        self.x = x
        self.y = y
        # 段落 , 行数, 行高
        self.duanluo, self.note_height, self.line_height = self.split_text()

    def get_duanluo(self, text):
        txt = Image.new('RGBA', (self.font_size, self.font_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        # 获取图片宽度
        png_width = Image.open(self.png_path).size[0]
        for char in text:
            width, height = draw.textsize(char, self.font)
            sum_width += width
            # 超过预设宽度就修改段落 以及当前行数。 居中代码 TODO
            if sum_width > png_width - 2 * self.x:
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count

    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height

    def draw_text(self):
        """
        绘图以及文字
        :return:
        """
        note_img = Image.open(self.png_path).convert("RGBA")
        draw = ImageDraw.Draw(note_img)
        # 左上角开始
        x, y = self.x, self.y
        for duanluo, line_count in self.duanluo:
            # fill=(255, 0, 0) fill = "white"
            draw.text((x, y), duanluo, fill=self.font_color, font=self.font)
            y += self.line_height * line_count
        result_file = os.path.join(BASE_DIR, 'sources', 'IMG',
                                   'addText_' + ''.join(str(uuid.uuid1())).replace('-', '') + '.png')
        note_img.save(result_file)
        return result_file
#
# if __name__ == '__main__':
#     n = ImgText("十年生死两茫茫，不思量" * 5, r'D:\cool_server\testsources\bg1@3x.png', 80, 100, 200)
#     n.draw_text()

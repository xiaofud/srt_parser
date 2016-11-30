# coding=utf-8
__author__ = 'smallfly'


from srt_lexical_analyser import LexicalAnalyser
from srt_parser import SrtParser
from subtitle import Subtitle

import os
import time

def read_srt_file(filename):
    if not os.path.exists(filename):
        print("{} doesn't exist".format(filename))
        return None
    with open(filename) as f:
        return f.read()

def parse(srt):
    analyser = LexicalAnalyser()
    parser = SrtParser(analyser)
    subtitles = parser.parse(srt)
    # print(subtitles)
    if subtitles is None:
        print("ERROR OCCURRED WHILE PARSING SRT")
    return subtitles

def display_subtitles(subtitles):
    # print("Display subtitle:")
    os.system("clear")
    then = time.time()
    index = 0
    # print(len(subtitles))
    while index < len(subtitles):
        sub = subtitles[index]
        assert isinstance(sub, Subtitle)
        start_time = sub.get_start_second()
        end_time = sub.get_end_second()
        # print(start_time, "-->", end_time)
        # 如果现在时间处于该字幕的播放时间
        # 那么就播放该内容
        displayed = False
        while True:
            now = time.time()
            passed_time = now - then
            # print("Time passed: ", passed_time)
            if not displayed and passed_time >= start_time:
                print(sub.subtitle)
                displayed = True
            if passed_time > end_time:
                # 清屏
                os.system("clear")
                # print('this line should disappear')
                break
            # 100ms检查一次
            time.sleep(.100)
        index += 1

def move_subtitles(subtitles, seconds, filename):
    for sub in subtitles:
        assert isinstance(sub, Subtitle)
        start_time = sub.get_start_second()
        end_time = sub.get_end_second()

        start_time += seconds
        end_time += seconds

        sub.start_time = Subtitle.to_srt_timestamp(start_time)
        sub.end_time = Subtitle.to_srt_timestamp(end_time)
    Subtitle.to_srt_file(subtitles, filename)
    print('saved to', filename)

def test(filename):
    subtitles = parse(read_srt_file("movie.srt"))
    display_subtitles(subtitles)


if __name__ == '__main__':
    subtitles = parse(read_srt_file("subtitle"))
    move_subtitles(subtitles, 70, "subtitle_forward_70s")
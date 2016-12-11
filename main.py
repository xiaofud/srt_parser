# coding=utf-8
__author__ = 'smallfly'


from srt_lexical_analyser import LexicalAnalyser
from srt_parser import SrtParser
from subtitle import Subtitle

import os
import time
import argparse

def read_srt_file(filename):
    if not os.path.exists(filename):
        # print("{} doesn't exist".format(filename))
        return None
    with open(filename, encoding="UTF-8") as f:
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

        if start_time < 0 or end_time < 0:
            print("TIMESTAMP OUT OF RANGE!!!")
            return

        sub.start_time = Subtitle.to_srt_timestamp(start_time)
        sub.end_time = Subtitle.to_srt_timestamp(end_time)
    Subtitle.to_srt_file(subtitles, filename)
    print('saved to', filename)

def test(filename):
    subtitles = parse(read_srt_file("movie.srt"))
    display_subtitles(subtitles)

def lexical_analyse(text):
    analyser = LexicalAnalyser()
    # with open("subtitle") as f:
    #     text = f.read()
    i = 0
    ch = text[i]
    while i <= len(text):
        # print('reading', ch)
        if analyser.read_char(ch):
            i += 1
            if i < len(text):
                ch = text[i]
            else:
                ch = None
    print("input\n", text, sep="")
    # print(analyser.tokens)
    for token in analyser.tokens:
        print(token)

def arg_handle():
    # https://docs.python.org/3/library/argparse.html#nargs
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--display", metavar="filename", help="Display the subtitles in the file")
    arg_parser.add_argument("-p", "--parse", metavar="filename", help="Parse the srt file")
    arg_parser.add_argument("-l", "--lexical", metavar="filename", help="Analyse the srt file lexically")
    arg_parser.add_argument("-m", "--manipulate", metavar=("input", "seconds", "output"), nargs=3, help="forward/delay subtitles of input file by seconds and dump to output file")

    args = arg_parser.parse_args()

    if args.display:
        # 显示字幕
        content = read_srt_file(args.display)
        if content is None:
            print(args.display, "doesn't exist")
            return
        subtitles = parse(content)
        if subtitles is None:
            print("INCORRECT FORMAT IN FILE", args.display)
            return
        display_subtitles(subtitles)

    elif args.parse:
        # 解析字幕
        print("parsing", args.parse, ":")
        content = read_srt_file(args.parse)
        if content is None:
            print(args.parse, "doesn't exist")
            return
        parse(content)
    elif args.lexical:
        content = read_srt_file(args.lexical)
        if content is None:
            print(args.lexical, "doesn't exist")
            return
        lexical_analyse(content)
    elif args.manipulate:
        # print(args.manipulate)
        input_, seconds, output_ = args.manipulate
        try:
            seconds = int(seconds)
        except Exception as e:
            print("argument seconds must be an integer")
            return
        content = read_srt_file(input_)
        if content is None:
            print(input_, "doesn't exist")
            return
        subtitles = parse(content)
        if subtitles is None:
            print("INCORRECT FORMAT IN FILE", input_)
            return
        move_subtitles(subtitles, seconds, output_)
    else:
        arg_parser.print_help()

if __name__ == '__main__':
    # subtitles = parse(read_srt_file("subtitle"))
    # move_subtitles(subtitles, 70, "subtitle_forward_70s")
    arg_handle()
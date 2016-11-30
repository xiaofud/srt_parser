# coding=utf-8
__author__ = 'smallfly'


from srt_lexical_analyser import LexicalAnalyser
from srt_parser import SrtParser


if __name__ == '__main__':
    analyser = LexicalAnalyser()
    # text = "0\n00:00:00,000 --> 11:11:11,111\nHello World!\nHello from the other side\n\n1\n00:00:00,000 --> 11:11:11,111\nThe Second Subtitle\n"
    text = """0
00:00:00,000 --> 00:00:01,000
this is the last line of subtitle 0
what's going on?
00:00:00,000
1995
-->

1
00:00:02,000 --> 00:00:03,000
Hello!
Hello from the other side.

2
00:00:02,000 --> 00:00:03,000
Hi!
Hi from the other side.
"""
    parser = SrtParser(LexicalAnalyser())
    parser.parse(text)
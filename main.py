# coding=utf-8
__author__ = 'smallfly'


from srt_lexical_analyser import LexicalAnalyser
from srt_parser import SrtParser


if __name__ == '__main__':
    analyser = LexicalAnalyser()
    text = "0\n00:00:00,000 --> 11:11:11,111\nHello World!\nHello from the other side\n\n1\n00:00:00,000 --> 11:11:11,111\nThe Second Subtitle\n"
    parser = SrtParser(LexicalAnalyser())
    parser.parse(text)
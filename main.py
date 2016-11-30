# coding=utf-8
__author__ = 'smallfly'


from srt_lexical_analyser import LexicalAnalyser
from srt_parser import SrtParser

def test():
    analyser = LexicalAnalyser()
    text = "0\n00:00:00,000 -->00:00:00,100\n 00:00:00,200\n"
    # text = "\n\n"
    # text = "10\n"
    # with open("subtitle") as f:
    #     text = f.read()
    i = 0
    ch = text[i]
    while i < len(text):
        # print('reading', ch)
        if analyser.read_char(ch):
            i += 1
            if i < len(text):
                ch = text[i]
            else:
                break
    print("input\n", text, sep="")
    print(analyser.tokens)

if __name__ == '__main__':
    analyser = LexicalAnalyser()
    # text = "1\n00:00:00,000 --> 00:00:01,000\nHello World!\n"
    text = "0\n00:00:00,000 --> 11:11:11,111\nHello World!\nHello from the other side\n\n1\n00:00:00,000 --> 11:11:11,111\nThe Second Subtitle\n"
    parser = SrtParser(LexicalAnalyser())
    parser.parse(text)
    # test()
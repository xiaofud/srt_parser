# coding=utf-8
__author__ = 'smallfly'

class SrtToken:

    """
    SRT 文件的单词符号

    Notice: 最终类型为COUNTER TIMESTAMP TIME_ARROW 的类型
    语法分析器都可以根据需要将其解释为TEXT类型, 因为TEXT(字幕内容)可以是任意字符
    所以对于词法分析器来说 1995 这个串是无法确认为是序号还是字幕内容的
    """

    # 计数器类型
    TYPE_COUNTER = 0
    # 时间戳类型
    TYPE_TIMESTAMP = 1
    # 时间跨度标识
    TYPE_TIME_ARROW = 2
    # 字符串
    TYPE_TEXT = 3
    # 空
    TYPE_EMPTY = 4


    def __init__(self, type_=None, value=None):
        self.type = type_
        self.value = value

    def set_type(self, type_):
        self.type = type_

    def set_value(self, val):
        self.value = val

    def __repr__(self):
        return "<%r>: %r" % ( self.value, self.type)

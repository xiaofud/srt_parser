# coding=utf-8
__author__ = 'smallfly'

""""
用于对srt文件词法分析

1
00:02:17,440 --> 00:02:20,375
Senator, we're making
our final approach into Coruscant.

2
00:02:20,476 --> 00:02:22,501
Very good, Lieutenant.
"""

from token import SrtToken

class LexicalAnalyser:
    """
    对输入进行词法分析
    """

    def __init__(self):
        self.tokens = []
        self.state = SrtToken.TYPE_TEXT
        # 用于记录已经读到的字符, 以便赋值给 Token 的 value 字段
        self.char_buffer = ""

    def read_char(self, ch):
        # 用于确定是否需要往后读
        move_cursor = True
        # 用于判断构建什么类型的token
        createType = None
        # 当前缓冲区 加入 新字符 后的状态, 方便判断应该转入哪个状态
        after_append_ch = self.char_buffer + ch
        # print('state: ', self.state)
        # 进入到TEXT模式
        if self.state == SrtToken.TYPE_TEXT:
            # 可能到COUNTER的情况
            # 如果读取该ch后, 缓冲区依然是个数字的话, 那么应该跳入COUNTER状态
            if after_append_ch.strip().isdigit():
                self.char_buffer = self.char_buffer.strip()
                self.char_buffer += ch
                self.state = SrtToken.TYPE_COUNTER
            # 可能到箭头的情况
            elif ch == "-":
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TIME_ARROW
            # 字符串结束状态
            elif ch == '\n':
                createType = SrtToken.TYPE_TEXT
                self.state = SrtToken.TYPE_TEXT
                # self.char_buffer = ""
            # 其他空字符状态
            # elif ch.strip() == "":
            #     self.state = SrtState.STATE_EMPTY
            else:
                self.char_buffer += ch
                move_cursor = True

        elif self.state == SrtToken.TYPE_COUNTER:
            if ch.isdigit():
                self.char_buffer += ch
                self.state = SrtToken.TYPE_COUNTER
            elif ch == '\n':
                createType = SrtToken.TYPE_COUNTER
                self.state = SrtToken.TYPE_TEXT
                # self.char_buffer = ""
            # 可能是时间串
            elif ch == ":":
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TIMESTAMP
            else:
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TEXT

        elif self.state == SrtToken.TYPE_TIME_ARROW:
            if after_append_ch == "-->":
                self.char_buffer += ch
                createType = SrtToken.TYPE_TIME_ARROW
                self.state = SrtToken.TYPE_TEXT
                # self.char_buffer = ""
            elif after_append_ch in "-->":
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TIME_ARROW
            else:
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TEXT

        elif self.state == SrtToken.TYPE_TIMESTAMP:
            tmp_len = len(after_append_ch)
            # 00:00:00,000
            # 至少到了第一个:
            if tmp_len in (4, 5, 7, 8, 10, 11, 12):
                if ch.isdigit():
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            elif tmp_len in (3, 6):
                if ch == ':':
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            elif tmp_len == 9:
                if ch == ",":
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            else:
                if ch.strip() == "":
                    createType = SrtToken.TYPE_TIMESTAMP
                    self.state = SrtToken.TYPE_TEXT
                    # self.char_buffer = ""
                else:
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
        elif self.state == SrtToken.TYPE_EMPTY:
            if ch.strip() == "":
                self.char_buffer += ch
                self.state = SrtToken.TYPE_EMPTY
            else:
                self.state = SrtToken.TYPE_TEXT
                # 留给下一次判断类型
                move_cursor = False


        if createType is not None:
            self.tokens.append(SrtToken(createType, self.char_buffer))
            self.char_buffer = ""

        return move_cursor


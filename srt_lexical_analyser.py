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

class SrtState:
    # 计数器类型
    STATE_COUNTER = 0
    # 时间戳类型
    STATE_TIMESTAMP = 1
    # 时间跨度标识
    STATE_TIME_ARROW = 2
    # 字符串
    STATE_TEXT = 3
    # 空
    STATE_EMPTY = 4

    def __init__(self, STATE_=None, value=None):
        self.STATE = STATE_
        self.value = value

    def set_STATE(self, STATE_):
        self.STATE = STATE_

    def set_value(self, val):
        self.value = val

    def __repr__(self):
        return "<%r>: %r" % ( self.value, self.STATE)

class LexicalAnalyser:
    """
    对输入进行词法分析
    """

    def __init__(self):
        self.tokens = []
        self.state = SrtState.STATE_TEXT
        self.char_buffer = ""

    def read_char(self, ch):
        # 用于确定是否需要往后读
        move_cursor = True
        # 用于判断构建什么类型的token
        createType = None

        tmp = self.char_buffer + ch
        # print('state: ', self.state)
        if self.state == SrtState.STATE_TEXT:
            # 可能到COUNTER的情况
            if tmp.strip().isdigit():
                self.char_buffer = self.char_buffer.strip()
                self.char_buffer += ch
                self.state = SrtState.STATE_COUNTER
            # 可能到箭头的情况
            elif ch == "-":
                self.char_buffer += ch
                self.state = SrtState.STATE_TIME_ARROW
            # 字符串结束状态
            elif ch == '\n':
                createType = SrtState.STATE_TEXT
                self.state = SrtState.STATE_TEXT
                # self.char_buffer = ""
            # 其他空字符状态
            # elif ch.strip() == "":
            #     self.state = SrtState.STATE_EMPTY
            else:
                self.char_buffer += ch
                move_cursor = True

        elif self.state == SrtState.STATE_COUNTER:
            if ch.isdigit():
                self.char_buffer += ch
                self.state = SrtState.STATE_COUNTER
            elif ch == '\n':
                createType = SrtState.STATE_COUNTER
                self.state = SrtState.STATE_TEXT
                # self.char_buffer = ""
            # 可能是时间串
            elif ch == ":":
                self.char_buffer += ch
                self.state = SrtState.STATE_TIMESTAMP
            else:
                self.char_buffer += ch
                self.state = SrtState.STATE_TEXT

        elif self.state == SrtState.STATE_TIME_ARROW:
            if tmp == "-->":
                self.char_buffer += ch
                createType = SrtState.STATE_TIME_ARROW
                self.state = SrtState.STATE_TEXT
                # self.char_buffer = ""
            elif tmp in "-->":
                self.char_buffer += ch
                self.state = SrtState.STATE_TIME_ARROW
            else:
                self.char_buffer += ch
                self.state = SrtState.STATE_TEXT

        elif self.state == SrtState.STATE_TIMESTAMP:
            tmp_len = len(tmp)
            # 00:00:00,000
            # 至少到了第一个:
            if tmp_len in (4, 5, 7, 8, 10, 11, 12):
                if ch.isdigit():
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TEXT
            elif tmp_len in (3, 6):
                if ch == ':':
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TEXT
            elif tmp_len == 9:
                if ch == ",":
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TIMESTAMP
                else:
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TEXT
            else:
                if ch.strip() == "":
                    createType = SrtState.STATE_TIMESTAMP
                    self.state = SrtState.STATE_TEXT
                    # self.char_buffer = ""
                else:
                    self.char_buffer += ch
                    self.state = SrtState.STATE_TEXT
        elif self.state == SrtState.STATE_EMPTY:
            if ch.strip() == "":
                self.char_buffer += ch
                self.state = SrtState.STATE_EMPTY
            else:
                self.state = SrtState.STATE_TEXT
                # 留给下一次判断类型
                move_cursor = False


        if createType is not None:
            self.tokens.append(SrtState(createType, self.char_buffer))
            self.char_buffer = ""

        return move_cursor

if __name__ == '__main__':
    analyser = LexicalAnalyser()
    # text = "1\n00:00:00,000 --> 00:00:01,000\nHello World!\n"
    text = "00:00:00,000 --> 11:11:11,111\n"
    with open("subtitle") as f:
        text = f.read()
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
    print("Input\n", text, sep="")
    print(analyser.tokens)
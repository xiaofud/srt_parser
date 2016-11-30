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

    """
    Notice: 最终类型为COUNTER TIMESTAMP TIME_ARROW 的类型
    语法分析器都可以根据需要将其解释为TEXT类型, 因为TEXT(字幕内容)可以是任意字符
    所以对于词法分析器来说 1995 这个串是无法确认为是序号还是字幕内容的
    """

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
        self.state = STATE_
        self.value = value

    def set_STATE(self, STATE_):
        self.state = STATE_

    def set_value(self, val):
        self.value = val

    def __repr__(self):
        return "<%r>: %r" % ( self.value, self.state)

class LexicalAnalyser:
    """
    对输入进行词法分析
    """

    def __init__(self):
        self.tokens = []
        self.state = SrtState.STATE_TEXT
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
        if self.state == SrtState.STATE_TEXT:
            # 可能到COUNTER的情况
            # 如果读取该ch后, 缓冲区依然是个数字的话, 那么应该跳入COUNTER状态
            if after_append_ch.strip().isdigit():
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
            if after_append_ch == "-->":
                self.char_buffer += ch
                createType = SrtState.STATE_TIME_ARROW
                self.state = SrtState.STATE_TEXT
                # self.char_buffer = ""
            elif after_append_ch in "-->":
                self.char_buffer += ch
                self.state = SrtState.STATE_TIME_ARROW
            else:
                self.char_buffer += ch
                self.state = SrtState.STATE_TEXT

        elif self.state == SrtState.STATE_TIMESTAMP:
            tmp_len = len(after_append_ch)
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


class SrtParser:

    # 同时也作为终止态
    start_state = 0
    # 标号态
    counter_state = 1
    # 开始时间态
    start_time_state = 2
    # 跨度串状态, 即 --> 态
    arrow_state = 3
    # 结束时间态
    end_time_state = 4
    # 字幕态
    text_state = 5

    def __init__(self, lexical_analyser):
        self.analyser = lexical_analyser
        # 置为开始态
        self.state = SrtParser.start_state
        # 读取字符串的指针
        self.i = 0

    def parse(self, content):
        self.i = 0
        ch = content[self.i]
        token_count = len(self.analyser.tokens)
        while self.i < len(content):
            move_cursor = self.analyser.read_char(ch)

            # 检查是否有新的token被读到了
            if len(self.analyser.tokens) > token_count:
                token_count += 1

                new_token = self.analyser.tokens[-1]
                assert isinstance(new_token, SrtState)
                # 根据当前state分析
                if self.state == SrtParser.start_state:
                    # 期待输入为标号类型
                    if new_token.state != SrtState.STATE_COUNTER:
                        print("ERROR, TYPE COUNTER NEEDED BUT", new_token.state, "FOUND")
                        return
                    print("COUNTER", new_token.value)
                    # 跳转到标号态
                    self.state = SrtParser.counter_state

                elif self.state == SrtParser.counter_state:
                    if new_token.state != SrtState.STATE_TIMESTAMP:
                        print("ERROR, TYPE TIMESTAMP NEEDED BUT", new_token.state, "FOUND")
                        return
                    print("START TIME", new_token.value)
                    # 跳转到开始时间态
                    self.state = SrtParser.start_time_state

                elif self.state == SrtParser.start_time_state:
                    if new_token.state != SrtState.STATE_TIME_ARROW:
                        print("ERROR, TYPE ARROW NEEDED BUT", new_token.state, "FOUND")
                        return
                    print(new_token.value)
                    # 跳转到 --> 态
                    self.state = SrtParser.arrow_state

                elif self.state == SrtParser.arrow_state:
                    if new_token.state != SrtState.STATE_TIMESTAMP:
                        print("ERROR, TYPE TIMESTAMP NEEDED BUT", new_token.state, "FOUND")
                        return
                    print("END TIME", new_token.value)
                    # 结束时间态
                    self.state = SrtParser.end_time_state

                elif self.state == SrtParser.end_time_state:
                    # 接受任意非空字符串
                    if new_token.value != "":
                        # 进入字幕态
                        self.state = SrtParser.text_state
                        print("TEXT:", new_token.value)
                    else:
                        # 跳到起始态
                        self.state = SrtParser.start_state
                        print("END OF A BLOCK OF SUBTITLE")


                elif self.state == SrtParser.text_state:
                    # 接受任意非空字符
                    if new_token.value != "":
                        # 进入字幕态
                        self.state = SrtParser.text_state
                        print("TEXT:", new_token.value)
                    else:
                        # 跳到起始态
                        self.state = SrtParser.start_state
                        print("END OF A BLOCK OF SUBTITLE")

            if move_cursor:
                self.i += 1
                if self.i < len(content):
                    ch = content[self.i]
                else:
                    break

        print(self.analyser.tokens)

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
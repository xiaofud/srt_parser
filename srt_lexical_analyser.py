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

from srt_token import SrtToken

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
        if ch is not None:
            after_append_ch = self.char_buffer + ch
        else:
            after_append_ch = self.char_buffer

        # 进入到TEXT模式
        if self.state == SrtToken.TYPE_TEXT:
            # 可能到COUNTER的情况
            # 如果读取该ch后, 缓冲区依然是个数字的话, 那么应该跳入COUNTER状态
            if after_append_ch.lstrip().isdigit():
                # 这一步是为了 时间戳 类型能够准确判断TIMESTAMP类型
                # self.char_buffer = self.char_buffer.strip()
                if ch is not None:
                    self.char_buffer += ch
                self.state = SrtToken.TYPE_COUNTER

            # 如果ch为 - 符号, 那么可能这个串是 -->
            # 缓冲区加入 ch 并且状态跳转到 TIME_ARROW 类型
            elif ch == "-":
                self.char_buffer += ch
                self.state = SrtToken.TYPE_TIME_ARROW
            # 字符串结束状态
            # 生成一个类型为 TEXT 的 Token
            # 状态保持在TEXT中
            elif ch == '\n' or ch is None:
                if ch is not None:
                    self.char_buffer += ch
                    createType = SrtToken.TYPE_TEXT
                elif ch is None and len(self.char_buffer) == 0:
                    createType = None
                # 别忘了这个情况
                else:
                    createType = SrtToken.TYPE_TEXT
                self.state = SrtToken.TYPE_TEXT

            # 其他输字符, 直接加入到缓冲区
            else:
                if ch is not None:
                    self.char_buffer += ch

        # 标号状态的情况
        elif self.state == SrtToken.TYPE_COUNTER:
            # 现在处于counter状态
            # 如果读到的任然是数字
            # 那么应该继续保持状态不变
            if ch is not None and ch.isdigit():
                # 往缓冲区中加入该字符
                self.char_buffer += ch

            # 如果处于counter状态的时候遇到了 \n 或者 文件末尾
            # 那么将现在缓冲区内的内容作为值, 生成一个新的类型为 COUNTER 的 TOKEN
            # 状态跳转到TEXT模式
            elif ch == '\n' or ch is None:
                createType = SrtToken.TYPE_COUNTER
                self.state = SrtToken.TYPE_TEXT

            # 如果此时输入为 : 号, 那么可能满足 TIMESTAMP 类型
            # 缓冲区中加入该符号, 并且状态跳到 TIMESTAMP
            elif ch == ":":
                if ch is not None:
                    self.char_buffer += ch
                self.state = SrtToken.TYPE_TIMESTAMP

            # 其他情况的话说明类型为字幕内容类型, 即 TEXT
            # 缓冲区加入该字符并且状态跳转到TEXT类型
            else:
                if ch is not None:
                    self.char_buffer += ch
                self.state = SrtToken.TYPE_TEXT

        # 时间跨度字符状态
        elif self.state == SrtToken.TYPE_TIME_ARROW:
            # 如果读入ch后, 直接为 --> 那么生成新的Token
            # 或者 读入 ch 以前就是 --> 但是ch是空白字符的话, 依然认为为 -->, 并且会吃掉后面的空格
            if self.char_buffer == "-->" and ( ch is None or ch.strip() == ""):
                if ch is not None:
                    self.char_buffer += ch
                createType = SrtToken.TYPE_TIME_ARROW
                self.state = SrtToken.TYPE_TEXT
            # 仍然可能满足 -->
            elif after_append_ch in "-->":
                if ch is not None:
                    self.char_buffer += ch
                self.state = SrtToken.TYPE_TIME_ARROW
            # 不满足 --> 那么跳回到TEXT状态
            else:
                if ch is not None:
                    self.char_buffer += ch
                self.state = SrtToken.TYPE_TEXT
        # 时间戳状态
        elif self.state == SrtToken.TYPE_TIMESTAMP:

            # 去掉前置0

            tmp_string = after_append_ch.lstrip()

            # 用长度判断格式
            # tmp_len = len(after_append_ch)
            tmp_len = len(tmp_string)

            # 00:00:00,000
            # 至少到了第一个:
            if tmp_len in (4, 5, 7, 8, 10, 11, 12):
                # 如果ch在这几个位置上是数字的话, 那么状态继续保持为 时间戳
                if ch is not None and ch.isdigit():
                    self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                # 否则跳回到TEXT模式
                else:
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            elif tmp_len in (3, 6):
                # 如果ch在这几个位置上是 : 的话
                # 那么满足 TIMESTAMP 类型
                if ch == ':':
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                # 否则跳回到 TEXT 类型
                else:
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            elif tmp_len == 9:
                if ch == ",":
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TIMESTAMP
                else:
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT
            else:
                # 长度已经超过12
                # 如果输入为空白字符的话, 那么
                # 创建一个类型为 TIMESTAMP 的 Token
                if ch is not None and ch.strip() == "":
                    createType = SrtToken.TYPE_TIMESTAMP
                    # 跳到TYPE_TEXT
                    self.state = SrtToken.TYPE_TEXT
                # 仅仅视为字符串, 如 00:00:00,000x
                else:
                    if ch is not None:
                        self.char_buffer += ch
                    self.state = SrtToken.TYPE_TEXT

        if createType is not None:
            if createType in (SrtToken.TYPE_COUNTER, SrtToken.TYPE_TIMESTAMP, SrtToken.TYPE_TIME_ARROW):
                self.char_buffer = self.char_buffer.strip()
            self.tokens.append(SrtToken(createType, self.char_buffer))
            # 记得清空缓冲区
            self.char_buffer = ""

        return move_cursor

def test(text):
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
    print(analyser.tokens)

if __name__ == '__main__':
    # test("   ABD ABC")
    text = """0
00:00:00,000 --> 00:00:01,000
this is the last line of subtitle 0
what's going on?
-->
1995

1
00:00:02,000 --> 00:00:03,000
Hello!
Hello from the other side.

2
00:00:02,000 --> 00:00:03,000
Hi!
Hi from the other side.
"""
    text = "1 "
    test(text)
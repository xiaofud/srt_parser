# coding=utf-8
__author__ = 'smallfly'

from srt_token import SrtToken
from subtitle import Subtitle

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

        subtitles = []
        number = None
        start_time = None
        end_time = None
        text = ""

        self.i = 0
        ch = content[self.i]
        token_count = len(self.analyser.tokens)
        while self.i < len(content):
            move_cursor = self.analyser.read_char(ch)

            # 检查是否有新的token被读到了
            if len(self.analyser.tokens) > token_count:
                token_count += 1

                new_token = self.analyser.tokens[-1]
                assert isinstance(new_token, SrtToken)
                # 根据当前state分析
                if self.state == SrtParser.start_state:
                    # 期待输入为标号类型
                    if new_token.type != SrtToken.TYPE_COUNTER:
                        print("ERROR, TYPE COUNTER NEEDED BUT", new_token.type, "FOUND")
                        return
                    print("COUNTER", new_token.value)
                    number = int(new_token.value)
                    # 跳转到标号态
                    self.state = SrtParser.counter_state

                elif self.state == SrtParser.counter_state:
                    if new_token.type != SrtToken.TYPE_TIMESTAMP:
                        print("ERROR, TYPE TIMESTAMP NEEDED BUT", new_token.type, "FOUND")
                        return
                    print("START TIME", new_token.value)
                    start_time = new_token.value
                    # 跳转到开始时间态
                    self.state = SrtParser.start_time_state

                elif self.state == SrtParser.start_time_state:
                    if new_token.type != SrtToken.TYPE_TIME_ARROW:
                        print("ERROR, TYPE ARROW NEEDED BUT", new_token.type, "FOUND")
                        return
                    print(new_token.value)
                    # 跳转到 --> 态
                    self.state = SrtParser.arrow_state

                elif self.state == SrtParser.arrow_state:
                    if new_token.type != SrtToken.TYPE_TIMESTAMP:
                        print("ERROR, TYPE TIMESTAMP NEEDED BUT", new_token.type, "FOUND")
                        return
                    print("END   TIME", new_token.value)
                    end_time = new_token.value
                    # 结束时间态
                    self.state = SrtParser.end_time_state

                elif self.state == SrtParser.end_time_state or self.state == SrtParser.text_state:
                    # 接受任意非换行符字符串(即空行)
                    # print("TYPE:", new_token.type, [new_token.value])
                    if new_token.value != "\n":
                        # 进入字幕态
                        self.state = SrtParser.text_state
                        print("TEXT:", new_token.value)
                        if not new_token.value.endswith("\n"):
                            new_token.value += "\n"
                        text += new_token.value
                    else:
                        # 跳到起始态
                        self.state = SrtParser.start_state
                        print("------- END OF A BLOCK OF SUBTITLE -------")
                        # 生成新的subtitle对象
                        subtitle = Subtitle(number, start_time, end_time, text)
                        subtitles.append(subtitle)

                        # 清空数据
                        number = None
                        start_time = end_time = None
                        text = ""


            if move_cursor:
                self.i += 1
                if self.i < len(content):
                    ch = content[self.i]
                else:
                    break

        print("Tokens:")
        for token in self.analyser.tokens:
            print(token)
        return subtitles
# coding=utf-8
__author__ = 'smallfly'

class Subtitle:
    """
    用于存储最终解析好的字幕
    """

    def __init__(self, number, start_time, end_time, subtitle):
        """
        生成字幕对象
        :param number: 序号
        :param start_time: 开始时间
        :param end_time:  停止时间
        :param subtitle:  字幕内容
        :return:
        """
        self.number = number
        self.start_time = start_time
        self.end_time = end_time
        self.subtitle = subtitle

    def get_start_second(self):
        if self.start_time is None:
            return None
        return Subtitle.get_second(self.start_time)

    def get_end_second(self):
        if self.end_time is None:
            return None
        return Subtitle.get_second(self.end_time)

    @staticmethod
    def get_second(timestamp):
        # 00:00:00,000
        assert isinstance(timestamp, str)
        timestamp = timestamp.replace(",", ".")
        hour, minute, second = list(map(lambda x: float(x), timestamp.split(":")))
        return hour * 60 * 60 + minute * 60 + second

    @staticmethod
    def to_srt_file(subtitles, filename):
        with open(filename, "w") as f:
            for sub in subtitles:
                assert isinstance(sub, Subtitle)
                f.write(str(sub.number) + "\n")
                f.write(sub.start_time + " --> " + sub.end_time + "\n")
                f.write(sub.subtitle + "\n")

    @staticmethod
    def to_srt_timestamp(seconds):
        hour = str(int (seconds // (60 * 60) ))
        if len(hour) == 1: hour = "0" + hour

        seconds = seconds % (60 * 60)

        minutes = str( int(seconds // (60) ) )
        if len(minutes) == 1: minutes = "0" + minutes

        seconds = seconds % 60
        seconds = str(seconds)

        if "." not in seconds:
            if len(seconds) == 1:
                seconds = "0" + seconds
            seconds += ",000"

        elif "." in seconds:
            # 划分为小数部分和整数部分
            integer, decimal = seconds.split(".")
            decimal_len = len(decimal)

            if len(integer) == 1:
                integer = "0" + integer

            if decimal_len == 1:
                decimal += "00"
            elif decimal_len == 2:
                decimal += "0"
            elif decimal_len > 3:
                decimal = decimal[:3]

            seconds = integer + "," + decimal

        return hour + ":" + minutes + ":" + seconds


    def __repr__(self):
        return "<%d %r --> %r>: %r" % (self.number, self.start_time, self.end_time, self.subtitle)

if __name__ == '__main__':
    # sub = Subtitle(0, "00:01:00,000", "00:00:04,444", "Hello World!")
    # print(sub.get_start_second())
    # print(sub.get_end_second())
    # seconds = 1.4444
    # seconds = 37001
    # print(Subtitle.to_srt_timestamp(seconds))
    pass
# -*- coding: utf-8 -*
import sys, io, time
import term


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

class SimpleProgressBar:

    def __init__(self, total_requests=1):
        self.displayed = False
        self.total_steps = total_requests + 3
        self.current_steps = 0
        self.status = 'Processing...'
        self.total_req_len = len(str(self.total_steps))
        # 定义进度条总长 103 格，第一格表示开始发送request 动作，
        # 第二格是发送总排行信息，之后的100格表示对需要显示详细信息的基金的请求，
        # 最后一格表示显示动作
        self.bar = '({:<13}) ├{:─<100}┤[{:>%s}/{:>%s}]' % (self.total_req_len, self.total_req_len)

    def update(self):
        self.displayed = True
        bar = '█' * (self.current_steps * 100 // self.total_steps)
        bar = self.bar.format(self.status, bar, self.current_steps, self.total_steps)
        sys.stdout.write('\r' + bar)
        sys.stdout.flush()

    def update_current_steps(self, n):
        self.current_steps = n

    def done(self):
        if self.displayed:
            print()
            self.displayed = False
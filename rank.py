# -*- coding: utf-8 -*
import re
import requests
from datetime import datetime, timedelta

'''
URL:
http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=zq&rs=&gs=0&sc=3nzf&st=desc&sd=2019-01-07&ed=2020-01-07&qdii=041|&tabSubtype=041,,,,,&pi=1&pn=50&dx=1&v=0.9225948918241171

以下全为主观YY的翻译
op=ph - 无解 (p≧w≦q)
dt=kf - data type = 开放
ft=zq - fund type = 债券
rs=
gs=0
sc=3nzf - 按三年排序
st=desc - 降序
sd=2019-01-07 - 开始日期
ed=2020-01-07 - 截止日期
qdii=| - 是否包含 qdii
tabSubtype=,,,,,
pi=1 - page index
pn=50 - page number
dx=1

response sample:
var rankData = {
    datas:[
    "003860,招商招旭纯债C,ZSZXCZC,...
    ...
    "003788,方正富邦惠利纯债C,FZFBHLCZC,...
    ],allRecords:715...fofNum:89};

datas 部分是对应的债券信息，结为是一些其他附加信息
'''
url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=zq&rs=&gs=0&sc=3nzf&st=desc&sd={}&ed={}&qdii=041|&tabSubtype=041,,,,,&pi=1&pn={}&dx=1'

today = datetime.now()
# 1 year before today
start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
end_date = today.strftime('%Y-%m-%d')

ret = requests.get(url.format(start_date, end_date, 100))

# 正则匹配债券信息部分 'datas:' 到 ',allRecords' 之间的部分
bonds = re.search(r'(\[.+\])', ret.text).group(1)
'''
这个 API 返回值中我想要的数据有：基金号，中文名，近三年总收益，成立时间，近一年收益，近第二年，近第三年收益

字符串中各位置代表的意义：
"003741,鹏华丰盈债券,PHFYZQ,2020-01-08,1.3580,1.4459,
0：基金号， 1：中文名称，2：拼音首字母，3：当前时间，4：单位净值，5：累计净值
------
0.0074,-0.0589,0.6672,1.3055,2.3438,
6：日增长，7：近一周，8：近一个月，9：近三个月，10：近六个月
------
35.7922,42.5302,47.3382,-0.0589,47.9570,2016-11-22,
11：近一年，12：近两年，13：近三年，14：今年来，15：成立来，16：自定义，17：成立时间
------
1,35.8599,0.80%,0.08%,1,0.08%,1,"
18：?, 19:看着像是估值，20：手续费，21：折后，22：打折，23，24貌似和前两个重复的

eval(str) 把 str 转成 list
'''
bonds_list = eval(bonds)

# 创建一个 Info 类来简化存储
class BondInfo:
    def __init__(self, infostr):
        info = infostr.split(',')
        self.originstr = infostr
        self.id = info[0]
        self.name = info[1]
        #... 后面再补齐

# 把 list 信息拆解成 id - info 的 dict 对象
bonds_dict = {}
for sub in bonds_list:
    one_bond = sub.split(',')
    id = one_bond[0]
    bonds_dict[id] = BondInfo(sub)

for k,v in bonds_dict.items():
    print("id: %s, name: %s" % (k, v.name))
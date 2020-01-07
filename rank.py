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

# -*- coding: utf-8 -*
import re
import requests
from bs4 import BeautifulSoup
from terminaltables import AsciiTable
from datetime import datetime, timedelta

'''
为了便于管理，对象属性中只存放 request 解析出来的原始值，再方法中进行类型转化，返回处理数据
'''
#ret = soup.find_all('div', class_='box') 
# ret[0].tbody.contents
def _requestManager(code):
    '''
    替换下面 URL 里面的基金代码部分可以得到对应的基金经理的数据, 使用 BeautifulSoup 提取所需要的经理数据, 类似 xpath 的思路
    http://fundf10.eastmoney.com/jjjl_206018.html

    需要收集的数据有：姓名，任职时长，任期收益，同类平均收益，根据目前的需求，只拿当前经理的信息，历史数据暂且忽略

    @param code:
        bond code
    return:
        the manager object of this bond
    '''
    html_text = requests.get('http://fundf10.eastmoney.com/jjjl_{}.html'.format(code)).text

    html = BeautifulSoup(html_text, 'html.parser')
    current_mrg = html.find('div', class_='box').find('tbody').find('tr').contents

    manager_dict = {}
    manager_dict['name'] = current_mrg[2].text.strip()
    manager_dict['workTime'] = current_mrg[3].text.strip()
    manager_dict['termEarn'] = current_mrg[4].text.strip().replace('%','')

    size_txt = html.find('div', class_='bs_gl').find_all('label')[-1].text
    manager_dict['fundSize'] = re.search('\d+[.]\d+', size_txt).group()

    return manager_dict


class Manager:
    def __init__(self, code):
        mgr_dict = _requestManager(code)
        self.name = mgr_dict['name']
        self.workTime = mgr_dict['workTime']
        self.termEarn = mgr_dict['termEarn']
        self.fundSize = mgr_dict['fundSize']

    def getWorkTime(self):
        yearMatched = re.search(r'(\w+)年', self.workTime)
        dayMatched = re.search(r'(\d+)天', self.workTime)
        yearNum = 0 if yearMatched is None else int(yearMatched.group(1))
        dayNum = 0 if yearMatched is None else int(dayMatched.group(1))
        return timedelta(days=(yearNum*365+dayNum))
    
    def getTermAvgPerYear(self):
        return round(float(self.termEarn)/self.getWorkTime().days*365, 3)


    def __str__(self):
        return "Manager: %s, work time: %s, term earn: %s" % (self.name, self.workTime, self.termEarn)


def filterFund(manager):
    # 剔除基金经理任职时间少于 3 年的品种
    if manager.getWorkTime().days - 3*365 < 0:
        return True
    # 剔除任职期间平均年收益低于 7% 的品种
    if manager.getTermAvgPerYear() < 7:
        return True
    return False

def getBondsList(count):
    '''
    删选出当前时间点的最佳纯债基金名单，只是初步删选，后续还要更具基金的管理细节再进行选优
    @param: 删选基金的数量
    @return: 删选出的基金 list

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

    ret = requests.get(url.format(start_date, end_date, count))

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
    11：近一年，12：近两年，13：近三年，14：今年来，15：成立来，16：成立时间
    ------
    1,35.8599,0.80%,0.08%,1,0.08%,1,"
    17：?, 18:看着像是估值，19：手续费，20：折后，21：打折，22，23貌似和前两个重复的

    eval(str) 把 str 转成 list
    '''
    return eval(bonds)


# 创建一个 Info 类来简化存储
class BondInfo:
    def __init__(self, infostr):
        info = infostr.split(',')
        self.originstr = infostr
        self.code = info[0]
        self.name = info[1]
        self.earn3YTotal = info[13]
        self.earn2YTotal = info[12]
        self.earn1YTotal = info[11]
        self.established = info[16]
    
    def setManager(self, manager):
        self.manager = manager

    def getEarnLastYear(self):
        return float(self.earn1YTotal)

    def getEarn2YearsAgo(self):
        return '%.3f' % (float(self.earn2YTotal) - float(self.earn1YTotal))

    def getEarn3YearsAgo(self):
        return '%.3f' % (float(self.earn3YTotal) - float(self.earn2YTotal))

    def getEstablishedDate(self):
        start = datetime.strptime(self.established, '%Y-%m-%d')
        days = (datetime.now() - start).days
        return "%s年%s天" % (int(days/365), days%365)

    def getEarn3YearsAvg(self):
        return '%.3f' % (float(self.earn3YTotal)/3)

    def __str__(self):
        return "Code: %s, name: %s, [1-3] earn/year: [%s, %s, %s], %s" % (self.id, self.name, self.earn1YTotal, self.earn2YTotal, self.earn3YTotal, self.manager)


def transferInfoToList(bondInfo, manager):
    tmp = []
    # set bond info
    tmp.append(bondinfo.code)
    tmp.append(bondinfo.name)
    tmp.append(bondinfo.getEstablishedDate())
    tmp.append(bondinfo.earn3YTotal)
    tmp.append(bondinfo.getEarnLastYear())
    tmp.append(bondinfo.getEarn2YearsAgo())
    tmp.append(bondinfo.getEarn3YearsAgo())

    # set manager info
    tmp.append(manager.name)
    tmp.append(manager.workTime)

    tmp.append(bondInfo.getEarn3YearsAvg())

    tmp.append(manager.getTermAvgPerYear())
    tmp.append(manager.fundSize)
    return tmp

if __name__ == '__main__':
    bonds_list = getBondsList(100)

    # 把 list 信息拆解成 id - info 的 dict 对象
    table_data = []
    for sub in bonds_list:
        bondinfo = BondInfo(sub)
        manager = Manager(bondinfo.code)
        # filter funds
        if filterFund(manager):
            continue

        row = transferInfoToList(bondinfo, manager)
        table_data.append(row)

    tableHeader = ['Code', '名称', '成立时间', '近三年收益(%)', '去年收益(%)', '前年收益(%)', '大前年收益(%)', '经理', '任期', '年均收益(3年)', '年均收益(总)', '规模(亿)']
    table_data.insert(0, tableHeader)

    table = AsciiTable(table_data)
    print(table.table)




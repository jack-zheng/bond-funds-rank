# -*- coding: utf-8 -*
import re
import requests
from datetime import datetime, timedelta

'''
为了便于管理，对象属性中只存放 request 解析出来的原始值，再方法中进行类型转化，返回处理数据
'''

class ManagerInfo:
    def __init__(self, dict):
        self.name = dict['name']
        self.workTime = dict['workTime']
        self.fundSize = dict['fundSize']
        self.termEarn = dict['profit']['series'][0]['data'][0]['y']
        self.fundAvg = dict['profit']['series'][0]['data'][1]['y']

    def getWorkTime(self):
        yearMatched = re.search(r'(\w+)年', self.workTime)
        dayMatched = re.search(r'(\d+)天', self.workTime)
        yearNum = 0 if yearMatched is None else int(yearMatched.group(1))
        dayNum = 0 if yearMatched is None else int(dayMatched.group(1))
        return timedelta(days=(yearNum*365+dayNum))

    def __str__(self):
        return "Manager: %s, work time: %s, fond size: %s, term earn: %s, fund avg: %s" % (self.name, self.workTime, self.fundSize, self.termEarn, self.fundAvg)


def getManager(code):
    '''
    替换下面 URL 里面的基金代码部分可以得到对应的基金经理的数据
    http://fund.eastmoney.com/pingzhongdata/206018.js

    数据部分样本：
    var Data_currentFundManager =[{"id":"30282133","pic":"https://pdf.dfcfw.com/pdf/H8_JPG30282133_1.jpg","name":"祝松","star":3,"workTime":"5年又322天","fundSize":"205.00亿(9只基金)","power":{"avr":"58.97","categories":["经验值","收益率","抗风险","稳定性","管理规模"],"dsc":["反映基金经理从业年限和管理基金的经验","根据基金经理投资的阶段收益评分，反映\u003cbr\u003e基金经理投资的盈利能力","反映基金经理投资的回撤控制能力","反映基金经理投资收益的波动","根据基金经理现任管理基金资产规模评分"],"data":[77.10,64.40,46.60,33.40,89.0],"jzrq":"2020-01-08"},"profit":{"categories":["任期收益","同类平均"],"series":[{"data":[{"name":null,"color":"#7cb5ec","y":61.0114},{"name":null,"color":"#414c7b","y":49.15}]}],"jzrq":"2020-01-08"}}] ;

    需要收集的数据有：姓名，任职时长，总共管理资产额度，任期收益，同类平均收益

    @param code:
        bond code
    return:
        the manager object of this bond
    '''
    bond_detail = requests.get('http://fund.eastmoney.com/pingzhongdata/{}.js'.format(code))

    manager_reg = r'Data_currentFundManager =(\[.+?}}\])'
    managerstr = (re.search(manager_reg, bond_detail.text)).group(1)

    # 任期收益 和 同类平均收益 的数据中有 "name":null 的类型，把 null 替换掉，不然转化会抛错
    managerstr = managerstr.replace('null', '\"undefined\"')
    manager_dict = eval(managerstr)[0]

    return ManagerInfo(manager_dict)


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
    11：近一年，12：近两年，13：近三年，14：今年来，15：成立来，16：自定义，17：成立时间
    ------
    1,35.8599,0.80%,0.08%,1,0.08%,1,"
    18：?, 19:看着像是估值，20：手续费，21：折后，22：打折，23，24貌似和前两个重复的

    eval(str) 把 str 转成 list
    '''
    return eval(bonds)


# 创建一个 Info 类来简化存储
class BondInfo:
    def __init__(self, infostr):
        info = infostr.split(',')
        self.originstr = infostr
        self.id = info[0]
        self.name = info[1]
        self.earn3YTotal = info[13]
        self.earn2YTotal = info[12]
        self.earn1YTotal = info[11]
        self.established = info[15]
    
    def setManager(self, manager):
        self.manager = manager

    def __str__(self):
        return "Code: %s, name: %s, [1-3] earn/year: [%s, %s, %s], %s" % (self.id, self.name, self.earn1YTotal, self.earn2YTotal, self.earn3YTotal, self.manager)


if __name__ == '__main__':
    bonds_list = getBondsList(5)

    # 把 list 信息拆解成 id - info 的 dict 对象
    bonds_dict = {}
    for sub in bonds_list:
        one_bond = sub.split(',')
        code = one_bond[0]
        bondinfo = BondInfo(sub)
        bondinfo.setManager(getManager(code))
        # bonds_dict[code] = bondinfo
        print(bondinfo)



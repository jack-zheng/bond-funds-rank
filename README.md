# bond-funds-rank

分析天天基金网债券基金数据，选择符合自己预期的投资标的

## 预期功能

1. 显示债券基金 rank 前 100 的数据信息
1. eprogress 显示爬取进度
1. 要有 report
1. 通过 pipy release，熟悉一下流程
1. 可以的话试下加权计算得分

## 工作环境搭建

pipenv: 用于创建一个独立的开发环境，避免和本地版本冲突 `pip3 install pipenv`

```bash
pipenv shell - 创建环境
pipenv install xxx - 安装包
pipenv install pytest --dev - 安装开发包
pipenv lock - 生成版本文件
pipenv install --ignore-pipfile - 通过lock file 安装依赖
pipenv graph - 查看依赖
pipenv graph --reverse - 回滚
pipenv sync - 同步安装 lock 文件中的依赖
```

requests: 用于发送 http reqeust

terminaltables: 格式化输出结果

### Step 1

通过 F12 找到网站一些可用的 API 接口

```url
天天基金 -> 基金排行 -> 债券型 -> 长期纯债 -> 近三年降序

http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=zq&rs=&gs=0&sc=3nzf&st=desc&sd=2019-01-06&ed=2020-01-06&qdii=041|100-150&tabSubtype=041,100-150,,,,&pi=1&pn=50&dx=1&v=0.6502916043370328
```

```url
 基金经理数据页面

http://fundf10.eastmoney.com/jjjl_206018.html
```

```url
基金基本信息

http://fund.eastmoney.com/pingzhongdata/206018.js
```

删选基金规则

1. 必须是纯债基金，控制分享，这个项目选的是稳健型产品
1. 杠杆 < 160% (看了下基本上不是定开基金基本都是小于这个数的，选全部算了)
1. 规模限制 1.5亿 < size < 20亿
1. 成立时间大于3年，按3年总收益降序排列
1. 再上一个删选基础上查看基金经理对该基金的管理年限
1. 在上一个删选基础上优先年纪更大的

我想要看的信息

1. 前100基金列表名单
1. 各基金的总金额，近三年收益，对应的基金经理信息

## Issue Log

运行脚本的时候抛错

```txt
jack@DESKTOP-9TGTFK1:~/gitStore/bond-funds-rank$ python rank.py
  File "rank.py", line 8
SyntaxError: Non-ASCII character '\xe4' in file rank.py on line 9, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details
```

在文件头部追加 `# -*- coding: utf-8 -*` 指定编码

使用正则匹配时默认使用的是贪婪模式，在匹配时添加 ? 比如： `\w+?` 就会把匹配转化成非贪婪模式

WSL 使用 pipenv shell 时抛错

```txt
OSError: [Errno 8] Exec format error: '/mnt/c/Users/lanmo/AppData/Local/Microsoft/WindowsApps/python.exe'
```

这是因为 windows 环境下安装的的python 版本要优先于 WSL。通过 WSL 本地安装 pipfile 对应版本的 python 然后 `pipenv --python /usr/bin/python3` 问题解决

## 参考资料

* [pipenv guide](https://realpython.com/pipenv-guide/)

## 进度记录

day6: 1 hours, 基本完成基金删选，发现一个问题，xx.js 页面返回的数据上，基金经理的任职期限有几个不对，改成从页面去拿会更准确
day5: 1.5 hours, 基本完成打印功能，下次增加更具体的删选条件，比如剔除任期收益低于 18% 的品种
day4: 1 hours, 完成基本功能，剩下的就是如何让他更友好
day3: 1.5 hours, 基本整合完基金经理信息，但是代码结构需要再调整一下
day2: 1.5 hours, 删选基金信息
day1: 2 hours, setup env, 完成部分信息爬取

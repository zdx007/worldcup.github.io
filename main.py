# -*- coding: utf-8 -*-
"""爬虫运行主脚本.

Created on Wed Jul 25 17:57:18 2018

@author: Administrator

"""

import login
import list
from sqlalchemy import create_engine

# 输入账号和密码用于模拟登陆
username = input('请输入账号')
password = input('请输入密码')

login.Launcher(username, password).login()

# 爬取搜索页数据
info_user_d = list.crawl_list()

# 将爬取到的搜索页数据存入数据库
engine = create_engine('mysql+pymysql://root:12345@127.0.0.1:3306/worldcup?charset=utf8mb4')

try:
    info_user_d.to_sql(name='user_list', con=engine, if_exists='append', index=False, index_label=False) 
    print('导入数据库成功！')    
except Exception as e:
    print(e)

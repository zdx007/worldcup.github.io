# -*- coding: utf-8 -*-
"""搜索页爬虫脚本.

Created on Tue Jul 17 18:20:00 2018

@author: zan

"""

import requests
from lxml import etree
import json
from http import cookiejar
import re
import pandas as pd
import random
import time

def crawl_list(i=1, j=50):
    """ 爬取搜索页数据.
    
    i表示开始页，j表示终止页
    
    步骤如下：
    1、加载模拟登录后的cookie
    2、遍历搜索页，对搜索页发送请求
    3、解析字段
    4、存储到DataFrame
    
    """
    
    # 加载cookie
    session = requests.session()
    session.cookies = cookiejar.LWPCookieJar('cookie')
    session.cookies.load(ignore_discard=True)
    
    # 创建空的DataFrame
    info_user_d = pd.DataFrame()
    
    # 遍历搜索页
    while i:
        l = ['http://s.weibo.com/user/%25E4%25B8%2596%25E7%2595%258C%25E6%259D%25AF&auth=org_vip&page=',str(i)]
        search_url = ''.join(l)
        data = session.get(search_url).content.decode('utf-8')
        
        # 从源码的json文件中取出所需字段的html内容
        lines = data.splitlines()
        for line in lines:
            if not line.startswith('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_user_feedList","js":'):
                continue
            json_pattern = re.compile('\((.*)\)')
            # 利用正则取出json
            json_data = json_pattern.search(line).group(1)
            # 将json包装成字典并提取出html内容
            html = json.loads(json_data)['html']
            
        # 创建字典
        info_user = {}
        # 使用xpath从html中解析所需字段
        page = etree.HTML(html)
        info_user['uid'] = page.xpath('//a[@class="W_btn_b6 W_fr"]/@uid')
        info_user['name'] = page.xpath('//a[@class="W_texta W_fb"]/@title')
        info_user['weibo_addr'] = page.xpath('//a[@class="W_texta W_fb"]/@href')
        info_user['follow'] = page.xpath('//p[@class="person_num"]/span[1]/a/text()')
        info_user['fans'] = page.xpath('//p[@class="person_num"]/span[2]/a/text()')
        info_user['weibo_number'] = page.xpath('//p[@class="person_num"]/span[3]/a/text()')
        info_user['location'] = page.xpath('//p[@class="person_addr"]/span[2]/text()')
        
        # 判断是否存在下一页，存在则继续遍历，不存在则停止
        next_page = page.xpath('//a[@class="page next S_txt1 S_line1"]/@href')
        if next_page:
            i = int(next_page[0][70:])
            if i>j:
                break
            else:
                info_user_d = info_user_d.append(pd.DataFrame(info_user))
            time.sleep(random.randint(5, 10))
        else:
            break
        
    # 返回DataFrame    
    return info_user_d
    
if __name__ == '__main__':
    info_user_d = crawl_list(i=, j=)
    print(info_user_d.shape)
    
    

# -*- coding: utf-8 -*-
"""模拟登陆脚本.

@author: zan

"""

import base64
import binascii
import random
import re
from urllib import parse
import rsa
import requests
from PIL import Image
from http import cookiejar

class Launcher():
    """模拟登陆.
    
    说明：
    本类的方法分为两块。获取模拟登陆表单数据的方法和模拟登陆的方法。
    获取的表单数据包括生成用户名、密码、验证码。
    
    """
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple\
                        WebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }


    def get_su(self):
        """使用base64对username进行编码，获得编码后的username"""
        
        username_quote = parse.quote_plus(self.username)     
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))    
        return username_base64.decode("utf-8")     

    def get_server_data(self):
        """模拟预登陆过程，从服务器返回的json文件中取得nonce , servertime , pubkey 等字段值，用于密码加密"""
        
        pre_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=s\
        inaS\SOController.preloginCallBack&su=' + self.get_su() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)'
        pre_data_res = self.session.get(pre_url, headers = self.headers)
        sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))
        
        return sever_data   

    def get_cha(self, pcid):
        """获取验证码图片"""
        
        cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        cha_page = self.session.get(cha_url, headers=self.headers)
        # 保存验证码到本地
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        try:
            # 弹出验证码图片
            im = Image.open("cha.jpg")
            im.show()
            im.close()
        except:
            print(u"请到当前目录下，找到验证码后输入")

    def get_password(self):
        """获取加密后的密码"""
        
        # 获取预登陆阶段的相关字段
        sever_data = self.get_server_data()
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        pubkey = sever_data["pubkey"]
        
        # 加密密码
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password) 
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  
        passwd = binascii.b2a_hex(passwd) 
        
        return passwd

    def postdata(self):
        """创建用于登陆的表单数据"""
        
        sever_data = self.get_server_data()
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        password_secret = self.get_password()
        postdata = {
                'entry': 'weibo',
                'gateway': '1',
                'from': '',
                'savestate': '0',
                'useticket': '1',
                'pagerefer': '',
                'vsnf': '1',
                'su': self.get_su(),
                'service': 'miniblog',
                'servertime': servertime,
                'nonce': nonce,
                'pwencode': 'rsa2',
                'rsakv': '1330428213',
                'sp': password_secret,
                'sr': '1366*768',
                'encoding': 'UTF-8',
                'prelt': '183',
                'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                'returntype': 'META'
        }
        
        return postdata

    def login(self):
        """模拟登陆，这里需请求三次才能成功登录"""

        # 加载cookie失败则执行表单登陆，加载cookie成功但登陆失败也执行表单登陆
        self.session.cookies = cookiejar.LWPCookieJar('cookie')
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print('Cookie未能加载，将执行正常表单登录')
        test = self.session.get('http://s.weibo.com/')  
        test.encoding = 'utf-8'
        if test.text.find("$CONFIG['islogin'] = '1';") != -1:
            print('登录成功！\r\n')
            
        # 执行表单登陆    
        else: 
            postdata = self.postdata()
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
            sever_data = self.get_server_data()
            showpin = sever_data["showpin"] 
            
            # showpin为0则无需识别验证码
            if showpin == 0:
                # 向表单入口提交请求
                login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
                login_page = self.session.post(login_url, data=postdata, headers=self.headers)
                
                # 再次请求
                login_loop = (login_page.content.decode("GBK"))
                pa = r'location\.replace\([\'"](.*?)[\'"]\)'
                loop_url = re.findall(pa, login_loop)[0]
                login_index = self.session.get(loop_url, headers=self.headers)
                
                # 再次请求
                uuid = login_index.text
                uuid_pa = r'"uniqueid":"(.*?)"'
                uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
                web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
                weibo_page = self.session.get(web_weibo_url, headers=self.headers)
                
                # 打印登录成功提示
                weibo_pa = r'<title>(.*?)</title>'
                user_name = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
                print('登陆成功，你的用户名为：'+user_name)
                
                # 保存登录成功的cookie
                self.session.cookies.save(ignore_discard=True, ignore_expires=True)
                
            # showpin为1则需识别验证码，其他操作同上
            else:
                # 获得验证码
                pcid = sever_data["pcid"]
                self.get_cha(pcid)
                postdata['door'] = input(u"请输入验证码:")
                login_page = self.session.post(login_url, data=postdata, headers=self.headers)
                
                login_loop = (login_page.content.decode("GBK"))
                pa = r'location\.replace\([\'"](.*?)[\'"]\)'
                loop_url = re.findall(pa, login_loop)[0]
                login_index = self.session.get(loop_url, headers=self.headers)
                
                uuid = login_index.text
                uuid_pa = r'"uniqueid":"(.*?)"'
                uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
                web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
                weibo_page = self.session.get(web_weibo_url, headers=self.headers)
                
                weibo_pa = r'<title>(.*?)</title>'
                user_name = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
                print('登陆成功，你的用户名为：'+user_name)
                
                self.session.cookies.save(ignore_discard=True, ignore_expires=True)

if __name__ == '__main__':
	username = input('请输入账号')
	password = input('请输入密码')
    Launcher(username, password).login()
        
   
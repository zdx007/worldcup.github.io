# worldcup.github.io

这是个人爬虫项目，爬取新浪微博世界杯博主信息。
爬取的字段如下：
1、博主id
2、博主名称
3、微博地址
4、粉丝数
5、关注数
6、发微博数
7、地区

爬取的表结构为：

爬取的入口为：
http://s.weibo.com/user/%25E4%25B8%2596%25E7%2595%258C%25E6%259D%25AF&auth=org_vip&page=1

爬取的流程：
1、模拟登陆新浪微博
2、向搜索页发送请求，获得包含字段的html源码，它被包装成了json，需从中提取出来
3、利用xpath解析html源码，获得字段，存储在DataFrame
4、将DataFrame写入MySQL

文件说明：
main.py 为主文件，运行即可爬取数据
login.py 为模拟登陆脚本
list.py 为解析字段脚本

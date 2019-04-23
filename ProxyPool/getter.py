#coding:utf-8
from tester import Tester
from db import RedisClient
from crawler import Crawler
from setting import *
import sys

'''
获取器
'''

class Getter():
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        '''
        判断是否达到了代理池限制
        '''
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__): #获取所有crawl开头的列表
                callback = self.crawler.__CrawlFunc__[callback_label]
                #获取代理
                proxies = self.crawler.get_proxies(callback)  # 调用每一个获取函数
                for proxy in proxies:
                    self.redis.add(proxy) #添加进数据库

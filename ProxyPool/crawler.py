import json
import re
from utils import get_page
from pyquery import PyQuery as pq
'''
获取模块
'''
class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items(): #返回可遍历的(键，值)元组
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)

class Crawler(object, metaclass=ProxyMetaclass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)): #eval()执行字符串表达式，并返回表达式的值
            print('成功获取到代理', proxy)
            proxies.append(proxy)
        return proxies

    def crawl_ip3366(self):
        for page in range(1, 4):
            start_url = 'http://www.ip3366.net/free/?stype=1&page={}'.format(page)
            html = get_page(start_url)
            ip_address = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            # \s* 匹配空格，起换行作用
            re_ip_address = ip_address.findall(html)  #findall生成列表形式
            for address, port in re_ip_address:
                result = address + ':' + port
                yield  result.replace(' ', '') #形成生成器并将 ' ' 用 '' 代替

    def crawl_kuaidaili(self):
        for i in range(1,4):
            start_url = 'http://www.kuaidaili.com/free/inha/{}/'.format(i)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<td data-title="IP">(.*?)</td>')
                re_ip_address = ip_address.findall(html)
                port = re.compile('<td data-title="PORT">(.*?)</td>')
                re_port = port.findall(html)
                for address,port in zip(re_ip_address, re_port):  #zip()将对象打包为一个元组
                    address_port = address + ':' + port
                    yield address_port.replace(' ','')

    def crawl_xicidaili(self):
        for i in range(1,3):
            start_url = 'http://www.xicidaili.com/nn/{}'.format(i)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cookie': '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWRjYzc5MmM1MTBiMDMzYTUzNTZjNzA4NjBhNWRjZjliBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUp6S2tXT3g5a0FCT01ndzlmWWZqRVJNek1WanRuUDBCbTJUN21GMTBKd3M9BjsARg%3D%3D--2a69429cb2115c6a0cc9a86e0ebe2800c0d471b3',
                'Host': 'www.xicidaili.com',
                'Referer': 'http://www.xicidaili.com/nn/3',
                'Upgrade-Insecure-Requests': '1',
            }
            html = get_page(start_url,options=headers)
            if html:
                find_trs = re.compile('<tr class.*?>(.*?)</tr>', re.S) #re.S匹配除了换行符之外的所有字符
                trs = find_trs.findall(html)
                for tr in trs:
                    #可以直接使用下面的匹配，也可先找到所有tr后再匹配
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(tr)
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(tr)
                    for address,port in zip(re_ip_address,re_port):
                        address_port = address + ':' + port
                        yield address_port.replace(' ','')

    def craw_iphai(self):
        start_url = 'http://www.iphai.com/'
        html = get_page(start_url)
        if html:
            #搞不懂为他为什么做这么复杂，可以直接用正则匹配
            find_tr = re.compile('<tr>(.*?)</tr>',re.S)
            trs = find_tr.findall(html)
            for s in range(1,len(trs)): #网站只有一页，有多少行匹配循环多少次
                find_ip = re.compile('<td>\s*?(\d+\.\d+\.\d+\.\d+)\s*?</td>', re.S)
                re_ip_address = find_ip.findall(trs[s])
                find_port = re.compile('<td>\s*?(\d+)\s*?</td>',re.S)
                re_port = find_port.findall(trs[s])
                for address, port in zip(re_ip_address, re_port):
                    address_port = address + ':' + port
                    yield address_port.replace(' ','')

    def crawl_data5u(self):
        start_url = 'http://www.data5u.com/free/gngn/index.shtml'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=47AA0C887112A2D83EE040405F837A86',
            'Host': 'www.data5u.com',
            'Referer': 'http://www.data5u.com/free/index.shtml',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }
        html = get_page(start_url, options=headers)
        if html:
            ip_address = re.compile('<span><li>(\d+\.\d+\.\d+\.\d+)</li>.*?<li class="port.*?>(\d+)</li>',re.S)
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield  result.replace(' ','')

    def crawl_ip3366_2(self):
        for i in range(1,4):
            start_url = 'http://www.ip3366.net/?stype=1&page={}'.format(i)
            html = get_page(start_url)
            if html:
                find_tr = re.compile('<tr>(.*?)</tr>',re.S)
                trs = find_tr.findall(html)
                for s in trs:
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(s)
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(s)
                    for address,port in zip(re_ip_address, re_port):
                        address_port = address + ':' + port
                        yield address_port.replace(' ','')
#coding:utf-8
import requests
from requests.exceptions import ConnectionError

#建立头部
base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

def get_page(url,options={}):
    '''
    抓取代理
    :param url: 代理网站 
    :param options: 添加的访问头部
    :return: 
    '''
    headers = dict(base_headers, **options) #创建字典headers,并添加字典数据，如果已有，便覆盖
    print(headers)
    print('正在抓取', url)
    try:
        response = requests.get(url, headers=headers)
        print('抓取成功', url, response.status_code)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        print('抓取失败', url)
        return None


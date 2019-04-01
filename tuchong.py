#爬取图虫私房图片
#coding:utf-8
from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from hashlib import md5
import requests
import os

base_url = "https://tuchong.com/rest/tags/%E7%A7%81%E6%88%BF/posts?"
headers = {
    'Host': 'tuchong.com',
    "Referer": 'https://tuchong.com/tags/%E7%A7%81%E6%88%BF/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_page(page):
    #这是一个Ajax请求网站，这是get请求的参数
    params = {
        'page': page,
        'count': '20',
        'order': 'weekly'
    }
    url = base_url + urlencode(params) #拼接真实URL的json
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("连接成功")
            return response.json() #返回为json格式
    except requests.ConnectionError as e:
        print("连接失败", e.args)

#分析网址
def parse_page(json):
    if json:
        items = json.get('postList')
        for item in items:
            try:
                item = item.get('url') #获取真实网页地址
                return down_load(item)
            except AttributeError as e:
                print("获取失败", e.args)
                continue

#下载图片网址
def down_load(url):
    html = requests.get(url,headers=headers)
    try:
        if html.status_code == 200:
            print("连接成功")
            soup = BeautifulSoup(html.text,'lxml')  #解析网页
            photo_list = soup.find(class_='post-content').find_all(name='img',class_="multi-photo-image")
            for photo in photo_list:
                save_img(photo.get('src')) #获取图片地址
    except requests.ConnectionError as e:
        print('url连接失败', e.args)

def save_img(img_url):
    #使用os创建文件夹
    if not os.path.exists("G://exercise//2019//tuchong"):
        os.mkdir("G://exercise//2019//tuchong")
    try:
        img = requests.get(img_url)
        if img.status_code == 200:
            file_path = '{0}.{1}'.format(md5(img.content).hexdigest(),'jpg')   #md5是将二进制数据转化为16位字符串，这里用作保存名字
            with open("G://exercise//2019//tuchong//" + file_path, 'wb') as f:
                f.write(img.content)
                print('下载成功')
        else:
            print("已经下载")
    except requests.ConnectionError:
        print('图片保存失败')

def main(i):
    json = get_page(i)
    parse_page(json)

if __name__ == "__main__":
    pool = Pool()    #开启进程池
    num = ([int(i) for i in range(1,40)])  #将循环数化为列表
    pool.map(main,num) # map()函数开启多进程，第一个参数为运行函数，第二个参数为进程数列表
    pool.close()       # 关闭进程池
    pool.join()

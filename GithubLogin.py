#coding:utf-8
import requests
from bs4 import BeautifulSoup
from lxml import etree

'''
模拟登陆github
'''
class login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            'Host': 'github.com'
        }
        self.login_url = 'https://github.com/login'
        self.post_url = 'https://github.com/session'
        self.login_url = 'https://github.com/settings/profile'
        self.feed_url = 'https://github.com/dashboard-feed'  # ajax 加载请求
        self.session = requests.Session()  # Session() 维持会话,自动处理cookies

    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)  #etree.HTML(html)解析，得到Element对象
        token = selector.xpath('//input[@name="authenticity_token"]/@value')[0]#选取所有div节点下的第二个input节点下的value属性的值
        print("token>>>>>>>>>>>>>>>>>>>>>>>",token)
        return token

    def login(self, email, password):
        post_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': self.token(),
            'login': email,
            'password': password,
        }
        #先请求登陆，再请求一次获取动态ajax
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        response = self.session.get(self.feed_url, headers = self.headers)
        if response.status_code == 200:
            self.dynamics(response.text)

        response = self.session.get(self.login_url, headers = self.headers)
        if response.status_code == 200:
            self.profile(response.text)

    #关注人的动态
    def dynamics(self,html):
        #print(html)
        selector = BeautifulSoup(html, 'lxml')
        dynamics = selector.find_all(class_='d-flex flex-items-baseline')
        #print(dynamics)
        for item in dynamics:
            dynamic = (item.find(name='div').get_text().replace('\n',' ')) #replace('\n',' ')将换行更改为空格
            print(dynamic)

    #个人信息
    def profile(self, html):
        selector = etree.HTML(html)
        name = selector.xpath('//input[@id="user_profile_name"]/@value')[0]
        email = selector.xpath('//select[@id="user_profile_email"]/option[2]/text()')[0] #获取id为user_profile_email下的第二个option的所有文档，返回为列表，所以取第一个
        print(name,email)

if __name__ == "__main__":
    login = login()
    login.login(email='302559651@qq.com', password='*****')

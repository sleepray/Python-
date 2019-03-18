#coding:utf-8
from bs4 import BeautifulSoup
import re
from urllib import parse

class HtmlParser(object):

    def _get_new_urls(self, page_url, soup):
        new_urls = set()

        #<a target="_blank" href="/item/%E5%8D%A1%E8%80%90%E5%9F%BA%E6%A2%85%E9%9A%86%E5%A4%A7%E5%AD%A6">卡耐基梅隆大学</a>
        links = soup.find_all('a', href= re.compile(r"/item/")) #通过正则表达式匹配新的URL
        print("links>>>>>",links)
        for link in links:
            new_url = link['href']  #获得新的URL
            new_full_url =parse.urljoin(page_url, new_url) # 通过 urlparse.urljoin 补全网站网址
            print(">>>>>> new_full_url", new_full_url)
            new_urls.add(new_full_url) #将补全的 URL 加入进 new_urls
        return new_urls


    def _get_new_data(self, page_url, soup):
        res_data = {}

        #url
        res_data['url'] = page_url

        #<dd class="lemmaWgt-lemmaTitle-title"><h1>***</h1>
        title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1") #找到标题
        res_data['title'] = title_node.get_text()                                   # 将标题内容赋值到 res_data[]

        #<div class="lemma-summary" label-module="lemmaSummary"><div>
        summary_node = soup.find('div', class_="lemma-summary")                     # 找到日志
        res_data['summary'] = summary_node.get_text()                               # 将日志内容加入到 res_data

        return res_data

    def parser(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return

        soup = BeautifulSoup(html_cont, 'html.parser',from_encoding='utf-8')        # 解析html_cont
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data


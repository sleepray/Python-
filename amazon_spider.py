# coding:utf-8
import codecs
from urllib import parse
import requests
from bs4 import BeautifulSoup


ur = "https://www.amazon.cn/gp/bestsellers/books/"

def download(URL):
    # 伪装成浏览器发送请求并使用requests获取网页  content 打开网页为二进制数据
    reques = requests.get(URL, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
    #判断是否连接成功
    if reques.status_code == 200:
        return reques
    else:
        return None

def parse_html(html):
    soup = BeautifulSoup(html.text,"html.parser") #解析网页

    books = []

    book_list = soup.find("ol", attrs={'id':"zg-ordered-list"})
    for book_list_name in book_list.find_all('li'):
        #print(book_list_name)

        book_name = book_list_name.find("div", attrs = {"class":"p13n-sc-truncate p13n-sc-line-clamp-1"}).get_text()
        book_anthor = book_list_name.find('span', attrs = {"class":"a-size-small a-color-base"}).get_text()
        book_price = book_list_name.find('span', attrs = {"class":"p13n-sc-price"}).get_text()


        books.append(book_name)
        books.append(book_anthor)
        books.append(book_price)

    next_page = soup.find('li', attrs = {"class":"a-last"}).find('a')

    #获取下一页
    if next_page:
        return books, next_page['href']
    else:
        return books, None


def main():

    url = ur
    with codecs.open("books", "wb", encoding="utf-8") as f:
        while url:
            html = download(url)
            books, url = parse_html(html)
            f.write('{books}\n'.format(books='\n'.join(books))) #写入资料

    f.close()
if __name__ == "__main__":
    main()
# coding:utf-8
import xlwt
from urllib import parse
import requests
from bs4 import BeautifulSoup
Url = "https://movie.douban.com/top250"
root = "G://exercise//2019//imooc//spider//douban_spider//img//" #文件夹地址

def downlod(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        html = requests.get(url, headers = headers)
        if html.status_code == 200:
            return html.text
    except requests.RequestException: #如果请求错误，返回None
        return None


book = xlwt.Workbook(encoding='utf-8', style_compression=0) # 建立excel文档，编码为 utf-8，不压缩
print("book>>>>",book)
sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)# 加入一个工作表
#写入数据
sheet.write(0, 0, '名称')
sheet.write(0, 1, '图片')
sheet.write(0, 2, '排名')
sheet.write(0, 3, '评分')
sheet.write(0, 4, '作者')
sheet.write(0, 5, '简介')

n = 1

def lxml(html):

    soup = BeautifulSoup(html, 'lxml')
    movies_list = soup.find(class_ = 'grid_view').find_all('li') # 解析网页
    for movies in movies_list:
        movies_name = movies.find('span', class_ = 'title').string
        movies_author = movies.find('p').text
        movies_star = movies.find(class_ = 'rating_num').string
        movies_num = movies.find(class_ = 'pic').find('em').string
        movies_img = movies.find('img').get('src')
        #判断movies_intr有没有简介，没有就不赋值
        if(movies.find(class_ = 'inq')!=None):
            movies_intr = movies.find(class_ = 'inq').string
        #print("爬取电影：" + movies_num + ' | ' + movies_name + ' | ' + movies_star + ' | ' + movies_author + ' | ' + movies_intr
        print("爬取电影：" + movies_num + ' | ' + movies_name + ' | ' + movies_star + ' | ' + movies_author + ' | ' + movies_intr)

        global n
        # 写入数据
        sheet.write(n, 0, movies_name)
        sheet.write(n, 1, movies_img)
        sheet.write(n, 2, movies_num)
        sheet.write(n, 3, movies_star)
        sheet.write(n, 4, movies_author)
        sheet.write(n, 5, movies_intr)


        # 获取图片链接
        img = requests.get(movies_img)
        path = root + movies_num + '.jpg' # 设置保存图片路径
        with open(path, "wb") as f:
            f.write(img.content) #写入文件夹

        n += 1
    # 下一页
    next_page = soup.find(class_ = 'next').find('a')
    if next_page:
        urls = Url + next_page['href'] # 将URL拼接
        return urls
    else:
        return None

def main():
    url = Url
    while url:
        url = downlod(url)
        url = lxml(url)



if __name__ == "__main__":
    main()

book.save(u"豆瓣TOP250.xlsx")

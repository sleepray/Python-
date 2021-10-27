#爬取豆瓣电影新片榜，影片信息存入excel，宣传片及剧照存入文件夹

import os
import requests
from bs4 import BeautifulSoup
import lxml,string,re,xlwt


url = 'https://movie.douban.com/chart'  #新片榜url
excel_local = 'F://code//test_code//test1//test_file' #excel位置
img_down= excel_local + '//img//' #图片及视频位置

def getHTMLText(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
        html = requests.get(url, headers = headers)
        if html.status_code == 200:
            return html.text
    except requests.RequestException:
        return "产生异常"

book = xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet = book.add_sheet('豆瓣电影',cell_overwrite_ok=True)
#写入
sheet.write(0,0,'标题')
sheet.write(0,1,'导演')
sheet.write(0,2,'演员')
sheet.write(0,3,'评分')
sheet.write(0,4,'国家')
sheet.write(0,5,'时间')

#解析url并写入excel
def lxml(url,num):

    soup = BeautifulSoup(getHTMLText(url), 'lxml')
    soups = soup.find_all(id = 'info')
    for data in soups:
        a = data.text
    actor = re.findall(r'主演: (.*)',a)
    local = re.findall(r'制片国家/地区: (.*)',a)
    title = soup.find(property = 'v:itemreviewed').text
    score = soup.find(class_="ll rating_num").text
    time = re.findall(r'上映日期: (.*)',a)
    director = re.findall(r'导演: (.*)',a)
    summary = soup.find(property='v:summary').text.replace(" ", '')
    img_list = soup.find(class_='related-pic-bd').find_all('img')
    img_title = soup.find('img').get('src')
    print('正在爬取： {0},评分：{1}'.format(title,score))

    #封面写入
    down_load(img_title,img_down + title + '//{}'.format(title) +'.jpg',img_down + title)
    #列表图片写入
    i = 1
    for img in img_list:
        src = img.get('src')
        path_title = img_down + title
        path = img_down + title + '//{0}{1}'.format(title,i) + '.jpg'
        down_load(src, path, path_title)
        i += 1

    #宣传视频写入
    video_url = soup.find(class_='related-pic-video').get('href')
    video_herf = BeautifulSoup(getHTMLText(video_url), 'lxml')
    video_content = video_herf.find('source').get('src')
    down_load(video_content, img_down + title + '//{}'.format(title) + '.mp4', img_down + title)

    sheet.write(num,0,title)
    sheet.write(num,1,''.join(director))
    sheet.write(num,2,''.join(actor))
    sheet.write(num,3,score)
    sheet.write(num,4,''.join(local))
    sheet.write(num,5,''.join(time))
    sheet.write(num,6,summary)


#视频图片存入函数
def down_load(img_url,path,path_title):
    img = requests.get(img_url).content
    folder = os.path.exists(path_title)
    if not folder:
        os.makedirs(path_title)
        with open(path, 'wb') as f:
            f.write(img)
    else:
        with open(path, 'wb') as f:
             f.write(img)

#获取排行榜上的每一个电影详情页的url
def get_url(url):
    n = 0
    soup = BeautifulSoup(getHTMLText(url), 'lxml')
    html = soup.find_all(width='100%')
    for url_list in html:
        n += 1
        url = url_list.find('a').get('href')
        lxml(url,n)



if __name__ == "__main__":
    get_url(url)
    book.save('{}//豆瓣新片榜.xlsx'.format(excel_local))
    print('---------------------------------')
    print('爬取结束')
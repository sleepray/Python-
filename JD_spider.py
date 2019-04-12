#coding:utf-8
import pymongo
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote

#无界模式（不打开浏览器）
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)

#连接MongoDB
MONGO_URL = 'localhost'
MONGO_DB = 'JD'
MONGO_COLLECTION ='products'
client = pymongo.MongoClient(MONGO_URL)
#创建指定集合 MONGO_DB
db = client[MONGO_DB]

# 搜索的物品与搜索多少页
page = 100
search = '手机'
#等待时长最多10s
wait = WebDriverWait(browser,10)
browser.get("https://www.jd.com/")


def search_page():
    '''
    搜索关键字
    '''
    try:
        #获取京东搜索框并输入search后搜索
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#search .form > input')))
        clik = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search .form .iconfont')))
        input.clear()
        input.send_keys(search)
        clik.click()
        #等待第搜索结果的搜索节点出现，防止还未加载出搜索页就返回URL
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage .p-skip > input')))
        for i in range(1,page + 1):
            index_page(i)
    except TimeoutException:
        search_page()

def index_page(page):
    '''

    抓取索引页
    :param page: 页码
    '''
    print('正在爬取第', page, '页')
    try:
        # 将浏览器拉到底部，将未加载的30个Ajax加载出
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)') #此时浏览器browser已经是搜索结果界面
        #停留1s ,让下一页和Ajax加载完成
        time.sleep(1)
        if page > 1:
            # 等待获取页码输入框完成后传入定位元组
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage .p-skip > input')))#获取id为J_bottomPage的内部class为p-skip的内部class为input-txt的节点
            # 等待获取确定按钮完成
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage .p-skip .btn.btn-default')))
            input.clear()
            input.send_keys(page)
            submit.click()
            #和上面同理
            browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
            # 等待当这个节点包含 page 文字
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#J_bottomPage .p-num .curr'), str(page)))
            #等待当所有商品信息节点加载完成
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#J_goodsList .gl-warp.clearfix > li > div ')))
        html = browser.page_source
        get_products(html)
    except TimeoutException:
        index_page(page)

def get_products(html):
    '''

    提取商品数据
    '''
    doc = BeautifulSoup(html,'lxml')
    infors = doc.find(class_ = 'gl-warp').find_all(class_ = 'gl-item')
    n = 0
    for infor in infors:
        n += 1
        # 查看源码得知，大多数图片并不是保存在src内，而是保存在 data-lazy-img中
        if infor.find(class_='p-img').find(name='img').get('data-lazy-img') != 'done':
            image = infor.find(class_='p-img').find(name='img').get('data-lazy-img')
        else:
            image = infor.find(class_='p-img').find(name='img').get('src')
        price = infor.find(class_='p-price').find(name='i').string #string获取字符串
        title = infor.find(class_='p-name p-name-type-2').find(name='em').get_text() #get_text()获取全部文本
        commit = infor.find(class_='p-commit').find(name='strong').find(name='a').string
        try:  #有些没有，用try跳过失效字节
            shop = infor.find(class_='J_im_icon').find(name='a').string
        except:
            continue
        product = {
            'image': image,
            'price': price,
            'title': title,
            'commit': commit,
            'shop': shop,
        }
        print(n, product)
        save_to_mongo(product)


def save_to_mongo(result):
    """
     保存至 MongoDB
     :param result: 结果
    """
    try:
        if db[MONGO_COLLECTION].insert_one(result): #写入
            print("存储到MongoDB成功")
    except Exception:
        print("存储到MongoDB失败")


# 不能使用多进程，因为浏览器是单个进行，会导致一直在获取直到cpu占满
if __name__ == "__main__":
    search_page()
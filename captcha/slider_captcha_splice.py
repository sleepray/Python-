#coding:utf-8

'''
使用拼接图片通过bilibili验证码
思路： 1.获取打乱后的图片
      2.获取每个小图片对应的位置偏移量
      3.根据图片的位置偏移量拼接图片
      4.通过图片的RGB作为对应，超出阈值为图片不同处，也就是需要滑动的距离
     5.需要模拟人的滑动，采用先加速后减速的方法,并生成多次位移距离形成拖动躲过检查。
'''

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from io import BytesIO
from selenium.webdriver import ActionChains
from PIL import Image
import requests
import re
import time

user = '15882123308'
word = 'iloveyou88'
BORDER = 10 #由于滑块前还有10个像素的空余，需减掉才为滑动距离

class CrackGeetest():
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.user = user
        self.word = word

    # 当引用计数为0时，自动运行
    def __del__(self):
        self.browser.close()

    def get_div(self):
        '''
        获取标签
        :return: 缺口图片和未缺口图片div
        '''
        bg_div = []
        fullbg_div = []
        # 如果bg_div标签和 fullbg_div标签还未加载出来便一直获取
        while bg_div == [] and fullbg_div ==[]:
            bs = BeautifulSoup(self.browser.page_source, 'lxml')
            bg_div = bs.find_all(class_='gt_cut_bg_slice')
            fullbg_div = bs.find_all(class_='gt_cut_fullbg_slice')
        return bg_div,fullbg_div

    def get_code(self,bg_div,fullbg_div):
        '''
        获取验证码图片
        :return:缺口图片与未缺口图片的二进制数据
        '''
        # 获取缺口背景图片url
        bg_url = re.findall('background-image:\surl\("(.*?)"\)', bg_div[0].get('style'))
        # 获取背景图片url
        fullbg_url = re.findall('background-image:\surl\("(.*?)"\)', fullbg_div[0].get('style'))

        # 将图片格式存为 jpg 格式
        bg_url = bg_url[0].replace('webp', 'jpg')
        fullbg_url = fullbg_url[0].replace('webp', 'jpg')

        # 下载图片
        bg_image = requests.get(bg_url).content
        fullbg_image = requests.get(fullbg_url).content
        print('完成图片下载')

        # 写入图片
        bg_image_file = BytesIO(bg_image)
        fullbg_image_file = BytesIO(fullbg_image)
        return bg_image_file,fullbg_image_file

    def get_list(self,bg_div, fullbg_div):
        '''
        获取图片位置列表
        :param bg_div: 缺口标签
        :param fullbg_div: 无缺口标签
        :return: 图片位置列表
        '''

        # 存放每个合成缺口背景图片的位置
        bg_location_list = []
        # 存放每个合成背景图片的位置
        fullbg_location_list = []

        for bg in bg_div:
            location = {}
            location['x'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][1])
            bg_location_list.append(location)

        for fullbg in fullbg_div:
            location = {}
            location['x'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', fullbg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', fullbg.get('style'))[0][1])
            fullbg_location_list.append(location)

        return bg_location_list,fullbg_location_list


    def get_mergy_Image(self, image_file, location_list):
        """
            将原始图片进行合成
            :param image_file: 图片文件
            :param location_list: 图片位置
            :return: 合成新的图片
            """

        # 存放上下部分的各个小块
        upper_half_list = []
        down_half_list = []

        image = Image.open(image_file)

        # 通过 y 的位置来判断是上半部分还是下半部分,然后切割
        for location in location_list:
            if location['y'] == -58:
                # 间距为10，y：58-116
                im = image.crop((abs(location['x']), 58, abs(location['x']) + 10, 116))
                upper_half_list.append(im)
            if location['y'] == 0:
                # 间距为10，y：0-58
                im = image.crop((abs(location['x']), 0, abs(location['x']) + 10, 58))
                down_half_list.append(im)

        # 创建一张大小一样的图片
        new_image = Image.new('RGB', (260, 116))

        # 粘贴好上半部分 y坐标是从上到下（0-116）
        offset = 0
        for im in upper_half_list:
            new_image.paste(im, (offset, 0))  #k.paste(i,(x,y))  i=图片文件  x,y=图片i在图片k所在位置坐标
            offset += 10  #  x轴偏移量每张图为10

        # 粘贴好下半部分
        offset = 0
        for im in down_half_list:
            new_image.paste(im, (offset, 58))
            offset += 10

        return new_image


    def get_slider(self):
        '''
        获取滑块
        :return: 滑块对象
        '''
        slider = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.gt_slider .gt_slider_knob.gt_show')))
        return slider

    def is_pixel_equal(self, image1, image2, x, y):
        '''
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        '''
        #取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60  # 像素差值的阈值
        #比较每一个像素点差值
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
            pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        '''
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        '''
        # 阈值
        print(image1.size[0])
        print(image2.size[1])
        left = 60 # 原网页图块的大小 * 截取图片的比例
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i  #因为是移动网页的图，要将比例转化为原比例100%
                    return left
        return left

    def get_track(self, distance):
        '''
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        '''
        #移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < (distance):
            if current < mid:
                # 加速度为正 2
                a = 2
            else:
                # 加速度为 负3
                a = -3
            # 初速度 v0
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a * t
            #移动距离 x = v0t + 1/2 * a * t^2
            move = v0 * t + 1/2 * a * t * t
            #当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, tracks):
        '''
        拖动滑块到缺口处
        :param slider: 滑块
        :param tracks: 轨迹
        :return:
        '''
        ActionChains(self.browser).click_and_hold(slider).perform()  # ActionChains 拖拽动作 click_and_hold() 点击并保持 perform() 执行动作
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset = x, yoffset = 0).perform()  #move_by_offset(x,y)移动到指定元素坐标位置(x,y)
        time.sleep(0.5)
        ActionChains(self.browser).release().perform() # 松开鼠标左键

    def open(self):
        '''
        打开网页输入用户名和密码
        :return: None
        '''
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#login-app .item.username.status-box > input'))) # 用户名
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#login-app .item.password.status-box > input'))) # 密码
        email.send_keys(self.user)
        password.send_keys(self.word)

    def login(self):
        '''
        登录
        :return:None
        '''
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login-app .btn.btn-login'))) # 登录按键
        submit.click()
        time.sleep(10)
        print('登录成功')

    def crack(self):
        # 输入用户密码
        self.open()
        # 获取滑块位置
        slider = self.get_slider()
        # 获取标签
        img1_div,img2_div = self.get_div()
        # 获取验证码图片
        img1,img2 = self.get_code(img1_div,img2_div)
        # 获取验证图片列表
        img1_list, img2_list = self.get_list(img1_div,img2_div)
        # 合成验证码图片
        image1 = self.get_mergy_Image(img1,img1_list)
        image2 = self.get_mergy_Image(img2,img2_list)
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print('缺口位置', gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        track = self.get_track(gap)
        print('滑动轨迹', track)
        # 拖动滑块
        self.move_to_gap(slider,track)
        time.sleep(0.5)  # 等待验证 Axja 信息加载
        word = self.browser.find_element_by_class_name('gt_info_type').text
        print(word)
        # 失败后重试
        if word == "验证通过:":
            self.login()
        else:
            self.crack()

if __name__ == "__main__":
    crack = CrackGeetest()
    crack.crack()
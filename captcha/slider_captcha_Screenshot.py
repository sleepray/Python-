#coding:utf-8
'''

使用截取验证码图片通过bilibili验证码
思路: 1.截取整个浏览器截屏
     2.获取验证码所在位置坐标
     3.通过所在位置坐标在整个截屏中获取验证码的图片(需注意截取图片和个人电脑所使用比列一致，而网页为100%，若有改变比例，需要改变相应比例）
     4.通过图片的RGB作为对应，超出阈值为图片不同处，也就是需要滑动的距离
     5.需要模拟人的滑动，采用先加速后减速的方法,并生成多次位移距离形成拖动躲过检查。

'''
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from io import BytesIO
from selenium.webdriver import ActionChains
from PIL import Image
import time

user = '15882123308'
word = 'iloveyou88'
BORDER = 10      #由于滑块前还有10个像素的空余，需减掉才为滑动距离

class CrackGeetest():
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.user = user
        self.word = word

    def __del__(self):
        self.browser.close()

    def get_geetest_button(self):
        '''
        获取初始验证
        :return: 点击对象
        '''

        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gt_slider .gt_guide_tip.gt_show')))
        return button

    def get_screenshot(self):
        '''
        获取网页截图
        :return: 截图对象
        '''
        screenshot = self.browser.get_screenshot_as_png() # 获取屏幕截图，保存为二进制数据
        screenshot = Image.open(BytesIO(screenshot)) # 打开这个截图
        return screenshot

    def get_position(self):
        '''
        获取验证码位置
        :return: 验证码位置元组
        '''
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#gc-box .gt_cut_fullbg.gt_show')))
        time.sleep(2.5)
        location = img.location #
        size = img.size
        #因为我电脑设置的放大125%的比例，而截图是截的原比例，所以需要放大至125%
        top, bottom, left, right = location['y']*1.25, location['y']*1.25 + size['height']*1.25, location['x']*1.25, location['x']*1.25 + size['width']*1.25
        return (top, bottom, left, right)

    def get_geetest_image(self, name='captcha.png'):
        '''
        获取验证码图片
        :return: 图片对象
        '''
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom)) # 获取验证码图片
        captcha.save(name)
        return captcha

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
        pixel1 = image1.load()[x, y] # load()[x,y] 获取 x,y 坐标的RGB元素
        pixel2 = image2.load()[x, y]
        threshold = 60 * 1.25  # 像素差值的阈值
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
        left = int(60 * 1.25) # 原网页图块的大小 * 截取图片的比例
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i/1.25  #因为是移动网页的图，要将比例转化为原比例100%
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
        # 点击验证按钮
        button = self.get_geetest_button()
        button.click()
        # 获取验证码图片
        image1 = self.get_geetest_image(name='captcha1.png')
        # 点按呼出缺口
        slider = self.get_slider()
        slider.click()
        # 获取带缺口的验证码图片
        image2 = self.get_geetest_image(name='captcha2.png')
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
        time.sleep(1)  # 等待验证 Axja 信息加载
        #try:
            #success = self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.gt_info_type'),"验证通过"))
            #word = self.browser.find_element_by_class_name('gt_info_type')
            #print(success,word.text)
        #except:
            #success = False
        #print(success, word.text)
        #失败后重试
        #if not success:
            #self.crack()
        #else:
            #self.login()

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
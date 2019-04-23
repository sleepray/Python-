import asyncio
import aiohttp
import time
import sys
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError
from db import RedisClient
from setting import *

'''
检测模块
'''

class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    #函数前面加 async 表示此函数是异步的
    async def test_single_proxy(self, proxy):
        '''
        测试单个代理
        :param proxy: 
        :return: 
        '''
        conn = aiohttp.TCPConnector(verify_ssl=False) #获取请求，verify_ssl=False防止ssl证书报错
        async with aiohttp.ClientSession(connector=conn) as session: #创建一个session对象(session用于存储特定对话所需信息)
            try:
                if isinstance(proxy, bytes): #判断proxy是不是bytes类型
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async  with session.get(TEST_URL, proxy=real_proxy, timeout=15, allow_redirects=False) as response:#allow_redirects=False禁止重定向
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy) #调用db的max()方法将score设为100
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)#调用db的decrease方法将score减一
                        print('请求响应码不合法', response.status, 'IP', proxy)
            except (ClientError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        '''
        测试主函数
        :return: 
        '''
        print('测试器开始运行')
        try:
            count = self.redis.count()
            print('当前剩余', count, '个代理')
            for i in range(0, count, BATCH_TEST_SIZE): # 步长为100
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                print('正在测试第', start + 1, '-', stop, '个代理')
                test_proxies = self.redis.batch(start, stop) # 调用db的batch()获取100个代理列表从高到低排列
                loop = asyncio.get_event_loop() # 获取EventLoop
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks)) #执行异步任务tasks。在等待网站返回的时候去执行另一个任务，网站返回后跳回任务继续执行原任务
                sys.stdout.flush() #输出实时信息，而不是等待运行完毕后输出
                time.sleep(5)
        except Exception as e:
            print('测试器发送错误', e.args)

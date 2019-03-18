# coding:utf-8
from baike_spider import url_manager, html_downloader, html_parser, html_outputer


class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()                                    #管理器
        self.downloader = html_downloader.HtmlDownloader()                      #下载器
        self.parser = html_parser.HtmlParser()                                  #解析器
        self.outputer = html_outputer.HtmlOutputer()                            #输出器

    def craw(self, root_url):
        count = 1
        self.urls.add_new_url(root_url)                                         # 获取原URL
        while self.urls.has_new_url():                                          # 当有新的URL时，循环
            try:                                                                # 尝试爬取，失败后打印
                new_url = self.urls.get_new_url()                               # 获取新的URL
                print(f"craw {count} : {new_url}")
                html_cont = self.downloader.download(new_url)                   # 下载新的URL
                new_urls, new_data = self.parser.parser(new_url, html_cont)     # 获取URL的数据和新的URL
                self.urls.add_new_urls(new_urls)                                # 将新的URL补充紧URL管理器
                self.outputer.collect_data(new_data)                            # 收集之前的数据

                if count == 10:
                    break

                count += 1
            except:
                print("craw failed")

        self.outputer.output_html()


if __name__ == "__main__":
    root_url = "https://baike.baidu.com/item/Python/407313?fr=aladdin" #入口url
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)
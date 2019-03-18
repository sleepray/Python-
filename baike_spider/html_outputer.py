#coding:utf-8
class HtmlOutputer(object):

    def __init__(self):
        self.datas = []

    def collect_data(self, data):
        if data is None:
            return
        self.datas.append(data)

    def output_html(self):
        fout = open('output.html', 'w', encoding='utf-8') #创建一个 output.html 文档，为写入模式
        fout.write('<meta charset="utf-8">')              #('<meta charset="utf-8">')这个标签在有中文的网页头部加入防止乱码
        # 写入 Html格式
        fout.write("<html>")
        fout.write("<style type='text/css'>")
        fout.write("table tr td,th{border:1px solid #000;}")#添加表格线
        fout.write("</style>")
        fout.write("<body>")                            #内容标签
        #<caption>标签表示标题 <strong>标签表示加粗
        fout.write("<caption><strong>爬取Python百度百科词条1000个链接</strong></caption>")
        fout.write("<table>")                           #表格标签
        fout.write("<tr>")                              #<tr>…</tr>：表格的一行，所以有几对tr 表格就有几行。
        fout.write("<th>URL</th>")
        fout.write("<th>标题</th>")
        fout.write("<th>简介</th>")
        fout.write("</tr>")

        for data in self.datas:                          #<tr>…</tr>：表格的一行，所以有几对tr 表格就有几行。)
            fout.write("<tr>")                           # <td>…</td>：表格的一个单元格，一行中包含几对，说明一行中就有几列。
            fout.write(f"<td>{data['url']}</td>")        #写入 URL
            fout.write(f"<td>{data['title']}</td>")      #写入 标题
            fout.write(f"<td>{data['summary']}</td")     #写入 简介
            fout.write("</tr>")


        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")

        fout.close()

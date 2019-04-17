#coding:utf-8

'''
图片验证码
'''

import tesserocr
from PIL import Image

image = Image.open('D:\\exercise\\code.jpg')  #先打开图片
result = tesserocr.image_to_text(image)    #imge_to_text()将图片转化为文字
print(result)
print(tesserocr.file_to_text('D:\\exercise\\code.jpg')) #file_to_text也行，但不稳定

image2 = Image.open('D:\\exercise\\code2.jpg')
result = tesserocr.image_to_text(image2)
print(result)

image2 = image2.convert('L')  # 使用convert()方法传入L，将图片灰度处理
image2 = image2.convert('1')  # 使用convert()方法传入1，将图片二值处理
image2.show()

image = image.convert('L')
threshold = 127     # 二值化的阈值
table = []
# 这个没懂，怀疑是添加rgb的的参数？
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
print('table>>>>>', table)

image = image.point(table, '1')  #将线条全部去掉
image.show()     #打开处理后的图片
result1 = tesserocr.image_to_text(image)
print(result1)
"""功能:通过爬虫快速获取数独图片"""

import os
import sys
import time
import urllib
import requests
import re
from bs4 import BeautifulSoup
import time

header = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36'
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}
url = "https://cn.bing.com/images/async?q={0}&first={1}&count={2}&scenario=ImageBasicHover&datsrc=N_I&layout=ColumnBased&mmasync=1&dgState=c*9_y*2226s2180s2072s2043s2292s2295s2079s2203s2094_i*71_w*198&IG=0D6AD6CBAF43430EA716510A4754C951&SFX={3}&iid=images.5599"

save_path = 'images'

DE_WEIGHT = False


def getImage(url, count):
    '''从原图url中将原图保存到本地'''
    try:
        num = 1
        datafiles = os.listdir(save_path)
        if DE_WEIGHT:
            img_name = str(num) + '.jpg'
            while img_name in datafiles:
                num += 1
                img_name = str(num) + '.jpg'
        else:
            img_name = str(count) + '.jpg'
        time.sleep(0.5)
        urllib.request.urlretrieve(url, os.path.join(save_path, img_name))
    except Exception as e:
        time.sleep(1)
        print("本张图片获取异常，跳过...")
    else:
        print("图片+1,成功保存 " + str(count + 1) + " 张图")


def findImgUrlFromHtml(html, rule, url, key, first, loadNum, sfx, count):
    '''从缩略图列表页中找到原图的url，并返回这一页的图片数量'''
    soup = BeautifulSoup(html, "lxml")
    link_list = soup.find_all("a", class_="iusc")
    url = []
    for link in link_list:
        result = re.search(rule, str(link))
        # 将字符串"amp;"删除
        url = result.group(0)
        # 组装完整url
        url = url[8:len(url)]
        # 打开高清图片网址
        getImage(url, count)
        count += 1
    # 完成一页，继续加载下一页
    return count


def getStartHtml(url, key, first, loadNum, sfx):
    '''获取缩略图列表页'''
    page = urllib.request.Request(url.format(key, first, loadNum, sfx),
                                  headers=header)
    html = urllib.request.urlopen(page)
    return html


if __name__ == '__main__':
    name = "行人"  # 图片关键词
    countNum = 2000  # 爬取数量
    key = urllib.parse.quote(name)
    first = 1
    loadNum = 35
    sfx = 1
    count = 0
    data_files = os.listdir(save_path)
    if len(data_files) != 0:
        nums = [int(i.split('.')[0]) for i in data_files]
        count = max(nums) + 1
    rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    while count < countNum:
        html = getStartHtml(url, key, first, loadNum, sfx)
        count = findImgUrlFromHtml(html, rule, url, key, first, loadNum, sfx,
                                   count)
        first = count + 1
        sfx += 1

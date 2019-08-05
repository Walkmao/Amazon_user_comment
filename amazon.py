# -*- coding: utf-8 -*-

import requests
import time
import codecs
from bs4 import BeautifulSoup
import pandas as pd

import lxml

# 反爬虫：构建header,cookie
def getUA():
    with open("newUA.txt") as fileua:

        uas = fileua.readlines()
        import random
        cnt = random.randint(0,len(uas)-1)
        return uas[cnt].replace("\n","")

def getHeader(referer):
    header = {
        'Referer': referer,
        'User-agent':getUA(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accetp-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    return header

# 下载页面到本地
def download_page(url, id, referer, header, cookie, pause):
    htmlpage = None
    while htmlpage is None:
        code = 404
        with requests.session() as s:
            html = s.get(url, headers= getHeader(referer), cookies = cookie)
            htmlpage = html.content.decode('utf-8','ignore')
            if not id in htmlpage:
                htmlpage = None
                continue
            code = html.status_code
            time.sleep(pause)
    if htmlpage:
        return htmlpage, code
    else:
        return None, code

#http://www.amazon.com/product-reviews/B01MZ5G6ZT/?ie=UTF8&reviewerType=all_reviews&pageNumber=1

def getPages(referer):
    header = getHeader(referer)
    htmlContent = requests.get(referer,headers = header)

    soup1 = BeautifulSoup(htmlContent.text,'lxml')
    tag = soup1.find_all('li',attrs={'class':'page-button'})
    pages = int(tag[-1].get_text())
    return pages

def ASIN_id():
    df = pd.read_excel(r"F:\project\id.xlsx")
    id = df['id']
    return id

def main():
    urlPart1 = "http://www.amazon.com/product-reviews/"
    urlPart2 = "/?ie=UTF8&reviewerType=all_reviews&pageNumber="

    # id为要抓取评论的商品ASIN码，pause为抓取页面时间间隔，lastPage为评论总页数
    pause = 0

    # 从excel表中一行一行输入id_
    ids = ASIN_id()
    for id_ in ids:
        print id_
        referer = urlPart1 + str(id_) + urlPart2 + "1"
        lastPage = getPages(referer)
        header = getHeader(referer)
        with requests.session() as s:
            req = s.get(referer, headers=header)
            cookie = requests.utils.dict_from_cookiejar(req.cookies)

        page = 1
        while page <= lastPage:
            url = urlPart1 + str(id_) + urlPart2 + str(page)
            htmlpage, code = download_page(url,id_, referer, header, cookie, pause)

            with codecs.open(id_+'_'+str(page)+'.html',mode='w',encoding='utf8') as file:
                file.write(htmlpage)

            page += 1
            referer = urlPart1 + str(id_) + urlPart2 + str(page)
            with requests.session() as s:
                req = s.get(referer, headers=getHeader(referer))
                cookie = requests.utils.dict_from_cookiejar(req.cookies)
        print '----------------------'

if __name__ == '__main__':
    main()
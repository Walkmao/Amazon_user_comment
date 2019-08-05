# -*- coding: utf-8 -*-

import re
import time
import codecs
import csv
import sys
import os
import fnmatch
import HTMLParser
import datetime

# 根据idre查找html页面对应的商品型号
idre = re.compile('product\-reviews/([A-Z0-9]+)/ref\=cm_cr_arp_d_hist', re.MULTILINE | re.S)
# 从html页面中抽取包含评论的部分，其他无用部分不要
contentre = re.compile('cm_cr-review_list.*?>(.*?)(?:askReviewsPageAskWidget|a-form-actions a-spacing-top-extra-large|/html)', re.MULTILINE | re.S)
# 抽取每一个评论的块，正常一个页面10个评论，然后对每个评论块抽取对应的信息
blockre = re.compile('a-section review\">(.*?)report-abuse-link', re.MULTILINE | re.S)
# 评分
ratingre = re.compile('star-(.) review-rating', re.MULTILINE | re.S)
# 标题
titlere = re.compile('review-title.*?>(.*?)</a>', re.MULTILINE | re.S)
# 链接
links = re.compile('review-title.*?href="(.*?)">', re.MULTILINE | re.S)
# 日期
datere = re.compile('review-date">(.*?)</span>', re.MULTILINE | re.S)
# 是否VP(Verified Purchase) *
vpre = re.compile('data-hook=\"avp-badge.*?>(.*?)</span>', re.MULTILINE | re.S)
# 型号（针对多机型合并页面） *
#formatre = re.compile('data-hook=\"format-strip.*?>(.*?)</a>', re.MULTILINE | re.S)
# 评论
reviewre = re.compile('base review-text">(.*?)</span', re.MULTILINE | re.S)
# 用户
userre = re.compile('profile\/(.*?)["/].*?\<\/div\>.*?\<\/div\>.', re.MULTILINE | re.S)
# 评论数  *
comnumre = re.compile('review-comment-total.*?>([0-9]+)</span>', re.MULTILINE | re.S)
# 点赞数
helpfulre = re.compile('review-votes.*?([0-9]+,[0-9]+|[0-9]+|One).*?</span>', re.MULTILINE | re.S)
# 当前评价数
totalre = re.compile('data-hook=\"total-review-count.*?>(.*?)</span>')
# 当前平均评分
averagere = re.compile('data-hook=\"rating-out-of-text.*?>(.*?) out of 5 stars</span>')

# 遍历文件夹，获取所有html文件名
def get_review_filesnames(input_dir):
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            yield os.path.join(root, filename)

def main():
    dir = r"F:\project"
    outfile = r"C:\Users\1111\Desktop\nameOfOutput.csv"
    reviews = dict()
    record_date = time.strftime("%Y/%m/%d/%H:%M:%S")
    with codecs.open(outfile,'w',encoding='utf8') as out:
        writer = csv.writer(out, lineterminator='\n')
        writeTitle = ['Product_ASIN','review_date','date_format','total_review', 'average_star','title', 'review_content', 'star', 'star_class', 'reply_num', 'helpfulVotes', 'user', 'VP','link_id', 'record_date']
        # 写入标题 对应为 产品ASIN码，评论时间，评论者，是否VP，评论标题，评论文本，评分，好/坏评分，评论回复数，评论点赞数,采集时间，评论链接
        writer.writerow(writeTitle)
        for filepath in get_review_filesnames(dir):
            with codecs.open(filepath, mode='r', encoding='utf8') as file:
                htmlpage = file.read()
            if not idre.search(htmlpage):
                continue
            id_ = idre.findall(htmlpage)[0]
            total_review = totalre.findall(htmlpage)[0]
            average_star = averagere.findall(htmlpage)[0]
            print(id_, filepath)
            htmlpage = contentre.findall(htmlpage)[0]
            for block in blockre.findall(htmlpage):
                link_id = 'https://www.amazon.com' + links.findall(block)[0]
                title = titlere.findall(block)[0]
                reviewtext = reviewre.findall(block)[0]
                # 评论里会包含很多的<**>和空格 需要去除, 一些html特殊字符需要进行转义
                remo = re.compile('<.*?>', re.MULTILINE | re.S)
                #remo1 = re.compile('&.*?;', re.MULTILINE | re.S)
                title = HTMLParser.HTMLParser().unescape(remo.sub(' ', title))
                reviewtext = HTMLParser.HTMLParser().unescape(remo.sub(' ', reviewtext))
                vpmatch = vpre.findall(block)
                if not vpmatch:
                    vp = u'Unverified'
                else:
                    vp = vpmatch[0]
                rating = int(ratingre.findall(block)[0])
                date = ''.join(datere.findall(block)[0].split(' ')[1:])
                date_format = datetime.datetime.strptime(date,'%B%d,%Y')
                user = 'ANONYMOUS'
                usermatch = userre.findall(block)
                if usermatch:
                    user = usermatch[0]
                comments = 0
                helptot = 0
                helpmatch = helpfulre.findall(block)
                commentsmatch = comnumre.findall(block)
                if helpmatch:
                    helptot = int(helpmatch[0].replace(',','').replace('One', '1'))
                if commentsmatch:
                    comments = int(commentsmatch[0])

                if rating >= 4:
                    binaryrating = 'positive'
                else:
                    binaryrating = 'negative'
                #对应于Python版本3.0版本以上进行如下操作
                if sys.version_info[0] >= 3:
                    review_row = [id_, date, date_format, total_review, average_star, title, reviewtext, rating, binaryrating, comments, helptot, user, vp, link_id, record_date]
                else:
                    review_row = [id_,unicode.encode(date, encoding='ascii', errors='ignore'),date_format,total_review,
                                  average_star,unicode.encode(title, encoding='ascii', errors='ignore'),
                                  unicode.encode(reviewtext, encoding='ascii', errors='ignore'), rating,
                                  binaryrating, comments, helptot,
                                  unicode.encode(user, encoding='ascii', errors='ignore'),
                                  unicode.encode(vp, encoding='ascii', errors='ignore'),
                                  unicode.encode(link_id, encoding='ascii', errors='ignore'),record_date]
                writer.writerow(review_row)

if __name__ == '__main__':
    main()
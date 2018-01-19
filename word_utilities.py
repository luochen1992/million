#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 12:52:39 2018

@author: luo
"""
import jieba.posseg as pseg
from datetime import datetime

FALSE = (
    "是错",
    "没有",
    "不属于",
    "不是",
    "不能",
    "不可以",
    "不对",
    "不正确",
    "不提供",
    "不包括",
    "不存在",
    "不经过",
    "未",
    "错误"
)
def pre_process_question(keyword):
    """
    strip charactor and strip ?
    :param question:
    :return:
    """
    now = datetime.today()
    for char, repl in [('\n',''),("“", ""), ("”", ""), ("？", ""), ("《", ""), ("》", ""), ("我国", "中国"),
                       ("今天", "{0}年{1}月{2}日".format(now.year, now.month, now.day)),
                       ("今年", "{0}年".format(now.year)),
                       ("这个月", "{0}年{1}月".format(now.year, now.month))]:
        keyword = keyword.replace(char, repl)

    keyword = keyword.split(r"．")[-1]
    keywords = keyword.split(" ")
    keyword = "".join([e.strip("\r\n") for e in keywords if e])
    return keyword

def parse_false(question):
    """
    :param question:
    :return:
    """
    for item in FALSE:
        if item in question:
            question = question.replace(item, "")
            return question, False

    return question, True



'''
initialize jieba Segment
'''


def postag(text):
    words = pseg.cut(text)
    return words
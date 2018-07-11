#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@auther = 'Redheat'
@create = '2018/7/11 18:25'
@email = 'qjyyn@qq.com'
'''
from bs4 import BeautifulSoup
import requests


class OpenUrl(object):
    @staticmethod
    def get_boot_tag():
        response = requests.get('https://book.douban.com/tag/?view=type&icn=index-sorttags-all')
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            tables = soup.find_all(name='table',class_='tagCol')
            tag_list = []
            for table in tables:
                a_tag = table.find_all(name='a')
                for a in a_tag:
                    tag_list.append(a.text)
            return tag_list
        except AttributeError as e:
            print(e)
    @staticmethod
    def get_book_urls(tag, start_num):
        response = requests.get("https://book.douban.com/tag/%s?start=%s&type=T" % (tag, start_num))
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            subject_item = soup.find_all(name='li', class_='subject-item')
            a_tag = lambda subject: subject.find(name='a')
            return [a_tag(subject).get('href') for subject in subject_item]
        except AttributeError as e:
            print(e)
            return False


tag = OpenUrl.get_boot_tag()

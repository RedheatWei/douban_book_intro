#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@auther = 'Redheat'
@create = '2018/7/11 18:25'
@email = 'qjyyn@qq.com'
'''
from bs4 import BeautifulSoup
import requests
import sqlite3
from concurrent.futures import ThreadPoolExecutor

proxies = {'http':'111.155.116.210:8123','https':'202.104.113.35:53281'}

class OpenUrl(object):
    @staticmethod
    def get_book_tag():
        response = requests.get('https://book.douban.com/tag/?view=type&icn=index-sorttags-all',proxies=proxies)
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
    def get_book_urls(**kwargs):
        response = requests.get("https://book.douban.com/tag/%s?start=%s&type=T" % (kwargs['tag'], kwargs['start_num']),proxies=proxies)
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            subject_item = soup.find_all(name='li', class_='subject-item')
            a_tag = lambda subject: subject.find(name='a')
            return [a_tag(subject).get('href') for subject in subject_item]
        except AttributeError as e:
            print(e)
            return False

class ProcessDb(object):
    def __init__(self,dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
    #插入获取的url到数据库
    def insertUrl(self,url_list,tag):
        for url in url_list:
            sql = 'insert or ignore into urls(url,tag) values("%s","%s")' % (url,tag)
            self.cursor.execute(sql)
    def selectTag(self):
        sql = 'SELECT tag FROM urls GROUP BY tag ORDER BY id'
        return self.cursor.execute(sql).fetchall()

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

class Collect(object):
    @staticmethod
    def read_tags():
        db = ProcessDb("douban.db3")
        tags = db.selectTag()
        tag_list = [tag[0] for tag in tags]
        return tag_list
    @staticmethod
    def urls():
        tag_list = OpenUrl.get_book_tag()
        end_tag = Collect.read_tags()
        tag_list = list(set(tag_list).difference(set(end_tag)))
        for tag in tag_list:
            for num in range(0,5001,20):
                kwargs = {"tag":tag,"start_num":num}
                print(kwargs)
                urls = OpenUrl.get_book_urls(**kwargs)
                if urls:
                    db = ProcessDb("douban.db3")
                    db.insertUrl(urls,tag)
                else:
                    break
Collect().urls()

# print(Collect.read_tags())

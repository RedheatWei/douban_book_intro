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

proxies = None


class OpenUrl(object):
    @staticmethod
    def get_book_tag():
        response = requests.get('https://book.douban.com/tag/?view=type&icn=index-sorttags-all', proxies=proxies)
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            tables = soup.find_all(name='table', class_='tagCol')
            tag_list = []
            for table in tables:
                a_tag = table.find_all(name='a')
                for a in a_tag:
                    tag_list.append(a.text)
            return tag_list
        except AttributeError as e:
            print(e)

    # 获取url
    @staticmethod
    def get_book_urls(**kwargs):
        response = requests.get("https://book.douban.com/tag/%s?start=%s&type=T" % (kwargs['tag'], kwargs['start_num']),
                                proxies=proxies)
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            subject_item = soup.find_all(name='li', class_='subject-item')
            a_tag = lambda subject: subject.find(name='a')
            return [a_tag(subject).get('href') for subject in subject_item]
        except AttributeError as e:
            print(e)
            return False

    # 获取简介
    @staticmethod
    def get_book_intro(url):
        response = requests.get(url=url, proxies=proxies)
        soup = BeautifulSoup(response.content, 'lxml')
        book_info = {}
        try:
            book_info['url'] = url
            book_info['name'] = soup.select("h1 span")[0].get_text()
            info_list = soup.select("div#info")[0].get_text('|', strip=True).split('|')
            print(info_list)
            book_info['auther'] = None
            try:
                book_info['ISBN'] = info_list[info_list.index("ISBN:") + 1]
            except Exception:
                try:
                    book_info['ISBN'] = info_list[info_list.index("ISBN") + 1]
                except Exception:
                    book_info['ISBN'] = info_list[info_list.index("统一书号:") + 1]

            try:
                book_info['original_name'] = info_list[info_list.index("原作名:") + 1].replace("'","@")
            except Exception:
                try:
                    book_info['original_name'] = info_list[info_list.index("原作名") + 1].replace("'","@")
                except Exception:
                    book_info['original_name'] = None
            intro_div = soup.select("div.intro")
            if len(intro_div) != 0:
                if len(intro_div) > 1:
                    book_info['intro'] = soup.select("div.intro")[-2].get_text('\n', strip=True).replace("'","@")
                    book_info['auther_intro'] = soup.select("div.intro")[-1].get_text('\n', strip=True).replace("'","@")
                else:
                    book_info['intro'] = soup.select("div.intro")[0].get_text('\n', strip=True).replace("'","@")
                    book_info['auther_intro'] = None
            else:
                book_info['intro'] = None
                book_info['auther_intro'] = None
            return book_info
        except Exception as e:
            print(e)
            return None


class ProcessDb(object):
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    # 插入获取的url到数据库
    def insertUrl(self, url_list, tag):
        for url in url_list:
            sql = 'insert or ignore into urls(url,tag) values("%s","%s")' % (url, tag)
            self.cursor.execute(sql)

    def insertIntro(self, **kwargs):
        sql = '''update urls set (`name`,auther,ISBN,original_name,intro,auther_intro) = ('%s','%s','%s','%s','%s','%s') WHERE url='%s' ''' % (
            kwargs['name'], kwargs['auther'], kwargs['ISBN'], kwargs['original_name'], kwargs['intro'],
            kwargs['auther_intro'], kwargs['url'])
        print(sql)
        self.cursor.execute(sql)

    # 查询tag
    def selectTag(self):
        sql = 'SELECT tag FROM urls GROUP BY tag ORDER BY id'
        return self.cursor.execute(sql).fetchall()

    # 查询出所有的url
    def select_urls(self):
        sql = "SELECT url FROM urls WHERE `name` IS NULL"
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
            for num in range(0, 5001, 20):
                kwargs = {"tag": tag, "start_num": num}
                print(kwargs)
                urls = OpenUrl.get_book_urls(**kwargs)
                if urls:
                    db = ProcessDb("douban.db3")
                    db.insertUrl(urls, tag)
                else:
                    break

    @staticmethod
    def intros():
        db = ProcessDb("douban.db3")
        urls = db.select_urls()
        url_list = [url[0] for url in urls]
        for url in url_list:
            print(url)
            intro = OpenUrl.get_book_intro(url)
            print(intro)
            db.insertIntro(**intro)


Collect.intros()

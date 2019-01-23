# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from dianping.utils.mongodb_utils import get_db
import pymysql
import traceback
import os


class YunfuCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    def __init__(self):
        self.db = get_db()
        self.collection = None

    def process_item(self, item, spider):
        self.collection = item.get('sort')
        item_dict = dict(item)
        if self.collection is None:
            print('other!')
        else:
            query = {
                'url': item.get('url')
            }
            # insert 不更新老数据
            # update 更新数据
            self.db.update_one(self.collection, query, item_dict)
            return item

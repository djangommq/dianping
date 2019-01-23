import datetime
import os
import pymongo
from dianping.settings import MONGODB_SERVER, MONGODB_PORT, MONGODB_DATABASE, USER, PASSWORD
import logging


class Mongodb(object):

    # 初始化
    def __init__(self, dbconfig):
        self.host = dbconfig.get('host')
        self.port = dbconfig.get('port')
        self.user = dbconfig.get('user')
        self.password = dbconfig.get('password')
        self.database = dbconfig.get('database')
        self._client = pymongo.MongoClient(self.host, self.port)
        self._db = self._client[self.database]
        self._db.authenticate(self.user, self.password)

    # 查询所有结果, 去掉_id后返回
    def all_items(self, collection_name):
        collection = self._db[collection_name]
        collection_list = collection.find()
        cl = []
        for r in collection_list:
            r.pop('_id')
            cl.append(r)
        return cl

    # 查询符合条件的所有结果
    def find(self, collection_name, query=None):
        collection = self._db[collection_name]
        if query is None:
            rs = collection.find()
        else:
            rs = collection.find(query)
        return rs

    # 查询符合条件的数量
    def find_count(self, collection_name, query=None):
        collection = self._db[collection_name]
        if query is None:
            rs = collection.find().count()
        else:
            rs = collection.find(query).count()
        return rs

    def find_and_mark(self, collection_name, query=None, update=None):
        collection = self._db[collection_name]
        if query is None:
            rs = collection.find()
        else:
            rs = collection.find_and_modify(query, update={"$set": update})
        return list(rs)

    # 查询符合条件的第一条结果
    def find_one(self, collection_name, query=None):
        if query is None:
            query = {}
        collection = self._db[collection_name]
        rs = collection.find_one(query)
        return rs

    # 查询符合条件的第一条结果
    def find_one_and_mark(self, collection_name, query, update):
        collection = self._db[collection_name]
        rs = collection.find_one_and_update(query, update={"$set": update})
        return rs

    # 插入时默认不去重, 可以按特定值去重
    # 可以插1条或多条
    def insert_many(self, collection_name, data_input, condition=None):
        if isinstance(data_input, list):
            for data in data_input:
                self.insert_one(collection_name, data, condition)
        else:
            self.insert_one(collection_name, data_input, condition)

    def insert_one(self, collection_name, input, condition=None):
        if input is None:
            pass
        else:
            collection = self._db[collection_name]
            query = {}
            if condition is None:
                collection.insert_one(input)
            else:
                for key in condition:
                    query[key] = input.get(key)
                tmp = self.find_one(collection_name, query)
                if tmp is None:
                    collection.insert_one(input)

    # 修改
    # upsert=True 表示如果不存在就创建
    def update_one(self, collection_name, query, item, upsert=True):
        collection_name = self._db[collection_name]
        # $set表示更新字段, 新数据不存在的字段, 更新后不影响旧数据的字段
        # form直接传item, 则完整更新
        form = {
            '$set': item,
        }
        collection_name.update_one(query, form, upsert=upsert)

    def update_many(self, collection_name, query, form):
        collection = self._db[collection_name]
        rs = collection.update_many(query, form)
        return rs

    # 删除
    def remove(self, collection_name, query):
        collection = self._db[collection_name]
        collection.remove(query)

    def __exit__(self, exception_type, exception_value, traceback):
        self._client.close()


def get_db():
    dbconfig = {
        'host': MONGODB_SERVER,
        # 'host': 'localhost',
        "port": MONGODB_PORT,
        "user": USER,
        "password": PASSWORD,
        'database': MONGODB_DATABASE,
    }
    db = Mongodb(dbconfig)
    return db


# def test():
#     dbconfig = {
#         'host': 'localhost',
#         "port": 27017,
#         'database': 'military',
#     }
#
#     collection = 'weapon'
#     db = Mongodb(dbconfig)
#     all = db.find_by_query(collection, {'secondary_ch': '多用途直升机'})
#     print(all)
#     print(len(all))
#     # result type: tuple
#     # 返回的是一个tuple, 内部也是tuple
#
#
# if __name__ == '__main__':
#     test()

# -*- coding: utf-8 -*-
import json
import pymongo
from redis import StrictRedis
import traceback
import config


class Store(object):
    """
    数据读取及存储
    """
    def __init__(self):
        self.mongo_client = pymongo.MongoClient(**config.mongo)  # 用于读取数据
        self.db = self.mongo_client.fxt  # 数据库: "fxt"
        self.collection = self.db.fxt_requests  # collection: "fxt_requests"
        self.redis_client = StrictRedis(**config.redis)  # 用于保存数据

    def read_request_datas(self, condition):
        """
        从mongodb一次性读取一条数据
        数据的样式:
            {
              "unique_key": "唯一key", // 唯一索引
              "request": {
                "url": "下载网址",
                "user_agent": "",
                "cookie": "",
                "body": "post数据"
              },
              "config": {
                "district": "地区",
                "response_types": ["header", "body", "capture"],
                "follow_redirect": true|false,
                "priority": "high|normal|low"
              },
              "status": -2|-1|0|1|2 //存储时增加状态列，加索引. 默认值是0, 发送成功之后改为1,发送失败改为-1,
                                    //将结果保存到redis之后改为2,status为-1的url再发送一次后,若仍发送失败就改为-2
            }
        """
        try:
            row = self.collection.find_one(condition)
            return row
        except Exception as e:
            print("read date from mongodb error.", e)
            traceback.print_exc()

    def store_data(self, store_data):
        """
        将数据存储到redis
        数据样式:
            data = {
                "unique_key": "",
                "response": {
                    "header": "",
                    "body": "",
                    "capture": ""
                }
            }
        """
        try:
            key = store_data['unique_key']
            value = json.dumps(store_data['response'])
            self.redis_client.set(key, value)
            self.redis_client.expire(key, 60 * 60 * 1)  # 设置过期时间为1小时
            print("save data to redis success.")
        except Exception as e:
            print("store data error", e)
            traceback.print_exc()

    def update_status(self, unique_key, status):
        """
        更新mongo中已查询数据的状态码
        """
        try:
            result = self.collection.update({"unique_key": unique_key}, {'$set': {"status": status}})
            print(result)
        except Exception as e:
            print("update status error", e)
            traceback.print_exc()


if __name__ == '__main__':
    store = Store()

    # data = {
    #     "unique_key": "unique_key",
    #     "response": {
    #         "header": "header",
    #         "body": "r_html",
    #         "capture": "r_capture"
    #     }
    # }
    # store.store_data(data)
    rows = store.read_request_datas({"$or": [{'status': 2}, {'status': 3}]})
    print(rows)
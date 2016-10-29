# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class HousePipeline(object):
    def process_item(self, item, spider):
        return item

class MongoDBPipleline(object):
    def __init__(self):
        client = MongoClient("mongodb://xxxx:xxxxx@localhost:27017/myspace")
        db = client.myspace
        self.house = db["house"]

        
    def process_item(self, item, spider):
        self.house.insert(dict(item))
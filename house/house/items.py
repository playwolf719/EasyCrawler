# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class HouseItem(scrapy.Item):
    _id = Field()  # id
    name = Field()  # 名称
    price = Field()  # 价格

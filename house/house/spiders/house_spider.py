# encoding=utf-8
import re,sys
import datetime
# import redis
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from house.items import HouseItem
import logging
from selenium import webdriver
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
import pymongo

# UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-3
reload(sys)
sys.setdefaultencoding("utf-8")

#log 
logger = logging.getLogger('myLogger') 
# self.logger.setLevel(logging.ERROR)
fh = logging.FileHandler('/xxx/xxx/xxxx/xxxx/house/log')  
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
fh.setFormatter(formatter) 
logger.addHandler(fh)

# from scrapy.spider import CrawlSpider

class HouseSpider(scrapy.Spider):
    name = "HouseSpider"
    host = "http://market.m.taobao.com/wh/tms/taobao/page/markets/paimai/housechannel"

    start_urls = []

    def __init__(self):
        # mongo
        client = MongoClient("mongodb://xxx:xxxx@localhost:27017/myspace")
        db = client.myspace
        self.house = db["house"]

    def start_requests(self):
        print "--------start_requests-------"
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # for page in xrange(980,8669):
        for page in xrange(8650,8710):
            url = self.pc_index_url+"&page="+str(page+1)
            # url=self.test_url
            # url = self.baidu_url+"?page="+str(page+1)
            yield Request(url=url, meta={"page": str(page+1)},callback=self.parse0,dont_filter=True)  


    def parse0(self, response):
        soup=BeautifulSoup(response.body, "html.parser")
        soup.prettify()
        items=soup.find(id="sf-item-list-data").getText()
        data = json.loads(items)

        logger.info("page:"+str(response.meta["page"])+"; length:"+str(len(data["data"] ) )+";" )

        print "--------page-"+str(response.meta["page"])+"-------------"
        print "length :"+str(len(data["data"]) );
        for index,house_info in enumerate(data["data"]):
            try:
                house_info["_id"]=house_info["id"]
                del house_info["id"]
                self.house.insert(dict(house_info))
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception, e:
                print "--------page-"+str(response.meta["page"])+"-Exception--------------"
                print e.__doc__
                print e.message
                logger.error("page:"+str(response.meta["page"]) )
                logger.error("house_id:"+str(house_info["_id"]) )
                logger.error(e.__doc__)
                logger.error(e.message)
                pass

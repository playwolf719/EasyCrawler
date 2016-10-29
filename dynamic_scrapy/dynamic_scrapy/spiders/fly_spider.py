# -*- coding: utf-8 -*-
import scrapy,random
from scrapy_splash import SplashRequest
from dynamic_scrapy.cookies import cookies
from dynamic_scrapy.agents import agents
import time,hashlib
import json,logging
from pymongo import MongoClient
import pymongo
from pprint import pprint
from bs4 import BeautifulSoup
import sys

# UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-3
reload(sys)
sys.setdefaultencoding("utf-8")

class FlySpider(scrapy.Spider):
    name = "FlySpider"
    house_pc_index_url='xxxxx'

    def __init__(self):
        client = MongoClient("mongodb://name:pwd@localhost:27017/myspace")
        db = client.myspace
        self.fly = db["fly"]

    def start_requests(self):
        

        for x in xrange(0,1):
            try:
                script = """
                function process_one(splash)
                    splash:runjs("$('#next_title').click()")
                    splash:wait(1)
                    local content=splash:evaljs("$('.scrollbar_content').html()")
                    return content
                end

                function process_mul(splash,totalPageNum)
                    local res={}
                    for i=1,totalPageNum,1 do
                        res[i]=process_one(splash)
                    end
                    return res
                end

                function main(splash)
                    splash.resource_timeout = 1800
                    local tmp=splash:get_cookies()
                    splash:add_cookie('PHPSESSID', splash.args.cookies['PHPSESSID'],"/", "www.feizhiyi.com")
                    splash:add_cookie('FEIZHIYI_LOGGED_USER', splash.args.cookies['FEIZHIYI_LOGGED_USER'],"/", "www.feizhiyi.com" )

                    splash:autoload("http://cdn.bootcss.com/jquery/2.2.3/jquery.min.js")

                    assert(splash:go{
                        splash.args.url,
                        http_method=splash.args.http_method,
                        headers=splash.args.headers,
                    })
                    assert(splash:wait(splash.args.wait) )

                    return {res=process_mul(splash,100)}
                    
                end
                """
                agent = random.choice(agents)
                print "------cookie---------"
                headers={
                    "User-Agent":agent,
                    "Referer":"xxxxxxx",
                }
                splash_args = {
                    'wait': 3,
                    "http_method":"GET",
                    # "images":0,
                    "timeout":1800,
                    "render_all":1,
                    "headers":headers,
                    'lua_source': script,
                    "cookies":cookies,
                    # "proxy":"http://101.200.153.236:8123",
                }
                yield SplashRequest(self.house_pc_index_url, self.parse_result, endpoint='execute',args=splash_args,dont_filter=True)
                # +"&page="+str(x+1)
            except Exception, e:
                print e.__doc__
                print e.message
                pass

    def parse_result(self, response):
        print '---------------success----------------'
        data=json.loads(response.body)        for k, value in data["res"].items():
            try:
                soup=BeautifulSoup(value, "html.parser")
                soup.prettify()
                item={}
                h2=soup.find("h2")
                imgs=soup.find("ul",attrs={"class": "Topic-picture"}).find_all("li")
                options=soup.find("ul",attrs={"class": "Answer-options"}).find_all("li")
                answer=soup.find("div",attrs={"class": "answer-question"}).find_all("p",attrs={"class": "a"})[1](text=True)

                answer="".join(answer)
                explan=soup.find(id="explanation")(text=True)
                explan="".join(explan)

                item["_id"]=h2["data-number"]
                item["topic"]=h2(text=True)[1].strip()
                print "---"+k+"-item----"
                for i in item: 
                    print "%s : " % i,item[i]
                print "----img----"
                for key,val in enumerate(imgs):
                    if val.find("img"):
                        print val.find("img")["src"]
                print "----img----"
                for key,val in enumerate(options):
                    print val(text=True)[0]
                print answer
                print explan
            except pymongo.errors.DuplicateKeyError:
                break
                pass
            except Exception, e:
                print e.__doc__
                print e.message
                pass

    def getAuthHeader(self):
        #请替换appkey和secret
        appkey = "xxxxxxxx"
        secret = "xxxxxxx"

        paramMap = {
            "app_key": appkey,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")  #如果你的程序在国外，请进行时区处理
        }
        #排序
        keys = paramMap.keys()
        keys.sort()
                
        codes= "%s%s%s" % (secret,str().join('%s%s' % (key, paramMap[key]) for key in keys),secret)

        #计算签名
        sign = hashlib.md5(codes).hexdigest().upper()

        paramMap["sign"] = sign

        #拼装请求头Proxy-Authorization的值
        keys = paramMap.keys()
        authHeader = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, paramMap[key]) for key in keys)

        print time.strftime("%Y-%m-%d %H:%M:%S")
        print authHeader
            
        return authHeader
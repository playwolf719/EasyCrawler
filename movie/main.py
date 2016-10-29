#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib2,urllib,urlparse
import re
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os,sys
from datetime import datetime
from dateutil import tz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import socket,random
from agents import agents



# UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-3
reload(sys)
sys.setdefaultencoding("utf-8")


class BTHeaven():

    """docstring for ClassName"""
    douban_movie_index_url="https://movie.douban.com/subject"

    def __init__(self, base_url,start_page, end_page):
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page
        self.norm_score = 7.5
        self.norm_audience_num = 3000
        self.goods=[]
        # self.driver = webdriver.PhantomJS() #指定使用的浏览器

    def get_one_page(self,page_num ):
        print "\n-----------page_num--------------"
        print "\n-------"+str(page_num)+"-----------"
        url=""
        if page_num is None or page_num==1:  
            url = self.base_url  + '/list/index.html'  
        else:
            url = self.base_url + '/list/index_'+str(page_num)+'.html'
        try:
            request = urllib2.Request(url)
            request.add_header('User-Agent', random.choice(agents)) 
            response = urllib2.urlopen(request,None, 10)
            # 返回UTF-8格式编码内容
            return response.read().decode('utf-8')
            # 无法连接，报错
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"错误原因",e.reason
                print url
            return None
        except socket.timeout:
            print "Timed out!"
            print url
            return None

    def get_the_page(self,page_url ):
        try:
            request = urllib2.Request( page_url )
            request.add_header('User-Agent', random.choice(agents)) 
            response = urllib2.urlopen(request,None, 10)
            # 返回UTF-8格式编码内容
            return response.read().decode('utf-8')
            # 无法连接，报错
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"错误原因",e.reason
                print page_url
            return None
        except socket.timeout:
            print "Timed out!"
            print page_url
            return None

    def post_the_url(self,url,values,referer):
        time.sleep(1)
        try:
        # url = 'http://www.someserver.com/cgi-bin/register.cgi'
        # values = {'name' : 'Michael Foord',
        #           'location' : 'Northampton',
        #           'language' : 'Python' }

            data = urllib.urlencode(values)
            request = urllib2.Request(url, data)
            request.add_header('User-Agent', random.choice(agents)) 
            request.add_header('Referer', referer)
            response = urllib2.urlopen(request,None, 10)
            the_page = response.read().decode('utf-8')
            return the_page
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"错误原因",e.reason
                print url
            return None
        except socket.timeout:
            print "Timed out!"
            print url
            return None
    
    def get_items(self,page_content):
        try:
            soup=BeautifulSoup(page_content, "html.parser")
            soup.prettify()
            items=soup.find_all("div", attrs={"class": "item cl"})
            for index,item in enumerate(items):
                tmp1=item.find("p", attrs={"class": "tt cl"})
                if tmp1:

                    tmp2=item.find_all("p")[1](text=True)
                    tmp3=item.find("p", attrs={"class": "des"})
                    tmp4=item.find("p", attrs={"class": "rt2"})
                    tmp5=item.find("div", attrs={"class": "litpic"}).img["src"]

                    douban_url=None;
                    if tmp4.a["href"].split("id="):
                        if len(tmp4.a["href"].split("id="))==2:
                            douban_url=self.douban_movie_index_url+"/"+str(tmp4.a["href"].split("id=")[1]);
                        elif len(tmp4.a["href"].split("url="))==2:
                            douban_url=str(tmp4.a["href"].split("url=")[1]);
                        else:
                            continue;
                    else:
                        continue;

                    # 先判断本页面的数据是否符合要求，再决定是否扒取豆瓣和片源
                    if re.match("^\d+?\.\d+?$", tmp4(text=True)[1] ) and float(tmp4(text=True)[1] )>=self.norm_score and douban_url:

                        grade=float(tmp4(text=True)[1] )
                        audience_num=0
                        desc=u""

                        print "\n------"+str(index+1)+"-douban_url------------"
                        print douban_url;

                        douban_content=self.getDoubanContent(douban_url)
                        if douban_content:
                            if douban_content["audience_num"]!=0:
                                grade=douban_content["grade"]
                                audience_num=douban_content["audience_num"]
                                desc=douban_content["desc"]
                        else:
                            continue

                        download_page_url=None
                        if "http" in tmp1.a["href"]:
                            download_page_url=tmp1.a["href"];
                        elif tmp1.a["href"]:
                            download_page_url=self.base_url+tmp1.a["href"];

                        # show_year=int(tmp1.b(text=True)[1]);
                        # 这个值有可能是字符串
                        show_year=int(re.findall("\d{4}",tmp1.b(text=True)[1] )[0] );
                        # print tmp1.b(text=True)[0][:-1]
                        # print show_year

                        if grade>=self.norm_score and show_year>=2010 and download_page_url:
                            dictElem={};
                            dictElem["name"]=tmp1.b(text=True)[0][:-1];
                            dictElem["other_name"]=''.join(tmp2)

                            dictElem["publish_date"]=tmp1.span(text=True)[0];
                            dictElem["show_year"]=show_year;
                            dictElem["download_page_url"]=download_page_url;
                            dictElem["staff"]=tmp3(text=True)[0];
                            dictElem["douban_url"]=douban_url;
                            dictElem["pic_url"]=tmp5;
                            dictElem["grade"]=float(grade);
                            dictElem["audience_num"]=int(audience_num);
                            dictElem["desc"]=desc;
                            dictElem["is_seen"]=0;
                            # 格式化成2016-03-20 11:45:39形式
                            dictElem["create_time"]=my_local_time()
                            dictElem["update_time"]=my_local_time()
                            # is_good范围
                            # 0:不确定是否值得看;
                            # 1:值得看;
                            # 2:不推荐看;
                            if dictElem["grade"]>=self.norm_score and dictElem["audience_num"]>=self.norm_audience_num:
                                dictElem["is_good"]=1;
                            # 其实这个过不来
                            elif dictElem["grade"]<self.norm_score and dictElem["audience_num"]>=self.norm_audience_num:
                                dictElem["is_good"]=2;
                            else:
                                dictElem["is_good"]=0;

                            # 片源抓取
                            isHD=0;
                            isHD=self.isMovieHD(download_page_url);
                            
                                
                            dictElem["is_hd"]=isHD;

                            self.goods.append(dictElem);
        except Exception, e:
            print "Exception"
            print e.__doc__
            print e.message
            print e
        

    # 豆瓣抓取：抓取评分，评分人数和电影描述
    def getDoubanContent(self,douban_url):
        try:
            res={"grade":0,"audience_num":0,"desc":""};
            # return
            douban_page_content=self.get_the_page(douban_url)
            if douban_page_content:

                douban_soup=BeautifulSoup(douban_page_content, "html.parser")
                douban_soup.prettify()

                douban_info=douban_soup.find("div", attrs={"class": "rating_self clearfix"} )
                if douban_info:
                    douban_info=douban_info(text=True)

                    if douban_info[1].strip() and douban_info[7].strip():
                        res["grade"]=float(douban_info[1].strip())
                        res["audience_num"]=int(douban_info[7].strip())
                        
                        desc_tmp=douban_soup.find(id="link-report")
                        if desc_tmp:
                            desc_tmp=desc_tmp.span(text=True)
                            desc_tmp_list=[];
                            for desc_index,desc_item in enumerate(desc_tmp):
                                desc_item=desc_item.strip();
                                if desc_item and u"展开全部" not in desc_item:
                                    desc_tmp_list.append("&nbsp;&nbsp;&nbsp;&nbsp;"+desc_item );
                            res["desc"]='<br>'.join(desc_tmp_list)
                        return res
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception, e:
            print "Exception"
            print e.__doc__
            print e.message
            print e
            return None

    def isMovieHD(self,download_page_url):
        isHD=0;
        try:
            _id=re.findall(u'/v/(\d+)', download_page_url)
            if _id is None or len(_id)==0:
                return isHD
            _id=_id[0];
            # _id="21364";
            # _id="23476";
            index_url=self.base_url
            page_content=self.post_the_url(index_url+"/e/show.php?classid=1&id="+_id,"",index_url)
            page_content=str(page_content).strip().lower()
            tmp=re.findall(u'document.write\(\'(.*?)\'\);',page_content)
            for cont in tmp:
                hd_list=[u"720p",u"1080p"];
                if doStrContainAnyWords(cont,hd_list):
                    isHD=1;
                    break
            # print "isMovieHD"
            # print isHD
            # time.sleep(10)
        except GetOutOfLoop:
            return isHD
            pass
        except Exception,e:
            print "Exception"
            print e.__doc__
            print e.message
            print e
            pass
        return isHD


    def start(self):
        client = MongoClient("mongodb://name:pwd@localhost:27017/myspace")
        db = client.myspace

        print "\n-------GO!------------"
        start_time=my_local_time()
        print "start:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        start_time_sec = time.time()


        try:

            for page_num in range(self.start_page,self.end_page+1):
                time.sleep(random.randint(20,30))
                one_page=self.get_one_page(page_num);
                self.get_items(one_page);
            print "\n-------mongodb crud------------"
            # 扒取内容并更新到数据库
            for item in self.goods:
                item1=db.movies.find_one({"name": item["name"],"other_name":item["other_name"] } ) 
                if item1 is None:
                    db.movies.insert(item)
                # audience_num为0，说明bt天堂上，爬取的豆瓣url无效，需要自行设置
                elif (item1["grade"]!=item["grade"] or item1["audience_num"]!=item["audience_num"] ) and item["audience_num"]!=0:
                    db.movies.update({"_id": item1["_id"]},{"$set":{'grade':item["grade"],"audience_num":item["audience_num"],"update_time": my_local_time() } } )

            # 对已经存在的不确定推荐的和不确定清晰片源的电影进行更新
            exist_movies=db.movies.find({"$or":[ {"is_good":0 }, {"is_good": { "$ne": 2 },"is_hd":0} ] }  )
            for movie in exist_movies:
                # 不确定清晰片源的
                if movie["is_hd"]==0:
                    # print "-------------片源-------------"
                    # print movie["name"]
                    is_hd=self.isMovieHD(movie['download_page_url']);
                    if is_hd==1:
                        db.movies.update({"_id": movie["_id"]},{"$set":{'is_hd':is_hd ,"update_time": my_local_time() } } )
                # 不确定推荐的
                if movie['is_good']==0:
                    res=self.getDoubanContent(movie['douban_url']);
                    if res:
                        if res["audience_num"]>=self.norm_audience_num and res["grade"]>=self.norm_score:
                            db.movies.update({"_id": movie["_id"]},{"$set":{'grade':res["grade"],"audience_num":res["audience_num"],"desc":res["desc"],"is_good":1,"update_time": my_local_time() } } )
                        elif res["grade"]<self.norm_score:
                            db.movies.update({"_id": movie["_id"]},{"$set":{'grade':res["grade"],"audience_num":res["audience_num"],"desc":res["desc"],"is_good":2,"update_time": my_local_time() } } )
                        else:
                            db.movies.update({"_id": movie["_id"]},{"$set":{'grade':res["grade"],"audience_num":res["audience_num"],"desc":res["desc"],"is_good":0,"update_time": my_local_time() } } )
            # task
            task={};
            task['name']=u"电影爬虫";
            task['status']=1;
            # 格式化成2016-03-20 11:45:39形式
            task["start_time"]=start_time
            task["end_time"]=my_local_time()
            end_time_sec = time.time()
            task["time_cost"]=int(end_time_sec-start_time_sec)
            task["update_time"]=my_local_time()
            db.tasks.insert(task);
            print "end:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print "DONE"
        except Exception, e:
            # task
            task={};
            task['name']=u"电影爬虫";
            task['status']=0;
            # 格式化成2016-03-20 11:45:39形式
            task["start_time"]=start_time
            task["end_time"]=my_local_time()
            end_time_sec = time.time()
            task["time_cost"]=int(end_time_sec-start_time_sec)
            task["update_time"]=my_local_time()
            db.tasks.insert(task);
            print e.__doc__
            print e.message

        


def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string\n"
    elif isinstance(s, unicode):
        print "unicode string\n"
    else:
        print "not a string\n"

def doStrContainAnyWords(str,words=[],exceptStr="1080p的画质"):
    for word in words:
        if word in str and exceptStr not in str:
            return True;

def my_local_time():
    # METHOD 1: Hardcode zones:
    # from_zone = tz.gettz('UTC')
    # to_zone = tz.gettz('America/New_York')

    # METHOD 2: Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = datetime.utcnow()
    # utc = datetime.strptime('2011-01-21 02:37:21', '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    return utc.astimezone(to_zone)


class GetOutOfLoop( Exception ):
    pass

# bt_heaven=BTHeaven("https://movie.douban.com/subject/25928065/",1)
bt_heaven=BTHeaven(u"http://www.bttt99.com",1,7)
bt_heaven.start();

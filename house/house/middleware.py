# encoding=utf-8
import random
import datetime
from user_agents import agents
from proxies import proxies
from selenium import webdriver
from scrapy.http import HtmlResponse
import time,hashlib
from selenium.common.exceptions import WebDriverException
import json
from scrapy.exceptions import IgnoreRequest

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

class DynamicProxyMiddleware(object):
    def process_request(self, request, spider):
    	time.sleep(1)
        authHeader = self.getAuthHeader()
        request.meta['proxy']="http://xxxxx:xxxx";
        request.headers['Proxy-Authorization']=authHeader;

    def getAuthHeader(self):
	    #请替换appkey和secret
	    appkey = "xxxxx"
	    secret = "xxxxxxxxxxxxx"

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

	    # print time.strftime("%Y-%m-%d %H:%M:%S")
	        
	    return authHeader

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = random.choice(proxies)
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
            print "**************ProxyMiddleware have pass************" + proxy['ip_port']
        else:
            print "**************ProxyMiddleware no pass************" + proxy['ip_port']
            request.meta['proxy'] = "http://%s" % proxy['ip_port']



class JavaScriptMiddleware(object):
	
	pc_index_url = "https://sf.taobao.com/item_list.htm?category=50025969"

	def process_request(self, request, spider):
		try:
			driver = webdriver.PhantomJS() #指定使用的浏览器
			 # driver = webdriver.Firefox()
			print "---"+str(request.meta["page"])+"-----js url start-------"
			print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			driver.get(self.pc_index_url+"&page="+str(request.meta["page"]) )
			# time.sleep(1)
			tmp=driver.find_element_by_id('sf-item-list-data').get_attribute("innerHTML")
			print "---"+str(request.meta["page"])+"-----js url end-------"
			print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			body = tmp
			return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
		except Exception,e:
			print "-------------------"
			print e.__doc__
			print e.message
			print "-------------------"
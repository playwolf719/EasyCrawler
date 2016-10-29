# encoding=utf-8
import random
from selenium import webdriver
from scrapy.http import HtmlResponse
import time,hashlib
from selenium.common.exceptions import WebDriverException
import json
from scrapy.exceptions import IgnoreRequest
from cookies import cookies

class CookiesMiddleware(object):
    """ 换Cookie """

    def process_request(self, request, spider):
        request.cookies = cookies

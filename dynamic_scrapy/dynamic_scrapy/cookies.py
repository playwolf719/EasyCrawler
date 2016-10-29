# encoding=utf-8
import json
import base64
import requests



def getCookies():
    """ 获取Cookies """
    loginURL = r'loginURL'
    username="xxxx";
    password="xxx"
    # username="15210883990";
    # password="playwolf719007"
    postData = {
        "username": username,
        "password": password,
    }
            
    
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode('utf-8')
    info = json.loads(jsonStr)
    if info["status"] == 1:
        print "Get Cookie Success!( username:%s )" % username
        cookies = session.cookies.get_dict()
        return cookies
    return None


cookies = getCookies()
print cookies

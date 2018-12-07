import requests
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import re
import rsa
import http.cookiejar
import base64
import urllib
import json
import binascii
import aiohttp
import asyncio
import client
from socket import *
import threading

HOST = '127.0.0.1'
PORT = 8000
BUFSIZE = 1024
ADDR = (HOST,PORT)
USER_URL  = 10
USER_HTML = 11
PRE_URL = 12
PRE_HTML = 13


class Scrapy:
    t0 = time.time()
    count = 0
    connect_count = 0
    login_url = "https://weibo.com"
    cookies_pool = []
    def __init__(self,time = 10):
        self.time = time
        self.user_pool = self.init_users()
        self.headers_pool = self.init_headers()

    def init_headers(self):
        file = open('./res/headers','r')
        headers_group = []
        for headers in file.readlines():
            headers = {"User-Agent":headers.strip('\n')}
            headers_group.append(headers)
        return headers_group

    def init_cookies(self,times = 3):
        cookies_pool = []
        i = 0
        for _ in range(times):
            for user in self.user_pool:
                cookies = self.login(user)
                print('Get cookies No.',i+1,"with user:",user[0])
                cookies_pool.append(cookies)
                i += 1
        print('\n................................cookies_pool len:',len(cookies_pool))
        return cookies_pool
    
    def init_users(self):
        file = open('./res/userform','r')#格式 用户名:密码
        users_group = []
        for users in file.readlines():
            users = (users.strip('\n').split(':')[0],users.strip('\n').split(':')[1])
            users_group.append(users)
        return users_group

    def get_encrypted_name(self,user):
        username_urllike = urllib.request.quote(user[0])
        username_encrypted = base64.b64encode(bytes(username_urllike,encoding = 'utf-8'))
        return username_encrypted.decode('utf-8')

    def get_prelogin_args(self,user):
        '''
        模拟预登陆 获取服务器返回的 nonce ，servertime，pub_key 等信息
        '''
        json_pattern = re.compile('\((.*)\)')
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + self.get_encrypted_name(user) + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)'
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            raw_data = response.read().decode('utf-8')
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except urllib.error as e:
            print("%d"%e.code)
            return None

    def get_encrypted_pw(self,data,user):
        rsa_e = 65537
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' +str(user[1])
        key = rsa.PublicKey(int(data['pubkey'],16),rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'),key)
        self.password = ''
        passwd = binascii.b2a_hex(pw_encypted)
        return passwd
        
    def build_post_data(self,raw,user):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F",
            "vsnf": "1",
            "su": self.get_encrypted_name(user),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw,user),
            "sr": "1440*900",
            "encoding": "UTF-8",
            "prelt": "329",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        return post_data

    def login(self,user):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        p = re.compile('location\.replace\(\"(.*?)\"\)')
        p1 = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"uniqueid":"(\d*?)"')
        headers = random.sample(self.headers_pool,1)[0]
        data = self.get_prelogin_args(user)
        post_data = self.build_post_data(data,user)
        try:
            request = requests.post(url = url,data = post_data,headers = headers)
            login_url = p.search(request.text).group(1)
            time.sleep(0.5)
        except:
            print("login errer")
            print("..............................Error html:\n",request)
            return None
        self.login_url = login_url
        return request.cookies

    async def connect_url(self,url):
        if url is "":
            return None
        if self.count % 250 is 0:
            print("Get Cookies ...")
            self.cookies_pool = []
            self.cookies_pool = self.init_cookies(3)
        print(self.count+1,".\tConnect url :",url,"\tuse time:",time.time()-self.t0)
        self.count += 1
        cookies = random.sample(self.cookies_pool,1)[0]
        headers = random.sample(self.headers_pool,1)[0]
        try:
            async with aiohttp.ClientSession(cookies = cookies) as session:
                async with session.get(url,headers = headers) as r:
                    html =await r.text()
                    await asyncio.sleep(self.time)
                    print("Get Url Success ...")
                    return html,1
        except:
            print("Get Url Error ...")
            return url,0
def get_some_data(tcpCliSock):
    global lock,unseen
    while True:
        urls = client.get_data_from_server(tcpCliSock)
        if urls is not None:
            lock.acquire()
            unseen.update(set(urls))
            lock.release()

async def main(loop):
    global seen,unseen
    att_urls = set()
    lost_url = set()
    user = Scrapy()
    tcpCliSock = socket(AF_INET,SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    tcpCliSock.send(str(USER_URL).encode())
    while True:
        buf = tcpCliSock.recv(100).decode()
        if 'WAIT' in buf:
            print("WAIT")
            break
    while True:
        buf = tcpCliSock.recv(100).decode()
        if 'OK' in buf:
            print("OK")
            break
    print("Connect Already  ....")
    recv_data = threading.Thread(target = get_some_data,args=(tcpCliSock,))
    recv_data.start()
    while True:
        while len(unseen) != 0:
            tasks = [loop.create_task(user.connect_url(url)) for url in unseen]
            finished,unfinished = await asyncio.wait(tasks)
            datas = [f.result() for f in finished]
            print("Connect Finished")
            htmls = []
            lost_url.clear()
            for data,flag in datas:
                if flag is 1:
                    htmls.append(data)
                    if len(htmls) > 5:
                        print("Post Data To Server ....")
                        client.post_data_to_server(tcpCliSock,htmls)
                        htmls = []
                        time.sleep(2)
                else:
                    lost_url.add(data)
            print("Post Data To Server ....")
            client.post_data_to_server(tcpCliSock,htmls)
            htmls = []
            seen.update(unseen)
            unseen = lost_url
            print("Get Data From Server ....")
    tcpCliSock.close()

if __name__ == "__main__":
    base_url = 'https://weibo.com/'
    lock=threading.Lock()
    unseen = set([base_url])
    seen = set()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
    
    

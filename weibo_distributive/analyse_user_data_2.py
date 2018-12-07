import time
from socket import *
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np
import multiprocessing as mp
import client
import threading

USER_URL  = 20
USER_HTML = 21
PRE_URL = 22
PRE_HTML = 23
HOST = '127.0.0.1'
PORT = 8000
BUFSIZE = 1024
ADDR = (HOST,PORT)

def analyse_user_data(html):
    if html is None:
        return ""
    html1 = re.sub(re.compile(r'\\/'),"/",html)
    html2 = re.sub(re.compile(r'\\"'),"\"",html1)
    html3 = re.sub(re.compile(r'\\t'),"\t",html2)
    html4 = re.sub(re.compile(r'\\n'),"\n",html3)
    html5 = re.sub(re.compile(r'\\r'),"\r",html4)
    p = re.compile('href="(/\d+/follow\?rightmod=\d&wvr=\d)"')
    p1 = re.compile(r'<span\s*class="item_ico\s*W_fl">\s*<em\s*class="W_ficon\s*ficon_cd_place\s*S_ficon">[^<>]*</em>[^<>]*</span>[^<>]*<span\s*class="item_text\s+W_fl">\s*([^<>\s]+)\s*[^<>\s]*\s*</span>') 
    p2 = re.compile(r'<title>([^<>]+)</title>')
    p3 = re.compile(r'href="//weibo.com(/p/\d+/follow\?from=page_\d+&wvr=6&mod=headfollow#place)"')
    p4 = re.compile(r'href="(/\d+/fans\?\w+=\d+&\w+=\d+)"')
    p5 = re.compile(r'href="//weibo.com(/p/\d+/follow\?relate=fans&from=\d+&wvr=\d+&mod=headfans&current=fans#place)"')
    p6 = re.compile(r'简介：([^<>]+)')
    p7 = re.compile(r'href="(/\d+/profile\?rightmod=\d+&wvr=\d+&mod=personinfo)"')
    try:
        title = p2.search(html5).group(1).split("的微博")[0]
    except:
        #print("Search title error ...")
        title = ""
    try:
        match = p3.search(html5)
        if match is None:
            match = p.search(html5)
        att_url = "https://weibo.com" + match.group(1)
    except:
        #print("Search att url error\t\t\t\t\t\tError Title:",title)
        att_url = ""
    try:
        match = p5.search(html5)
        if match is None:
            match = p4.search(html5)
        fans_url = "https://weibo.com" + match.group(1)
    except:
        #print("Search fans url error\t\t\t\t\t\tError Title:",title)
        fans_url = ""
    try:
        location = p1.search(html5).group(1)
    except:
        #print("Search location error ...but get the url:",url,"\tError Title:",title)
        location = ""
    try:
        r_autograph = p6.search(html5).group(1)
        autograph = re.sub(re.compile(r'\s+')," ",r_autograph)
    except:
        #print("Search autograph error ...but get the url:",url,"\tError Title:",title)
        autograph = ""
    print("\nFrom title:",title,"\n\tGet att url:",att_url,"\n\tGet fans url:",fans_url,"\n\tLocation:",location,"\tAutograph:",autograph)
    return title,att_url,fans_url,location,autograph

def main():
    pool = mp.Pool(4)
    locations = pd.Series([0],index = ['北京'])
    att_urls = set()
    file_userdata = open('./res/userdata','w')
    file_userdata.write("")
    tcpCliSock = socket(AF_INET,SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    tcpCliSock.send(str(USER_HTML).encode())
    while True:
        buf = tcpCliSock.recv(100).decode()
        print(buf)
        if 'WAIT' in buf:
            print("WAIT")
            break
    while True:
        buf = tcpCliSock.recv(100).decode()
        if 'OK' in buf:
            print("OK")
            break
    print("Connect Already ...")
    while True:
        htmls = client.get_data_from_server(tcpCliSock)
        if htmls is None or len(htmls) is 0:
            continue
        print("Already Get data ...")
        print('\nAnalyse attation html ing ...')
        parse_jobs = [pool.apply_async(analyse_user_data,args=(html,)) for html in htmls]
        user_datas = [j.get() for j in parse_jobs]
        file_userdata = open('./res/userdata','a')
        for title,att_url,fans_url,location,autograph in user_datas:
            if att_url is "":
                continue
            elif att_url in att_urls:
                continue
            user_data = "title:" + title + "att_url:" + att_url + "fans_url:" + fans_url + "location:" + location + "autograph:" + autograph + "\n"
            file_userdata.writelines(user_data)
            if location is not "":
                if location in locations:
                    locations[location] += 1
                else:
                    locations[location] = 1
            att_urls.add(att_url)
            if fans_url is not "":
                att_urls.add(fans_url)
        post_datas = []
        for url in att_urls:
            post_datas.append(url)
            print("Start Post Data ...")
            if len(post_datas) > 5:
                client.post_data_to_server(tcpCliSock,post_datas)
                post_datas = []
        client.post_data_to_server(tcpCliSock,post_datas)
        print("\nLocations:\n",locations)
        locations.to_csv('./res/location.csv')
        att_urls.clear()

if __name__ == "__main__":
    main() 
    

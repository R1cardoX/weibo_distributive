from socket import *
import json
import client

USER_URL  = 10
PRE_URL = 11
USER_HTML = 12
PRE_HTML = 13
HOST = '127.0.0.1'
PORT = 8000
BUFSIZE = 1024
ADDR = (HOST,PORT)

def main():
    tcpCliSock = socket(AF_INET,SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    tcpCliSock.send(str(5).encode())
    while True:
        buf = tcpCliSock.recv(100).decode()
        print(buf)
        if 'WAIT' in buf:
            break
    while True:
        buf = tcpCliSock.recv(100).decode()
        if 'OK' in buf:
            break
    print("Connect Already ...")
    unseen_url = set()
    seen_url = set()
    while True:
        urls = client.get_data_from_server(tcpCliSock)
        unseen_url.update(set(urls)-seen)
        url_list = []
        for url in unseen_url:
            if len(url_list) > 20:
                client.post_data_to_server(tcpCliSock,list(unseen_url))
                url_list = []
                tcpCliSock.send("NEXT".encode())
        client.post_data_to_server(tcpCliSock,list(unseen_url))
        url_list = []
        tcpCliSock.send("NEXT".encode())
        unseen_url.clear()
        seen_url.update(unseen_url)

if __name__ == "__main__":
   main() 
    

import json
import time
from socket import *
BUFSIZE = 1024
def get_data_from_server(tcpCliSock):
    json_dict = ""
    while True:
        while True:
            data = tcpCliSock.recv(BUFSIZE).decode()
            json_dict = json_dict + data
            if not data:
                break
            if data[-4:] == 'NEXT':
                break
        if len(json_dict) > 4:
            break
    json_dict = json_dict[0:-4]
    print(json_dict)
    datas = json.loads(json_dict)
    print(datas)
    return datas
    
def post_data_to_server(tcpCliSock,datas):
    json_dict = json.dumps(datas) + 'NEXT'
    for i in range(0,len(json_dict),BUFSIZE):
        data = json_dict[i:i+BUFSIZE]
        print(data)
        tcpCliSock.send(data.encode())  
    time.sleep(1)

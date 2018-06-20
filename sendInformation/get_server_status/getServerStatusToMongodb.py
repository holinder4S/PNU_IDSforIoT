'''
작성자 : DongKi Lee

수정일 : 2018-06-20

기능 :
일정한 시간마다 한번씩 서버의 상태를 중앙 서버로 전송하는 모듈

change log :

need to change :
1. 네트워크 값을 좀 더 정확하게 받아오는 코드로 변경할 필요성이 있다.
'''

from pymongo import MongoClient
import time
import psutil

client = MongoClient('164.125.14.151', 26543)
db = client.server_data

print(psutil.cpu_percent())

network = psutil.net_io_counters().packets_recv

while(True):
    now = time.localtime()
    if now.tm_mday <= 9:
        day = '0' + str(now.tm_mday)
    else:
        day = str(now.tm_mday)
    if now.tm_mon <= 9:
        mon = '0' + str(now.tm_mon)
    else:
        mon = str(now.tm_mon)
    coll = db[mon + day]

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network_usage = network
    network = psutil.net_io_counters().packets_recv
    network_usage = int((network - network_usage) / 5 / 10240)

    server_load = (cpu + network_usage) / 2
    hour = now.tm_hour
    obj = {'cpu': cpu,
           'ram': ram,
           'disk': disk,
           'network': network_usage,
           'server_load': server_load,
           'hour': hour}
    print(obj)
    coll.insert_one(obj)
    print("insert one data")

    time.sleep(5)
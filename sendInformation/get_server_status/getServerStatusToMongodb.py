from pymongo import MongoClient
import time
import psutil

client = MongoClient('164.125.14.151', 26543)
db = client.server_data

print(psutil.cpu_percent())

network = psutil.net_io_counters().packets_recv

while(True):
    now = time.localtime()
    day = ''
    mon = ''
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
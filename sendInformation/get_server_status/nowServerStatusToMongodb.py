from pymongo import MongoClient
import time
import psutil

client = MongoClient('164.125.14.151', 26543)
db = client.server_data
coll = db.now_stat
print(psutil.cpu_percent())

network = psutil.net_io_counters().packets_recv

while(True):

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network_usage = network
    network = psutil.net_io_counters().packets_recv
    network_usage = int((network - network_usage) / 5 / 10240)

    server_load = (cpu + network_usage) / 2
    obj = {'cpu': cpu,
           'ram': ram,
           'disk': disk,
           'network': network_usage,
           'server_load': server_load}
    print(obj)
    coll.drop()
    print("delete old data")
    coll.insert_one(obj)
    print("insert now data")

    time.sleep(1)
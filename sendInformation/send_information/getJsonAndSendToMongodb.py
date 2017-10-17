from pymongo import MongoClient
import json
import time
import datetime
import os

client = MongoClient('164.125.14.151', 26543)
db = client.packet_data
while(True):
    try:
        with open('/home/ids/pcap_data/output.json', 'r') as data_file:
            parser = json.load(data_file)
            for line in parser:
                try:

                    now = datetime.datetime.now()
                    date = now.strftime('%m%d')
                    manufacture = ''
                    data = ''
                    data_len = ''
                    lat = ''
                    lon = ''
                    created_at = line['_source']['layers']['frame']['frame.time']
                    try:
                        manufacture_mac = line['_source']['layers']['eth']['eth.src_tree']['eth.src_resolved']
                        manufacture_mac = manufacture_mac.split('_')
                        manufacture = manufacture_mac[0]
                        print(manufacture)
                        obj = {'manufacture': manufacture}
                        coll = db[date+'manufacture']
                        coll.insert_one(obj)
                    except:
                        manufacture = 'unknown'
                    try:
                        data = line['_source']['layers']['data']['data.data']
                        data_len = line['_source']['layers']['data']['data.len']
                    except:
                        data_len = -1

                    try:
                        location = line['_source']['layers']['ip']
                        geoIP = ''
                        for i in location.keys():
                            if 'Source GeoIP' in i:
                                geoIP = i
                        lat = location[geoIP]['ip.geoip.src_lat']
                        lon = location[geoIP]['ip.geoip.src_lon']
                        coll = db[date+'geo_data']
                        obj = {'lat': lat,
                               'lon': lon}
                        coll.insert_one(obj)
                    except:
                        lat = -9999
                        lon = -9999
                    obj = {'created_at': created_at,
                           'manufacture': manufacture,
                           'lat': lat,
                           'lon': lon,
                           'data': data,
                           'data_len': data_len}

                    coll = db[date]
                    coll.insert_one(obj)
                    print('insert data to mongodb')
                except:
                    print("error")
            try:
                os.remove('/home/ids/pcap_data/output.json')
            except:
                print('file not found')
    except:
        print('input file not found')
    time.sleep(30)
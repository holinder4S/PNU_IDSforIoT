'''
작성자 : DongKi Lee

수정일 : 2018-06-20

기능 :
IoT 디바이스의 패킷을 수집하고 전처리한 패킷데이터 파일을 읽어서 중앙 서버로 전송하는 모듈

change log :

need to change :
1. 패킷을 서버로 보낼 때 보안적인 문제가 없는지 확인이 필요.
'''

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
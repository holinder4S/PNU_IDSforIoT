'''
작성자 : DongKi Lee

수정일 : 2018-06-20

기능 :
매일 전날까지 모인 패킷데이터에 관련된 정보를 DB에 다시 저장하는 모듈

change log :

need to change :
1. 현재는 기능의 프로토타입 형식으로 제작이 되어 있다. 실제 구현으로 옮겨야함.
'''

import pymongo
import time
import datetime

def calculate_daily_packet(collection_name, weekday):
    try:
        client = pymongo.MongoClient("localhost", 26543)

        database = client['packet_data']
        collection = database[collection_name]
        outputCollection = database['daily_packet']
        count = collection.count()

        today = datetime.datetime.today()
        week = today.isocalendar()[1]
        t = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        obj = {'date': collection_name,
               'week': week,
               'packet_amount': count,
               'vul_amount': int(count/100),
               'weekday': t[weekday]}
        print(obj)
        outputCollection.insert_one(obj)
    except Exception as e:
        print(e)
saveDate = ''
while (True):
    try:
        now = datetime.datetime.now()
        getYesterday = now - datetime.timedelta(days=1)
        weekday = getYesterday.weekday()
        collection_date = getYesterday.strftime('%m%d')
        if saveDate != collection_date:
            calculate_daily_packet(collection_date, weekday)
            saveDate = collection_date

    except Exception as e:
        print(e)
    print('wait 15 minutes')
    time.sleep(900)
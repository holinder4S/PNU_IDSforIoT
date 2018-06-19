'''
작성자 : DongKi Lee

수정일 : 2018-06-20

기능 :
매일 전날까지 모인 데이터를 모아서 평균을 계산하고 DB에 다시 저장하는 모듈

change log :

need to change :
1. 현재는 계속 반복하며, 날짜가 바뀔 때에 연산을 진행하도록 되어있다. 이를 crontab에 등록하고 루프를 없애는 것으로 변경하는 것이 낫다고 생각함.
1-1. 이처럼 루프로 동작하는 모든 프로그램들을 하나로 모아서, crontab에 등록하는 쉘스크립트를 제작할 필요가 있음.
'''

import pymongo
import time
import datetime

def calculate_daily_average(collection_name, weekday):
    try:
        client = pymongo.MongoClient("localhost", 26543)

        database = client['server_data']
        collection = database[collection_name]
        outputCollection = database['daily_usage']
        list = collection.find({})
        daily_cpu_usage = 0
        daily_network_usage = 0
        daily_ram_usage = 0
        length = 0
        for i in list:
            daily_cpu_usage += i['cpu']
            daily_network_usage += i['network']
            daily_ram_usage += i['ram']
            length += 1

        daily_cpu_usage /= length
        daily_network_usage /= length
        daily_ram_usage /= length

        today = datetime.datetime.today()
        week = today.isocalendar()[1]
        t = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        obj = {'date': collection_name,
               'cpu': int(daily_cpu_usage),
               'network': int(daily_network_usage),
               'ram': int(daily_ram_usage),
               'weekday': t[weekday],
               'week': week}
        print(obj)
        outputCollection.insert_one(obj)
    except Exception as e:
        print(e)
saveDate = ''
while (True):
    try:
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        weekday = yesterday.weekday()
        collection_date = yesterday.strftime('%m%d')
        if saveDate != collection_date:
            calculate_daily_average(collection_date, weekday)
            saveDate = collection_date

    except Exception as e:
        print(e)
    print('wait 15 minutes')
    time.sleep(900)
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
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
        getYesterday = now - datetime.timedelta(days=1)
        weekday = getYesterday.weekday()
        collection_date = getYesterday.strftime('%m%d')
        if saveDate != collection_date:
            calculate_daily_average(collection_date, weekday)
            saveDate = collection_date

    except Exception as e:
        print(e)
    print('wait 15 minutes')
    time.sleep(900)
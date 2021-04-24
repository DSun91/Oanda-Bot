from datetime import datetime
import json
import requests
import pandas as pd
import datetime as dt





def read_data(lenght,api_name,name,tf,TOKEN,Startime=None,Endtime=None):

    if api_name == 'oalanda':
        if (Startime is not None) and (Endtime is None):
            candles = get_candles(instrument=name, period=tf, start=Startime,TOKEN=TOKEN,with_index=False)
        elif (Startime is None) and (Endtime is not None):
            candles = get_candles(instrument=name, period=tf, number=lenght, TOKEN=TOKEN,end=Endtime,with_index=False)
        elif (Startime is None) and (Endtime is None):
            candles = get_candles(instrument=name,period=tf,number=lenght,TOKEN=TOKEN,with_index=False)
        elif (Startime is not None) and (Endtime is not None):
            candles = get_candles(instrument=name, period=tf, start=Startime,  end=Endtime,with_index=False,TOKEN=TOKEN)
        #t = datetime.strptime(end_date_time, '%Y-%m-%d %H:%M:%S')
        #end_date_time = str(t.timestamp())
        temp_df=pd.DataFrame()
        temp_df[['day','hour']]=candles['open time'].str.split('T',expand=True)
        temp_df[['hour','butto']]=temp_df['hour'].str.split('Z',expand=True)
        temp_df[['hour', 'butto']] = temp_df['hour'].str.split('.', expand=True)
        candles['open time']=temp_df['day']+' '+temp_df['hour']

        candles['time_ticks']=pd.to_datetime(candles['open time'], format='%Y-%m-%d %H:%M:%S')
        candles['open time']=pd.to_datetime(candles['open time'], format='%Y-%m-%d %H:%M:%S')
        candles['time_ticks'] = candles['time_ticks'].apply(lambda x: x.timestamp())
        candles['time_ticks']=candles['time_ticks'].astype(int)
        candles['high'] = candles['high'].astype(float)
        candles['low'] = candles['low'].astype(float)
        #print(candles)

        #print(candles.head(4))
        #print(candles.dtypes)
        return candles

def get_candles(instrument, period,TOKEN, start=None, end=None,number=10,with_index=None):

    API = "https://api-fxpractice.oanda.com"
    instrument = instrument
    candles_path = f"/v3/instruments/{instrument}/candles"
    #print(period,number)
    query=dict()
    if start != None:
        query['from']=str(start)
    if number!=10:
        query['count'] = number
    if period:
        query['granularity']=str(period)
    if end !=None:
        query['to'] = str(end)


    header = {"Authorization": "Bearer " + TOKEN}

    resp = requests.get(API + candles_path, headers=header, params=query)

    resp = resp.json()
    #print(resp)
    candles = resp['candles']
    list_fin = []
    for i in candles:
        #list_p = [i['time'], i['mid']['o'], i['mid']['h'], i['mid']['l'], i['mid']['c'], i['complete'], i['volume']]
        list_p = [i['time'], float(i['mid']['o']), float(i['mid']['h']), float(i['mid']['l']), float(i['mid']['c']), float(i['complete']), float(i['volume'])]
        list_fin.append(list_p)


    candles = pd.DataFrame(list_fin, columns=['open time', 'open', 'high', 'low', 'close', 'complete', 'volume'])



    return candles
import pandas as pd
from datetime import datetime, timedelta
from allert_system import send_Email
def place_buy_order(symb,price,units,stop_loss_on_fill=None):
    from requests import post
    import requests
    import json

    TOKEN=""
    API = "https://api-fxpractice.oanda.com"
    candles_path = f"/v3/accounts"
    header = {"Authorization": "Bearer " + TOKEN}
    resp = requests.get(API + candles_path, headers=header)
    accountID = resp.json()['accounts']
    accountID = accountID[0]['id']
    print(resp.json())

    headers = {
        "Content-Type": "application/json",
        "Authorization": ""
    }
    data = {

            "order": {
                "price": str(price),
                "timeInForce": "GTC",
                "instrument": str(symb),
                "units": units,
                "type": "LIMIT",
                "positionFill": "DEFAULT"
            }
        }

    data = json.dumps(data)
    # Practice Account
    r = post(f"https://api-fxpractice.oanda.com/v3/accounts/{accountID}/orders",headers=headers,data=data)
    print(r.text)



def Api_call_buy_pattern(df,n_boxes,name,tf,email_receiver=None):
    high_col = 'high'
    low_col = 'low'
    lenght=len(df)
    # print(df)
    box_size = int(lenght / n_boxes)
    if box_size!=0:
        n = int(df.shape[0] / box_size)

    else:
        n=1
    p2 = 0
    p1 = 0
    p3 = 0
    p4 = 0
    p1_l_t = None
    p2_l_t = None
    p3_l_t = None
    p4_l_t = None
    p4_l_ticks = None
    p1_l_v = None
    p2_l_v = None
    p3_l_v = None
    p4_l_v = None
    buy_points=[None,None,None,None,None,None,None,None]
    for i in range(0, n - 1):
        chunk_1 = df[[high_col, low_col]].iloc[i * box_size: (i + 1) * box_size + 1]
        chunk_2 = df[[high_col, low_col]].iloc[(i + 1) * box_size: (i + 2) * box_size]

        min_1 = min(chunk_1[low_col])
        min_2 = min(chunk_2[low_col])

        if min_2 < min_1:
            p2 = chunk_2[chunk_2[low_col] == min_2].index[0]
            if p2 >= lenght:
                p2 = 0
        if min_1 < min_2:
            p2 = chunk_1[chunk_1[low_col] == min_1].index[0]

        if p2 is not 0:
            #print('P2 ',df['open time'].loc[p2])
            for j in reversed(range(df.index[0], p2 - 1)):
                indx = p2 - j
                if df[high_col].loc[p2 - indx] > df[high_col].loc[p2 - indx + 1]:
                    pass
                else:
                    p1 = p2 - indx + 1
                    break

        if p1 is not 0:
            #print('P1 ', df['open time'].loc[p1],p2,df.index[-1],df.shape[0])
            for j in range(p2,df.index[-1]+1):  # qua il range potrebbe andare fino alla fine del segnale anche volendo o no

                #print(df[high_col].loc[j],df[high_col].loc[p1],'\n')
                if df[high_col].loc[j] > df[high_col].loc[p1]:
                    p3 = j

                    break
                else:
                    pass

        if p3 is not 0:
            #print('P3 ', df['open time'].loc[p3])
            for j in range(p3 + 1, df.index[-1]+1):
                if (df[low_col].loc[j] < df['close'].astype(float).loc[p1]) and \
                        (df[low_col].loc[j] > df[low_col].loc[p2]) and \
                        (j < df.index[-1]+1):  # check extremes
                    p4 = j
                    #print('P4 ', df['open time'].loc[p4])

                    if p4 >= df.index[-1]:

                        place_buy_order(symb=name,price=df['close'].loc[p4],units=10000)
                        message = "Enter trade BUY on " + name + ' ' + tf
                        #print(message,'BUY')
                        send_Email(message, email_receiver, SUBJECT='ENTER TRADE BUY ALERT')


                    break
                else:
                    pass

        if (p1 and p2 and p3 and p4) is not 0:

            p1_l_t=df['open time'].loc[p1]
            p1_l_v=df['high'].loc[p1]

            p2_l_t=df['open time'].loc[p2]
            p2_l_v=df['low'].loc[p2]

            p3_l_t=df['open time'].loc[p3]
            p3_l_v=df['high'].loc[p3]

            p4_l_t=df['open time'].loc[p4]
            p4_l_ticks=df['time_ticks'].loc[p4]
            p4_l_v=df['low'].loc[p4]
            buy_points = [p1_l_t, p2_l_t, p3_l_t, p4_l_t, p1_l_v, p2_l_v, p3_l_v, p4_l_v]

        p2 = 0
        p1 = 0
        p3 = 0
        p4 = 0

    #print(df,'\n\n',current_price)

    return df,buy_points,p4_l_ticks

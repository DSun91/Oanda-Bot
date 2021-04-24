import pandas as pd
from datetime import datetime, timedelta
from allert_system import send_Email
from requests import post,get
import requests
import json
def place_buy_order(symb):
    from requests import post
    import requests
    import json

    TOKEN="b14ca133f87d5830690dff7ead123e1c-dab83b0b7be5f9f44465b7dea96f5e11"
    API = "https://api-fxpractice.oanda.com"
    candles_path = f"/v3/accounts"
    header = {"Authorization": "Bearer " + TOKEN}
    resp = requests.get(API + candles_path, headers=header)
    accountID = resp.json()['accounts']
    accountID=accountID[0]['id']
    print(resp.json())


    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer b14ca133f87d5830690dff7ead123e1c-dab83b0b7be5f9f44465b7dea96f5e11"
    }
    data = {
        "order": {
            "units": 1000,
            "instrument": str(symb),
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    data = json.dumps(data)
    # Practice Account
    r = post(f"https://api-fxpractice.oanda.com/v3/accounts/{accountID}/orders",headers=headers,data=data)
    print(r.text)
place_buy_order('EUR_USD')



'''
def cancell():

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer b0149636bd3054b79ce6d5a4593c094e-a727939dac15f89437a55296a7dbc610"
    }
    accountID = '101-012-18417282-001'
    API=f"https://api-fxpractice.oanda.com/v3/accounts/{accountID}/pendingOrders"
    #API=f"https://api-fxpractice.oanda.com/v3/accounts/{accountID}/orders/6372/cancel"

    r = get(
        API,
        headers=headers,

    )
    print(r.json())
  
    '''
import plotly.graph_objects as go
import plotly
import os
from datetime import datetime
import btalib
import pandas as pd
from plotly.subplots import make_subplots
def candlestick_chart(df,stock_symb,points,points_name,timeframe, candles_numb,type_p="BUY",extenstick=None):


    stock_symb=stock_symb.replace('/','-')
    Candle = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2], subplot_titles=("STOCK", "RSI"))
    Candle.add_trace(go.Candlestick(x=df['open time'],
                                    open=df['open'],
                                    high=df['high'],
                                    low=df['low'],
                                    close=df['close']))
    # print(p1_l_t)

    Candle.add_trace(go.Scatter(x=df['open time'], y=df['sma'], mode='lines', name='SMA', line_color='gold'), row=1,
                     col=1)
    Candle.add_trace(go.Scatter(x=df['open time'], y=df['rsi'], mode='lines', name='RSI', line_color='cadetblue'),
                     row=2, col=1)



    for pattern,legends in zip(points,points_name):
       if None not in pattern:
           #print(pattern,legends)
           Candle.add_trace(go.Scatter(x=[pattern[0]], y=[float(pattern[4])], mode='markers', name=str(legends[1]),
                                       marker=plotly.graph_objs.scatter.Marker(size=15, symbol=str(legends[0]),
                                                                               color='maroon', )), row=1, col=1)

           Candle.add_trace(go.Scatter(x=[pattern[1]], y=[pattern[5]], mode='markers', name=legends[3],
                                       marker=plotly.graph_objs.scatter.Marker(size=15, symbol=legends[2],
                                                                               color='yellow', )), row=1, col=1)

           Candle.add_trace(go.Scatter(x=[pattern[2]], y=[pattern[6]], mode='markers', name=legends[5],
                                       marker=plotly.graph_objs.scatter.Marker(size=15, symbol=legends[4],
                                                                               color='orange', )), row=1, col=1)

           Candle.add_trace(go.Scatter(x=[pattern[3]], y=[pattern[7]], mode='markers', name=legends[7],
                                       marker=plotly.graph_objs.scatter.Marker(size=15, symbol=legends[6],
                                                                               color='royalblue', )), row=1, col=1)



        #print(extenstick)
    if extenstick is not None:
        for value in extenstick:
            #print(value, '\n', value[0])
            if value[0] != None:
                temp = [str(datetime.fromtimestamp(value[0]))]
                Candle.add_trace(go.Scatter(x=temp, y=[value[1]], mode='markers', name=value[2],
                                            marker=plotly.graph_objs.scatter.Marker(size=15, symbol=value[3],
                                                                                    color=value[4])), row=1, col=1)

    Candle.update_layout(xaxis_rangeslider_visible=False,
                         title=stock_symb + " " + str(candles_numb) + " CANDLES CHART- TIME INTERVAL: " + timeframe)

    stock_name = stock_symb + "TIME INTERVAL_" + timeframe
    dir_name = './Results/' + stock_symb
    title = dir_name + '/' + stock_symb + str(candles_numb) + "CANDLES CHART-TIME INTERVAL_" + timeframe + type_p + ".html"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    Candle.write_html(title)
    return stock_name


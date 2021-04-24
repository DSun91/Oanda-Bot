import pandas as pd
import time
import datetime
import ast
from Buy_pattern import Api_call_buy_pattern
from allert_system import send_Email
from charting import candlestick_chart
from Sell_pattern import Api_call_sell_search
import btalib
from load_data import read_data
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

p_l_t_h = dict()
p_l_t_s=dict()
Buy_notebook=dict()
Open_short_notebook=dict()
check_points_buy=dict()
check_points_sell=dict()
start_time=dict()
datas=dict()
df_RSI=dict()
alerts=dict()


def fxcm_stock(n_box, list_pp, email_receiver,time_frames,times,number_of_c):

    c_ounter_n_candles = 0
    c = 0
    message = []
    col_num = len(list_pp) * len(time_frames)

    for tf in time_frames:
        for symbs in list_pp:
            #datas[symbs, tf]=None
            print("Downloading data: ", symbs, tf)

            datas[symbs, tf]=read_data(lenght=number_of_c[c_ounter_n_candles], api_name='oalanda', name=symbs,
                                       tf=tf, Startime=start_time[symbs, tf][0],Endtime=end_date_time,TOKEN=TOKEN)
            df_RSI[symbs, tf] = read_data(lenght=480, api_name='oalanda', name=symbs, tf=tf,Endtime=end_date_time,TOKEN=TOKEN)






    for tf in time_frames:
        for symbs in list_pp:

            print('Symbol: ', symbs, '   Timeframe:', times[c])

            buy_base_points=[None,None,None,None,None,None,None,None]
            sell_base_points=[None,None,None,None,None,None,None,None]

            last_tick_BUY_search = 0
            last_tick_SELL_search = 0
            df_data=datas[symbs, tf]
            #print(df_data.tail(3))
            #df_data=pd.read_csv('t3BINANCE_BTCUSDT_ 60.csv')
            #df_data['time_ticks'] = df_data['time']
            #df_data['open time'] = df_data['time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
            #df_data.columns=[]
            #print(df_data.head(20))

            df_rsi = pd.DataFrame()
            df_rsi[['Date', 'High', 'Low', 'Close']] = df_RSI[symbs, tf][['open time', 'high', 'low', 'close']]
            #print(df_data)
            df_rsi = df_rsi.set_index('Date')

            if len(df_rsi) > RSI_PERIOD:
                rsii = btalib.rsi(df_rsi['Close'].astype(float), period=RSI_PERIOD)
                rsii = rsii.df.reset_index()
                sma = btalib.sma(df_rsi['High'], period=SMA_PERIOD)
                df_data['sma'] = sma.df.tail(len(df_data))['sma'].reset_index(drop=True)
                df_data['rsi'] = rsii.tail(len(df_data))['rsi'].reset_index(drop=True)
            else:
                df_data['rsi'] = None
                df_data['sma'] = None
            #df_data['rsi']=df_data['RSI']
            df_filter_rsi_start = df_data[df_data['rsi'] <= buy_pattern_rsi]
            if len(df_filter_rsi_start) > 0:
                last_tick_BUY_search = df_filter_rsi_start['time_ticks'].values[-1]

            df_filter_rsi_start = df_data[df_data['rsi'] >= sell_pattern_rsi]
            if len(df_filter_rsi_start) > 0:
                last_tick_SELL_search = df_filter_rsi_start['time_ticks'].values[-1]

            #print('Last time RSI<',buy_pattern_rsi,'%', last_tick_SELL_search,'  Last time RSI>',sell_pattern_rsi," ",last_tick_SELL_search)
            #print(df_rsi.head())
            df = df_data


            if (last_tick_BUY_search > last_tick_SELL_search):

                if (Buy_notebook[symbs, tf][3] is None) and (Open_short_notebook[symbs, tf][3] is None):
                    #print('Searching Buy')
                    Open_short_notebook[symbs, tf]=[None, None, None, None, None, None, None, None]
                    df, buy_base_points, p4_buy_ticks = Api_call_buy_pattern(
                        df=df_data,
                        n_boxes=n_box,
                        name=symbs,
                        tf=tf,
                        email_receiver=email_receiver
                    )
                elif Buy_notebook[symbs, tf][3] is not None:
                    buy_base_points[0]=Buy_notebook[symbs, tf][0]
                    buy_base_points[1]=Buy_notebook[symbs, tf][1]
                    buy_base_points[2]=Buy_notebook[symbs, tf][2]
                    buy_base_points[3]=Buy_notebook[symbs, tf][3]
                    buy_base_points[4]=Buy_notebook[symbs, tf][4]
                    buy_base_points[5]=Buy_notebook[symbs, tf][5]
                    buy_base_points[6]=Buy_notebook[symbs, tf][6]
                    buy_base_points[7]=Buy_notebook[symbs, tf][7]
                    p4_buy_ticks=df[df['open time']==Buy_notebook[symbs, tf][3]]['time_ticks'].values[0]
                elif Open_short_notebook[symbs, tf][3] is not None:
                    sell_base_points[0]=Open_short_notebook[symbs, tf][0]
                    sell_base_points[1]=Open_short_notebook[symbs, tf][1]
                    sell_base_points[2]=Open_short_notebook[symbs, tf][2]
                    sell_base_points[3]=Open_short_notebook[symbs, tf][3]
                    sell_base_points[4]=Open_short_notebook[symbs, tf][4]
                    sell_base_points[5]=Open_short_notebook[symbs, tf][5]
                    sell_base_points[6]=Open_short_notebook[symbs, tf][6]
                    sell_base_points[7]=Open_short_notebook[symbs, tf][7]
                    p4_sell_ticks=df[df['open time']==sell_base_points[3]]['time_ticks'].values[0]



            elif(last_tick_SELL_search>last_tick_BUY_search  ):
                #print('Searching Open Short')
                if (Open_short_notebook[symbs, tf][3] is None) and (Buy_notebook[symbs, tf][3] is None):# se non ho ancora un sell
                    Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]

                    df, sell_base_points,p4_sell_ticks = Api_call_sell_search(
                        df=df_data,
                        n_boxes=n_box,
                        name=symbs,
                        tf=tf,
                        email_receiver=email_receiver
                    )
                elif Open_short_notebook[symbs, tf][3] is not None:
                    sell_base_points[0]=Open_short_notebook[symbs, tf][0]
                    sell_base_points[1]=Open_short_notebook[symbs, tf][1]
                    sell_base_points[2]=Open_short_notebook[symbs, tf][2]
                    sell_base_points[3]=Open_short_notebook[symbs, tf][3]
                    sell_base_points[4]=Open_short_notebook[symbs, tf][4]
                    sell_base_points[5]=Open_short_notebook[symbs, tf][5]
                    sell_base_points[6]=Open_short_notebook[symbs, tf][6]
                    sell_base_points[7]=Open_short_notebook[symbs, tf][7]
                    p4_sell_ticks=df[df['open time']==sell_base_points[3]]['time_ticks'].values[0]
                elif Buy_notebook[symbs, tf][3] is not None:
                    buy_base_points[0]=Buy_notebook[symbs, tf][0]
                    buy_base_points[1]=Buy_notebook[symbs, tf][1]
                    buy_base_points[2]=Buy_notebook[symbs, tf][2]
                    buy_base_points[3]=Buy_notebook[symbs, tf][3]
                    buy_base_points[4]=Buy_notebook[symbs, tf][4]
                    buy_base_points[5]=Buy_notebook[symbs, tf][5]
                    buy_base_points[6]=Buy_notebook[symbs, tf][6]
                    buy_base_points[7]=Buy_notebook[symbs, tf][7]
                    p4_buy_ticks=df[df['open time']==Buy_notebook[symbs, tf][3]]['time_ticks'].values[0]




####################################################################################  OPEN SHORT

            if (len(sell_base_points)>0) and (None not in sell_base_points):  # Se entro nel short
                #print(symbs, " entrato nel sell")
                PS = ['circle-x','P1 SELL','circle-cross','P2 SELL','star-triangle-down','P3 SELL','star-diamond','P4 SELL']
                PB = ['x', 'P1 BUY', 'cross', 'P2 BUY', 'triangle-down', 'P3 BUY', 'star', 'P4 BUY']
                candlestick_chart(df=df, stock_symb=symbs, points=[sell_base_points],
                                  points_name=[PS] ,timeframe=times[c],candles_numb=number_of_c[c_ounter_n_candles],type_p="SELL-")
                start_time[symbs, tf][0] = df['time_ticks'].iloc[0]
                Open_short_notebook[symbs, tf] = sell_base_points



                low_150_extension = float(sell_base_points[7]) - 1.5 * (float(sell_base_points[5]) - float(sell_base_points[6]))
                df_stop_loss_p2_short = df[df['low'] > sell_base_points[5]]  # pt2 short stop loss al p2

                if len(df_stop_loss_p2_short)>0:
                    p2_short_stp_ponit = df_stop_loss_p2_short['time_ticks'].iloc[0]
                    candlestick_chart(df, symbs, [sell_base_points],[PS] ,
                                      times[c], number_of_c[c_ounter_n_candles], type_p='OPEN SHORT STOP LOSS AT P2 SELL',
                                      extenstick=[
                                          [df_stop_loss_p2_short['time_ticks'].iloc[0], df_stop_loss_p2_short['low'].iloc[0],
                                           "SELL -> STOP LOSS", "circle-x", 'darkorchid']])

                    Open_short_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                    alerts[symbs, tf] =  [None, None, None, None]
                    start_time[symbs, tf][0] = df_stop_loss_p2_short[df_stop_loss_p2_short['time_ticks'] == p2_short_stp_ponit]['time_ticks'].values[0]
                    message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+ " AT P2 SELL AFTER OPEN SHORT"
                    send_Email(message_stop_losses, email_receiver, SUBJECT='SELL STOP LOSS ALERT')
                    sell_base_points = [None, None, None, None, None, None, None, None]

                else:
                    low_50_extension = float(sell_base_points[7]) - FIB_ext_SELL * (float(sell_base_points[5]) - float(sell_base_points[6]))
                    filter_df_50_ext_short = df[df['time_ticks'] > int(p4_sell_ticks)]  # filtro tutti i valori sopra al 150% e dopo il sell point
                    filter_df_50_ext_short = filter_df_50_ext_short[filter_df_50_ext_short['low'] <= low_50_extension]

                    if len(filter_df_50_ext_short) > 0:
                        check_points_sell[symbs, tf][0] = '50_EXT_DOWN'
                        tick_after_50_short = filter_df_50_ext_short['time_ticks'].iloc[0]

                        df_stop_loss_p2_50_short = df[df['time_ticks'] > tick_after_50_short]
                        df_stop_loss_p2_50_short = df_stop_loss_p2_50_short[df_stop_loss_p2_50_short['high'] > Open_short_notebook[symbs, tf][7]]  # pt4 buy

                        if len(df_stop_loss_p2_50_short) > 0:
                            p2_buy_stop_loss_50_short = df_stop_loss_p2_50_short['time_ticks'].iloc[0]
                            candlestick_chart(df, symbs, [sell_base_points], [PS],
                                              times[c], number_of_c[c_ounter_n_candles],
                                              type_p='OPEN SHORT STOP LOSS 50 FIB',
                                              extenstick=[[df_stop_loss_p2_50_short['time_ticks'].iloc[0],
                                                           df_stop_loss_p2_50_short['high'].iloc[0],
                                                           "STOP LOSS AT P4 SELL", "circle-x", 'darkorchid'],
                                                          [tick_after_50_short, filter_df_50_ext_short['low'].iloc[0],
                                                           "1th FIB EXT",
                                                           "diamond-wide", 'blue']])

                            Open_short_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                            check_points_sell[symbs, tf] = [None, None, None]
                            alerts[symbs, tf] =  [None, None, None, None]
                            start_time[symbs, tf][0] = p2_buy_stop_loss_50_short
                            message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+" AT P4 SELL AFTER 50% FIB."
                            send_Email(message_stop_losses, email_receiver, SUBJECT='SELL -> 1th FIB -> STOP LOSS ALERT')
                            sell_base_points = [None, None, None, None, None, None, None, None]

                        elif len(df_stop_loss_p2_50_short) <= 0:
                            filter_df_150_ext_short = df[df['time_ticks'] > int(p4_sell_ticks)]  # filtro tutti i valori sopra al 150% e dopo il sell point
                            filter_df_150_ext_short = filter_df_150_ext_short[filter_df_150_ext_short['low'] <= low_150_extension]

                            if len(filter_df_150_ext_short) > 0:  # se effetivamente ci sono valori dopo il 150% dopo il buy pattern e il df non è solo 1 riga# si perte il real time
                                check_points_sell[symbs, tf][1] = '150_EXT_DOWN'
                                tick_after_150_short = filter_df_150_ext_short['time_ticks'].iloc[0]

                                if alerts[symbs, tf][0] is None:
                                    message_150_S = "150 EXTENSION REACHED ON " + symbs + ' ' + tf + " SELL PATTERN"
                                    alerts[symbs, tf][0] = message_150_S
                                    send_Email(message_150_S, email_receiver, SUBJECT='SELL -> 150%EXT')


                                candlestick_chart(df, symbs, [sell_base_points], [PS], times[c],
                                                  number_of_c[c_ounter_n_candles], type_p='SELL-',
                                                  extenstick=[
                                                      [tick_after_150_short, filter_df_150_ext_short['low'].iloc[0],
                                                       "150% EXT SHORT",
                                                       "diamond-cross", 'blue']])  # disegno con il tick al 150%

                                df_stop_loss_p2_150_short = df[df['time_ticks'] > tick_after_150_short]
                                df_stop_loss_p2_150_short = df_stop_loss_p2_150_short[df_stop_loss_p2_150_short['high'] > Open_short_notebook[symbs, tf][7]]  # pt4 buy

                                if len(df_stop_loss_p2_150_short) > 0:
                                    p2_buy_stop_loss_150_short = df_stop_loss_p2_150_short['time_ticks'].iloc[0]
                                    candlestick_chart(df, symbs, [sell_base_points], [PS],
                                                      times[c], number_of_c[c_ounter_n_candles],
                                                      type_p='OPEN SHORT STOP LOSS AFTER 150 SHORT',
                                                      extenstick=[[df_stop_loss_p2_150_short['time_ticks'].iloc[0],df_stop_loss_p2_150_short['high'].iloc[0],
                                                                   "STOP LOSS AT P4 SELL AFTER 150% EXT", "circle-x",'darkorchid'], [tick_after_150_short,
                                                                   filter_df_150_ext_short['low'].iloc[0], "150% EXT SHORT","diamond-wide", 'blue']])

                                    Open_short_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                                    check_points_sell[symbs, tf] = [None, None, None]
                                    alerts[symbs, tf] = [None, None, None, None]
                                    start_time[symbs, tf][0] = p2_buy_stop_loss_150_short
                                    message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf +' AT P4 SELL AFTER 150% EXT'
                                    send_Email(message_stop_losses, email_receiver, SUBJECT='SELL -> 150% EXT -> STOP LOSS')
                                    sell_base_points = [None, None, None, None, None, None, None, None]

                                elif len(df_stop_loss_p2_150_short) <= 0:
                                    # check RSI<40
                                    df_filter_rsi_short = df[df['time_ticks'] > int(tick_after_150_short)]
                                    df_filter_rsi_short = df_filter_rsi_short[(df_filter_rsi_short['rsi'] <= buy_pattern_rsi)]

                                    if len(df_filter_rsi_short) > 0:
                                        # print("YEEE LIGHT WEIGH BABY! RSI40")
                                        check_points_sell[symbs, tf][2] = 'HIT RSI40'
                                        tick_after_RSI_short = df_filter_rsi_short['time_ticks'].iloc[0]
                                        df_b = df[df['time_ticks'] >= tick_after_RSI_short]

                                        if alerts[symbs, tf][1] is None:
                                            message_150_SRSI = "RSI" + str(buy_pattern_rsi) + " REACHED ON" + symbs + ' ' + tf + " SELL PATTERN"
                                            send_Email(message_150_SRSI, email_receiver, SUBJECT='SELL -> 150%EXT -> RSI-THRESHOLD')
                                            alerts[symbs, tf][1] = message_150_SRSI



                                        candlestick_chart(df, symbs, [sell_base_points], [PS], times[c],
                                                          number_of_c[c_ounter_n_candles], type_p='SELL-',
                                                          extenstick=[[tick_after_150_short,
                                                                       filter_df_150_ext_short['low'].iloc[0],
                                                                       "150% SHORT EXT", "diamond-wide", 'blue'],
                                                                      [tick_after_RSI_short,
                                                                       df_filter_rsi_short['low'].iloc[0], "40 RSI",
                                                                       "hexagram", 'black']])
                                        # parte la ricerca del buy dopo RSI40
                                        df_buy, buy_points, p4_l_buy_tt = Api_call_buy_pattern(
                                            df=df_b,
                                            n_boxes=2,
                                            name=symbs,
                                            tf=tf,
                                            email_receiver=email_receiver
                                        )

                                        # piglio il tempo dove ci può essere uno stop loss ad RSI70
                                        df_stop_loss_RSI_p2_short = df[df['time_ticks'] > tick_after_RSI_short]
                                        df_stop_loss_RSI_p2_short = df_stop_loss_RSI_p2_short[
                                        df_stop_loss_RSI_p2_short['rsi'] >= sell_pattern_rsi]  # pt2 buy
                                        # print(df_stop_loss_RSI_p2_short)
                                        if len(df_stop_loss_RSI_p2_short) > 0:
                                            p2_buy_stop_loss_RSI_short = df_stop_loss_RSI_p2_short['time_ticks'].iloc[0]
                                        else:
                                            p2_buy_stop_loss_RSI_short = df['time_ticks'].loc[df.index[-1]]

                                        # piglio il tempo in tick del buy
                                        if p4_l_buy_tt is not None:
                                            # print(df)
                                            p_buy4_ticks = df[df['time_ticks'] == p4_l_buy_tt]['time_ticks'].values[0]
                                        else:
                                            p_buy4_ticks = 0

                                        if p_buy4_ticks < p2_buy_stop_loss_RSI_short:
                                            if None not in buy_points:
                                                candlestick_chart(df, symbs, [sell_base_points, buy_points],[PS, PB],times[c], number_of_c[c_ounter_n_candles],
                                                                  type_p='SELL-', extenstick=[
                                                                      [tick_after_RSI_short,df_filter_rsi_short['low'].iloc[0],"40 RSI","hexagram", 'black'],
                                                                      [tick_after_150_short,filter_df_150_ext_short['low'].iloc[0],"150% EXT SHORT","diamond-wide", 'blue']])

                                                last_sell_pt = df_buy[df_buy['time_ticks'] == p4_l_buy_tt]['time_ticks'].values[0]
                                                # print('Last buy Pt', last_sell_pt, p4_l_sell_t)
                                                Open_short_notebook[symbs, tf] = [None, None, None, None, None, None,None, None]
                                                start_time[symbs, tf][0] = last_sell_pt  # rinizio a cercare dall'ultimo sell point
                                                check_points_sell[symbs, tf] = [None, None, None]
                                                sell_base_points = [None, None, None, None, None, None, None,
                                                                               None]
                                                if alerts[symbs, tf][2] is None:
                                                    message_150_SB = "BUY PATTERN FOUND ON" + symbs + ' ' + tf + " SELL PATTERN"
                                                    send_Email(message_150_SB, email_receiver, SUBJECT='SELL -> 150%EXT -> RSI-THRESHOLD -> BUY')
                                                    alerts[symbs, tf][2] = message_150_SB


                                        # STOP LOSS RSI

                                        elif p_buy4_ticks > p2_buy_stop_loss_RSI_short:
                                            candlestick_chart(df, symbs, [sell_base_points], [PS],
                                                              times[c], number_of_c[c_ounter_n_candles],
                                                              type_p='OPEN SHORT STOP LOSS AT 70 RSI',
                                                              extenstick=[[df_stop_loss_RSI_p2_short['time_ticks'].iloc[0],df_stop_loss_RSI_p2_short['high'].iloc[0],"STOP LOSS AFTER AT 70 RSI","circle-x", 'darkorchid'],
                                                                          [tick_after_RSI_short,df_filter_rsi_short['low'].iloc[0],"40 RSI","hexagram", 'black'],
                                                                          [tick_after_150_short,filter_df_150_ext_short['low'].iloc[0],"150% EXT SHORT","diamond-wide",'blue'],
                                                                  ])

                                            Open_short_notebook[symbs, tf] = [None, None, None, None, None, None, None,None]
                                            check_points_sell[symbs, tf] = [None, None, None]
                                            alerts[symbs, tf]=[None,None,None,None]
                                            start_time[symbs, tf][0] = p2_buy_stop_loss_RSI_short
                                            message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+' LOSS AT 70 RSI AFTER OPEN SHORT AND 40 RSI'
                                            send_Email(message_stop_losses, email_receiver, SUBJECT='SELL -> 150 EXT -> RSI THRESHOLD -> STOP LOSS')
                                            sell_base_points = [None, None, None, None, None, None, None,
                                                                           None]

            ################################################################################################################# BUY

            if (len(buy_base_points)>0) and (None not in buy_base_points):# Se entro nel buy

                #print(symbs, "   entrato nel buy")
                #print(buy_base_points)
                hundred_extension = float(buy_base_points[4]) + 1.5 * (float(buy_base_points[6]) - float(buy_base_points[5]))
                fifty_extension = float(buy_base_points[4]) + FIB_ext_BUY * (float(buy_base_points[6]) - float(buy_base_points[5]))
                PB = ['x', 'P1 BUY', 'cross', 'P2 BUY', 'triangle-down', 'P3 BUY', 'star', 'P4 BUY']
                candlestick_chart(df=df, stock_symb=symbs,points=[buy_base_points],points_name=[PB],timeframe=times[c],
                                  candles_numb=number_of_c[c_ounter_n_candles],type_p='BUY-')


                start_time[symbs,tf][0]=df['time_ticks'].iloc[0]

                Buy_notebook[symbs, tf] = buy_base_points

                #stopp loss buy 1th
                df_stop_loss_p2 = df[df['low'] < Buy_notebook[symbs, tf][5]]  # stop loss al p2

                if len(df_stop_loss_p2) > 0:
                    p2_buy_stop_loss = df_stop_loss_p2['time_ticks'].iloc[0]
                    candlestick_chart(df, symbs,[buy_base_points],[PB],times[c], number_of_c[c_ounter_n_candles],type_p='BUY STOP LOSS P2',
                                      extenstick=[[df_stop_loss_p2['time_ticks'].iloc[0], df_stop_loss_p2['low'].iloc[0],"STOP LOSS AT P2 BUY", "circle-x", 'darkorchid']])
                    Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                    check_points_buy[symbs, tf]=[None, None, None]
                    alerts[symbs, tf] = [None, None, None,None]
                    start_time[symbs, tf][0] = df_stop_loss_p2[df_stop_loss_p2['time_ticks'] == p2_buy_stop_loss]['time_ticks'].values[0]
                    message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+ " AT P2 BUY"
                    send_Email(message_stop_losses, email_receiver, SUBJECT='BUY -> STOP LOSS')
                    buy_base_points = [None, None, None, None, None, None, None, None]
                elif len(df_stop_loss_p2) <= 0:

                    filter_df_50_ext = df[df['time_ticks'] > int(p4_buy_ticks)]
                    filter_df_50_ext = filter_df_50_ext[filter_df_50_ext['high'] >= fifty_extension]

                    if len(filter_df_50_ext)>0:
                        tick_after_50 = filter_df_50_ext['time_ticks'].iloc[0]
                        df_stop_loss_p2_50_ext = df[df['low']>tick_after_50]  # pt4 buy
                        df_stop_loss_p2_50_ext = df_stop_loss_p2_50_ext[df_stop_loss_p2_50_ext['low'].astype(float) <= buy_base_points[7]]  # pt4 buy

                        if len(df_stop_loss_p2_50_ext) > 0:
                            p2_buy_stop_loss = df_stop_loss_p2_50_ext['time_ticks'].iloc[0]
                            candlestick_chart(df, symbs, [buy_base_points], [PB], times[c],
                                              number_of_c[c_ounter_n_candles],
                                              type_p='BUY STOP LOSS AFTER 50 FIB',
                                              extenstick=[
                                                  [df_stop_loss_p2_50_ext['time_ticks'].iloc[0],
                                                   df_stop_loss_p2_50_ext['low'].iloc[0],
                                                   "STOP LOSS P2 BUY", "circle-x", 'darkorchid']])
                            Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                            check_points_buy[symbs, tf] = [None, None, None]
                            alerts[symbs, tf] = [None, None, None, None]
                            start_time[symbs, tf][0] = df_stop_loss_p2_50_ext[df_stop_loss_p2_50_ext['time_ticks'] == p2_buy_stop_loss]['time_ticks'].values[0]
                            message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+ " AT P2 BUY AFTER 50 FIB"
                            send_Email(message_stop_losses, email_receiver, SUBJECT='BUY -> 1th FIB -> STOP LOSS')
                            buy_base_points = [None, None, None, None, None, None, None, None]
                        elif len(df_stop_loss_p2_50_ext)<=0:
                            filter_df_150_ext = df[df['time_ticks'] > int(p4_buy_ticks)]  # filtro tutti i valori sopra al 150% e dopo il sell point
                            filter_df_150_ext = filter_df_150_ext[filter_df_150_ext['high'] >= hundred_extension]

                            if len(filter_df_150_ext) > 0:  # se effetivamente ci sono valori dopo il 150% dopo il buy pattern e il df non è solo 1 riga# si perte il real time
                                check_point_150 = 1000
                                check_points_buy[symbs, tf][0] = check_point_150
                                tick_after_150 = filter_df_150_ext['time_ticks'].iloc[0]
                                if alerts[symbs, tf][0] is None:
                                    message_150 = "150 EXTENSION REACHED ON " + symbs + ' ' + tf + " BUY PATTERN"
                                    send_Email(message_150, email_receiver, SUBJECT='BUY -> 150%EXT')
                                    alerts[symbs, tf][0] = message_150

                                candlestick_chart(df, symbs, [buy_base_points], [PB], times[c],
                                                  number_of_c[c_ounter_n_candles], type_p='BUY-',
                                                  extenstick=[[tick_after_150, filter_df_150_ext['high'].iloc[0],
                                                               "150% EXT SELL1/2", "diamond-wide",
                                                               'blue']])  # disegno con il tick al 150%

                                # secondo me lo stop loss al pt4 after 150%
                                df_stop_loss_p2_150_ext = df[df['time_ticks'] > tick_after_150]
                                df_stop_loss_p2_150_ext = df_stop_loss_p2_150_ext[df_stop_loss_p2_150_ext['low'] < Buy_notebook[symbs, tf][7]]  # pt4 buy
                                if len(df_stop_loss_p2_150_ext) > 0:
                                    p2_buy_stop_loss_150_ext = df_stop_loss_p2_150_ext['time_ticks'].iloc[0]
                                    candlestick_chart(df, symbs, [buy_base_points], [PB],
                                                      times[c], number_of_c[c_ounter_n_candles],
                                                      type_p='BUY STOP LOSS AFTER 150',
                                                      extenstick=[
                                                          [df_stop_loss_p2_150_ext['time_ticks'].iloc[0],
                                                           df_stop_loss_p2_150_ext['low'].iloc[0],
                                                           "STOP LOSS AT P4 BUY AFTER 150", "circle-x", 'darkorchid'],
                                                          [tick_after_150, filter_df_150_ext['high'].iloc[0],
                                                           "150% EXT SELL 1/2", "diamond-wide", 'blue']])

                                    Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                                    check_points_buy[symbs, tf] = [None, None, None]
                                    alerts[symbs, tf] = [None, None, None, None]
                                    start_time[symbs, tf][0] = p2_buy_stop_loss_150_ext
                                    message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+ " AT P4 BUY AFTER 150% EXT"
                                    send_Email(message_stop_losses, email_receiver, SUBJECT='BUY -> 150 EXT -> STOP LOSS')
                                    buy_base_points = [None, None, None, None, None, None, None, None]

                                elif len(df_stop_loss_p2_150_ext) <= 0:
                                    # check RSI>70
                                    df_filter_rsi = df[df['time_ticks'] > int(tick_after_150)]
                                    df_filter_rsi = df_filter_rsi[(df_filter_rsi['rsi'] >= sell_pattern_rsi)]

                                    if len(df_filter_rsi) > 0:
                                        # print('RAGGIUNTO RSI 70')
                                        check_point_RSI = 1000
                                        check_points_buy[symbs, tf][1] = check_point_RSI
                                        tick_after_RSI = df_filter_rsi['time_ticks'].iloc[0]
                                        df_search_sell = df[df['time_ticks'] > tick_after_RSI]
                                        if alerts[symbs, tf][1] is None:
                                            message_RSI = "RSI" + str(sell_pattern_rsi) + " REACHED ON " + symbs + ' ' + tf + " : SEARCHING A SELL PATTERN NOW ON"
                                            send_Email(message_RSI, email_receiver, SUBJECT='BUY -> 150%EXT -> RSI-THRESHOLD')
                                            alerts[symbs, tf][1] = message_RSI


                                        candlestick_chart(df, symbs, [buy_base_points], [PB], times[c],
                                                          number_of_c[c_ounter_n_candles], type_p='BUY-',
                                                          extenstick=[[tick_after_150, filter_df_150_ext['high'].iloc[0],"150% EXT", "diamond-wide", 'blue'],
                                                              [tick_after_RSI, df_filter_rsi['high'].iloc[0], "70 RSI","hexagram", 'black']])

                                        df_sell, sell_points, _ = Api_call_sell_search(df=df_search_sell,
                                                                                                      n_boxes=n_box,
                                                                                                      name=symbs, tf=tf,
                                                                                                      email_receiver=email_receiver)

                                        df_stop_loss_RSI_p2 = df[df['time_ticks'] > tick_after_RSI]
                                        df_stop_loss_RSI_p2 = df_stop_loss_RSI_p2[df_stop_loss_RSI_p2['rsi'] < buy_pattern_rsi]  # pt2 buy
                                        if len(df_stop_loss_RSI_p2)>0:
                                            p2_buy_stop_loss_RSI = df_stop_loss_RSI_p2['time_ticks'].iloc[0]
                                        else:
                                            p2_buy_stop_loss_RSI=df['time_ticks'].iloc[-1]

                                        # print("-----------------------------",sell_points)
                                        if None not in sell_points:
                                            p_sel4_ticks = df[df['open time'] == sell_points[3]]['time_ticks'].values[0]
                                        else:
                                            p_sel4_ticks = 0

                                        if p_sel4_ticks < p2_buy_stop_loss_RSI:
                                            if None not in sell_points:  ### Da qua inizia il after sale lol
                                                PS = ['circle-x', 'P1 SELL', 'circle-cross', 'P2 SELL','star-triangle-down', 'P3 SELL', 'star-diamond','P4 SELL REM & OPEN SHORT']
                                                candlestick_chart(df, symbs, [buy_base_points, sell_points], [PB, PS],times[c], number_of_c[c_ounter_n_candles],
                                                                  type_p='BUY-',extenstick=[[tick_after_RSI, df_filter_rsi['high'].iloc[0], "70 RSI","hexagram", 'black'],
                                                                                                 [tick_after_150, filter_df_150_ext['high'].iloc[0], "150% EXT SELL 1/2","diamond-wide", 'blue']])


                                                last_sell_pt = df_sell[df_sell['open time'] == sell_points[3]]['time_ticks'].values[0]
                                                df_after_p4_sell = df[df['open time'] > sell_points[3]]
                                                if alerts[symbs, tf][2] is None:
                                                    message_SELL_FOUND = "SELL PATTERN FOUND AFTER RSI THRESHOLD OF " + str(sell_pattern_rsi) + " ON " + symbs + ' ' + tf
                                                    send_Email(message_SELL_FOUND, email_receiver, SUBJECT='BUY -> 150%EXT -> RSI-THRESHOLD -> SELL')
                                                    alerts[symbs, tf][2] = message_SELL_FOUND

                                                if len(df_after_p4_sell) > 0:
                                                    # print("OPEND SHORT AFTER SELL, sono semplicemente nei i valori dopo di sell")
                                                    check_points_buy[symbs, tf][2] = 1000
                                                    df_stop_loss_p2_short = df_after_p4_sell[df_after_p4_sell['low'] > sell_points[5]]  # pt2 short stop loss al p2

                                                    if len(df_stop_loss_p2_short) > 0:
                                                        p2_short_stp_ponit = df_stop_loss_p2_short['time_ticks'].iloc[0]

                                                        candlestick_chart(df, symbs, [buy_base_points, sell_points],
                                                                          [PB, PS],times[c], number_of_c[c_ounter_n_candles],
                                                                          type_p='BUY STOP LOSS AT P2 SHORT AFTER SELL',
                                                                          extenstick=[[df_stop_loss_p2_short['time_ticks'].iloc[0],df_stop_loss_p2_short['low'].iloc[0],"STOP LOSS P2 SHORT", "circle-x",'darkorchid'],
                                                                              [tick_after_RSI,df_filter_rsi['high'].iloc[0], "70 RSI","hexagram", 'black'],
                                                                              [tick_after_150,filter_df_150_ext['high'].iloc[0],"150% EXT", "diamond-wide", 'blue']])

                                                        # print('Last Sell Pt', last_sell_pt, p4_l_sell_t)
                                                        Buy_notebook[symbs, tf] = [None, None, None, None, None, None,None, None]
                                                        start_time[symbs, tf][0] = p2_short_stp_ponit  # rinizio a cercare dall'ultimo  point
                                                        check_points_buy[symbs, tf] = [None, None, None]
                                                        alerts[symbs, tf]=[None,None,None, None]
                                                        message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf+ ' AT P2 AFTER SELL REMAINDER AND OPEN SHORT'
                                                        send_Email(message_stop_losses, email_receiver, SUBJECT='BUY -> 150% EXT -> RSI THRESHOLD -> SELL ->STOP LOSS')
                                                        buy_base_points = [None, None, None, None, None,
                                                                                      None, None, None]

                                                    else:
                                                        low_fib_extension_AFTS = float(sell_points[7]) - FIB_ext_SELL * (float(sell_points[5]) - float(sell_points[6]))
                                                        filter_df_50_ext_aft = df[df['time_ticks'] > last_sell_pt]
                                                        filter_df_50_ext_aft = filter_df_50_ext_aft[filter_df_50_ext_aft['low'] <= low_fib_extension_AFTS]

                                                        if len(filter_df_50_ext_aft) > 0:
                                                            tick_after_50_ext_aft= filter_df_50_ext_aft['time_ticks'].iloc[0]
                                                            df_stop_loss_fib_short = df[df['time_ticks'] > tick_after_50_ext_aft]  # pt7 short stop loss al p2
                                                            df_stop_loss_fib_short = df_stop_loss_fib_short[df_stop_loss_fib_short['high'] > sell_points[7]]  # pt7 short stop loss al p2

                                                            if len(df_stop_loss_fib_short) > 0:
                                                                p2_short_stop_fib_50 = df_stop_loss_fib_short['time_ticks'].iloc[0]
                                                                candlestick_chart(df, symbs, [buy_base_points, sell_points],
                                                                                  [PB, PS], times[c], number_of_c[c_ounter_n_candles],
                                                                                  type_p='BUY STOP LOSS AT P4 SHORT AFTER SELL',
                                                                                  extenstick=[
                                                                                      [df_stop_loss_fib_short['time_ticks'].iloc[0], df_stop_loss_fib_short['high'].iloc[0], "STOP LOSS P4 SHORT", "circle-x", 'darkorchid'],
                                                                                      [tick_after_RSI, df_filter_rsi['high'].iloc[0], "70 RSI", "hexagram", 'black'],
                                                                                      [tick_after_150, filter_df_150_ext['high'].iloc[0], "150% EXT", "diamond-wide", 'blue']])

                                                                # print('Last Sell Pt', last_sell_pt, p4_l_sell_t)
                                                                Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                                                                start_time[symbs, tf][0] = p2_short_stop_fib_50  # rinizio a cercare dall'ultimo  point
                                                                check_points_buy[symbs, tf] = [None, None, None]
                                                                alerts[symbs, tf] = [None, None, None, None]
                                                                buy_base_points = [None, None, None, None,
                                                                                              None, None, None, None]
                                                                message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf + ' AT P4 AFTER SELL REMAINDER AND OPEN SHORT'
                                                                send_Email(message_stop_losses, email_receiver, SUBJECT='BUY -> 150% EXT -> RSI THRESHOLD -> SELL -> 1th FIB-> STOP LOSS')
                                                            elif len(df_stop_loss_fib_short) <= 0:
                                                                low_150_extension_AFTS = float(sell_points[7]) - 1.5 * (float(sell_points[5]) - float(sell_points[6]))
                                                                filter_df_150_ext_short = df[df['time_ticks'] > int(last_sell_pt)]  # filtro tutti i valori sopra al 150% e dopo il sell point
                                                                filter_df_150_ext_short = filter_df_150_ext_short[filter_df_150_ext_short['low'] <= low_150_extension_AFTS]

                                                                if len(filter_df_150_ext_short) > 0:  # se effetivamente ci sono valori dopo il 150% dopo il buy pattern e il df non è solo 1 riga# si perte il real time

                                                                    tick_after_150_short = filter_df_150_ext_short['time_ticks'].iloc[0]

                                                                    candlestick_chart(df, symbs, [buy_base_points, sell_points], [PB, PS],
                                                                                      times[c], number_of_c[c_ounter_n_candles],
                                                                                      type_p='BUY-',
                                                                                      extenstick=[[tick_after_150_short, filter_df_150_ext_short['low'].iloc[0], "150% EXT SHORT", "diamond-cross", 'blue'],
                                                                                                  [tick_after_RSI, df_filter_rsi['high'].iloc[0], "70 RSI", "hexagram", 'black'],
                                                                                                  [tick_after_150, filter_df_150_ext['high'].iloc[0], "150% EXT", "diamond-wide", 'blue']])
                                                                    Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                                                                    start_time[symbs, tf][0] = tick_after_150_short  # rinizio a cercare dall'ultimo  point
                                                                    check_points_buy[symbs, tf] = [None, None, None]
                                                                    buy_base_points = [None, None, None,
                                                                                                  None, None, None,
                                                                                                  None, None]
                                                                    if alerts[symbs, tf][3] is None:
                                                                        message_SELL_CLOSE = "CLOSED THE OPEN SHORT OF PT4 SELL ON " + symbs + ' ' + tf
                                                                        send_Email(message_SELL_CLOSE, email_receiver, SUBJECT='BUY -> 150%EXT -> RSI-THRESHOLD -> SELL -> CLOSE-OPEN-SHORT')
                                                                        alerts[symbs, tf][3] = message_SELL_CLOSE

                                        # STOP LOSS RSI

                                        elif p_sel4_ticks > p2_buy_stop_loss_RSI:
                                            candlestick_chart(df, symbs, [buy_base_points], [PB],
                                                              times[c], number_of_c[c_ounter_n_candles],
                                                              type_p='BUY STOP_LOSS_70',
                                                              extenstick=[[df_stop_loss_RSI_p2['time_ticks'].iloc[0],
                                                                           df_stop_loss_RSI_p2['low'].iloc[0],
                                                                           "STOP LOSS AFTER 70 RSI",
                                                                           "circle-x", 'darkorchid'],
                                                                          [tick_after_RSI,
                                                                           df_filter_rsi['high'].iloc[0],
                                                                           "70 RSI",
                                                                           "hexagram", 'black'],
                                                                          [tick_after_150,
                                                                           filter_df_150_ext['high'].iloc[0],
                                                                           "150% EXT",
                                                                           "diamond-wide",
                                                                           'blue'],
                                                                          ])

                                            Buy_notebook[symbs, tf] = [None, None, None, None, None, None, None, None]
                                            check_points_buy[symbs, tf] = [None, None, None]
                                            alerts[symbs, tf] = [None, None, None, None]
                                            start_time[symbs, tf][0] = p2_buy_stop_loss_RSI
                                            buy_base_points = [None, None, None, None, None, None, None,
                                                                          None]
                                            message_stop_losses = "STOP LOSS ON " + symbs + ' ' + tf + ' AT P4 AFTER RSI SELL THRESHOLD'
                                            send_Email(message_stop_losses, email_receiver,SUBJECT='"BUY -> 150% EXT -> RSI THRESHOLD ->STOP LOSS"')






            if len(p_l_t_h.keys()) < (col_num - 1) and ((None not in buy_base_points) or (None not in sell_base_points)):  # solo una volta
                pp = symbs + tf
                message.append(pp)


            if len(p_l_t_h.keys()) > (col_num - 1):# cioè dopo che tutti i buy iniziali sono trovati entra ogni volta qua
                if p_l_t_h[symbs, tf] == [buy_base_points[0], buy_base_points[1],
                                          buy_base_points[2], buy_base_points[3]]:
                    print('nothing changed on buy')
                    pass
                else:
                    message = []
                    #pp = 'Something changed on ' + symbs + " " + tf+ " BUY CHARTS"
                    #message.append(pp)
                    #send_Email(message, email_receiver, SUBJECT="BUY PATTERN CHECK ALERT")
                    message = ''
            if len(p_l_t_s.keys()) > (col_num - 1):
                if p_l_t_s[symbs, tf] == [sell_base_points[0], sell_base_points[1],
                                          sell_base_points[2], sell_base_points[3]]:
                    print('Nothing changed on sell')
                    pass
                else:
                    message = []
                    #pp = 'Something changed on ' + symbs + " " + tf+ " SELL CHARTS"
                    #message.append(pp)
                    #send_Email(message, email_receiver, SUBJECT="SELL PATTERN CHECK ALERT")
                    message = ''

            p_l_t_h[symbs, tf] = [buy_base_points[0], buy_base_points[1],buy_base_points[2], buy_base_points[3]]
            p_l_t_s[symbs, tf] = [sell_base_points[0], sell_base_points[1], sell_base_points[2], sell_base_points[3]]
        c += 1
        c_ounter_n_candles += 1

    BUY_STCB=pd.DataFrame.from_dict(Buy_notebook)
    BUY_STCB.index=['P1 timestamp','P2 timestamp','P3 timestamp','P4 timestamp','P1 value','P2 value','P3 value','P4 value']
    OPSHT=pd.DataFrame.from_dict(Open_short_notebook)
    OPSHT.index=['P1 timestamp','P2 timestamp','P3 timestamp','P4 timestamp','P1 value','P2 value','P3 value','P4 value']
    print('\nBUY STOCK-BOARD\n\n',BUY_STCB)
    #print('\nCLOSE BUY',CLOSE_BUY)
    print('\n\n\nOPEN SHORT STOCK-BOARD\n\n',OPSHT)

    if message is not None:
        pass
        #message = '\n'.join([str(elem) for elem in message])
        #return message


file = open("Configuration.txt", "r")
contents = file.read()
configuration = ast.literal_eval(contents)
file.close()
n_box = 2

list_pp = configuration['FOREX SYMBS']
TOKEN = configuration['FOREX TOKEN']
dt = configuration['Query time in minutes']
lenght = configuration['Number of candles']
dt = (dt * 60)
email_adrs = configuration['Email address']
times = configuration['time frames']
buy_pattern_rsi=configuration['BUY RSI TRESHOLD']
sell_pattern_rsi=configuration['SELL RSI TRESHOLD']
RSI_PERIOD=configuration['RSI PERIOD']
SMA_PERIOD=configuration['SIMPLE MOVING AVG PERIOD']
FIB_ext_BUY=configuration['FIB EXT LEVEL BUY PATTERN']
FIB_ext_SELL=configuration['FIB EXT LEVEL SELL PATTERN']

starting_time=configuration["START DATE AND TIME"]
end_date_time=configuration["END DATE AND TIME"]


if starting_time!='auto':
    t = datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S')
    start_t = str(t.timestamp())
else:
    start_t=None


if end_date_time!='present':
    t = datetime.strptime(end_date_time, '%Y-%m-%d %H:%M:%S')
    end_date_time = str(t.timestamp())
else:
    end_date_time=None



times_dictionary={'1Minutes': 'M1',
                  '5Minutes':'M5',
                   '15Minutes':'M15',
                   '30Minutes':'M30',
                   '1Hour':'H1',
                   '2Hour':'H2',
                   '3Hour':'H3',
                   '4Hour':'H4',
                   '6Hour':'H6',
                   '8Hour':'H8',
                   '1Day':'D',
                   '1Week':'W',}

time_frames=[]
for i in times:
    time_frames.append(times_dictionary[i])



number_of_c = [lenght,lenght,lenght, lenght, lenght, lenght]

for tf in time_frames:
    for symbs in list_pp:
        Buy_notebook[symbs, tf]=[None,None,None,None,None,None,None,None]
        Open_short_notebook[symbs, tf]=[None,None,None,None,None,None,None,None]
        alerts[symbs, tf]= [None, None, None, None]
        check_points_buy[symbs,tf]=[None,None,None]
        check_points_sell[symbs,tf]=[None,None,None]
        if start_t is not None:
            start_time[symbs, tf] = [start_t]
        else:
            start_time[symbs, tf] = [None]





print('BINANCE STOCKS LIST: \n')
for i in list_pp:
    print(i)
print('\n\n')
initial_money=1000
email = "These are the stocks with the pattern: \n\n"

while 1:
    print("\n\nAnalyzing Stocks data:\n")
    binance_message = fxcm_stock(n_box=n_box,
                                    list_pp=list_pp,
                                    email_receiver=email_adrs,
                                    time_frames=time_frames,
                                    times=times,
                                    number_of_c=number_of_c)

    if binance_message is not '':
        pass
        #email += "\n\nBINANCE STOCKS:\n"
        #email += binance_message


    tot_msg = binance_message  # + alpaca_message
    # print(("tot---", tot_msg, "----tot"))

    if tot_msg is not '':
        pass
        #send_Email(email, email_adrs)

    #time.sleep(dt)

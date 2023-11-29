
import pandas as pd
import numpy as np
import csv
import os

def get_data( filename, start_date, end_date):

    df = pd.read_csv(filename)
    #df = pd.DataFrame(dpd).astype('float64')
    df['date'] = pd.to_datetime(df['periodStartUnix'], unit='s')
    df['Date'] = df['date']
    df.set_index('Date', inplace=True)
    df = df.loc[start_date:end_date]
    return df

def calculate_sma(df, short_len, long_len):
    # 策略計算
    short_ma = df['close'].rolling(short_len).mean()
    long_ma = df['close'].rolling(long_len).mean()
    df['short_ma'] = short_ma
    df['long_ma'] = long_ma
    return df
    

def my_strategy(df):
    df = calculate_sma(df, 20, 60)

    df['signal'] = 0

    # Long entry
    long_mask = df['short_ma'] > df['long_ma']
    df.loc[long_mask, 'signal'] = 1
    # Long exit
    longExit_mask = df['short_ma']<=df['long_ma']
    df.loc[longExit_mask, 'signal'] = -2
    # Short entry
    short_mask = df['short_ma']<=df['long_ma']
    df.loc[short_mask, 'signal'] = -1
    # Short exit
    shortExit_mask = df['short_ma'] > df['long_ma']
    df.loc[shortExit_mask, 'signal'] = 2
 
    # ST:設定停損停利
    df['stopLoss'] = 0.0
    df['takeProfit'] = 0.0
    df['open_nextbar'] = df['open'].shift(-1)  #for 下一根開盤價進場
    '''
    # Long entry
    df.loc[long_mask, 'stopLoss'] = None #df['open_nextbar'] - 5 #df['open_nextbar'] * 0.995
    df.loc[long_mask, 'takeProfit'] = None #df['open_nextbar'] + 20 #df['open_nextbar'] * 1.01
    # Short entry
    df.loc[short_mask, 'stopLoss'] = None #df['open_nextbar'] + 5 #df['open_nextbar'] * 1.005
    df.loc[short_mask, 'takeProfit'] = None #df['open_nextbar'] - 20 #df['open_nextbar'] * 0.99
    '''
    # Long entry
    df.loc[long_mask, 'stopLoss'] = df['open_nextbar'] * 0.995
    df.loc[long_mask, 'takeProfit'] = df['open_nextbar'] * 1.01
    # Short entry
    df.loc[short_mask, 'stopLoss'] = df['open_nextbar'] * 1.005
    df.loc[short_mask, 'takeProfit'] = df['open_nextbar'] * 0.99


    # LP:設定 LP 上限界
    df['lpMinPrice'] = 0.0
    df['lpMaxPrice'] = 0.0
    # Long entry
    df.loc[long_mask, 'lpMinPrice'] = df.loc[long_mask, 'stopLoss']
    df.loc[long_mask, 'lpMaxPrice'] = df.loc[long_mask, 'takeProfit']
    # Short entry
    df.loc[short_mask, 'lpMinPrice'] = df.loc[short_mask, 'takeProfit']
    df.loc[short_mask, 'lpMaxPrice'] = df.loc[short_mask, 'stopLoss']

    return df

def do_strategy(filename_in, filename_out, start_date, end_date):
    print(f"=== 策略訊號計算中 {filename_in}===\n")
    # 載入收盤歷史資料(candles)
    _candles = get_data( filename_in, start_date, end_date)

    # 策略訊號
    df = my_strategy(_candles)
    df_st_out = df[[ 'periodStartUnix', 'date', 'open','high','low','close','signal','stopLoss', 'takeProfit', 'lpMinPrice','lpMaxPrice']].copy()
    df_st_out.to_csv( filename_out, index=False)
    print(f"=== 策略訊號計算完成 {filename_out} ===\n")

def run_strategy():
    start_date = "2021-08-01"
    end_date   = "2023-07-31"

    filename_in  = ('./candles.csv')
    filename_out = ('./backtest_signal.csv')

    # 策略訊號
    do_strategy( filename_in, filename_out, start_date, end_date)

#run_strategy()

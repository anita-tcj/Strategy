import csv
import pandas as pd


def calculate_bb_b(df, length, mult):
    
    # 設定 天數(n),係數(K1,K2)
    n = 3
    K1 = 1.5
    K2 = 1.5

    # 策略計算
    hh = df["high"].rolling(n).max()
    hc = df["close"].rolling(n).max()
    lc = df["close"].rolling(n).min()
    ll = df["low"].rolling(n).min()
    df['hh'] = hh
    df['hc'] = hc
    df['lc'] = lc
    df['ll'] = ll
    df_count = pd.DataFrame()
    df_count['count1'] = df['hh']-df['lc']
    df_count['count2'] = df['hc']-df['ll']
    df['ran'] = df_count.max(axis=1)
    upper = df['open'] + df['ran']*K1
    lower = df['open'] - df['ran']*K2
    df['upper'] = upper
    df['lower'] = lower
    df['bbr'] = (df['close']-lower)/(upper-lower)
    return df

    

def my_strategy(df):
    df = calculate_bb_b(df, length=21, mult=2.0)

    df['signal'] = 0
    df['stopLoss'] = 0
    df['takeProfit'] = 0
    df['lpMinPrice'] = 0
    df['lpMaxPrice'] = 0

    # Buy signal (long entry)
    buy_mask = (df['close'] < df['upper']) & (df['signal'].shift(1) == 0)
    df.loc[buy_mask, 'signal'] = 1

    # Sell signal (long exit)
    sell_mask = (df['close'] >=  df['upper']) & (df['signal'].shift(1) == 1)
    df.loc[sell_mask, 'signal'] = -1

    # Sell signal (short entry)
    short_mask = (df['close'] > df['lower']) & (df['signal'].shift(1) == 0)
    df.loc[short_mask, 'signal'] = -1

    # Buy signal (short exit)
    cover_mask = (df['close'] <= df['lower']) & (df['signal'].shift(1) == -1)
    df.loc[cover_mask, 'signal'] = 1


    # 符合策略進場條件時 設定 signal = 1(進場訊號) 和 takeProfit(停利) stopLoss(停損) 
    # lpMaxPrice(流動池價格上限) lpMinPrice(流動池價格下限) 
   
    df.loc[buy_mask, 'signal'] = 1
    df.loc[buy_mask, 'stopLoss'] = df['close'] - (df['close'] * 0.09)
    df.loc[buy_mask, 'takeProfit'] = df['close'] * 1.01

    df.loc[buy_mask, 'lpMinPrice'] = df['close'] - 10
    df.loc[buy_mask, 'lpMaxPrice'] = df['close'] + 5

   
    df.loc[cover_mask, 'signal'] = 1
    df.loc[cover_mask, 'stopLoss'] = df['close'] 
    df.loc[cover_mask, 'takeProfit'] = df['close'] * 1.03
    
    df.loc[cover_mask, 'lpMinPrice'] = df['close'] - 30
    df.loc[cover_mask, 'lpMaxPrice'] = df['close'] + 10
    
    return df

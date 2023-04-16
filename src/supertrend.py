import ccxt
import schedule
import pandas as pd
import numpy as np
import json
from stringcolor import *

def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close', 'volume', 'timestamp'])

    heikin_ashi_df['volume'] = df['volume']
    heikin_ashi_df['timestamp'] = df['timestamp']
    
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2
        
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
    
    return heikin_ashi_df

def check_positions(exchange, coin):
    global in_position
    data = json.loads(json.dumps(exchange.fetch_positions([coin])[0]))
    if data["side"] == None:
        in_position = False
    elif data["side"] == "long":
        in_position = { "side": True , "amount": data["contracts"] }
    elif data["side"] == "short":
        in_position = { "side": False , "amount": data["contracts"] }
    else:
        in_position = False
    return in_position

def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def supertrend(df, periods=12, multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    tr1 = abs(df['high'] - df['low'])
    tr2 = abs(df['high'] - hl2.shift())
    tr3 = abs(df['low'] - hl2.shift())
    tr = tr1.combine(tr2, max).combine(tr3, max)
    atr = tr.rolling(window=periods).mean().fillna(0)
    up = hl2 - multiplier * atr
    dn = hl2 + multiplier * atr
    trend = pd.Series(0, index=df.index)
    trend[0] = 1 if df['close'][0] > up[0] else -1
    for i in range(1, len(df)):
        if df['close'][i] > up[i-1]:
            trend[i] = "uptrend"
            up[i] = max(up[i], up[i-1])
            atr[i] = atr[i-1]
        else:
            trend[i] = "downtrend"
            dn[i] = min(dn[i], dn[i-1])
            atr[i] = atr[i-1]
    df['trend'] = trend
    return df

def check_buy_sell_signals(df, exchange, coin):
    print(cs("Checking for buy and sell signals", "orange"))
    pos = check_positions(exchange, coin)
    print(df.tail(5))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if df['trend'][previous_row_index] == "downtrend" and df['trend'][last_row_index] == "uptrend":
        print(cs("Changed to uptrend, checking to buy", "red").bold())
        if not in_position:
            exchange.create_market_buy_order('BTC/USDT', 0.001)
            print(cs(f"Bought 0.001 {coin}", "red"))
            check_positions()
        elif in_position.side == False:
            exchange.create_market_buy_order('BTC/USDT', in_position.amount+0.001)
            print(cs(f"Bought {in_position.amount+0.001} {coin} (Closed {in_position.amount} short position)", "red"))
            check_positions()
        elif in_position.side == True:
            print(cs("You are already in position, nothing to buy", "red"))
        
    
    elif df['trend'][previous_row_index] == "uptrend" and df['trend'][last_row_index] == "downtrend":
        print(cs("Changed to downtrend, checking to sell.", "red").bold())
        if not in_position:
            exchange.create_market_sell_order('BTC/USDT', 0.001)
            print(cs(f"Sold 0.001 {coin}", "red"))
            check_positions()
        elif in_position.side == True:
            exchange.create_market_sell_order('BTC/USDT', in_position.amount+0.001)
            print(cs(f"Sold {in_position.amount+0.001} {coin} (Closed {in_position.amount} long position)", "red"))
            check_positions()
        elif in_position.side == False:
            print(cs("You are already in position, nothing to sell", "red"))
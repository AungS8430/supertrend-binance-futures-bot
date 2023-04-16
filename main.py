import ccxt
import data.config as config
import datetime
from src.supertrend import *
import pandas as pd
import sys
from stringcolor import * 
sys.path.insert(0, 'path/to/your/directory')
coins = open("data/coins.txt", "r").read().splitlines()

pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

exchange = ccxt.binance ({
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': { 'defaultType': 'future' },
})

exchange.setSandboxMode(True)

def run_bot():
    for coin in coins:
        print(cs(f"Fetching new bars for {datetime.now().isoformat()} {coin}", "yellow").bold())
        bars = exchange.fetch_ohlcv(coin, timeframe='4h', limit=100)
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = heikin_ashi(df)
        supertrend_data = supertrend(df)
        check_positions(exchange, coin)
        check_buy_sell_signals(supertrend_data, exchange, coin)

print("                   ,.=ctE55ttt553tzs.,                    \n",
          "              ,,c5;z==!!::::  .::7:==it3>.,               \n",
          "           ,xC;z!::::::    ::::::::::::!=c33x,            \n",
          "         ,czz!:::::  ::;;..===:..:::   ::::!ct3.          \n",
          "       ,C;/.:: :  ;=c!:::::::::::::::..      !tt3.        \n",
          "      /z/.:   :;z!:::::J  :E3.  E:::::::..     !ct3.      \n",
          "    ,E;F   ::;t::::::::J  :E3.  E::.     ::.     \ztL     \n",
          "   ;E7.    :c::::F******   **.  *==c;..    ::     Jttk    \n",
          "  .EJ.    ;::::::L                    \:.   ::.    Jttl   \n",
          "  [:.    :::::::::773.    JE773zs.     I:. ::::.    It3L  \n",
          " ;:[     L:::::::::::L    |t::!::J     |::::::::    :Et3  \n",
          " [:L    !::::::::::::L    |t::;z2F    .Et:::.:::.  ::[13  \n",
          " E:.    !::::::::::::L               =Et::::::::!  ::|13  \n",
          " E:.    (::::::::::::L    .......       \:::::::!  ::|i3  \n",
          " [:L    !::::      ::L    |3t::::!3.     ]::::::.  ::[13  \n",
          " !:(     .:::::    ::L    |t::::::3L     |:::::; ::::EE3  \n",
          "  E3.    :::::::::;z5.    Jz;;;z=F.     :E:::::.::::II3[  \n",
          "  Jt1.    :::::::[                    ;z5::::;.::::;3t3   \n",
          "   \z1.::::::::::l......   ..   ;.=ct5::::::/.::::;Et3L   \n",
          "    \z3.:::::::::::::::J  :E3.  Et::::::::;!:::::;5E3L    \n",
          "     \cz\.:::::::::::::J   E3.  E:::::::z!     ;Zz37`     \n",
          "       \z3.       ::;:::::::::::::::;='      ./355F       \n",
          "         \z3x.         ::~======='         ,c253F         \n",
          "           \ z3=.                      ..c5t32^           \n",
          "              =zz3==...          ...=t3z13P^              \n",
          "                   `*=zjzczIIII3zzztE3>*^`                \n")

print(bold("Welcome to SuperTrend Bot!"), "Please choose an option: ", "1. Start Trading", "2. Scan for Symbols")
choice = input("Enter your choice: ")

if choice == "1":
    print(cs("Starting Trading Bot...", "green"))
    schedule.every(10).seconds.do(run_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)

elif choice == "2":
    print(cs("Scanning for symbols...", "green"))
    symbols = exchange.load_markets()
    print(symbols)

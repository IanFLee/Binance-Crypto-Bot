# -*- coding: utf-8 -*-
"""
@author: Ian Lee

ianforrestlee@gmail.com
https://github.com/IanFLee

"""

import plotly
import winsound
import plotly.graph_objects as go

import plotly.io as pio


from pandas import DataFrame
from ta.utils import dropna
from ta.volume import *
from ta.trend import *
from ta.momentum import *
from ta.volatility import *



pio.renderers.default='svg'


import datetime
from time import sleep

from binance.client import Client
from binance.exceptions import *

##############################################################################

# TO RUN THIS PROGRAM, YOU MUST PLUG IN YOUR API KEY AND SECRET BELOW

api_keys = {
                "key" : 'abc',
                "secret" : 'xyz'
            }
        
api_key = api_keys['key']
api_secret = api_keys['secret']

client = Client(api_key, api_secret, tld='us')
def get_klines(coin, interval, date_range):
    try:
        klines = client.get_historical_klines(coin, interval, date_range)
        
        candles = []        
        if len(klines) > 1:
            for kline in klines:
                date = kline[0]
                x = int(date)
                y = datetime.datetime.fromtimestamp(x / 1e3)
                z = y.isoformat()
                candle = { 'open':float(kline[1]), 'high':float(kline[2]), 'low':float(kline[3]),
                          'close':float(kline[4]), 'volume':float(kline[5]), 'datetime':z }
                candles.append(candle)
        return candles
    except:
        err('there was an error getting binance klines')

##############################################################################

def err(*args):
    print('THERE WAS A SYSTEM ERROR:')
    output = ''
    for arg in args:
        if type(arg) != str:
            arg = str(arg)
        output += arg
    print(output)
    sfx('error')

##############################################################################

def io(*args):
    output = ''
    for arg in args:
        if type(arg) != str:
            arg = str(arg)
        output += arg
    print(output)

##############################################################################

def getPercentChange(from_a, to_b):
    if from_a == 0 or to_b == 0:
        err('one arg of getpercent change is a zero value')
    else:
        return ((float(to_b) / float(from_a)) * 100) - 100
    
##############################################################################

def sfx(sound_type):
    if sound_type == 'big earn':
        winsound.PlaySound('sfx/sell big earn sound.wav', winsound.SND_FILENAME)
    if sound_type == 'earn':
        winsound.PlaySound('sfx/sell earn sound.wav', winsound.SND_FILENAME)
    if sound_type == 'lose':
        winsound.PlaySound('sfx/sell lose sound 2.wav', winsound.SND_FILENAME)
    if sound_type == 'buy':
        winsound.PlaySound('sfx/buy sound.wav', winsound.SND_FILENAME)
    if sound_type == 'startup':
        winsound.PlaySound('sfx/startup sound.wav', winsound.SND_FILENAME)
    if sound_type == 'update':
        winsound.PlaySound('sfx/update sound 5.wav', winsound.SND_FILENAME)
    if sound_type == 'error':
        winsound.PlaySound('sfx/error sound.wav', winsound.SND_FILENAME)

##############################################################################

fig = go.Figure()

def do_plot(x, y_list, traces):
    global fig
    fig.data = []
    
    colors = ['orange', 'blue', 'yellow', 'purple', 'black']
    c=-1
    for y in y_list:
        
        c += 1
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                fillcolor=colors[c],
                name=traces[c]
            ))

    fig.show()
    sleep(0.2)

##############################################################################

class coinBot:

    def __init__(self, coin, interval):
        self.coin = coin
        self.interval = interval
        self.balance = 100
        self.quantity = -7
        self.holding_coin = False
        self.buy_position = -7
        self.confidence = -7
        self.bullish = False
        self.bottom = False
        self.bearish = False
        self.dataset = []
        self.receipt_name = "crypto_trade_history.txt"

        self.get_candles()
        

    
    def get_candles(self):
        candles = get_klines(self.coin, self.interval, "1 month ago UTC")
        df = DataFrame(candles, columns=['open', 'high', 'low', 'close', 'volume', 'datetime']) 
        # Clean NaN values
        df = dropna(df)
        
        """
        USE THESE TO ATTACH DIFFERENT INDICATORS

        # Initialize Indicators
        mfi_short = MFIIndicator(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=3)
        mfi_long = MFIIndicator(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=12)
        bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        atr = AverageTrueRange(close=df['close'], high=df['high'], low=df['low'], window=3)
        stoch = StochasticOscillator(close)
        mavgcd = MACD(close=df["close"], window_fast=12, window_slow=26, window_sign=9)
        vwap = VolumeWeightedAveragePrice(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=18)

        # Add Features
        df['mfi short'] = mfi_short.money_flow_index()
        df['mfi long'] = mfi_long.money_flow_index()
        df['macd'] = mavgcd.macd()
        df['stoch'] = stochastic.stoch()
        df['vwap'] = vwap.volume_weighted_average_price()
        df['atr'] = atr.average_true_range()
        
        df['bbm'] = bb.bollinger_mavg()
        df['bbh'] = bb.bollinger_hband()
        df['bbl'] = bb.bollinger_lband() 
        """

        mfi = MFIIndicator(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=3)
        stochRSI = StochRSIIndicator(close=df['close'], window=14)
        
        df['mfi'] = mfi.money_flow_index()
        # STOCH VAL IS * BY 100 BECAUSE THE VALUES COME NORMALIZED BETWEEN 0 & 1
        # WE WANT THEM NORMALIZED BETWEEN 0 & 100
        df['stoch'] = stochRSI.stochrsi() * 100

        candles_dict = df.to_dict('records')
        self.dataset = candles_dict


      
    def plot_coin(self):
        
        dates = []
        close_line = []

        mfi = []
        stoch = []

        candles = self.dataset

        for i in range(100):
            dates.append(candles[i]['datetime'])
            close_line.append(candles[i]['close'])
            mfi.append(candles[i]['mfi'])
            stoch.append(candles[i]['stoch'])

        do_plot(dates, [close_line], ['price'])
        do_plot(dates, [stoch, mfi], ['stoch', 'mfi'])
  
   
     
    def signal_check(self):
        
        io('-----')
        io(self.coin)

        candles = self.dataset
        # CANDLES LOAD BY DEFAULT FROM PAST -> PRESENT
        # REVERSE THEM TO VIEW THEM FROM PRESENT -> PAST
        candles.reverse()
        
        current = float(candles[0]['close'])
        mfi = candles[0]['mfi']
        stoch = candles[0]['stoch']

        io(candles[0]['datetime'])
        io()
        io('current USD value is $', current)
        
        # this strategy tests to see if the MFI has sharply jumped
        # from 0 to 100 in four periods or less
        if self.holding_coin == False:
            if mfi > 99:
                for i in range(1, 4):
                    if candles[i]['mfi'] < 1:
                        sfx('buy')
                        self.buy_position = current
                        self.holding_coin = True
                        self.bottom = False
                        self.print_receipt('buy', -7, -7, self.buy_position)
                        break

            
        io('this mfi is '+str(mfi))
        io('prev mfi was '+str(candles[1]['mfi']))
        io('third mfi was '+str(candles[2]['mfi']))
        io('4th mfi was '+str(candles[3]['mfi']))
 

            
        if self.holding_coin == True:
            io('holding coin currently')
            io('bought at '+str(self.buy_position))
            
            # if we stand to make or lose 1% of our investment, sell the coin
            if current > self.buy_position * 1.01 or current < self.buy_position * 0.91:
                self.print_receipt('sell', -7, -7, current)
                self.bottom = False
                self.holding_coin = False
                self.buy_position = -7
                if current > self.buy_position:
                    sfx('big earn')
                elif current < self.buy_position:
                    sfx('lose')

        io()
        io('mfi = '+ str(mfi))
        io('stoch = '+ str(stoch))
        io()
        
        self.plot_coin()
        
 
    def run(self):
        
        # run for a week (10 min * 6, or 1 hour; 1 hr * 24 or 1 day; 1 day * 7 or 1 week)
        for i in range(6 * 24 * 7):
            self.get_candles()
            self.signal_check()
            self.plot_coin()
            # if holding coin, refresh every minute
            if self.holding_coin == True:
                for i in range(10):
                    self.get_candles()
                    self.signal_check()
                    self.plot_coin()
                    sleep(60)
            else:
                # if not holding coin, refresh every 10 minutes
                sleep(600)
     
    def print_receipt(self, order_type, qty, usd_val, price):
        # Open function to open the file "MyFile1.txt" 
        # (same directory) in append mode and
        receipt = open(self.receipt_name,"a")
        percent_script = ''
        current = self.dataset[0]['close']
        now = datetime.datetime.now()
        current_time = now.strftime("%m/%d %H:%M")
        
        if order_type == 'sell':
            percent_change = getPercentChange(self.buy_position, current)
            percent_script = 'and a percentage change of ' + str(percent_change - 0.002)
        L = [
            """

-----
""" + str(current_time) + """
""" + str(self.coin) + """
""" + str(order_type) + """ order
of """ + str(qty) + """ coins
at a price of """ + str(price) + """
for a total USD value of $""" + str(usd_val) + """
""" + percent_script + """
-----

            """]
        receipt.writelines(L)   
     

    def print_msg(self, msg):
        receipt = open(self.receipt_name,"a")
        now = datetime.datetime.now()
        current_time = now.strftime("%d:%m:%y: %H:%M:%S")
        
        L = [
            str(current_time) + 
            """
            """
            + str(msg) +
            """
            """
            ]
        
        receipt.writelines(L)
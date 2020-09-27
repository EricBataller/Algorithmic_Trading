# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:09:21 2020

@author: Eric
"""

# =============================================================================
# Import OHLCV data and calculate MACD technical indicator
# =============================================================================

'''
MACD is a technical momentum-follower indicator widely used. 

1. Calculate a fast and a slow moving average (tipically 12 and 26 period). Normally exponential MA is used.
2. Substract the slow from the fast = MACD line
3. Calculate the moving average of the MACD line also known as Signal line (tipically 9 period) 
4. When de MACD line cuts the signal line from below = bullish period, cuts the signal from above = bearish period

Cons: Many false positives (especially during sideways markets). It's a lagging indicator.

- People use it in conjunction with another indicator.
'''

# Import necesary libraries
import pandas_datareader.data as pdr
import datetime
import matplotlib.pyplot as plt

# Download historical data for required stocks
ticker = "MSFT"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(1825),datetime.date.today())

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy() #Copy because i don't wanna make any change in the original DF
    df["MA_Fast"]=df["Adj Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Adj Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True) #Delete the NaN rows
    return df

# Visualization - plotting MACD/signal along with close price and volume for last 100 data points
df = MACD(ohlcv, 12, 26, 9)

plt.subplot(311)
plt.plot(df.iloc[-100:,4])
plt.title('MSFT Stock Price')
plt.xticks([])

plt.subplot(312)
plt.bar(df.iloc[-100:,5].index, df.iloc[-100:,5].values)
plt.title('Volume')
plt.xticks([])

plt.subplot(313)
plt.plot(df.iloc[-100:,[-2,-1]])
plt.title('MACD')
plt.legend(('MACD','Signal'),loc='lower right')

plt.show()






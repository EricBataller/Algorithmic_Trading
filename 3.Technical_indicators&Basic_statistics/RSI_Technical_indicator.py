# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 20:42:58 2020

@author: Eric
"""

# =============================================================================
# Import OHLCV data and calculate Relative Strength Index technical indicators
# =============================================================================

'''
RSI is a momentum oscillator which measures the speed and change of price movements.

RSI conveys is the strenght of a price value of a stock at a given moment compared to
its previous stock prices. Its value oscillates between 0 and 100 with values above 70
indicating that the asset is overbought. If value is below 30 it signifies oversold, and
then a pull back is expected. Underdeveloped markets like india for example have tipical 
values of 20-80 instead.

Problem is that even we can see a stock at 80, oftentimes that overbought position persists
in time. More often than not though, it does predict pretty accurately.

Calculation follows a two step method wherein the second step acts as a smoothening 
technique (similar to calculating exponential MA).
'''


# Import necesary libraries
import pandas as pd
import pandas_datareader.data as pdr
import numpy as np
import datetime


# Download historical data for required stocks
ticker = "AAPL"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(364),datetime.date.today())

def RSI(DF,n): #n is the number of periods we are calculating the RSI with
    "function to calculate RSI"
    df = DF.copy()
    df['delta']=df['Adj Close'] - df['Adj Close'].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0) #np.where is an if condition (first element in parenthesis). If true, the 2nd element is taken as a result, if false, the 3rd
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n]) #The n element of the list will be a regular moving average based on n first elements 
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100/(1+df['RS']))
    return df['RSI']

RSI(ohlcv, 14)

# Calculating RSI without using loop
def rsi(df, n):
    "function to calculate RSI"
    delta = df["Adj Close"].diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[n-1]] = np.mean( u[:n] ) #first value is sum of avg gains
    u = u.drop(u.index[:(n-1)])
    d[d.index[n-1]] = np.mean( d[:n] ) #first value is sum of avg losses
    d = d.drop(d.index[:(n-1)])
    rs = pd.stats.moments.ewma(u, com=n-1, adjust=False) / \
         pd.stats.moments.ewma(d, com=n-1, adjust=False)
    return 100 - 100 / (1 + rs)
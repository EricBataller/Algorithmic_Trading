# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 16:11:10 2020

@author: Eric
"""

# =============================================================================
# Import OHLCV data and calculate Average True Range and Bollinger Band
# =============================================================================

'''
These are volatility based indicators.

BB is when you encompass a simple moving average line (tipically period=20) with two lines (one is a simple standard div above the MA line, and
the other one is a standard div below the MA line of tipically 2). The bands widen during periods of increased volatility and shrinks during periods of reduced
volatility. Usually traders use it when there is a squeeze on the bands, indicating that things might get interesting in the future.

ATR is not based on the std of the prices, all it does is that is looks at 3 ragnes. One is the difference between high-low, then there is the 
difference between high-previous desclous, and low-previous disclouse. Then we take the average of these. It approches the volatility from a range
perspective. Focused on total price movement and conveys how wildly the market is swinging as it moves.

When shrinking or going down in case of the ATR, volatility is going down and traders use it as a possible indicator that a break out or trend will
start to form.
'''


# Import necesary libraries
import pandas_datareader.data as pdr
import datetime

# Download historical data for required stocks
ticker = "MSFT"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(1825),datetime.date.today())


def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1)) #Shift(1) to substract the adj close of the previous day
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False) #True range (some people take the average of the 3 as the true range)
    df['ATR'] = df['TR'].rolling(n).mean() #n is the amount of periods we are rolling averaging to get the points of the plot (tipically 20) 
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

ATR(ohlcv, 20)

def BollBnd(DF,n):
    "function to calculate Bollinger Band"
    df = DF.copy()
    df["MA"] = df['Adj Close'].rolling(n).mean()
    df["BB_up"] = df["MA"] + 2*df["MA"].rolling(n).std()
    df["BB_dn"] = df["MA"] - 2*df["MA"].rolling(n).std()
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df

# Visualizing Bollinger Band of the stocks for last 100 data points
BollBnd(ohlcv,20).iloc[-100:,[-4,-3,-2]].plot(title="Bollinger Band")


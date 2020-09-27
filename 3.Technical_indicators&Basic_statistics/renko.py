# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 18:57:30 2020

@author: Eric
"""
# =============================================================================
# Import OHLCV data and transform it to Renko
# =============================================================================

'''
Renko chart is built using price movement and not price against standarized
time intervals - This filters out the noise and lets you visualize the true trend. Renko charts filter 
out noise and help traders to more clearly see the trend, since all movements that are smaller than the 
box size are filtered out.

Price movements (fixed) are represented as bricks stacked at 45 degrees to each other. A new
brick is added to the chart only when the price moves by a pre determined amount in either direction.

While a fixed box size is common, ATR is also used. ATR is a measure of volatility, and therefore it 
fluctuates over time. Renko charts based on ATR will use the fluctuating ATR value as the box size.

Rencko charts have a time axis, but the time scale is not fixed. Some bricks may take longer to form 
than others, depending on how long it takes the price to move the required box size.

Renko charts typically use only the closing price based on the chart time frame chosen.

'''

# Import necesary libraries
import pandas_datareader.data as pdr
import datetime
from stocktrends import Renko

# Download historical data for required stocks
ticker = "AAPL"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(364),datetime.date.today())

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def renko_DF(DF):
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,6,5]]
    df.columns = ["date","open","high","low","close","volume"]
    df2 = Renko(df)
    df2.brick_size = round(ATR(DF,120)["ATR"][-1],0) #We just want the last number of the column. We use ATR as the brick size in here but it can also be fix. 
    df2.chart_type = Renko.PERIOD_CLOSE #Renko box calcuation based on periodic close
    #df2.chart_type = Renko.PRICE_MOVEMENT #Renko box calcuation based on price movement
    renko_df = df2.get_ohlc_data() #Adds a column to df called "uptrend" with boolean values depending on whether the ranko chart goes up or down
    return renko_df

result = renko_DF(ohlcv)


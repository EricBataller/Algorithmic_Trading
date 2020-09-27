# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 20:32:41 2020

@author: Eric

Import intraday OHLCV data using alphavantage. Most of services to get intraday data are paid 
"""
#First go to www.alphavantage.co and get an API key

#ALphaVantage is not in python but thankfully, someone has coded a wrapper for python: https://github.com/RomelTorres/alpha_vantage


# importing libraries
from alpha_vantage.timeseries import TimeSeries
import pandas as pd


all_tickers = ["AAPL","MSFT","CSCO","AMZN"]
key_path = "C:\\Users\\Eric\\Desktop\\Algorithmic_Tradin&Quantitative_Analysis_Python\\1.Getting_data\\alphavantage_key.txt"

ts = TimeSeries(key=open(key_path,'r').read(), output_format='pandas') #Initiate a TimeSeries data object with format pandas
data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')[0] #Notice this returns a list of [data,metadata]. We just want the data
data.columns = ["open","high","low","close","volume"]

# extracting stock data (historical close price) for the stocks identified
close_prices = pd.DataFrame()
cp_tickers = all_tickers
attempt = 0
drop = []
while len(cp_tickers) != 0 and attempt <=5:
    print("-----------------")
    print("attempt number ",attempt)
    print("-----------------")
    cp_tickers = [j for j in cp_tickers if j not in drop]
    for i in range(len(cp_tickers)):
        try:
            ts = TimeSeries(key=open(key_path,'r').read(), output_format='pandas')
            data = ts.get_intraday(symbol=cp_tickers[i],interval='1min', outputsize='full')[0]
            data.columns = ["open","high","low","close","volume"]
            close_prices[cp_tickers[i]] = data["close"]
            drop.append(cp_tickers[i])       
        except:
            print(cp_tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1
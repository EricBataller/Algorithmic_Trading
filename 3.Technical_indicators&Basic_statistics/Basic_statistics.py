# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 20:43:33 2020

@author: Eric
"""

# =============================================================================
# Import OHLCV data and perform basic data operations
# Author : Mayank Rasu

# Please report bug/issues in the Q&A section
# =============================================================================

# Import necesary libraries
import pandas as pd
import pandas_datareader.data as pdr
import datetime

# Download historical data for required stocks
tickers = ["MSFT","AMZN","AAPL","CSCO","IBM","FB"]

close_prices = pd.DataFrame() # dataframe to store close price of each ticker
attempt = 0 # initializing passthrough variable
drop = [] # initializing list to store tickers whose close price was successfully extracted
while len(tickers) != 0 and attempt <= 5:
    tickers = [j for j in tickers if j not in drop] # removing stocks whose data has been extracted from the ticker list
    for i in range(len(tickers)):
        try:
            temp = pdr.get_data_yahoo(tickers[i],datetime.date.today()-datetime.timedelta(3650),datetime.date.today())
            temp.dropna(inplace = True)
            close_prices[tickers[i]] = temp["Adj Close"]
            drop.append(tickers[i])       
        except:
            print(tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1
    
# Handling NaN Values
close_prices.fillna(method='bfill',axis=0,inplace=True) # Replaces NaN values with the next valid value along the column
close_prices.dropna(axis=0,inplace=True) # Deletes any row where NaN value exists

# Mean, Median, Standard Deviation, daily return
close_prices.mean() # prints mean stock price for each stock
close_prices.median() # prints median stock price for each stock
close_prices.std() # prints standard deviation of stock price for each stock

daily_return = close_prices.pct_change() # Creates dataframe with daily return for each stock (percentage change over subsequent day)
daily_return2 = (close_prices/close_prices.shift(1))-1 #Another way to calculate the same

daily_return.mean() # prints mean daily return for each stock
daily_return.std() # prints standard deviation of daily returns for each stock

# Rolling mean and standard deviation
daily_return.rolling(window=20, min_periods= 18).mean() # simple moving average of the last 20 days. The command does the average as long as there are at least 18 values
daily_return.rolling(window=20).std()

daily_return.ewm(span=20,min_periods=20).mean() # exponential moving average (for the most recent data we'll assign a higher weight). Good for time moving data since the latest data has more prediction power
daily_return.ewm(span=20,min_periods=20).std()

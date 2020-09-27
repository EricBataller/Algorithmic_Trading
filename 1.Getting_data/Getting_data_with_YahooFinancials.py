# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 17:04:19 2020

@author: Eric

Importing OHLCV (open-high-low-close-volume) data using YahooFinancials
"""


import pandas as pd
from yahoofinancials import YahooFinancials
import datetime

all_tickers = ["AAPL","MSFT","CSCO","AMZN","INTC"]

# extracting stock data (historical close price) for the stocks identified
close_prices = pd.DataFrame()
end_date = (datetime.date.today()).strftime('%Y-%m-%d')
beg_date = (datetime.date.today()-datetime.timedelta(1825)).strftime('%Y-%m-%d')
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
            yahoo_financials = YahooFinancials(cp_tickers[i]) #Initiate an object YahooFinance(<Company ticker>)
            json_obj = yahoo_financials.get_historical_price_data(beg_date,end_date,"daily") #Returns a json object (dictionary) with all the data
            ohlv = json_obj[cp_tickers[i]]['prices']  #We just want the prices of all that data. Still, each element in the list ohlv is a dictionary with the values: value, open, low, high,...
            temp = pd.DataFrame(ohlv)[["formatted_date","adjclose"]] #with pandas you can directly restructure a list of dictionaries into a dataframe made of the elements you want
            temp.set_index("formatted_date",inplace=True) #set formatted_data to be the indexes of the dataframe
            temp = temp[~temp.index.duplicated(keep='first')] #For some reason, some of the elements of ohlv are the dividends/payouts prices. These are dictionaries of 5 elements and one of them are Formatted_date. We therefore have some duplicated indexes that have no prices associated. We need to get rid of the second duplicates. This would return a list of booleans where those second duplicates have a true, but since we put the ~ we get the opposite . 
            #Update: In the last version of YahooFinancials I thinkt the problem explained in the line above has been fixed
            close_prices[cp_tickers[i]] = temp["adjclose"]
            drop.append(cp_tickers[i])       
        except:
            print(cp_tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1
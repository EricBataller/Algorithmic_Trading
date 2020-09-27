# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:07:50 2020

@author: Eric
"""

# =============================================================================
# Backtesting strategy - II : Intraday resistance breakout strategy
# =============================================================================

'''
Resistance breakout is a technical trading term which means that the price of the
stock has breached a presumed resistance level (determined by the price chart).

Chose high volume, high activity stocks for this strategy (pre market movers,
historically high volume stock etc.)

Define breakout rule - I will be using price breaching 20 period rolling max/min
price in conjunction volume breaching rolling max volume - go long/short stocks
based on the signals.

Define exit/stop loss signal - I will be using previous price plus/minus 20 period
ATR as the rolling stop loss price.

Backtest the strategy by calculating comulative return for each stock.
'''


import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries #Tipically used for free intradate data
import copy


def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2['ATR']

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78) #252 (days) * 78 (5 minute periods)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr
    

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

# Download historical data (monthly) for selected stocks

tickers = ["MSFT","AAPL","FB","AMZN","INTC", "CSCO","VZ","IBM","QCOM","LYFT"] #Most active/traded tech companies

ohlc_intraday = {} # directory with ohlc value for each stock    
key_path = "C:\\Users\\Eric\\Desktop\\Algorithmic_Tradin&Quantitative_Analysis_Python\\1.Getting_data\\alphavantage_key.txt"
ts = TimeSeries(key=open(key_path,'r').read(), output_format='pandas')

attempt = 0 # initializing passthrough variable
drop = [] # initializing list to store tickers whose close price was successfully extracted
while len(tickers) != 0 and attempt <=5:
    tickers = [j for j in tickers if j not in drop]
    for i in range(len(tickers)):
        try:
            ohlc_ticki = ts.get_intraday(symbol=tickers[i],interval='5min', outputsize='full')[0]
            ohlc_intraday[tickers[i]] = ohlc_ticki.iloc[::-1,:] ##Alpha vantage puts the latest data in the top, that's why I invert it
            ohlc_intraday[tickers[i]].columns = ["Open","High","Low","Adj Close","Volume"]
            drop.append(tickers[i])      
        except:
            print(tickers[i]," :failed to fetch data...retrying")
            continue
    attempt+=1

 
tickers = ohlc_intraday.keys() # redefine tickers variable after removing any tickers with corrupted data

################################Backtesting####################################

# calculating ATR and rolling max price for each stock and consolidating this info by stock in a separate dataframe
ohlc_dict = copy.deepcopy(ohlc_intraday)
tickers_signal = {} #Here we'll put the buy and sell signals at every moment
tickers_ret = {}
for ticker in tickers: #For every ticker apart from ohlc i calculate whatever other values i need for my backtesting and populate them into the df
    print("calculating ATR and rolling max price for ",ticker)
    ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker],20)
    ohlc_dict[ticker]["roll_max_cp"] = ohlc_dict[ticker]["High"].rolling(20).max()
    ohlc_dict[ticker]["roll_min_cp"] = ohlc_dict[ticker]["Low"].rolling(20).min()
    ohlc_dict[ticker]["roll_max_vol"] = ohlc_dict[ticker]["Volume"].rolling(20).max()
    ohlc_dict[ticker].dropna(inplace=True)
    tickers_signal[ticker] = "" #fill ticker in tickers_signal with a blank
    tickers_ret[ticker] = [] #fill ticker in tickers_ret with a blank list


# identifying signals and calculating daily return (stop loss factored in)
for ticker in tickers:
    print("calculating returns for ",ticker)
    for i in range(len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "": #If tickers in tickers_signal is blank it means we exited during the last period and its time to see if we are going to buy or sell in the next one 
            tickers_ret[ticker].append(0) #If there is no signal, then for that particular period the return will be 0
            if ohlc_dict[ticker]["High"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
                ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]: #If the high is greater than the resistance and volume is grater than 1.5 times the highest volume, go long ("buy").
                tickers_signal[ticker] = "Buy"
            elif ohlc_dict[ticker]["Low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
                ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]: #If the low is lower than the support  and greatly traded in volume, go short ("sell")
                tickers_signal[ticker] = "Sell"
        
        elif tickers_signal[ticker] == "Buy": #If the signal is buy you can either exit the call ("") or reverse the order and go short ("sell")
            if ohlc_dict[ticker]["Adj Close"][i]<ohlc_dict[ticker]["Adj Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]: #If the value goes down passed the ATR, exit.
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Adj Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Adj Close"][i-1])-1) #assuming that the stop loss works, the negative return per stock will be (ADJ_CLOSEprev-ATR)-ADJ_CLOSEprev 
            elif ohlc_dict[ticker]["Low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
                ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]: #If the value has gone down passed the ATR and besides it fullfils the condition to go short, exit and go short
                tickers_signal[ticker] = "Sell"
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Adj Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Adj Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Adj Close"][i]/ohlc_dict[ticker]["Adj Close"][i-1])-1) #If it hasn't gone down passed the ATR, the return of this period will be ADJ_CLOSE-ADJ_CLOSEprev
                
        elif tickers_signal[ticker] == "Sell":
            if ohlc_dict[ticker]["Adj Close"][i]>ohlc_dict[ticker]["Adj Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]:
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append((ohlc_dict[ticker]["Adj Close"][i-1]/(ohlc_dict[ticker]["Adj Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]))-1)
            elif ohlc_dict[ticker]["High"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
               ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                tickers_signal[ticker] = "Buy"
                tickers_ret[ticker].append((ohlc_dict[ticker]["Adj Close"][i-1]/(ohlc_dict[ticker]["Adj Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]))-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Adj Close"][i-1]/ohlc_dict[ticker]["Adj Close"][i])-1)
                
    ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker]) #Attach the return of the tickers fully populated to the DF


# calculating overall strategy's KPIs
strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlc_dict[ticker]["ret"] #Create a df with the return columns of the stocks in my portfolio
strategy_df["ret"] = strategy_df.mean(axis=1) #This column represents the total return if we had one stock of each kind

'''
Bear in mind we haven't had in consideration the borkerage cost of intraday trading and the slippage which is essential in a strategy such as this one.
'''

# vizualization of strategy return
(1+strategy_df["ret"]).cumprod().plot()

#Using the KPI for this kind of strategies doesn't make much sense specially without considering the signigicant intraday trading costs.
CAGR(strategy_df)
sharpe(strategy_df,0.025)
max_dd(strategy_df)  


#calculating individual stock's KPIs
cagr = {}
sharpe_ratios = {}
max_drawdown = {}
for ticker in tickers:
    print("calculating KPIs for ",ticker)      
    cagr[ticker] =  CAGR(ohlc_dict[ticker])
    sharpe_ratios[ticker] =  sharpe(ohlc_dict[ticker],0.025)
    max_drawdown[ticker] =  max_dd(ohlc_dict[ticker])

KPI_df = pd.DataFrame([cagr,sharpe_ratios,max_drawdown],index= ["Return","Sharpe Ratio","Max Drawdown"])      
KPI_df.T



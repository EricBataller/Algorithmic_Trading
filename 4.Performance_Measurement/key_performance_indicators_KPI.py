# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 20:15:25 2020

@author: Eric
"""

# =============================================================================
# Measuring the performance of a buy and hold strategy
# =============================================================================

# Import necesary libraries
import pandas_datareader.data as pdr
import numpy as np
import datetime

# Download historical data for required stocks
ticker = "^GSPC"
SnP = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(1825),datetime.date.today())


def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["daily_ret"] = DF["Adj Close"].pct_change()
    df["cum_return"] = (1 + df["daily_ret"]).cumprod()
    n = len(df)/252 #252 is the number of trading days in a typical year
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR


def volatility(DF): #Using the std on the return as a measure of risk is very common. However, this approach assumes normal distribution of returns which is not true. Therefore it does not capture tail risk.
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    df["daily_ret"] = DF["Adj Close"].pct_change()
    vol = df["daily_ret"].std() * np.sqrt(252) #Annualized volatility. Multiply by np.sqrt(52) in case u want weekly and np.sqrt(12) for monthly.
    return vol

def sharpe(DF,rf): #"Risk weighted return". Excess of return per unit of risk. Excess returns are the return earned by a stock (or portfolio of stocks) and the risk free rate, which is usually estimated using the most recent short-term government treasury bill.
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr #Sharpe >1 is good, >2 is very good, >3 is excellent.
    
def sortino(DF,rf): #variation of sharpe ratio which takes into account std of only negative returns. One of the criticisms of Sharpe is that it fails to distinguish between upside and downside fluctuations.
    "function to calculate sortino ratio ; rf is the risk free rate"
    df = DF.copy()
    df["daily_ret"] = DF["Adj Close"].pct_change()
    neg_vol = df[df["daily_ret"]<0]["daily_ret"].std() * np.sqrt(252)
    sr = (CAGR(df) - rf)/neg_vol
    return sr

def max_dd(DF): #Largest percentage drop in asset price over a specified time period (distance between peak and trough in the line curve of the asset). Investments with longer backtesting period will likely have larger max drawdown and therefore caution must be applied in comparing across strategies.
    "function to calculate max drawdown"
    df = DF.copy()
    df["daily_ret"] = DF["Adj Close"].pct_change()
    df["cum_return"] = (1 + df["daily_ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax() #Rolling maximum of the cum_return. It generates a column where every element is the maximum cumulative return as of that point.
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"] #Evolution of drawdown
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"] #Evol of drawdown in percentages
    max_dd = df["drawdown_pct"].max() #The maximum drawdown in percentage value
    return max_dd
    
def calmar(DF): #Calmar Ratio is the ratio of CAGR and Max drawdown and it's a measure of risk adjusted return
    "function to calculate calmar ratio"
    df = DF.copy()
    clmr = CAGR(df)/max_dd(df)
    return clmr

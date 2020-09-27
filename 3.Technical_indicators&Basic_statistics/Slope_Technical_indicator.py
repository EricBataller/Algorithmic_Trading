# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 17:28:11 2020

@author: Eric
"""

# =============================================================================
# Calculate slope of n successive points on a time series
# =============================================================================

'''
Slope is a function that returns a list of computed slopes IN DEGREES of every n successive 
points on a time series by using Ordinary Least Squares (OLS) regression method.

'''

# Import necesary libraries
import pandas_datareader.data as pdr
import numpy as np
import datetime
import statsmodels.api as sm

# Download historical data for required stocks
ticker = "AAPL"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(364),datetime.date.today())



def slope(ser,n): # use (DF,n) in case u wanna work with dataframe instead of a np series directly
    #n = number of consecutive points that you want to find the slope for
    "function to calculate the slope of n consecutive points on a plot"
    #ser = Df["column"] #In case u wanna work with dataframe
    slopes = [i*0 for i in range(n-1)] #First n-1 slopes will be 0 since we need n numbers to compute the slope
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled) #Add a constant so that we are fitting the regression of a y=ax + b line instead of y=ax
        model = sm.OLS(y_scaled,x_scaled) 
        results = model.fit()
        #results.summary() 
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes)))) #convert slopes into degrees
    return np.array(slope_angle)

slope(ohlcv["Adj Close"],5) 
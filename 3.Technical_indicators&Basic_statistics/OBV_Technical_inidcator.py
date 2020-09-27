# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 14:10:51 2020

@author: Eric
"""

# =============================================================================
# Import OHLCV data and calculate OBV technical indicator
# =============================================================================

'''
OBV is a momentum indicator which uses changes in trading volume as an indicator
of future asset prices.

OBV formulation is based on the theory that volume precedes price movement. A rising
OBV reflects a positive volume pressure that can lead to higher prices and falling 
OBV predicts decline in prices.

Leading market indicator but prone to making false signals. Typically used in conjunction 
with lagging indicators such as MACD.

The calculation of OBS is fairly straightforward and it is simply the cumulative sum of volume
traded adjussted for the direction of the corresponding asset price move.

OBVcurr = OBVprev + VOLcurr*H(VOLcurr-VOLprev) - VOLcurr*H(VOLprev-VOLcurr) Where H(x) is the Heaviside function
'''

# Import necesary libraries
import pandas_datareader.data as pdr
import numpy as np
import datetime

# Download historical data for required stocks
ticker = "AAPL"
ohlcv = pdr.get_data_yahoo(ticker,datetime.date.today()-datetime.timedelta(364),datetime.date.today())

def OBV(DF):
    """function to calculate On Balance Volume"""
    df = DF.copy()
    df['daily_ret'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily_ret']>=0,1,-1) #First number in the column will be a NaN and therefore it'll return a -1
    df['direction'][0] = 0 #Assign a 0 to first element instead of the -1
    df['vol_adj'] = df['Volume'] * df['direction']
    df['obv'] = df['vol_adj'].cumsum()
    return df['obv']

OBV(ohlcv)









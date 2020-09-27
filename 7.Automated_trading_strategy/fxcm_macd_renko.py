# -*- coding: utf-8 -*-
"""
@author: Eric Bataller
"""

import fxcmpy
import numpy as np
from stocktrends import Renko
import statsmodels.api as sm
import time
import copy

#----------Initiating API connection and defining trade parameters--------------
token_path = 'C:\\Users\\Eric\\Desktop\\Algorithmic_Tradin&Quantitative_Analysis_Python\\7.Automated_trading_strategy\\FXCM_API_token.txt'
con = fxcmpy.fxcmpy(access_token = open(token_path,'r').read(), log_level = 'error', server = 'demo')

#------------------------Defining strategy parameters----------------------------
pairs = ['EUR/USD','GBP/USD','USD/CHF','AUD/USD','USD/CAD'] #currency pairs to be included in the strategy
pos_size = 10 #max capital allocated/position size for any currency pair


def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2


def slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def renko_DF(DF):
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date","open","high","low","close","volume"]
    df2 = Renko(df)
    df2.brick_size = max(0.5,round(ATR(DF,120)["ATR"][-1],0))
    df2.chart_type = Renko.PERIOD_CLOSE 
    renko_df = df2.get_ohlc_data() 
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    return renko_df

def renko_merge(DF):
      "functin to merge renko df with original ohlc df (mainly to overlap the date axis)"
      df = copy.deepcopy(DF)
      renko = renko_DF(DF)
      df['date'] = df.index
      df.reset_index(drop=True, inplace = True)
      merged_df = df.merge(renko.loc[:,["date","bar_num"]],how='outer',on ='date')
      merged_df["macd"]= MACD(merged_df,12,26,0)[0]
      merged_df["macd_sig"]= MACD(merged_df,12,26,0)[1]
      merged_df["macd_slope"]= slope(merged_df["macd"],5)
      merged_df["macd_sig_slope"]= slope(merged_df["macd_sig"],5)
      return merged_df

def trade_signal(MERGED_DF,l_s): #l_s is a variable that will have the info about weather at the moment we hace a long or short position
      "function to generate signal"
      signal = ""
      df = copy.deepcopy(MERGED_DF)
      if l_s == "":
          if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
              signal = "Buy"
          elif df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
              signal = "Sell"
  
      elif l_s == "long":
          if df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
              signal = "Close_Sell"
          elif df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
              signal = "Close"
          
      elif l_s == "short":
          if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
              signal = "Close_Buy"
          elif df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
              signal = "Close"
      return signal

def main():
      try:
            open_pos = con.get_open_positions()
            for currency in pairs:
                  long_short = ""
                  if len(open_pos)>0:
                        open_pos_cur = open_pos[open_pos["currency"] == currency]
                        if len(open_pos_cur)>0:
                              if open_pos_cur["isBuy"].tolist()[0]==True:
                                    long_short = "long"
                              elif open_pos_cur["isBuy"].tolist()[0]==False:
                                    long_short = "short"
                  data = con.get_candles(currency, period='m5',number=250)
                  ohlc = data.iloc[:,[0,1,2,3,8]]
                  ohlc.columns = ["Open","Close","High","Low","Volume"]
                  signal = trade_signal(renko_merge(ohlc), long_short)
                  
                  if signal == "Buy":
                        con.open_trade(symbol=currency, is_buy=True, is_in_pips=True, amount=pos_size,
                                       time_in_force='GTC', stop=-8, trailing_step=True, order_type='AtMarket')
                        print("New long position initiated for ", currency)
                  if signal == "Sell":
                        con.open_trade(symbol=currency, is_buy=False, is_in_pips=True, amount=pos_size,
                                       time_in_force='GTC', stop=-8, trailing_step=True, order_type='AtMarket')
                        print("New short position initiated for ", currency)
                  if signal == "Close":
                        con.close_all_for_symbol(currency)
                        print("All positions closed for", currency)
                  if signal == "Close_Buy":
                        con.close_all_for_symbol(currency)
                        print("Existing short positions closed for", currency)
                        con.open_trade(symbol=currency, is_buy=True, is_in_pips=True, amount=pos_size,
                                       time_in_force='GTC', stop=-8, trailing_step=True, order_type='AtMarket')
                        print("New long position initiated for ", currency)
                  if signal == "Close_Sell":
                        con.close_all_for_symbol(currency)
                        print("Existing long positions closed for", currency)
                        con.open_trade(symbol=currency, is_buy=False, is_in_pips=True, amount=pos_size,
                                       time_in_force='GTC', stop=-8, trailing_step=True, order_type='AtMarket')
                        print("New short position initiated for ", currency)
              
      except:
            print("error encountered...skipping this iteration")

#----------------------Continuaous execution-------------------------
starttime = time.time() #returns the exact time in system time representation
timeout = time.time() + 60*60*1 # 60 seconds *60 min = 1 hour
while time.time() <= timeout:
      try:
            print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            main()
            time.sleep(300- ((time.time()-starttime) % 300.0)) #300 sec = 5min*60 sec
      except KeyboardInterrupt:
            print("\n\nKeyboard exception recived. Exiting.")
            break
            
#----------------------Close all positions and exit--------------------
for currency in pairs:
      print("Closing all positions for ",currency)
      con.close_all_for_symbol(currency)
con.close()
        
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
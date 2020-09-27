# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 13:59:28 2020

@author: Eric
"""

# ============================================================================
#How to use FXCM RESTful API to open and close trading positions in the market
# ============================================================================


import fxcmpy
import time

#initiating API connection and defining trade parameters
token_path = 'C:\\Users\\Eric\\Desktop\\Algorithmic_Tradin&Quantitative_Analysis_Python\\7.Automated_trading_strategy\\FXCM_API_token.txt'
con = fxcmpy.fxcmpy(access_token = open(token_path,'r').read(), log_level = 'error', server = 'demo')

pair = 'EUR/USD' #This is the pair we are gonna trade

#get historical data
data = con.get_candles(pair, period = 'm5', number = 250) #5 min period
""" periods can be m1, m5 ,m15 and m30, H1, H2, H3, H4, H5 and H8, D1, W1, M1"""

#streaming data
""" for streaming data, we first need to "subscribe" to a currency pair"""
con.subscribe_market_data('EUR/USD')
#2 ways of doing it:
con.get_last_price('EUD/USD') #Gives you the las price (meaning: Bid, Ask, High, Low, Name(date), dtype)
con.get_prices('EUR/USD') # Gives you a df with the series of last few prices 

con.unsubscribe_market_data('EUR/USD')

#To actually use those commands to stream data, we use time:
starttime = time.time() #returns the exact time in system time representation
timeout = time.time() + 60*0.2 #for 12 seconds 
while time.time() <= timeout:
      print(con.get_last_price('EUD/USD')[0]) #print just the bid price

#Trading account data
con.get_account().T  #Might be useful for example to keep fetching the dayPL (profit/loss) info in order to stop the trading session sometime

con.get_open_positions().T #tells you all the open positions you have and their info
con.get_open_position_summary()# just gives you the summary of all opened positions and gives you info like the grossPL
con.get_closed_positions()  # Gives you info about the close positions
con.get_orders()#Gives you info about all the orders that might not be excecuted but you have ordered already

#orders
con.create_market_buy_order('EUR/USD',10)
con.create_market_buy_order('USD/CAD',10)
con.create_market_sell_order('USD/CAD',10)
con.create_market_sell_order('EUR/USD',10) #Notice we are opening off-setting positions that essentially close the previous ones... FXCM doesn't want us to do that, They want us to close the trades

order = con.open_trade(symbol='USD/CAD', is_buy = True,
                       is_in_pips=False, amount=10, #number of lots
                       time_in_force ='GTC', stop =1.28,
                       trailing_step = True, order_type='AtMarket',
                       limit= 1.45) #This way of placing an order allows you to put stoploss, etc.

con.close_trade(trade_id = tradeId, amount=1000) #trade_id can be found in the info of the order when pulling get_open_position() for example (that's why its a pain in the ass to close the positions and sometimes you just off-set them)
con.close_all_for_symbol('EUR/USD')

#closing connection
con.close()  
 



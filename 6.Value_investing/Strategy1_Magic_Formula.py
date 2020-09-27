# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 17:41:14 2020

@author: Eric Bataller
"""

# ============================================================================
# Greenblatt's Magic Formula Implementation
# Author - Mayank Rasu

# Please report bugs/issues in the Q&A section
# =============================================================================

'''
Inestment philosophy published in 2006 bestseller 'The little book that beats
the market'. Investment approach centered around indentifying "wonderful stocks"
at "bargain price".

"Wonderful stock" quantified by the metric Return on Invested Capital (ROIC)
which measures bang-for-buck on actual capital employed. Excludes excess
cash and interest-bearing assets to focus only on assets actually used in the
business to generate the return.

"Bargain price" is quantified by Earning Yield which is the ratio of EBIT to
Enterprise Value (Like P/E ratio but capital structure independent).

Earning Yield = EBIT/Enterprise Value
ROIC = EBIT/(Net Fixed Assets + Net Working Capital)

Magic Formula = Rank(Rank(Earning Yield) + Rank(ROIC))

Invest in the top 20-30 companies (excluding finance, Insurance companies and utilities),
accumulating 2-3 positions per month over a 12-month period. Re-balance the portfolio
once a year.
'''

import re
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

url_financials = 'https://finance.yahoo.com/quote/{}/financials?p={}'
url_stat = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'

tickers = ["AXP","AAPL"]#,"BA","CAT","CVX","CSCO","DIS","DOW", "XOM",
           #"HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
           #"NKE","PFE","PG","TRV","UTX","UNH","VZ","V","WMT","WBA"]

#list of tickers whose financial data needs to be extracted
financial_dir = {}

for ticker in tickers:
    try:
          
      temp_dir = {} #To put the statements and the key-stats
      
      response = requests.get(url_financials.format(ticker, ticker)) #Fill the 1rst and 2nd {} in url_financials with ticker
      soup = BeautifulSoup(response.text, 'html.parser')
      
      '''
      Going into the source code of the website at some point when you scroll down the code you'll notice
      what it seems to be json format strings. What's happening is that the website is dinamically loading this data 
      from this java functions contained within the script tag. Fortunately for us there is a comment that is properly
      commented as /*--Data--*/. This will contain all the data that's dinamically uploaded onto the page. Now, because
      this data is embbeded in a java script function, what we actually have to do is get the script tag first, then 
      extract the content, chop the edges off so that what we're left with is just the json formatted stream which we can convert
      into a python dictionary.
      
      '''
      pattern = re.compile(r'\s--\sData\s--\s')#Since there is nothing really unique about the script that identifies it as a tag, We'll have to use a text pattern with regular expressions
      script_data = soup.find('script', text=pattern).contents[0]#Use this pattern to find the script element that has text that matches this pattern, return the content (this returns as a list so we'll have to take the first (and only) element of it)
      
      #We have to get rid of the java script code wrapping the code we actually want 
      #Since the bounderies of the json string we want is '...root.App.main = {"context":{"dispatcher":...' at the front end and '..."td-app-finance"}}}};\n}(this));\n' at the back end
      #We can use the word 'context' and the fact at the back end the string starts around 12 elements from the end
      start = script_data.find("context")-2
      final = -12
      json_data = json.loads(script_data[start:final]) #dictionary with all the data
      
      annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory'][0] #[0] because we just want the last year
      annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements'][0]
      annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements'][0]
      statements_data = {**annual_is,**annual_cf, **annual_bs} #Using ** is a shortcut that allows you to pass multiple arguments to a function directly using a dictionary. It can be used aswell to put all the dicts into one
 
      #Each statement contains a list of dictionaries of all the accounting in a variaty of formats as you can see printing the following:     
      #Let's consolidate the annual data so we have it just in raw accounting format
      for key, val in statements_data.items():
            try:
                  temp_dir[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue

      #Repeat the process for the Key-Statistics part       
      response = requests.get(url_stat.format(ticker, ticker)) #Fill the 1rst and 2nd {} in url_financials with ticker
      soup = BeautifulSoup(response.text, 'html.parser')
      script_data = soup.find('script', text=pattern).contents[0]#Use this pattern to find the script element that has text that matches this pattern, return the content (this returns as a list so we'll have to take the first (and only) element of it)
      start = script_data.find("context")-2
      final = -12
      json_data2 = json.loads(script_data[start:final]) #dictionary with all the data
        
      def_key_stats = json_data2['context']['dispatcher']['stores']['QuoteSummaryStore']['defaultKeyStatistics']
      financial_data = json_data2['context']['dispatcher']['stores']['QuoteSummaryStore']['financialData']
      price_data = json_data2['context']['dispatcher']['stores']['QuoteSummaryStore']['price']
      summary_data = json_data2['context']['dispatcher']['stores']['QuoteSummaryStore']['summaryDetail']
      key_stats = {**def_key_stats,**financial_data,**price_data,**summary_data} 
      
      for key, val in key_stats.items():
            try:
                  temp_dir[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue

      
      financial_dir[ticker] = temp_dir    
    except:
      print("Problem scraping data for ",ticker)

#storing information in pandas dataframe
combined_financials = pd.DataFrame(financial_dir)
combined_financials.dropna(how='all',axis=1,inplace=True) #dropping columns with all NaN values
tickers = combined_financials.columns #updating the tickers list based on only those tickers whose values were successfully extracted
combined_financials.sort_index(inplace=True)

# creating dataframe with relevant financial information for each stock using fundamental data
stats = ["ebitda",
         "depreciation",
         "marketCap",
         "netIncomeApplicableToCommonShares",
         "totalCashFromOperatingActivities",
         "capitalExpenditures",
         "totalCurrentAssets",
         "totalCurrentLiabilities",
         "propertyPlantEquipment",
         "totalStockholderEquity",
         "longTermDebt",
         "dividendYield"] # change as required

indx = ["EBITDA","D&A","MarketCap","NetIncome","CashFlowOps","Capex","CurrAsset",
        "CurrLiab","PPE","BookValue","TotDebt","DivYield"]
all_stats = {}
for ticker in tickers:
    try:
        temp = combined_financials[ticker]
        ticker_stats = []
        for stat in stats:
            ticker_stats.append(temp.loc[stat])
        all_stats['{}'.format(ticker)] = ticker_stats
    except:
        print("can't read data for ",ticker)

all_stats_df = pd.DataFrame(all_stats,index=indx)

# calculating relevant financial metrics for each stock
transpose_df = all_stats_df.transpose()
final_stats_df = pd.DataFrame()
final_stats_df["EBIT"] = transpose_df["EBITDA"] - transpose_df["D&A"]
final_stats_df["TEV"] =  transpose_df["MarketCap"].fillna(0) \
                         +transpose_df["TotDebt"].fillna(0) \
                         -(transpose_df["CurrAsset"].fillna(0)-transpose_df["CurrLiab"].fillna(0)) #CurrAss-CurrLiab is aprox. cash (but the real value is also in the json_data in case you wanna be precise)
final_stats_df["EarningYield"] =  final_stats_df["EBIT"]/final_stats_df["TEV"]
final_stats_df["FCFYield"] = (transpose_df["CashFlowOps"]-transpose_df["Capex"])/transpose_df["MarketCap"]
final_stats_df["ROC"]  = (transpose_df["EBITDA"] - transpose_df["D&A"])/(transpose_df["PPE"]+transpose_df["CurrAsset"]-transpose_df["CurrLiab"])
final_stats_df["BookToMkt"] = transpose_df["BookValue"]/transpose_df["MarketCap"]
final_stats_df["DivYield"] = transpose_df["DivYield"]


################################Output Dataframes##############################

# finding value stocks based on Magic Formula
final_stats_val_df = final_stats_df.loc[tickers,:]
final_stats_val_df["CombRank"] = final_stats_val_df["EarningYield"].rank(ascending=False,na_option='bottom')+final_stats_val_df["ROC"].rank(ascending=False,na_option='bottom')
final_stats_val_df["MagicFormulaRank"] = final_stats_val_df["CombRank"].rank(method='first')
value_stocks = final_stats_val_df.sort_values("MagicFormulaRank").iloc[:,[2,4,8]]
print("------------------------------------------------")
print("Value stocks based on Greenblatt's Magic Formula")
print(value_stocks)


# finding highest dividend yield stocks
high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:,6]
print("------------------------------------------------")
print("Highest dividend paying stocks")
print(high_dividend_stocks)


# # Magic Formula & Dividend yield combined
final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False,method='first') \
                              +final_stats_df["ROC"].rank(ascending=False,method='first')  \
                              +final_stats_df["DivYield"].rank(ascending=False,method='first')
final_stats_df["CombinedRank"] = final_stats_df["CombRank"].rank(method='first')
value_high_div_stocks = final_stats_df.sort_values("CombinedRank").iloc[:,[2,4,6,8]]
print("------------------------------------------------")
print("Magic Formula and Dividend Yield combined")
print(value_high_div_stocks)






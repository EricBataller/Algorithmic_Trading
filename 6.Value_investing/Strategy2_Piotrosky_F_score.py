# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 23:34:26 2020

@author: Eric Bataller
"""

# ============================================================================
# Piotroski f score implementation (data scraped from yahoo finance)
# =============================================================================

'''
Piotrosky F-Score is a number between 0-9 which is used to assess strength of company's financial position (9 being the best). 

Scores are assigned for various parameters based on the below criteria

Profitability criteria:
      - Positive return on assets in the current year (1 point)
      - Positive operating cash flow in the current year (1 point)
      - Return on assets higher in current year compared to previous year (1 point)
      - Cash flow from operations divided by total assets greater than ROA in current year (A.K.A. Accruals)(1 point)
Leverage, Liquidity and Source of Funds Criteria:
      - Lower ratio of long term debt in the current period, compared to the previous year (decreased leverage) (1 point)
      - Higher current ratio this year compared to the previous year (more liquidity) (1 point)
      - No new shares were issued in the last year (lack of dilution) (1 point)
Operating Efficiency criteria:
      - A higher gross margin (gross profit/revenue) compared to the previous year (1 point)
      - A higher asset turnover ratio (revenue/average total assets) compared to the previous year (1 point)
      
Pick stocks with score 8-9 and rebalance every 6 months or 1 year. Best results observed in mid cap and small cap stocks.
'''

import re
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd


url_financials = 'https://finance.yahoo.com/quote/{}/financials?p={}'
url_stat = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'

tickers = ["AXP","AAPL","BA","CAT","CVX","CSCO","DIS","DOW", "XOM",
           "HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
           "NKE","PFE","PG","TRV","UTX","UNH","VZ","V","WMT","WBA"]

financial_dir_cy = {} #directory to store current year's information
financial_dir_py = {} #directory to store last year's information
financial_dir_py2 = {} #directory to store last to last year's information


for ticker in tickers:
    try:
      temp_dir, temp_dir2, temp_dir3  = {},{},{}
      
      response = requests.get(url_financials.format(ticker, ticker)) #Fill the 1rst and 2nd {} in url_financials with ticker
      soup = BeautifulSoup(response.text, 'html.parser')
      pattern = re.compile(r'\s--\sData\s--\s')#Since there is nothing really unique about the script that identifies it as a tag, We'll have to use a text pattern with regular expressions
      script_data = soup.find('script', text=pattern).contents[0]#Use this pattern to find the script element that has text that matches this pattern, return the content (this returns as a list so we'll have to take the first (and only) element of it)
      
      #We have to get rid of the java script code wrapping the code we actually want 
      start = script_data.find("context")-2
      final = -12
      json_data = json.loads(script_data[start:final]) #dictionary with all the data
      
      annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory'] 
      annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
      annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
      statements_data_cy = {**annual_is[0],**annual_cf[0], **annual_bs[0]} #Using ** is a shortcut that allows you to pass multiple arguments to a function directly using a dictionary. It can be used aswell to put all the dicts into one
      statements_data_py = {**annual_is[1],**annual_cf[1], **annual_bs[1]} 
      statements_data_py2 = {**annual_is[2],**annual_cf[2], **annual_bs[2]} 
      
      #Each statement contains a list of dictionaries of all the accounting in a variaty of formats as you can see printing the following:     
      #Let's consolidate the annual data so we have it just in raw accounting format
      for key, val in statements_data_cy.items():
            try:
                  temp_dir[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue
      for key, val in statements_data_py.items():
            try:
                  temp_dir2[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue
      for key, val in statements_data_py2.items():
            try:
                  temp_dir3[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue
      
      financial_dir_cy[ticker] = temp_dir
      financial_dir_py[ticker] = temp_dir2 
      financial_dir_py2[ticker] = temp_dir3
    except:
      print("Problem scraping data for ",ticker)

#storing information in pandas dataframe
combined_financials_cy = pd.DataFrame(financial_dir_cy)
combined_financials_cy.dropna(axis=1,how='all',inplace=True) #dropping columns with all NaN values
combined_financials_py = pd.DataFrame(financial_dir_py)
combined_financials_py.dropna(axis=1,how='all',inplace=True)
combined_financials_py2 = pd.DataFrame(financial_dir_py2)
combined_financials_py2.dropna(axis=1,how='all',inplace=True)
combined_financials_cy.sort_index(inplace=True)
combined_financials_py.sort_index(inplace=True)
combined_financials_py2.sort_index(inplace=True)
tickers = combined_financials_cy.columns #updating the tickers list based on only those tickers whose values were successfully extracted


# selecting relevant financial information for each stock using fundamental data

stats = ["netIncomeApplicableToCommonShares",
         "totalAssets",
         "totalCashFromOperatingActivities",
         "longTermDebt",
         "deferredLongTermLiab",
         "totalCurrentLiabilities",
         "totalCurrentAssets",
         "commonStock",
         "totalRevenue",
         "grossProfit"]


indx = ["NetIncome","TotAssets","CashFlowOps","LTDebt","OtherLTDebt",
        "CurrLiab","CurrAssets","CommStock","TotRevenue","GrossProfit"]


def info_filter(df,stats,indx):
    """function to filter relevant financial information for each 
       stock and transforming string inputs to numeric"""
    tickers = list(df.columns.values)
    all_stats = {}
    for ticker in tickers:
        try:
            temp = df[ticker]
            ticker_stats = []
            for stat in stats:
                ticker_stats.append(temp.loc[stat])
            all_stats['{}'.format(ticker)] = ticker_stats
        except:
            print("can't read data for ",ticker)
    
    all_stats_df = pd.DataFrame(all_stats,index=indx)
    return all_stats_df

def piotroski_f(df_cy,df_py,df_py2):
    """function to calculate f score of each stock and output information as dataframe"""
    f_score = {}
    tickers = df_cy.columns
    for ticker in tickers:
        ROA_FS = int(df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2) > 0)
        CFO_FS = int(df_cy.loc["CashFlowOps",ticker] > 0)
        ROA_D_FS = int(df_cy.loc["NetIncome",ticker]/(df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2 > df_py.loc["NetIncome",ticker]/(df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2)
        CFO_ROA_FS = int(df_cy.loc["CashFlowOps",ticker]/df_cy.loc["TotAssets",ticker] > df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2))
        LTD_FS = int((df_cy.loc["LTDebt",ticker] + df_cy.loc["OtherLTDebt",ticker])<(df_py.loc["LTDebt",ticker] + df_py.loc["OtherLTDebt",ticker]))
        CR_FS = int((df_cy.loc["CurrAssets",ticker]/df_cy.loc["CurrLiab",ticker])>(df_py.loc["CurrAssets",ticker]/df_py.loc["CurrLiab",ticker]))
        DILUTION_FS = int(df_cy.loc["CommStock",ticker] <= df_py.loc["CommStock",ticker])
        GM_FS = int((df_cy.loc["GrossProfit",ticker]/df_cy.loc["TotRevenue",ticker])>(df_py.loc["GrossProfit",ticker]/df_py.loc["TotRevenue",ticker]))
        ATO_FS = int(df_cy.loc["TotRevenue",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2)>df_py.loc["TotRevenue",ticker]/((df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2))
        f_score[ticker] = [ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df = pd.DataFrame(f_score,index=["PosROA","PosCFO","ROAChange","Accruals","Leverage","Liquidity","Dilution","GM","ATO"])
    return f_score_df

# Selecting stocks with highest Piotroski f score
transformed_df_cy = info_filter(combined_financials_cy,stats,indx)
transformed_df_py = info_filter(combined_financials_py,stats,indx)
transformed_df_py2 = info_filter(combined_financials_py2,stats,indx)

f_score_df = piotroski_f(transformed_df_cy,transformed_df_py,transformed_df_py2)
print(f_score_df.sum().sort_values(ascending=False))




























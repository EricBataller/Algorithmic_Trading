# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:09:10 2020

@author: Eric
"""

"""
Following the procedure seen in https://www.youtube.com/watch?v=fw4gK-leExw
"""

import re
import json
import requests
from bs4 import BeautifulSoup

url_financials = 'https://finance.yahoo.com/quote/{}/financials?p={}'
url_stat = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'

tickers = ["AAPL","MSFT"] #list of tickers whose financial data needs to be extracted
financial_dir = {} #I prefer using dictionary instead of lists but you could also use lists. Importing a dic to a pandas df is really easy

for ticker in tickers:
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
      
      #The data for the finantial statements is located in:
      json_data['context']['dispatcher']['stores']['QuoteSummaryStore'].keys() 
      
      annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory']
      annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
      annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
        
      quarter_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistoryQuarterly']['incomeStatementHistory']
      quarter_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistoryQuarterly']['cashflowStatements']
      quarter_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistoryQuarterly']['balanceSheetStatements']
        
      #every one of the previous dictionaries contain a list of statements each one for every of the last 4 years
      #Each statement contains a list of dictionaries of all the accounting in a variaty of formats as you can see printing the following:
      #print(annual_is[0]['operatingIncome'])
      
      #Let's consolidate the annual data so we have it just in raw accounting format
      annual_is_stmts = []
      for s in annual_is:
            statement = {}
            for key, val in s.items():
                  try:
                        statement[key]= val['raw']
                  except TypeError:
                        continue
                  except KeyError:
                        continue
            annual_is_stmts.append(statement)
      temp_dir['IncomeStatement'] = annual_is_stmts
      
      annual_cf_stmts = []
      for s in annual_cf:
            statement = {}
            for key, val in s.items():
                  try:
                        statement[key]= val['raw']
                  except TypeError:
                        continue
                  except KeyError:
                        continue
            annual_cf_stmts.append(statement)
      temp_dir['CashflowStatement'] = annual_cf_stmts
      
      annual_bs_stmts = []
      for s in annual_bs:
            statement = {}
            for key, val in s.items():
                  try:
                        statement[key]= val['raw']
                  except TypeError:
                        continue
                  except KeyError:
                        continue
            annual_bs_stmts.append(statement)
      temp_dir['BalanceSheetStatement'] = annual_bs_stmts
      
      
      #Repeat the process for the Key-Statistics part       
      response = requests.get(url_stat.format(ticker, ticker)) #Fill the 1rst and 2nd {} in url_financials with ticker
      soup = BeautifulSoup(response.text, 'html.parser')
      pattern = re.compile(r'\s--\sData\s--\s')#Since there is nothing really unique about the script that identifies it as a tag, We'll have to use a text pattern with regular expressions
      script_data = soup.find('script', text=pattern).contents[0]#Use this pattern to find the script element that has text that matches this pattern, return the content (this returns as a list so we'll have to take the first (and only) element of it)
      start = script_data.find("context")-2
      final = -12
      json_data = json.loads(script_data[start:final]) #dictionary with all the data
        
      key_stats = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['defaultKeyStatistics']
           
      key_stats_stmts = []
      statement = {}
      for key, val in key_stats.items():
            try:
                  statement[key]= val['raw']
            except TypeError:
                  continue
            except KeyError:
                  continue
      key_stats_stmts.append(statement)
      temp_dir['KeyStatistics'] = key_stats_stmts
      
      financial_dir[ticker] = temp_dir











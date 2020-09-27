# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:35:29 2020

@author: Eric
"""
# ============================================================================
# Getting financial data from yahoo finance using webscraping
# =============================================================================


'''
This is the basic syntax of an HTML webpage. Every <tag> serves a block inside the webpage:
1. <!DOCTYPE html>: HTML documents must start with a type declaration.
2. The HTML document is contained between <html> and </html>.
3. The meta and script declaration of the HTML document is between <head>and </head>.
4. The visible part of the HTML document is between <body> and </body>tags.
5. Title headings are defined with the <h1> through <h6> tags.
6. Paragraphs are defined with the <p> tag.

Other useful tags include <a> for hyperlinks, <table> for tables, <tr> for table rows, and <td> for table columns.

Also, HTML tags sometimes come with id or class attributes. The id attribute specifies a unique id for an HTML tag 
and the value must be unique within the HTML document. The class attribute is used to define equal styles for HTML 
tags with the same class. We can make use of these ids and classes to help us locate the data we want.
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd

tickers = ["AAPL","MSFT"] #list of tickers whose financial data needs to be extracted
financial_dir = {} #I prefer using dictionary instead of lists but you could also use lists. Importing a dic to a pandas df is really easy

''' 
If we search any Balance Sheet of any Ticker in Yahoo Finance, by clicking inspect, we will realize that in the HTML script of the table:
- Table rows in the table have the class D(tbr)
- Values such as the title "Cash And Cash Equivalents" and the numbers like "115,184" for example, are within a span within each row
'''

for ticker in tickers:
    #getting balance sheet data from yahoo finance for the given ticker
    temp_dir = {}

    url = 'https://finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
    page = requests.get(url)
    page_content = page.content #This gets everything from page
    soup = BeautifulSoup(page_content,'html.parser') # Initiate an object from BeautifulSoap that is a html parser of the page content
    tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"}) # tbal is the part of the html we are interesed in (it's the table with the data in the website). Find all the divisions (div) of "class" = "Lh(1.7) W(100%) M(0)" (is the specific name of the class we wanna get from the HTML (you see this info straightforward when u look at the HTML script)).
    #tabl is just a piece of the html script type(tabl)=bs4.ResultsSet. A table is a set of several tags
    for t in tabl: #For each tag in table
        rows = t.find_all("div", {"class" : "D(tbr)"}) #Find tr tags (table row) in t. In every tr you have to specify the format, spacing, etc of the numbers of the table. we only want the text so we still will have to clean the data
        for row in rows: #in every tr
            if len(row.get_text(separator='|').split("|")[0:2])>1: #Get text generates a string with just the hard coded text of the HTML (each part separated with "|"). Then split converts it into a list of elements delimitated by |. Then, we just take the first 2 elements corresponding to the title of the row and the last year's data. The if >1 is because there are some rows with just one element: a title and no numerical values
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1] #Building the dictionary with the title and the numerical value
    
    #getting income statement data from yahoo finance for the given ticker
    url = 'https://finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
    for t in tabl:
        rows = t.find_all("div", {"class" : "D(tbr)"})
        for row in rows:
            if len(row.get_text(separator='|').split("|")[0:3])>1:
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]

    #getting cashflow statement data from yahoo finance for the given ticker
    url = 'https://finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
    for t in tabl:
        rows = t.find_all("div", {"class" : "D(tbr)"})
        rw_expanded = t.find_all("div")
        for row in rows:
            if len(row.get_text(separator='|').split("|")[0:3])>1:
                temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
          
    #getting key statistics data from yahoo finance for the given ticker
    url = 'https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    tabl = soup.find_all("table") #We've got a regular table now
    for t in tabl:
        rows = t.find_all("tr") #rows are now of class tr
        for row in rows:
            if len(row.get_text(separator='|').split("|")[0:2])>0:
                a = row.get_text(separator='|').split("|")
                temp_dir[a[0]]=a[-1]    

    #combining all extracted information with the corresponding ticker into a nested dictionary finantial_dir
    financial_dir[ticker] = temp_dir



#storing information in pandas dataframe
combined_financials = pd.DataFrame(financial_dir)
tickers = combined_financials.columns
for ticker in tickers:
    combined_financials = combined_financials[~combined_financials[ticker].str.contains("[a-z]",na=False)] # Panda_Series.str can be used to access the values of the series as strings and apply several methods to it. .contains("[a-z]") function is used to test if pattern or regex is contained within a string of a Series or Index. The function return boolean Series or Index based on whether a given pattern or regex is contained within a string of a Series or Index. Not capital letters since Billions = B and Trilions = T
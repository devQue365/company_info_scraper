import requests
import yfinance as yf
from tabulate import tabulate
import pandas as pd
import csv
import feedparser
from newspaper import Article
def extract_ticker(company_name):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
    mock_header = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers = mock_header)
    results = response.json().get("quotes", [])
    for result in results:
        if "symbol" in result and "shortname" in result:
            return result["symbol"]
    return None


def extract_stock_data(t_object, period = 'max'): 
    # fetch data accoding to your need
    data = t_object.history(period = period)
    # return the data
    return data

def extract_news(company_name):
    # Pass RSS url
    url = f"https://news.google.com/rss/search?q={company_name}+company+latest+insights"
    # Get the feed
    feed = feedparser.parse(url)
    if feed.bozo == True:
        # print('Error extracting news')
        return None
    # print(f'\033[1m\033[33m{len(feed.entries)} entries found !\033[0m')
    container = []
    # Examine each entry
    for entry in feed.entries[:5]:
        data = []
        # Get the title
        data.append(entry.title)
        data.append(entry.published if 'published' in entry else 'Unknown')
        data.append(entry.author if 'author' in entry else 'Unknown')
        # data.append(entry.summary if 'summary' in entry else None)
        data.append(entry.link)
        # Create newspaper object
        article = Article(entry.link)
        # download the article
        article.download()
        article.parse()
        # Get the text
        data.append(article.text[:300])
        # Add to the main container
        container.append(data)
    return container



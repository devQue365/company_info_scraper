import requests
import yfinance as yf
from tabulate import tabulate
import pandas as pd
import csv
import feedparser
from newspaper import Article
import time
# main scraping libraries / modules
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from app.Parser import customizedParser
mock_header = {
        "User-Agent": "Mozilla/5.0"
    }

def extract_about(company_name):
    try:
        # First of all request data from yfinance API
        # create a ticker object
        ticker = extract_ticker(company_name)
        t_object = yf.Ticker(ticker)
        # get company's information
        information = t_object.info
        # request company's longBusinessSummary
        if 'longBusinessSummary' in information:
            business_summary = information['longBusinessSummary']
            return business_summary
        options = uc.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        # if(headless):
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows") 
        options.add_argument("--disable-renderer-backgrounding")  
        options.add_argument("--blink-settings=imagesEnabled=false")
        driver = webdriver.Chrome(options = options)
        # sanitize the query
        company_name+=' company'
        company_name = company_name.replace('+',' plus ').replace('-',' minus ')
        url = f"https://www.google.com/search?q={company_name.replace(' ', '+')}"
        # url = f"https://www.google.com/search?q={company}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 5)
        # wiki_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='Q7PwXb a-no-hover-decoration ztWovc']")))
        wiki_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='y171A Q7PwXb a-no-hover-decoration' or @class='Q7PwXb a-no-hover-decoration ztWovc']")))
        wiki_link.click()
        # wait for sometime
        time.sleep(5)
        wiki_src = driver.page_source
        soup = BeautifulSoup(wiki_src, 'html.parser')
        # select paragraph tag
        p = soup.select('p')
        for each_para in p:
            # select only valuable text
            if(len(each_para.text.strip()) > 150):
                return each_para.text.strip()
    except Exception as e:
        return None
    
def extract_salary(company_name, job_title):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options)
    url = f"https://www.levels.fyi/companies/{company_name}/salaries/{job_title.replace(' ','-')}"
    driver.get(url)
    driver.maximize_window()
    
    try:
        # Wait for the clickable button
        wait = WebDriverWait(driver, 10)
        view_more_levels = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textNeutral MuiButton-sizeLarge MuiButton-textSizeLarge MuiButton-colorNeutral MuiButton-root MuiButton-text MuiButton-textNeutral MuiButton-sizeLarge MuiButton-textSizeLarge MuiButton-colorNeutral css-y5b368']")))
        view_more_levels.click()
        print('clicked sir')
        time.sleep(2)
    except Exception as e:
        pass
    # get the raw html
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    driver.close()
    # get the table
    table = soup.find('table', class_ = 'MuiTable-root css-1f6fkxk')
    if not table:
        return None
    # print('table found')
    result = []
    # find tbody
    try:
        tbody = table.find('tbody', class_ = 'MuiTableBody-root job-family_tableBody__MaiIw css-1xnox0e')
        if not tbody:
            return None
        # print('found tbody')
        # find all rows
        rows = tbody.find_all('tr', class_ = 'MuiTableRow-root job-family_bodyRow__WuAug css-140sacz')
        # traver each row
        for row in rows:
            # get columns as td value
            col = row.find_all('td', class_ = 'MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft MuiTableCell-sizeMedium css-k1mugk')
            # we want minimum results
            if len(col) >= 5:
                salary_record = {
                    'level': col[0].get_text(strip = True),
                    'Total': col[1].get_text(strip = True),
                    'Base': col[2].get_text(strip = True),
                    'Stock (/yr)': col[3].get_text(strip = True),
                    'Bonus': col[4].get_text(strip = True)
                }
                result.append(salary_record)
        return result
    except Exception as e:
        return None
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


def extract_stock_data(t_object, period = '1d'): 
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